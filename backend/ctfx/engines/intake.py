import hashlib
import math
import os
import re
import stat
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

CHUNK_SIZE = 64 * 1024  # 64 KB streaming chunk

class FileIntakeEngine:
    """Handles content-addressed streaming ingestion, cryptographic hashing, 
    magic-byte true-type detection, Shannon entropy, and structural anomalies."""

    MAGIC_SIGNATURES: List[Tuple[bytes, int, str, str]] = [
        # (signature, offset, type_code, mime_type)
        (b"\x89PNG\r\n\x1a\n", 0, "PNG", "image/png"),
        (b"\xff\xd8\xff", 0, "JPEG", "image/jpeg"),
        (b"GIF87a", 0, "GIF", "image/gif"),
        (b"GIF89a", 0, "GIF", "image/gif"),
        (b"BM", 0, "BMP", "image/bmp"),
        (b"II*\x00", 0, "TIFF", "image/tiff"),
        (b"MM\x00*", 0, "TIFF", "image/tiff"),
        (b"%PDF-", 0, "PDF", "application/pdf"),
        (b"7z\xbc\xaf\x27\x1c", 0, "7Z", "application/x-7z-compressed"),
        (b"\x1f\x8b", 0, "GZIP", "application/gzip"),
        (b"Rar!\x1a\x07\x00", 0, "RAR", "application/vnd.rar"),
        (b"Rar!\x1a\x07\x01\x00", 0, "RAR", "application/vnd.rar"),
        (b"\x7fELF", 0, "ELF", "application/x-executable"),
        (b"SQLite format 3\x00", 0, "SQLITE", "application/vnd.sqlite3"),
        # PCAP & PCAPNG
        (b"\xd4\xc3\xb2\xa1", 0, "PCAP", "application/vnd.tcpdump.pcap"),
        (b"\xa1\xb2\xc3\xd4", 0, "PCAP", "application/vnd.tcpdump.pcap"),
        (b"\x4d\x3c\xb2\xa1", 0, "PCAP", "application/vnd.tcpdump.pcap"),
        (b"\xa1\xb2\x3c\x4d", 0, "PCAP", "application/vnd.tcpdump.pcap"),
        (b"\x0a\x0d\x0d\x0a", 0, "PCAPNG", "application/x-pcapng"),
        # Mach-O
        (b"\xfe\xed\xfa\xce", 0, "MACHO_32", "application/x-mach-binary"),
        (b"\xce\xfa\xed\xfe", 0, "MACHO_32", "application/x-mach-binary"),
        (b"\xfe\xed\xfa\xcf", 0, "MACHO_64", "application/x-mach-binary"),
        (b"\xcf\xfa\xed\xfe", 0, "MACHO_64", "application/x-mach-binary"),
        (b"\xca\xfe\xba\xbe", 0, "MACHO_FAT", "application/x-mach-binary"),
        # Audio / Video
        (b"ID3", 0, "MP3", "audio/mpeg"),
        (b"OggS", 0, "OGG", "audio/ogg"),
        (b"fLaC", 0, "FLAC", "audio/flac"),
    ]

    @staticmethod
    def compute_sha256_and_size(file_path: Path) -> Tuple[str, int]:
        """Stream file in chunks to calculate SHA-256 and total byte size without full RAM load."""
        hasher = hashlib.sha256()
        total_size = 0
        with open(file_path, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                hasher.update(chunk)
                total_size += len(chunk)
        return hasher.hexdigest(), total_size

    @staticmethod
    def compute_entropy(file_path: Path, max_bytes: int = 10 * 1024 * 1024) -> float:
        """Calculate Shannon entropy (0.0 to 8.0) using streaming frequency analysis."""
        byte_counts = [0] * 256
        total_read = 0
        with open(file_path, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                for b in chunk:
                    byte_counts[b] += 1
                total_read += len(chunk)
                if total_read >= max_bytes:
                    break

        if total_read == 0:
            return 0.0

        entropy = 0.0
        for count in byte_counts:
            if count > 0:
                p = count / total_read
                entropy -= p * math.log2(p)
        return round(entropy, 4)

    @classmethod
    def detect_file_type(cls, file_path: Path) -> Dict[str, str]:
        """Detect true file type using magic bytes, structure analysis, and format inspection."""
        with open(file_path, "rb") as f:
            header = f.read(512)

        if not header:
            return {"type": "EMPTY", "mime": "application/x-empty", "description": "Empty file (0 bytes)"}

        # Check standard headers
        for sig, offset, type_code, mime in cls.MAGIC_SIGNATURES:
            if len(header) >= offset + len(sig):
                if header[offset:offset + len(sig)] == sig:
                    return {"type": type_code, "mime": mime, "description": f"{type_code} binary file"}

        # MP3 frame sync check (0xFFE0 mask)
        if len(header) >= 2 and header[0] == 0xFF and (header[1] & 0xE0) == 0xE0:
            return {"type": "MP3", "mime": "audio/mpeg", "description": "MPEG Audio Stream (MP3)"}

        # RIFF container checks (WAV or WEBP)
        if header.startswith(b"RIFF") and len(header) >= 12:
            riff_type = header[8:12]
            if riff_type == b"WAVE":
                return {"type": "WAV", "mime": "audio/wav", "description": "WAV Audio"}
            if riff_type == b"WEBP":
                return {"type": "WEBP", "mime": "image/webp", "description": "WebP Image"}
            return {"type": "RIFF", "mime": "application/x-riff", "description": f"RIFF Container ({riff_type.decode('latin1', 'ignore')})"}

        # ISO base media file format (MP4 / MOV)
        if len(header) >= 8 and header[4:8] == b"ftyp":
            brand = header[8:12].decode("latin1", "ignore").strip()
            return {"type": "MP4", "mime": "video/mp4", "description": f"MPEG-4 Container (brand: {brand})"}

        # Windows PE Executable check
        if header.startswith(b"MZ"):
            try:
                with open(file_path, "rb") as f:
                    f.seek(0x3C)
                    pe_offset_bytes = f.read(4)
                    if len(pe_offset_bytes) == 4:
                        pe_offset = int.from_bytes(pe_offset_bytes, byteorder="little")
                        f.seek(pe_offset)
                        if f.read(4) == b"PE\x00\x00":
                            return {"type": "PE", "mime": "application/vnd.microsoft.portable-executable", "description": "Windows Portable Executable (PE)"}
            except Exception:
                pass
            return {"type": "DOS_MZ", "mime": "application/x-dosexec", "description": "DOS MZ Executable"}

        # ZIP Container & Office documents (.docx, .xlsx, .pptx)
        if header.startswith(b"PK\x03\x04") or header.startswith(b"PK\x05\x06"):
            office_type = cls._inspect_zip_type(file_path)
            if office_type:
                return office_type
            return {"type": "ZIP", "mime": "application/zip", "description": "ZIP Archive"}

        # TAR archive check (USTAR at offset 257)
        if len(header) >= 262 and (header[257:262] == b"ustar" or header[257:265] == b"ustar  \x00"):
            return {"type": "TAR", "mime": "application/x-tar", "description": "POSIX tar Archive"}

        # Text format inspection (UTF-8, JSON, XML, HTML, CSV, TXT)
        text_info = cls._inspect_text_type(header)
        if text_info:
            return text_info

        return {"type": "BINARY", "mime": "application/octet-stream", "description": "Generic Binary Data"}

    @staticmethod
    def _inspect_zip_type(file_path: Path) -> Optional[Dict[str, str]]:
        """Determine if a ZIP container is an Office Open XML document or JAR."""
        import zipfile
        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                namelist = zf.namelist()
                if any(n.startswith("word/") for n in namelist):
                    return {"type": "DOCX", "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "description": "Microsoft Word Document (DOCX)"}
                if any(n.startswith("xl/") for n in namelist):
                    return {"type": "XLSX", "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "description": "Microsoft Excel Spreadsheet (XLSX)"}
                if any(n.startswith("ppt/") for n in namelist):
                    return {"type": "PPTX", "mime": "application/vnd.openxmlformats-officedocument.presentationml.presentation", "description": "Microsoft PowerPoint Presentation (PPTX)"}
                if any(n.startswith("META-INF/") for n in namelist):
                    return {"type": "JAR", "mime": "application/java-archive", "description": "Java Archive (JAR)"}
        except Exception:
            pass
        return None

    @staticmethod
    def _inspect_text_type(header: bytes) -> Optional[Dict[str, str]]:
        """Sniff text data for JSON, XML, SVG, HTML, CSV, or Plain Text."""
        try:
            text = header.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = header.decode("latin1")
            except Exception:
                return None

        # Check for SVG
        if "<svg" in text.lower():
            return {"type": "SVG", "mime": "image/svg+xml", "description": "Scalable Vector Graphics (SVG)"}

        # Check for HTML
        if any(tag in text.lower() for tag in ["<!doctype html", "<html", "<head", "<body"]):
            return {"type": "HTML", "mime": "text/html", "description": "HTML Document"}

        # Check for XML
        if text.strip().startswith("<?xml"):
            return {"type": "XML", "mime": "application/xml", "description": "XML Document"}

        # Check for JSON
        stripped = text.strip()
        if (stripped.startswith("{") and "}" in stripped) or (stripped.startswith("[") and "]" in stripped):
            return {"type": "JSON", "mime": "application/json", "description": "JSON Data"}

        # Printable character ratio for plain text
        printable = sum(1 for c in text if c.isprintable() or c in "\r\n\t")
        if len(text) > 0 and (printable / len(text)) > 0.85:
            # Check for CSV delimiter hints
            lines = text.strip().split("\n")
            if len(lines) > 1 and (lines[0].count(",") > 1 or lines[0].count(";") > 1):
                return {"type": "CSV", "mime": "text/csv", "description": "Comma-Separated Values (CSV)"}
            return {"type": "TXT", "mime": "text/plain", "description": "Plain Text"}

        return None

    @staticmethod
    def detect_trailing_bytes(file_path: Path, detected_type: str) -> Optional[Dict[str, Any]]:
        """Detect trailing or appended data beyond format boundaries (e.g., hidden payload after PNG IEND)."""
        file_size = os.path.getsize(file_path)
        if file_size < 16:
            return None

        if detected_type == "PNG":
            # PNG chunk ends with IEND + 4 bytes CRC
            with open(file_path, "rb") as f:
                content = f.read()
            iend_idx = content.find(b"IEND")
            if iend_idx != -1:
                expected_end = iend_idx + 8  # 4 bytes 'IEND' + 4 bytes CRC
                if expected_end < file_size:
                    trailing_len = file_size - expected_end
                    return {
                        "has_trailing_bytes": True,
                        "expected_end_offset": expected_end,
                        "trailing_byte_count": trailing_len,
                        "trailing_offset": expected_end,
                        "note": f"Found {trailing_len} trailing bytes beyond PNG IEND marker."
                    }

        elif detected_type == "JPEG":
            # JPEG ends with EOI marker \xFF\xD9
            with open(file_path, "rb") as f:
                content = f.read()
            eoi_idx = content.rfind(b"\xff\xd9")
            if eoi_idx != -1 and (eoi_idx + 2) < file_size:
                expected_end = eoi_idx + 2
                trailing_len = file_size - expected_end
                return {
                    "has_trailing_bytes": True,
                    "expected_end_offset": expected_end,
                    "trailing_byte_count": trailing_len,
                    "trailing_offset": expected_end,
                    "note": f"Found {trailing_len} trailing bytes beyond JPEG EOI marker."
                }

        elif detected_type == "ZIP":
            # ZIP ends with End of Central Directory record (signature PK\x05\x06) + 22 bytes min
            with open(file_path, "rb") as f:
                content = f.read()
            eocd_idx = content.rfind(b"PK\x05\x06")
            if eocd_idx != -1:
                # EOCD length is 22 bytes plus comment length
                if len(content) >= eocd_idx + 22:
                    comment_len = int.from_bytes(content[eocd_idx + 20:eocd_idx + 22], "little")
                    expected_end = eocd_idx + 22 + comment_len
                    if expected_end < file_size:
                        trailing_len = file_size - expected_end
                        return {
                            "has_trailing_bytes": True,
                            "expected_end_offset": expected_end,
                            "trailing_byte_count": trailing_len,
                            "trailing_offset": expected_end,
                            "note": f"Found {trailing_len} trailing bytes beyond ZIP End of Central Directory."
                        }

        return None

    @staticmethod
    def detect_null_regions(file_path: Path, min_null_bytes: int = 512) -> List[Dict[str, Any]]:
        """Identify significant contiguous blocks of null (0x00) bytes."""
        null_regions = []
        current_start: Optional[int] = None
        current_count = 0
        offset = 0

        with open(file_path, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                for b in chunk:
                    if b == 0:
                        if current_start is None:
                            current_start = offset
                        current_count += 1
                    else:
                        if current_count >= min_null_bytes:
                            null_regions.append({
                                "start_offset": current_start,
                                "end_offset": offset,
                                "length": current_count
                            })
                        current_start = None
                        current_count = 0
                    offset += 1

        if current_count >= min_null_bytes and current_start is not None:
            null_regions.append({
                "start_offset": current_start,
                "end_offset": offset,
                "length": current_count
            })

        return null_regions

    @classmethod
    def ingest_file(cls, src_path: Path, storage_dir: Path) -> Dict[str, Any]:
        """Ingest a file into immutable, content-addressed storage (read-only mode 0o444)."""
        sha256_hash, file_size = cls.compute_sha256_and_size(src_path)
        dest_filename = f"{sha256_hash}"
        dest_path = storage_dir / dest_filename

        if not dest_path.exists():
            import shutil
            shutil.copyfile(src_path, dest_path)
            # Make file read-only on disk
            try:
                dest_path.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
            except Exception:
                pass

        type_info = cls.detect_file_type(dest_path)
        entropy = cls.compute_entropy(dest_path)
        trailing = cls.detect_trailing_bytes(dest_path, type_info["type"])
        null_blocks = cls.detect_null_regions(dest_path, min_null_bytes=1024)

        return {
            "sha256": sha256_hash,
            "size_bytes": file_size,
            "stored_path": str(dest_path),
            "file_type": type_info["type"],
            "mime_type": type_info["mime"],
            "type_description": type_info["description"],
            "entropy": entropy,
            "trailing_anomaly": trailing,
            "null_regions_count": len(null_blocks),
            "null_regions": null_blocks[:10],  # sample up to 10
        }
