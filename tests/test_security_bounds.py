import zipfile
import tarfile
import pytest
from pathlib import Path
from backend.ctfx.engines.archive import SafeArchiveExtractor, ArchiveSecurityError
from backend.ctfx.modules.web import WebAnalyzer, SSRFProtectionError

def test_zip_slip_absolute_and_relative_traversal(tmp_path: Path):
    extractor = SafeArchiveExtractor()

    # 1. Relative dot-dot traversal
    rel_zip = tmp_path / "traversal_rel.zip"
    with zipfile.ZipFile(rel_zip, "w") as zf:
        zf.writestr("../../etc/shadow", "root:x:0:0:::")
    
    with pytest.raises(ArchiveSecurityError) as exc1:
        extractor.extract_zip(rel_zip, tmp_path / "out_rel")
    assert "Zip-Slip" in str(exc1.value)

    # 2. Absolute path traversal
    abs_zip = tmp_path / "traversal_abs.zip"
    with zipfile.ZipFile(abs_zip, "w") as zf:
        zf.writestr("/etc/passwd", "root:x:0:0:::")

    with pytest.raises(ArchiveSecurityError) as exc2:
        extractor.extract_zip(abs_zip, tmp_path / "out_abs")
    assert "Zip-Slip" in str(exc2.value)

def test_archive_bomb_limits(tmp_path: Path):
    # Limit max uncompressed bytes to 5000 bytes
    extractor = SafeArchiveExtractor(max_uncompressed_bytes=5000, max_file_count=10)

    bomb_zip = tmp_path / "bomb_bytes.zip"
    with zipfile.ZipFile(bomb_zip, "w") as zf:
        zf.writestr("large.dat", "0" * 10000)

    with pytest.raises(ArchiveSecurityError) as exc:
        extractor.extract_zip(bomb_zip, tmp_path / "out_bomb")
    assert "Decompression bomb" in str(exc.value)

def test_ssrf_protection_subnets():
    # 1. AWS metadata
    with pytest.raises(SSRFProtectionError) as e1:
        WebAnalyzer.validate_url_safe("http://169.254.169.254/latest/meta-data/")
    assert "SSRF Protection Blocked" in str(e1.value)

    # 2. Localhost IPv4
    with pytest.raises(SSRFProtectionError) as e2:
        WebAnalyzer.validate_url_safe("http://127.0.0.1:8000/api")
    assert "SSRF Protection Blocked" in str(e2.value)

    # 3. Private 10.x.x.x
    with pytest.raises(SSRFProtectionError) as e3:
        WebAnalyzer.validate_url_safe("http://10.10.10.10:80/secret")
    assert "SSRF Protection Blocked" in str(e3.value)

    # 4. Private 192.168.x.x
    with pytest.raises(SSRFProtectionError) as e4:
        WebAnalyzer.validate_url_safe("http://192.168.1.254/")
    assert "SSRF Protection Blocked" in str(e4.value)

    # 5. Non-HTTP scheme
    with pytest.raises(SSRFProtectionError) as e5:
        WebAnalyzer.validate_url_safe("file:///etc/passwd")
    assert "Prohibited protocol scheme" in str(e5.value)
