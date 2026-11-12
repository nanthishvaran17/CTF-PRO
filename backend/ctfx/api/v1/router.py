import asyncio
import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...config import settings
from ...db.session import get_db
from ...db.models import (
    Challenge, ChallengeFile, FileHash, AnalysisJob, AnalysisResult,
    CandidateFlag, FlagEvidence, DecodingOperation, VerificationEvent,
    ExtractedArtifact, Report, AuditLog
)
from ...engines.intake import FileIntakeEngine
from ...engines.evidence import (
    EvidenceGraphBuilder, ReproduceScriptGenerator,
    AutoWriteupGenerator, SmartTriageEngine
)
from ...engines.verifier import CandidateVerifier, FlagStatus
from ...core.orchestrator import AnalysisOrchestrator, event_bus
from ...tools.manager import ToolInventoryManager
from ...tools.ai_advisor import AIAdvisor
from ...plugins.base import PluginManager
from ...reporting.exporter import ReportExporter

router = APIRouter(prefix="/api/v1")

# Pydantic Schemas
class ChallengeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    category: str = Field("Misc", max_length=64)
    description: str = Field("", max_length=10000)
    flag_format: Optional[str] = Field(None, max_length=128)

class ValidateRequest(BaseModel):
    validator: str = Field("analyst_verification", max_length=128)
    is_success: bool
    raw_response: str = Field("", max_length=4096)
    notes: Optional[str] = Field(None, max_length=512)

class ReportRequest(BaseModel):
    challenge_id: str
    format: str = Field("HTML", pattern="^(HTML|JSON|CSV|PDF)$")

# --- Challenge Endpoints ---

@router.post("/challenges", status_code=status.HTTP_201_CREATED)
async def create_challenge(payload: ChallengeCreate, db: AsyncSession = Depends(get_db)):
    c = Challenge(
        title=payload.title,
        category=payload.category,
        description=payload.description,
        flag_format=payload.flag_format
    )
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return {"id": c.id, "title": c.title, "category": c.category, "created_at": c.created_at.isoformat()}

@router.get("/challenges")
async def list_challenges(db: AsyncSession = Depends(get_db)):
    stmt = select(Challenge).order_by(desc(Challenge.created_at))
    res = await db.execute(stmt)
    challenges = res.scalars().all()

    out = []
    for c in challenges:
        # Count files
        fc = (await db.execute(select(func.count(ChallengeFile.id)).where(ChallengeFile.challenge_id == c.id))).scalar() or 0
        flc = (await db.execute(select(func.count(CandidateFlag.id)).where(CandidateFlag.challenge_id == c.id))).scalar() or 0
        vlc = (await db.execute(select(func.count(CandidateFlag.id)).where(
            CandidateFlag.challenge_id == c.id, CandidateFlag.status == "VERIFIED-BY-CHALLENGE"
        ))).scalar() or 0

        out.append({
            "id": c.id,
            "title": c.title,
            "category": c.category,
            "status": c.status,
            "file_count": fc,
            "candidate_count": flc,
            "verified_count": vlc,
            "created_at": c.created_at.isoformat()
        })
    return out

@router.get("/challenges/{challenge_id}")
async def get_challenge(challenge_id: str, db: AsyncSession = Depends(get_db)):
    c = await db.get(Challenge, challenge_id)
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    files = (await db.execute(select(ChallengeFile).where(ChallengeFile.challenge_id == challenge_id))).scalars().all()
    candidates = (await db.execute(select(CandidateFlag).where(CandidateFlag.challenge_id == challenge_id))).scalars().all()
    
    return {
        "id": c.id,
        "title": c.title,
        "category": c.category,
        "description": c.description,
        "flag_format": c.flag_format,
        "status": c.status,
        "created_at": c.created_at.isoformat(),
        "files": [{
            "id": f.id, "name": f.name, "sha256": f.sha256,
            "size_bytes": f.size_bytes, "file_type": f.file_type,
            "mime_type": f.mime_type, "entropy": f.entropy,
            "has_trailing_bytes": f.has_trailing_bytes
        } for f in files],
        "candidates": [{
            "id": cand.id, "flag": cand.flag, "status": cand.status,
            "is_probable_decoy": cand.is_probable_decoy,
            "byte_offset": cand.byte_offset, "extraction_method": cand.extraction_method
        } for cand in candidates]
    }

@router.delete("/challenges/{challenge_id}")
async def delete_challenge(challenge_id: str, db: AsyncSession = Depends(get_db)):
    c = await db.get(Challenge, challenge_id)
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")
    await db.delete(c)
    await db.commit()
    return {"message": "Challenge deleted successfully"}

# --- File Intake & Hex View ---

@router.post("/challenges/{challenge_id}/files")
async def upload_files(
    challenge_id: str,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    c = await db.get(Challenge, challenge_id)
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")

    uploaded = []
    temp_dir = settings.DATA_DIR / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    for upload in files:
        temp_file = temp_dir / upload.filename
        content = await upload.read()
        temp_file.write_bytes(content)

        # Ingest through content-addressed engine
        intake_res = FileIntakeEngine.ingest_file(temp_file, settings.STORAGE_DIR)
        temp_file.unlink(missing_ok=True)

        cf = ChallengeFile(
            challenge_id=challenge_id,
            name=upload.filename,
            sha256=intake_res["sha256"],
            size_bytes=intake_res["size_bytes"],
            file_type=intake_res["file_type"],
            mime_type=intake_res["mime_type"],
            storage_path=intake_res["stored_path"],
            entropy=intake_res["entropy"],
            has_trailing_bytes=bool(intake_res.get("trailing_anomaly"))
        )
        db.add(cf)
        uploaded.append({
            "name": upload.filename,
            "sha256": intake_res["sha256"],
            "size_bytes": intake_res["size_bytes"],
            "file_type": intake_res["file_type"],
            "mime_type": intake_res["mime_type"],
            "entropy": intake_res["entropy"]
        })

    await db.commit()
    return {"uploaded_count": len(uploaded), "files": uploaded}

@router.get("/files/{file_id}/hex")
async def get_file_hex(
    file_id: str,
    offset: int = Query(0, ge=0),
    length: int = Query(512, ge=16, le=4096),
    db: AsyncSession = Depends(get_db)
):
    cf = await db.get(ChallengeFile, file_id)
    if not cf:
        raise HTTPException(status_code=404, detail="File not found")

    p = Path(cf.storage_path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Storage file not found on disk")

    with open(p, "rb") as f:
        f.seek(offset)
        chunk = f.read(length)

    hex_rows = []
    for i in range(0, len(chunk), 16):
        row_slice = chunk[i:i+16]
        hex_part = " ".join(f"{b:02x}" for b in row_slice)
        ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in row_slice)
        hex_rows.append({
            "offset": hex(offset + i),
            "offset_dec": offset + i,
            "hex": hex_part.ljust(48),
            "ascii": ascii_part
        })

    return {
        "file_id": file_id,
        "filename": cf.name,
        "total_size": cf.size_bytes,
        "offset": offset,
        "length": len(chunk),
        "rows": hex_rows
    }

# --- Analysis Orchestration ---

@router.post("/analysis/{challenge_id}/start")
async def start_analysis(challenge_id: str, db: AsyncSession = Depends(get_db)):
    c = await db.get(Challenge, challenge_id)
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")

    job = AnalysisJob(challenge_id=challenge_id, status="PENDING", progress=0)
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Launch worker task in background
    asyncio.create_task(AnalysisOrchestrator.run_job(job.id))
    return {"job_id": job.id, "status": "PENDING", "message": "Analysis initiated"}

@router.get("/analysis/{challenge_id}/status")
async def get_analysis_status(challenge_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(AnalysisJob).where(AnalysisJob.challenge_id == challenge_id).order_by(desc(AnalysisJob.started_at))
    job = (await db.execute(stmt)).scalars().first()
    if not job:
        return {"status": "NO_JOBS", "progress": 0}
    return {
        "job_id": job.id,
        "status": job.status,
        "progress": job.progress,
        "error_message": job.error_message,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None
    }

@router.get("/analysis/{challenge_id}/results")
async def get_analysis_results(challenge_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(AnalysisJob).where(AnalysisJob.challenge_id == challenge_id).order_by(desc(AnalysisJob.started_at))
    job = (await db.execute(stmt)).scalars().first()
    if not job:
        return {"results": []}

    res_stmt = select(AnalysisResult).where(AnalysisResult.job_id == job.id)
    results = (await db.execute(res_stmt)).scalars().all()
    return {
        "job_id": job.id,
        "status": job.status,
        "results": [{
            "module": r.module,
            "summary": r.summary,
            "data": json.loads(r.data_json),
            "created_at": r.created_at.isoformat()
        } for r in results]
    }

# --- Flag Candidates & Verification Engine ---

@router.get("/flags/candidates")
async def list_candidates(
    challenge_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(CandidateFlag)
    if challenge_id:
        stmt = stmt.where(CandidateFlag.challenge_id == challenge_id)
    if status_filter:
        stmt = stmt.where(CandidateFlag.status == status_filter)

    res = (await db.execute(stmt.order_by(desc(CandidateFlag.created_at)))).scalars().all()
    out = []
    for cand in res:
        out.append({
            "id": cand.id,
            "challenge_id": cand.challenge_id,
            "source_file_id": cand.source_file_id,
            "flag": cand.flag,
            "status": cand.status,
            "is_probable_decoy": cand.is_probable_decoy,
            "evidence_reasons": json.loads(cand.evidence_reasons_json or "[]"),
            "byte_offset": cand.byte_offset,
            "encoding": cand.encoding,
            "extraction_method": cand.extraction_method,
            "created_at": cand.created_at.isoformat()
        })
    return out

@router.get("/flags/{candidate_id}/evidence")
async def get_flag_evidence(candidate_id: str, db: AsyncSession = Depends(get_db)):
    cand = await db.get(CandidateFlag, candidate_id)
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")

    evidence = (await db.execute(select(FlagEvidence).where(FlagEvidence.candidate_id == candidate_id))).scalars().all()
    decodes = (await db.execute(select(DecodingOperation).where(DecodingOperation.candidate_id == candidate_id).order_by(DecodingOperation.step_index))).scalars().all()
    events = (await db.execute(select(VerificationEvent).where(VerificationEvent.candidate_id == candidate_id).order_by(desc(VerificationEvent.created_at)))).scalars().all()

    return {
        "candidate": {
            "id": cand.id,
            "flag": cand.flag,
            "status": cand.status,
            "byte_offset": cand.byte_offset,
            "extraction_method": cand.extraction_method,
            "evidence_reasons": json.loads(cand.evidence_reasons_json or "[]")
        },
        "evidence_snippets": [{
            "start_offset": e.start_offset,
            "end_offset": e.end_offset,
            "snippet": e.snippet,
            "hex_preview": e.hex_preview
        } for e in evidence],
        "decode_chain": [{
            "step": d.step_index,
            "method": d.method,
            "input_preview": d.input_preview,
            "output_preview": d.output_preview
        } for d in decodes],
        "verification_events": [{
            "validator": ev.validator,
            "result": ev.result,
            "new_status": ev.new_status,
            "raw_response": ev.raw_response,
            "notes": ev.notes,
            "timestamp": ev.created_at.isoformat()
        } for ev in events]
    }

@router.post("/flags/{candidate_id}/validate")
async def validate_candidate(candidate_id: str, payload: ValidateRequest, db: AsyncSession = Depends(get_db)):
    cand = await db.get(CandidateFlag, candidate_id)
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")

    new_status = FlagStatus.VERIFIED_BY_CHALLENGE.value if payload.is_success else FlagStatus.REJECTED.value
    cand.status = new_status

    event = VerificationEvent(
        candidate_id=candidate_id,
        validator=payload.validator,
        result="ACCEPTED" if payload.is_success else "REJECTED",
        new_status=new_status,
        raw_response=payload.raw_response,
        notes=payload.notes or ""
    )
    db.add(event)
    await db.commit()

    await event_bus.broadcast("flag_validated", {
        "candidate_id": candidate_id,
        "status": new_status,
        "result": event.result
    })

    return {"message": "Validation event recorded", "status": new_status}

@router.get("/flags/{candidate_id}/repro")
async def get_repro_script(candidate_id: str, db: AsyncSession = Depends(get_db)):
    cand = await db.get(CandidateFlag, candidate_id)
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")

    decodes = (await db.execute(select(DecodingOperation).where(DecodingOperation.candidate_id == candidate_id).order_by(DecodingOperation.step_index))).scalars().all()
    
    cand_dict = {
        "flag": cand.flag,
        "byte_offset": cand.byte_offset,
        "extraction_method": cand.extraction_method,
        "transform_chain": [{"step": d.step_index, "method": d.method, "input_preview": d.input_preview} for d in decodes]
    }
    script = ReproduceScriptGenerator.generate_python_script(cand_dict)
    return {"candidate_id": candidate_id, "flag": cand.flag, "python_script": script}

# --- Signature Features: Graph, Writeup & Triage ---

@router.get("/challenges/{challenge_id}/evidence-graph")
async def get_evidence_graph(challenge_id: str, db: AsyncSession = Depends(get_db)):
    c = await db.get(Challenge, challenge_id)
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")

    files = (await db.execute(select(ChallengeFile).where(ChallengeFile.challenge_id == challenge_id))).scalars().all()
    artifacts = (await db.execute(select(ExtractedArtifact))).scalars().all()
    candidates = (await db.execute(select(CandidateFlag).where(CandidateFlag.challenge_id == challenge_id))).scalars().all()

    file_dicts = [{"id": f.id, "name": f.name, "sha256": f.sha256, "file_type": f.file_type} for f in files]
    art_dicts = [{"id": a.id, "name": a.name, "sha256": a.sha256, "parent_id": a.parent_file_id} for a in artifacts]
    
    cand_dicts = []
    for cand in candidates:
        decodes = (await db.execute(select(DecodingOperation).where(DecodingOperation.candidate_id == cand.id).order_by(DecodingOperation.step_index))).scalars().all()
        cand_dicts.append({
            "id": cand.id,
            "flag": cand.flag,
            "status": cand.status,
            "byte_offset": cand.byte_offset,
            "source_file_id": cand.source_file_id,
            "extraction_method": cand.extraction_method,
            "transform_chain": [{"step": d.step_index, "method": d.method} for d in decodes]
        })

    graph = EvidenceGraphBuilder.build_graph(file_dicts, art_dicts, cand_dicts)
    return graph

@router.get("/challenges/{challenge_id}/writeup")
async def get_challenge_writeup(challenge_id: str, db: AsyncSession = Depends(get_db)):
    c = await db.get(Challenge, challenge_id)
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")

    files = (await db.execute(select(ChallengeFile).where(ChallengeFile.challenge_id == challenge_id))).scalars().all()
    candidates = (await db.execute(select(CandidateFlag).where(CandidateFlag.challenge_id == challenge_id))).scalars().all()

    file_dicts = [{"name": f.name, "sha256": f.sha256, "size_bytes": f.size_bytes, "file_type": f.file_type, "entropy": f.entropy} for f in files]
    cand_dicts = []
    for cand in candidates:
        decodes = (await db.execute(select(DecodingOperation).where(DecodingOperation.candidate_id == cand.id).order_by(DecodingOperation.step_index))).scalars().all()
        cand_dicts.append({
            "flag": cand.flag,
            "status": cand.status,
            "byte_offset": cand.byte_offset,
            "extraction_method": cand.extraction_method,
            "is_probable_decoy": cand.is_probable_decoy,
            "evidence_reasons": json.loads(cand.evidence_reasons_json or "[]"),
            "transform_chain": [{"step": d.step_index, "method": d.method, "output_preview": d.output_preview} for d in decodes]
        })

    md = AutoWriteupGenerator.generate_markdown(c.title, file_dicts, cand_dicts, notes=c.description)
    return {"challenge_id": challenge_id, "writeup_markdown": md}

@router.get("/challenges/{challenge_id}/triage")
async def get_challenge_triage(challenge_id: str, db: AsyncSession = Depends(get_db)):
    c = await db.get(Challenge, challenge_id)
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")

    files = (await db.execute(select(ChallengeFile).where(ChallengeFile.challenge_id == challenge_id))).scalars().all()
    all_recommendations = []
    for f in files:
        file_info = {
            "file_type": f.file_type,
            "entropy": f.entropy,
            "trailing_anomaly": {"has_trailing_bytes": f.has_trailing_bytes} if f.has_trailing_bytes else None
        }
        recs = SmartTriageEngine.recommend_next_steps(file_info, c.description)
        for r in recs:
            r["target_file"] = f.name
            all_recommendations.append(r)

    # Also obtain rule-based hypothesis
    f_type = files[0].file_type if files else "UNKNOWN"
    hypothesis = AIAdvisor.generate_rule_based_hypothesis(f_type, c.description)

    return {
        "challenge_id": challenge_id,
        "recommendations": all_recommendations,
        "ai_hypothesis": hypothesis
    }

# --- Tools, Plugins & Dashboard ---

@router.get("/tools")
async def list_tools():
    return ToolInventoryManager.get_inventory()

@router.get("/plugins")
async def list_plugins():
    pm = PluginManager(settings.PLUGINS_DIR)
    pm.discover_and_load()
    return pm.get_plugin_list()

@router.get("/dashboard/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    # All counts computed strictly from DB queries
    challenges_count = (await db.execute(select(func.count(Challenge.id)))).scalar() or 0
    files_count = (await db.execute(select(func.count(ChallengeFile.id)))).scalar() or 0
    candidates_count = (await db.execute(select(func.count(CandidateFlag.id)))).scalar() or 0
    verified_count = (await db.execute(select(func.count(CandidateFlag.id)).where(CandidateFlag.status == "VERIFIED-BY-CHALLENGE"))).scalar() or 0
    pending_count = (await db.execute(select(func.count(CandidateFlag.id)).where(CandidateFlag.status.in_(["CANDIDATE", "VALIDATION-PENDING"])))).scalar() or 0
    rejected_count = (await db.execute(select(func.count(CandidateFlag.id)).where(CandidateFlag.status == "REJECTED"))).scalar() or 0

    tool_inv = ToolInventoryManager.get_inventory()
    tools_installed = sum(1 for t in tool_inv if t["is_installed"])

    recent_challenges = (await db.execute(select(Challenge).order_by(desc(Challenge.created_at)).limit(5))).scalars().all()

    return {
        "challenges_total": challenges_count,
        "files_analyzed": files_count,
        "candidates_total": candidates_count,
        "verified_flags": verified_count,
        "pending_flags": pending_count,
        "rejected_flags": rejected_count,
        "tools_installed": tools_installed,
        "tools_total": len(tool_inv),
        "recent_challenges": [{"id": c.id, "title": c.title, "created_at": c.created_at.isoformat()} for c in recent_challenges]
    }

# --- Reports ---

@router.post("/reports/generate")
async def generate_report(payload: ReportRequest, db: AsyncSession = Depends(get_db)):
    c = await db.get(Challenge, payload.challenge_id)
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")

    files = (await db.execute(select(ChallengeFile).where(ChallengeFile.challenge_id == c.id))).scalars().all()
    candidates = (await db.execute(select(CandidateFlag).where(CandidateFlag.challenge_id == c.id))).scalars().all()

    c_data = {
        "id": c.id,
        "title": c.title,
        "category": c.category,
        "files": [{"name": f.name, "sha256": f.sha256, "file_type": f.file_type, "size_bytes": f.size_bytes, "entropy": f.entropy} for f in files],
        "candidates": [{
            "flag": cand.flag,
            "status": cand.status,
            "source_sha256": cand.source_file_id,
            "byte_offset": cand.byte_offset,
            "extraction_method": cand.extraction_method,
            "evidence_reasons": json.loads(cand.evidence_reasons_json or "[]")
        } for cand in candidates]
    }

    out_file = settings.REPORTS_DIR / f"report_{c.id}_{payload.format.lower()}.{payload.format.lower()}"
    if payload.format == "JSON":
        ReportExporter.export_json(c_data, out_file)
    elif payload.format == "CSV":
        ReportExporter.export_csv(c_data, out_file)
    elif payload.format == "HTML":
        ReportExporter.export_html(c_data, out_file)
    elif payload.format == "PDF":
        ReportExporter.export_pdf(c_data, out_file)

    rep = Report(
        challenge_id=c.id,
        format=payload.format,
        title=f"Report for {c.title}",
        content_path=str(out_file),
        summary_json=json.dumps({"files": len(files), "candidates": len(candidates)})
    )
    db.add(rep)
    await db.commit()
    await db.refresh(rep)

    return {"report_id": rep.id, "format": payload.format, "download_url": f"/api/v1/reports/{rep.id}/download"}

@router.get("/reports/{report_id}/download")
async def download_report(report_id: str, db: AsyncSession = Depends(get_db)):
    rep = await db.get(Report, report_id)
    if not rep or not Path(rep.content_path).exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(rep.content_path, filename=Path(rep.content_path).name)

# --- SSE Stream ---

@router.get("/events/stream")
async def event_stream():
    q = event_bus.subscribe()
    async def sse_gen():
        try:
            while True:
                msg = await q.get()
                yield f"data: {json.dumps(msg)}\n\n"
        except asyncio.CancelledError:
            event_bus.unsubscribe(q)
    return StreamingResponse(sse_gen(), media_type="text/event-stream")
