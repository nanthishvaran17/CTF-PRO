import os
import io
import zipfile
import pytest
from pathlib import Path
from backend.ctfx.engines.intake import FileIntakeEngine
from backend.ctfx.engines.archive import SafeArchiveExtractor, ArchiveSecurityError
from backend.ctfx.engines.strings import StringsExtractor
from backend.ctfx.engines.decoder import MultiLayerDecoder
from backend.ctfx.engines.flag_finder import FlagFinder
from backend.ctfx.engines.verifier import CandidateVerifier, FlagStatus
from backend.ctfx.engines.evidence import ReproduceScriptGenerator, AutoWriteupGenerator

def test_file_intake_magic_and_entropy(tmp_path: Path):
    # Create fake PNG
    png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 30 + b"IEND\xaeB`\x82"
    png_path = tmp_path / "sample.png"
    png_path.write_bytes(png_data)

    detected = FileIntakeEngine.detect_file_type(png_path)
    assert detected["type"] == "PNG"

    sha256, size = FileIntakeEngine.compute_sha256_and_size(png_path)
    assert len(sha256) == 64
    assert size == len(png_data)

    # Test trailing bytes detection
    appended_data = png_data + b"SECRET_TRAILING_BYTES_DATA"
    appended_path = tmp_path / "appended.png"
    appended_path.write_bytes(appended_data)
    trailing = FileIntakeEngine.detect_trailing_bytes(appended_path, "PNG")
    assert trailing is not None
    assert trailing["has_trailing_bytes"] is True
    assert trailing["trailing_byte_count"] == len(b"SECRET_TRAILING_BYTES_DATA")

def test_strings_extractor_with_offsets(tmp_path: Path):
    content = b"PADDING_DATA_0000\x00" + b"FLAG{found_in_strings}" + b"\x00\x00\x00"
    target_path = tmp_path / "strings.bin"
    target_path.write_bytes(content)

    results = StringsExtractor.scan_file(target_path, min_length=4)
    found_flags = [r for r in results if r["value"] == "FLAG{found_in_strings}"]
    assert len(found_flags) == 1
    flag_entry = found_flags[0]
    assert flag_entry["offset"] == 18
    assert flag_entry["encoding"] == "ascii"

def test_multilayer_decoder_chains():
    decoder = MultiLayerDecoder()

    # Chain: "FLAG{nested_secret_decoded}" -> Hex -> Base64
    flag = "FLAG{nested_secret_decoded}"
    hex_str = flag.encode("utf-8").hex()
    b64_str = import_b64 = __import__("base64").b64encode(hex_str.encode("utf-8")).decode("utf-8")

    discovered = decoder.decode_chain(b64_str)
    assert len(discovered) >= 1
    matched = [d for d in discovered if d["flag"] == flag]
    assert len(matched) >= 1
    # Check chain has 2 steps: base64 then hex
    methods = [step["method"] for step in matched[0]["history"]]
    assert "base64" in methods
    assert "hex" in methods

def test_archive_zip_slip_and_bomb_protection(tmp_path: Path):
    extractor = SafeArchiveExtractor(max_uncompressed_bytes=1000)

    # 1. Test Zip-Slip attack
    slip_zip = tmp_path / "slip.zip"
    with zipfile.ZipFile(slip_zip, "w") as zf:
        zf.writestr("../../evil.txt", "payload")

    extract_out = tmp_path / "out_slip"
    with pytest.raises(ArchiveSecurityError) as exc_info:
        extractor.extract_zip(slip_zip, extract_out)
    assert "Zip-Slip" in str(exc_info.value)

    # 2. Test Bomb protection (exceeds byte limit)
    bomb_zip = tmp_path / "bomb.zip"
    with zipfile.ZipFile(bomb_zip, "w") as zf:
        zf.writestr("big.bin", "A" * 5000)

    with pytest.raises(ArchiveSecurityError) as exc_info:
        extractor.extract_zip(bomb_zip, tmp_path / "out_bomb")
    assert "Decompression bomb" in str(exc_info.value)

def test_flag_finder_and_verifier():
    finder = FlagFinder()
    text = "Here is some dummy text with FLAG{actual_secret_key_123} inside!"
    results = finder.scan_text(text)
    assert len(results) == 1
    assert results[0]["flag"] == "FLAG{actual_secret_key_123}"

    # Auto-detect format from description
    custom_hint = "In this CTF, the flag format is hackme{something}"
    pat = FlagFinder.auto_detect_format_from_text(custom_hint)
    assert pat is not None
    assert "hackme" in pat

    # Candidate Verifier lifecycle
    cand = CandidateVerifier.create_candidate(
        flag="FLAG{actual_secret_key_123}",
        source_sha256="abc12345",
        byte_offset=100
    )
    assert cand["status"] == FlagStatus.EVIDENCE_SUPPORTED.value

    # Validate authoritative event
    cand = CandidateVerifier.record_validation_event(
        cand, validator="ctfd_api", is_success=True, raw_response='{"status": "correct"}'
    )
    assert cand["status"] == FlagStatus.VERIFIED_BY_CHALLENGE.value
    assert len(cand["verification_events"]) == 1

def test_repro_script_and_writeup():
    cand = {
        "flag": "FLAG{repro_test}",
        "byte_offset": 50,
        "source_sha256": "abcdef",
        "status": "VERIFIED-BY-CHALLENGE",
        "transform_chain": [{"step": 1, "method": "base64", "input_preview": "xxx", "output_preview": "yyy"}]
    }
    script = ReproduceScriptGenerator.generate_python_script(cand)
    assert "base64.b64decode" in script
    assert "FLAG{repro_test}" in script

    writeup = AutoWriteupGenerator.generate_markdown(
        challenge_name="Test Challenge",
        files=[{"name": "test.png", "sha256": "abcdef", "file_type": "PNG"}],
        candidates=[cand]
    )
    assert "# CTF Writeup: Test Challenge" in writeup
    assert "FLAG{repro_test}" in writeup
