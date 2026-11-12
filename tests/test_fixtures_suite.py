import pytest
from pathlib import Path
from backend.ctfx.engines.intake import FileIntakeEngine
from backend.ctfx.engines.archive import SafeArchiveExtractor
from backend.ctfx.engines.strings import StringsExtractor
from backend.ctfx.engines.decoder import MultiLayerDecoder
from backend.ctfx.engines.flag_finder import FlagFinder
from backend.ctfx.modules.stego import StegoAnalyzer
from backend.ctfx.modules.forensics import ForensicsAnalyzer
from backend.ctfx.modules.re import ReverseEngineeringAnalyzer

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

def test_clean_file_reports_nothing_found():
    clean_path = FIXTURES_DIR / "clean_sample.png"
    assert clean_path.exists()

    # 1. Trailing check
    trailing = FileIntakeEngine.detect_trailing_bytes(clean_path, "PNG")
    assert trailing is None  # Nothing found

    # 2. Strings check
    strings = StringsExtractor.scan_file(clean_path, min_length=4)
    finder = FlagFinder()
    flags = []
    for s in strings:
        flags.extend(finder.scan_text(s["value"]))
    assert len(flags) == 0  # Zero flags in clean file

    # 3. LSB check
    lsb_res = StegoAnalyzer.extract_lsb(clean_path)
    assert len(lsb_res.get("flags_found", [])) == 0  # Zero stego flags

def test_planted_multilayer_encoded_flag():
    multi_path = FIXTURES_DIR / "multilayer_encoded.txt"
    content = multi_path.read_text(encoding="utf-8").strip()

    decoder = MultiLayerDecoder()
    discovered = decoder.decode_chain(content)
    assert len(discovered) >= 1

    matched = [d for d in discovered if d["flag"] == "FLAG{multilayer_pipeline_unlocked}"]
    assert len(matched) == 1
    chain = [step["method"] for step in matched[0]["history"]]
    assert "base64" in chain
    assert "hex" in chain

def test_planted_lsb_stego_png():
    stego_path = FIXTURES_DIR / "lsb_stego.png"
    sha256, size = FileIntakeEngine.compute_sha256_and_size(stego_path)
    assert len(sha256) == 64
    assert size > 0

    lsb_res = StegoAnalyzer.extract_lsb(stego_path)
    found_flags = [f["flag"] for f in lsb_res.get("flags_found", [])]
    assert "FLAG{lsb_image_stego_authenticated}" in found_flags

def test_trailing_bytes_png():
    trailing_path = FIXTURES_DIR / "trailing_payload.png"
    trailing = FileIntakeEngine.detect_trailing_bytes(trailing_path, "PNG")
    assert trailing is not None
    assert trailing["has_trailing_bytes"] is True
    assert trailing["trailing_byte_count"] > 20

    # Scan trailing bytes
    with open(trailing_path, "rb") as f:
        f.seek(trailing["trailing_offset"])
        tail_data = f.read()

    finder = FlagFinder()
    flags = finder.scan_binary(tail_data)
    assert len(flags) == 1
    assert flags[0]["flag"] == "FLAG{trailing_iend_detected}"

def test_nested_zip_extraction(tmp_path: Path):
    nested_path = FIXTURES_DIR / "nested_archive.zip"
    extractor = SafeArchiveExtractor()
    extracted = extractor.extract_recursive(nested_path, tmp_path)

    # Must have extracted inner payload and flag
    extracted_names = [e["name"] for e in extracted]
    assert any("inner_payload.zip" in n for n in extracted_names)
    assert any("secret_flag.txt" in n for n in extracted_names)

    # Read extracted secret_flag.txt
    flag_file = [e["path"] for e in extracted if "secret_flag.txt" in e["name"]][0]
    flag_content = Path(flag_file).read_text(encoding="utf-8")
    assert "FLAG{nested_zip_carved_success}" in flag_content

def test_pcap_http_stream_reconstruction():
    pcap_path = FIXTURES_DIR / "network_http.pcap"
    res = ForensicsAnalyzer.analyze_pcap(pcap_path)
    assert res["is_pcap"] is True

    # Flag in payload
    flags = [f["flag"] for f in res["flags_discovered"]]
    assert "FLAG{pcap_stream_http_recovered}" in flags

    # Credential in basic auth
    creds = [c["credentials"] for c in res["credentials_found"] if c["type"] == "HTTP_BASIC_AUTH"]
    assert any("admin:super_secret_pass" in c for c in creds)

def test_elf_binary_strings_and_architecture():
    elf_path = FIXTURES_DIR / "embedded_string.elf"
    res = ReverseEngineeringAnalyzer.analyze_binary(elf_path)
    assert res["format"] == "ELF"
    assert res["bitness"] == 64
    assert "x86_64" in res["architecture"]
    assert "system" in res["suspicious_apis_detected"]

    # String extraction
    strings = StringsExtractor.scan_file(elf_path, min_length=4)
    flag_strings = [s for s in strings if "FLAG{elf_symbol_and_strings_found}" in s["value"]]
    assert len(flag_strings) == 1
    assert flag_strings[0]["offset"] > 0
