import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import AsyncSessionLocal
from ..db.models import (
    Challenge, ChallengeFile, AnalysisJob, AnalysisResult,
    CandidateFlag, FlagEvidence, DecodingOperation, ExtractedArtifact
)
from ..engines.intake import FileIntakeEngine
from ..engines.archive import SafeArchiveExtractor, ArchiveSecurityError
from ..engines.strings import StringsExtractor
from ..engines.flag_finder import FlagFinder
from ..engines.decoder import MultiLayerDecoder
from ..engines.verifier import CandidateVerifier, FlagStatus
from ..modules.stego import StegoAnalyzer
from ..modules.forensics import ForensicsAnalyzer
from ..modules.crypto import CryptoAnalyzer
from ..modules.re import ReverseEngineeringAnalyzer
from ..modules.media import MediaAnalyzer
from ..plugins.base import PluginManager
from ..config import settings

logger = logging.getLogger(__name__)

class EventBus:
    """In-memory broadcast queue for SSE events."""
    def __init__(self):
        self.subscribers: List[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self.subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        if q in self.subscribers:
            self.subscribers.remove(q)

    async def broadcast(self, event_type: str, data: Dict[str, Any]) -> None:
        msg = {"type": event_type, "timestamp": datetime.now(timezone.utc).isoformat(), "data": data}
        for q in list(self.subscribers):
            try:
                await q.put(msg)
            except Exception:
                pass

event_bus = EventBus()

class AnalysisOrchestrator:
    """Asynchronous background worker executing modular CTF analysis pipeline."""

    @classmethod
    async def run_job(cls, job_id: str) -> None:
        """Entrypoint for executing an analysis job in background."""
        async with AsyncSessionLocal() as db:
            job = await db.get(AnalysisJob, job_id)
            if not job:
                return

            job.status = "RUNNING"
            job.progress = 5
            job.started_at = datetime.now(timezone.utc)
            await db.commit()
            await event_bus.broadcast("job_started", {"job_id": job_id, "challenge_id": job.challenge_id})

            try:
                # 1. Fetch challenge and files
                challenge = await db.get(Challenge, job.challenge_id)
                files_stmt = select(ChallengeFile).where(ChallengeFile.challenge_id == job.challenge_id)
                res = await db.execute(files_stmt)
                files = res.scalars().all()

                custom_patterns = []
                if challenge and challenge.flag_format:
                    custom_patterns.append(challenge.flag_format)
                elif challenge and challenge.description:
                    auto_pat = FlagFinder.auto_detect_format_from_text(challenge.description)
                    if auto_pat:
                        custom_patterns.append(auto_pat)

                finder = FlagFinder(custom_regexes=custom_patterns)
                decoder = MultiLayerDecoder()
                plugin_mgr = PluginManager(settings.PLUGINS_DIR)
                plugin_mgr.discover_and_load()

                total_files = max(len(files), 1)
                for idx, c_file in enumerate(files):
                    file_path = Path(c_file.storage_path)
                    if not file_path.exists():
                        continue

                    # Update progress
                    job.progress = 10 + int((idx / total_files) * 80)
                    await db.commit()
                    await event_bus.broadcast("job_progress", {"job_id": job_id, "progress": job.progress})

                    # --- Step A: Strings Scan ---
                    strings_results = StringsExtractor.scan_file(file_path, min_length=4)
                    for s in strings_results:
                        # Check direct string match
                        matches = finder.scan_text(s["value"])
                        for m in matches:
                            await cls._record_candidate(
                                db, challenge.id, c_file.id, c_file.sha256,
                                m["flag"], s["offset"], s["encoding"], s["method"],
                                None, s["value"]
                            )

                        # Check multi-layer decode if candidate looks like base64 / hex
                        if len(s["value"]) >= 8 and len(s["value"]) <= 2048:
                            dec_results = decoder.decode_chain(s["value"])
                            for d in dec_results:
                                await cls._record_candidate(
                                    db, challenge.id, c_file.id, c_file.sha256,
                                    d["flag"], s["offset"], s["encoding"], "multilayer_decode",
                                    d["history"], s["value"]
                                )

                    # --- Step B: Format-Specific Domain Analysis ---
                    ftype = c_file.file_type

                    # Steganography
                    if ftype == "PNG" or ftype == "JPEG":
                        stego_res = StegoAnalyzer.analyze_png_chunks(file_path) if ftype == "PNG" else {}
                        lsb_res = StegoAnalyzer.extract_lsb(file_path)
                        for f in lsb_res.get("flags_found", []):
                            await cls._record_candidate(
                                db, challenge.id, c_file.id, c_file.sha256,
                                f["flag"], f.get("byte_offset", 0), "binary", "lsb_extract",
                                None, "Extracted from image LSB"
                            )
                        await cls._record_result(db, job_id, "stego", f"Stego scan: {len(lsb_res.get('flags_found', []))} flags", {**stego_res, **lsb_res})

                    # Network Forensics
                    elif ftype in ("PCAP", "PCAPNG"):
                        pcap_res = ForensicsAnalyzer.analyze_pcap(file_path)
                        for f in pcap_res.get("flags_discovered", []):
                            await cls._record_candidate(
                                db, challenge.id, c_file.id, c_file.sha256,
                                f["flag"], f.get("byte_offset", 0), "raw", "pcap_stream",
                                None, "Extracted from PCAP stream"
                            )
                        await cls._record_result(db, job_id, "forensics", f"PCAP: {len(pcap_res.get('tcp_streams', []))} streams", pcap_res)

                    # Reverse Engineering
                    elif ftype in ("ELF", "PE", "MACHO_64", "MACHO_32"):
                        re_res = ReverseEngineeringAnalyzer.analyze_binary(file_path)
                        await cls._record_result(db, job_id, "reverse_engineering", f"{re_res.get('format')} {re_res.get('architecture')}", re_res)

                    # Audio / Video
                    elif ftype == "WAV":
                        wav_res = MediaAnalyzer.analyze_wav(file_path)
                        await cls._record_result(db, job_id, "media", f"WAV {wav_res.get('duration_seconds')}s", wav_res)

                    # Safe Archive Extraction
                    elif ftype in ("ZIP", "TAR", "GZIP"):
                        extractor = SafeArchiveExtractor()
                        art_dir = settings.ARTIFACTS_DIR / c_file.sha256
                        try:
                            extracted = extractor.extract_recursive(file_path, art_dir)
                            for item in extracted:
                                art_path = Path(item["path"])
                                a_hash, a_size = FileIntakeEngine.compute_sha256_and_size(art_path)
                                artifact = ExtractedArtifact(
                                    parent_file_id=c_file.id,
                                    name=item["name"],
                                    sha256=a_hash,
                                    size_bytes=a_size,
                                    storage_path=str(art_path),
                                    extraction_method="safe_archive_extract"
                                )
                                db.add(artifact)
                            await cls._record_result(db, job_id, "archive", f"Unpacked {len(extracted)} safe artifacts", {"files": extracted})
                        except ArchiveSecurityError as e:
                            await cls._record_result(db, job_id, "archive_security", "Security block triggered", {"error": str(e)})

                    # Run third-party plugins
                    plugin_out = plugin_mgr.run_plugins_for_file(file_path, ftype)
                    if plugin_out:
                        await cls._record_result(db, job_id, "plugins", f"Executed {len(plugin_out)} plugins", {"results": plugin_out})

                # Mark complete
                job.status = "COMPLETED"
                job.progress = 100
                job.completed_at = datetime.now(timezone.utc)
                await db.commit()
                await event_bus.broadcast("job_completed", {"job_id": job_id, "challenge_id": job.challenge_id})

            except Exception as e:
                logger.exception("Analysis job error")
                job.status = "FAILED"
                job.error_message = str(e)
                job.completed_at = datetime.now(timezone.utc)
                await db.commit()
                await event_bus.broadcast("job_failed", {"job_id": job_id, "error": str(e)})

    @staticmethod
    async def _record_candidate(
        db: AsyncSession,
        challenge_id: str,
        source_file_id: Optional[str],
        source_sha256: Optional[str],
        flag_text: str,
        offset: Optional[int],
        encoding: str,
        method: str,
        history: Optional[List[Dict[str, Any]]],
        source_context: str
    ) -> None:
        """Deduplicate and insert candidate flag with complete provenance and decoy classification."""
        stmt = select(CandidateFlag).where(
            CandidateFlag.challenge_id == challenge_id,
            CandidateFlag.flag == flag_text
        )
        existing = (await db.execute(stmt)).scalars().first()
        if existing:
            return

        cand_data = CandidateVerifier.create_candidate(
            flag=flag_text,
            source_file_id=source_file_id,
            source_sha256=source_sha256,
            byte_offset=offset,
            encoding=encoding,
            extraction_method=method,
            transform_chain=history,
            source_context=source_context
        )

        cand_db = CandidateFlag(
            challenge_id=challenge_id,
            source_file_id=source_file_id,
            flag=flag_text,
            status=cand_data["status"],
            is_probable_decoy=cand_data["is_probable_decoy"],
            evidence_reasons_json=json.dumps(cand_data["evidence_reasons"]),
            byte_offset=offset,
            encoding=encoding,
            extraction_method=method
        )
        db.add(cand_db)
        await db.flush()

        # Record FlagEvidence snippet
        evidence = FlagEvidence(
            candidate_id=cand_db.id,
            file_id=source_file_id,
            start_offset=offset or 0,
            end_offset=(offset or 0) + len(flag_text),
            snippet=source_context[:250],
            hex_preview=source_context[:64].encode("utf-8", errors="ignore").hex()
        )
        db.add(evidence)

        # Record decode operations if present
        if history:
            for step in history:
                op = DecodingOperation(
                    candidate_id=cand_db.id,
                    step_index=step.get("step", 1),
                    method=step.get("method", "decode"),
                    input_preview=step.get("input_preview", ""),
                    output_preview=step.get("output_preview", "")
                )
                db.add(op)

        await db.commit()
        await event_bus.broadcast("flag_discovered", {
            "candidate_id": cand_db.id,
            "flag": flag_text,
            "status": cand_db.status,
            "is_decoy": cand_db.is_probable_decoy
        })

    @staticmethod
    async def _record_result(
        db: AsyncSession,
        job_id: str,
        module: str,
        summary: str,
        data: Dict[str, Any]
    ) -> None:
        res = AnalysisResult(
            job_id=job_id,
            module=module,
            summary=summary,
            data_json=json.dumps(data)
        )
        db.add(res)
        await db.commit()
