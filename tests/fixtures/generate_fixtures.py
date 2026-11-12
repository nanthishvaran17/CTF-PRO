import io
import os
import struct
import zipfile
import base64
from pathlib import Path
from PIL import Image

FIXTURES_DIR = Path(__file__).resolve().parent

def generate_all():
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Nested ZIP archive
    nested_zip_path = FIXTURES_DIR / "nested_archive.zip"
    inner_buffer = io.BytesIO()
    with zipfile.ZipFile(inner_buffer, "w") as z_inner:
        z_inner.writestr("secret_flag.txt", "FLAG{nested_zip_carved_success}")
    
    with zipfile.ZipFile(nested_zip_path, "w") as z_outer:
        z_outer.writestr("readme.txt", "Follow the trail deeper...")
        z_outer.writestr("inner_payload.zip", inner_buffer.getvalue())

    # 2. Stego PNG with LSB message
    stego_png_path = FIXTURES_DIR / "lsb_stego.png"
    img = Image.new("RGB", (24, 24), color=(60, 120, 180))
    msg = b"FLAG{lsb_image_stego_authenticated}\x00"
    bits = []
    for b in msg:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)

    pixels = list(img.getdata())
    new_pixels = []
    bit_i = 0
    for r, g, b in pixels:
        if bit_i < len(bits):
            r = (r & ~1) | bits[bit_i]
            bit_i += 1
        if bit_i < len(bits):
            g = (g & ~1) | bits[bit_i]
            bit_i += 1
        if bit_i < len(bits):
            b = (b & ~1) | bits[bit_i]
            bit_i += 1
        new_pixels.append((r, g, b))

    img.putdata(new_pixels)
    img.save(stego_png_path, format="PNG")

    # 3. Clean PNG (no stego, no trailing bytes)
    clean_png_path = FIXTURES_DIR / "clean_sample.png"
    clean_img = Image.new("RGB", (16, 16), color=(255, 0, 0))
    clean_img.save(clean_png_path, format="PNG")

    # 4. PNG with trailing bytes beyond IEND
    trailing_png_path = FIXTURES_DIR / "trailing_payload.png"
    raw_clean_png = clean_png_path.read_bytes()
    trailing_payload = b"\x00\x00FLAG{trailing_iend_detected}\x00\x00"
    trailing_png_path.write_bytes(raw_clean_png + trailing_payload)

    # 5. Multi-layer encoded text: flag -> hex -> base64
    multilayer_path = FIXTURES_DIR / "multilayer_encoded.txt"
    raw_flag = "FLAG{multilayer_pipeline_unlocked}"
    hex_repr = raw_flag.encode("utf-8").hex()
    b64_repr = base64.b64encode(hex_repr.encode("utf-8")).decode("utf-8")
    multilayer_path.write_text(b64_repr, encoding="utf-8")

    # 6. PCAP capture with HTTP stream & basic auth
    pcap_path = FIXTURES_DIR / "network_http.pcap"
    global_hdr = struct.pack("<IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
    http_payload = b"GET /v1/flag HTTP/1.1\r\nHost: ctf.local\r\nAuthorization: Basic YWRtaW46c3VwZXJfc2VjcmV0X3Bhc3M=\r\n\r\nHTTP/1.1 200 OK\r\n\r\nFLAG{pcap_stream_http_recovered}"
    tcp_len = 20 + len(http_payload)
    ip_total_len = 20 + tcp_len
    eth_hdr = b"\x00\x0c\x29\x11\x22\x33" + b"\x00\x50\x56\xaa\xbb\xcc" + struct.pack(">H", 0x0800)
    ip_hdr = struct.pack(">BBHHHBBH", 0x45, 0, ip_total_len, 42, 0, 64, 6, 0) + bytes([10, 0, 0, 2]) + bytes([10, 0, 0, 1])
    tcp_hdr = struct.pack(">HHIIBBHHH", 49152, 80, 100, 200, 0x50, 0x18, 16384, 0, 0)
    pkt_bytes = eth_hdr + ip_hdr + tcp_hdr + http_payload
    pkt_hdr = struct.pack("<IIII", 1710000000, 500, len(pkt_bytes), len(pkt_bytes))
    pcap_path.write_bytes(global_hdr + pkt_hdr + pkt_bytes)

    # 7. Minimal 64-bit ELF binary
    elf_path = FIXTURES_DIR / "embedded_string.elf"
    e_ident = b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 8
    e_hdr = struct.pack("<HHIQQQIHHHHHH", 2, 0x3E, 1, 0x401000, 64, 0, 0, 64, 56, 1, 64, 0, 0)
    elf_content = e_ident + e_hdr + b"__libc_start_main\x00FLAG{elf_symbol_and_strings_found}\x00system"
    elf_path.write_bytes(elf_content)

    print(f"[+] All 7 real fixtures successfully generated in {FIXTURES_DIR}")

if __name__ == "__main__":
    generate_all()
