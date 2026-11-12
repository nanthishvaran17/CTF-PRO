import io
import struct
import pytest
from pathlib import Path
from PIL import Image

from backend.ctfx.modules.stego import StegoAnalyzer
from backend.ctfx.modules.media import MediaAnalyzer
from backend.ctfx.modules.forensics import ForensicsAnalyzer
from backend.ctfx.modules.crypto import CryptoAnalyzer
from backend.ctfx.modules.web import WebAnalyzer, SSRFProtectionError
from backend.ctfx.modules.re import ReverseEngineeringAnalyzer
from backend.ctfx.modules.osint import OSINTAnalyzer
from backend.ctfx.plugins.base import PluginManager
from backend.ctfx.tools.manager import ToolInventoryManager

def test_stego_png_and_lsb(tmp_path: Path):
    # Create 32x32 RGB image
    img = Image.new("RGB", (32, 32), color=(100, 150, 200))
    pixels = list(img.getdata())

    # Plant LSB message: "FLAG{lsb_stego_revealed}"
    message = b"FLAG{lsb_stego_revealed}\x00"
    bit_list = []
    for byte in message:
        for i in range(7, -1, -1):
            bit_list.append((byte >> i) & 1)

    new_pixels = []
    bit_idx = 0
    for r, g, b in pixels:
        if bit_idx < len(bit_list):
            r = (r & ~1) | bit_list[bit_idx]
            bit_idx += 1
        if bit_idx < len(bit_list):
            g = (g & ~1) | bit_list[bit_idx]
            bit_idx += 1
        if bit_idx < len(bit_list):
            b = (b & ~1) | bit_list[bit_idx]
            bit_idx += 1
        new_pixels.append((r, g, b))

    img.putdata(new_pixels)
    stego_path = tmp_path / "stego.png"
    img.save(stego_path, format="PNG")

    # 1. Inspect chunks
    chunk_info = StegoAnalyzer.analyze_png_chunks(stego_path)
    assert chunk_info["is_png"] is True
    assert chunk_info["has_valid_structure"] is True

    # 2. Extract LSB
    lsb_info = StegoAnalyzer.extract_lsb(stego_path)
    found_flags = [f["flag"] for f in lsb_info["flags_found"]]
    assert "FLAG{lsb_stego_revealed}" in found_flags

def test_forensics_pcap_reconstruction(tmp_path: Path):
    # Construct a raw PCAP with Ethernet -> IPv4 -> TCP -> HTTP GET + FLAG
    pcap_path = tmp_path / "test.pcap"
    
    # PCAP Global Header (24 bytes, little-endian)
    global_hdr = struct.pack("<IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1) # linktype 1 = Ethernet
    
    # Packet: Ethernet (14) + IPv4 (20) + TCP (20) + Payload
    payload = b"GET /admin?flag=FLAG{pcap_packet_intercepted} HTTP/1.1\r\nAuthorization: Basic YWRtaW46c2VjcmV0MTIz\r\n\r\n"
    tcp_len = 20 + len(payload)
    ip_total_len = 20 + tcp_len
    
    eth_hdr = b"\x00\x11\x22\x33\x44\x55" + b"\x66\x77\x88\x99\xaa\xbb" + struct.pack(">H", 0x0800)
    # IPv4: version/ihl=0x45, tos=0, total_len, id=1, flags=0, ttl=64, proto=6 (TCP), checksum=0, src=192.168.1.100, dst=192.168.1.1
    ip_hdr = struct.pack(">BBHHHBBH", 0x45, 0, ip_total_len, 1, 0, 64, 6, 0) + bytes([192, 168, 1, 100]) + bytes([192, 168, 1, 1])
    # TCP: sport=54321, dport=80, seq=1, ack=0, offset=0x50, flags=0x18 (PSH, ACK), win=8192, check=0, urp=0
    tcp_hdr = struct.pack(">HHIIBBHHH", 54321, 80, 1, 0, 0x50, 0x18, 8192, 0, 0)
    
    pkt_bytes = eth_hdr + ip_hdr + tcp_hdr + payload
    pkt_hdr = struct.pack("<IIII", 1700000000, 0, len(pkt_bytes), len(pkt_bytes))
    
    pcap_path.write_bytes(global_hdr + pkt_hdr + pkt_bytes)

    res = ForensicsAnalyzer.analyze_pcap(pcap_path)
    assert res["is_pcap"] is True
    assert res["protocols"]["TCP"] >= 1
    # Check flags discovered
    flags = [f["flag"] for f in res["flags_discovered"]]
    assert any("FLAG{pcap_packet_intercepted}" in f for f in flags)
    # Check credentials carved
    assert any(c["type"] == "HTTP_BASIC_AUTH" and "admin:secret123" in c["credentials"] for c in res["credentials_found"])

def test_crypto_analysis():
    # Caesar
    secret = "FLAG{caesar_shift_solved}"
    def shift_c(c, s=7):
        if 'a' <= c <= 'z':
            return chr((ord(c) - ord('a') + s) % 26 + ord('a'))
        elif 'A' <= c <= 'Z':
            return chr((ord(c) - ord('A') + s) % 26 + ord('A'))
        return c

    shifted = "".join(shift_c(c, 7) for c in secret)
    solved = CryptoAnalyzer.solve_caesar(shifted)
    assert len(solved) == 25
    assert any("FLAG{caesar_shift_solved}" in s["flags_found"] for s in solved)

    # Hash identification
    md5_id = CryptoAnalyzer.identify_hash("5d41402abc4b2a76b9719d911017c592")
    assert any(h["algorithm"] == "MD5" for h in md5_id)
    bcrypt_id = CryptoAnalyzer.identify_hash("$2y$12$e8N4Yg7s76jA..dK")
    assert any(h["algorithm"] == "bcrypt" for h in bcrypt_id)

    # Small e RSA attack
    m = 133742
    c = m ** 3
    recovered = CryptoAnalyzer.rsa_cube_root_attack(c, e=3)
    assert recovered == m

def test_web_ssrf_blocking():
    # Loopback IP
    with pytest.raises(SSRFProtectionError) as exc1:
        WebAnalyzer.validate_url_safe("http://127.0.0.1:8080/flag")
    assert "SSRF Protection Blocked" in str(exc1.value)

    # AWS/Cloud Metadata IP
    with pytest.raises(SSRFProtectionError) as exc2:
        WebAnalyzer.validate_url_safe("http://169.254.169.254/latest/meta-data/")
    assert "SSRF Protection Blocked" in str(exc2.value)

    # Private IP
    with pytest.raises(SSRFProtectionError) as exc3:
        WebAnalyzer.validate_url_safe("http://192.168.1.1/admin")
    assert "SSRF Protection Blocked" in str(exc3.value)

def test_reverse_engineering_elf(tmp_path: Path):
    # Minimal 64-bit ELF header
    # e_ident: 0x7f, 'E', 'L', 'F', 2 (64-bit), 1 (little), 1 (version), 0...
    e_ident = b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 8
    # e_type=2 (EXEC), e_machine=0x3E (x86_64), e_version=1, e_entry=0x401000, e_phoff=64, e_shoff=0, e_flags=0, e_ehsize=64, ...
    rest_hdr = struct.pack("<HHIQQQIHHHHHH", 2, 0x3E, 1, 0x401000, 64, 0, 0, 64, 56, 1, 64, 0, 0)
    elf_file = tmp_path / "sample.elf"
    elf_file.write_bytes(e_ident + rest_hdr + b"system\x00FLAG{embedded_in_elf}")

    res = ReverseEngineeringAnalyzer.analyze_binary(elf_file)
    assert res["format"] == "ELF"
    assert res["bitness"] == 64
    assert "x86_64" in res["architecture"]
    assert "system" in res["suspicious_apis_detected"]

def test_plugin_discovery_and_execution(tmp_path: Path):
    plugins_dir = Path(__file__).resolve().parent.parent / "plugins"
    pm = PluginManager(plugins_dir)
    loaded = pm.discover_and_load()
    assert "CustomXorDetector" in loaded

    # Test running plugin against a test file
    test_file = tmp_path / "xored.bin"
    # Plant flag xored with 0x42
    flag_xored = bytes(b ^ 0x42 for b in b"FLAG{test_plugin_xor}")
    test_file.write_bytes(flag_xored)

    results = pm.run_plugins_for_file(test_file, "BINARY")
    assert len(results) >= 1
    xor_res = [r for r in results if r["plugin_name"] == "CustomXorDetector"][0]
    assert xor_res["success"] is True
    assert xor_res["data"]["xor_candidates_found"] >= 1
    assert any(m["key_hex"] == "0x42" for m in xor_res["data"]["matches"])

def test_tool_inventory_detection():
    inv = ToolInventoryManager.get_inventory()
    assert len(inv) >= 10
    python_tool = [t for t in inv if t["binary"] == "python"][0]
    assert python_tool["is_installed"] is True
    assert "Python" in python_tool["version"]
    git_tool = [t for t in inv if t["binary"] == "git"][0]
    assert git_tool["is_installed"] is True
