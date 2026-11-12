import os
import tarfile
import zipfile
import gzip
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

class ArchiveSecurityError(Exception):
    """Raised when an archive violates decompression safety policies (zip-slip, bomb, symlink traversal)."""
    pass

class SafeArchiveExtractor:
    """Safe archive extractor mitigating Zip-Slip, symlink attacks, and decompression bombs."""

    def __init__(
        self,
        max_uncompressed_bytes: int = 250 * 1024 * 1024,
        max_file_count: int = 2000,
        max_ratio: float = 100.0,
        max_depth: int = 5
    ):
        self.max_uncompressed_bytes = max_uncompressed_bytes
        self.max_file_count = max_file_count
        self.max_ratio = max_ratio
        self.max_depth = max_depth

    def is_safe_path(self, base_dir: Path, target_path: Path) -> bool:
        """Ensure resolved target path stays within base directory (prevents Zip-Slip)."""
        try:
            resolved_base = base_dir.resolve()
            resolved_target = target_path.resolve()
            return os.path.commonpath([str(resolved_base), str(resolved_target)]) == str(resolved_base)
        except Exception:
            return False

    def extract_zip(self, archive_path: Path, output_dir: Path) -> List[Dict[str, Any]]:
        """Safely extract ZIP archive with strict bomb and slip checks."""
        output_dir.mkdir(parents=True, exist_ok=True)
        extracted_files = []
        total_uncompressed = 0
        file_count = 0
        archive_size = max(archive_path.stat().st_size, 1)

        with zipfile.ZipFile(archive_path, "r") as zf:
            infolist = zf.infolist()
            if len(infolist) > self.max_file_count:
                raise ArchiveSecurityError(f"Decompression bomb blocked: file count {len(infolist)} exceeds limit {self.max_file_count}")

            for member in infolist:
                # Disallow symlinks
                if (member.external_attr >> 16) & 0o120000 == 0o120000:
                    raise ArchiveSecurityError(f"Symlink rejected for security: {member.filename}")

                # Path traversal check
                clean_name = os.path.normpath(member.filename)
                if clean_name.startswith("..") or os.path.isabs(clean_name):
                    raise ArchiveSecurityError(f"Zip-Slip path traversal blocked: {member.filename}")

                destination = output_dir / clean_name
                if not self.is_safe_path(output_dir, destination):
                    raise ArchiveSecurityError(f"Zip-Slip destination out of bounds: {member.filename}")

                # Bomb check
                total_uncompressed += member.file_size
                if total_uncompressed > self.max_uncompressed_bytes:
                    raise ArchiveSecurityError(f"Decompression bomb blocked: uncompressed size {total_uncompressed} exceeds limit {self.max_uncompressed_bytes}")

                if member.compress_size > 0:
                    ratio = member.file_size / member.compress_size
                    if ratio > self.max_ratio and member.file_size > 1024 * 1024:
                        raise ArchiveSecurityError(f"Decompression bomb blocked: ratio {ratio:.1f}:1 exceeds threshold")

                file_count += 1
                if member.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as source, open(destination, "wb") as target:
                        shutil.copyfileobj(source, target)
                    extracted_files.append({
                        "name": member.filename,
                        "path": str(destination),
                        "size": member.file_size,
                        "compressed_size": member.compress_size,
                    })

        return extracted_files

    def extract_tar(self, archive_path: Path, output_dir: Path) -> List[Dict[str, Any]]:
        """Safely extract TAR archive with path validation."""
        output_dir.mkdir(parents=True, exist_ok=True)
        extracted_files = []
        total_uncompressed = 0
        file_count = 0

        with tarfile.open(archive_path, "r:*") as tf:
            for member in tf.getmembers():
                if member.issym() or member.islnk():
                    # Check link target safety
                    link_dest = output_dir / member.linkname
                    if not self.is_safe_path(output_dir, link_dest):
                        raise ArchiveSecurityError(f"Tar symlink/hardlink traversal blocked: {member.name} -> {member.linkname}")

                clean_name = os.path.normpath(member.name)
                if clean_name.startswith("..") or os.path.isabs(clean_name):
                    raise ArchiveSecurityError(f"Tar path traversal blocked: {member.name}")

                destination = output_dir / clean_name
                if not self.is_safe_path(output_dir, destination):
                    raise ArchiveSecurityError(f"Tar destination out of bounds: {member.name}")

                total_uncompressed += member.size
                if total_uncompressed > self.max_uncompressed_bytes:
                    raise ArchiveSecurityError(f"Decompression bomb blocked: size {total_uncompressed} exceeds limit")

                file_count += 1
                if file_count > self.max_file_count:
                    raise ArchiveSecurityError(f"Decompression bomb blocked: file count {file_count} exceeds limit")

                if member.isdir():
                    destination.mkdir(parents=True, exist_ok=True)
                elif member.isreg():
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    f_in = tf.extractfile(member)
                    if f_in:
                        with open(destination, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                        extracted_files.append({
                            "name": member.name,
                            "path": str(destination),
                            "size": member.size,
                        })

        return extracted_files

    def extract_gzip(self, archive_path: Path, output_dir: Path) -> List[Dict[str, Any]]:
        """Extract a single GZIP stream safely."""
        output_dir.mkdir(parents=True, exist_ok=True)
        base_name = archive_path.stem
        if base_name.endswith(".tar"):
            base_name = Path(base_name).stem
        out_file = output_dir / f"{base_name}.extracted"

        total_bytes = 0
        with gzip.open(archive_path, "rb") as gz_in, open(out_file, "wb") as f_out:
            while chunk := gz_in.read(64 * 1024):
                total_bytes += len(chunk)
                if total_bytes > self.max_uncompressed_bytes:
                    raise ArchiveSecurityError(f"GZIP decompression bomb blocked: size {total_bytes} exceeds limit")
                f_out.write(chunk)

        return [{
            "name": out_file.name,
            "path": str(out_file),
            "size": total_bytes
        }]

    def extract_recursive(self, archive_path: Path, output_root: Path, current_depth: int = 1) -> List[Dict[str, Any]]:
        """Recursively unpack nested archives up to max_depth."""
        if current_depth > self.max_depth:
            return []

        from .intake import FileIntakeEngine
        file_info = FileIntakeEngine.detect_file_type(archive_path)
        ftype = file_info["type"]

        layer_dir = output_root / f"depth_{current_depth}_{archive_path.stem}"
        layer_dir.mkdir(parents=True, exist_ok=True)

        extracted = []
        try:
            if ftype == "ZIP":
                extracted = self.extract_zip(archive_path, layer_dir)
            elif ftype in ("TAR", "GZIP"):
                if ftype == "GZIP":
                    extracted = self.extract_gzip(archive_path, layer_dir)
                else:
                    extracted = self.extract_tar(archive_path, layer_dir)
        except Exception as e:
            if isinstance(e, ArchiveSecurityError):
                raise
            return []

        all_results = list(extracted)
        # Check if any extracted items are nested archives
        for item in extracted:
            sub_path = Path(item["path"])
            if sub_path.is_file():
                sub_type = FileIntakeEngine.detect_file_type(sub_path)["type"]
                if sub_type in ("ZIP", "TAR", "GZIP"):
                    sub_extracted = self.extract_recursive(sub_path, output_root, current_depth + 1)
                    all_results.extend(sub_extracted)

        return all_results
