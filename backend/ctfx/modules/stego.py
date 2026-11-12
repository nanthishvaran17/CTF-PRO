import io
import math
import struct
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image

class StegoAnalyzer:
    """Steganographic analysis engine inspecting PNG chunks, LSB bit planes, palette anomalies, and entropy."""

    @classmethod
    def analyze_png_chunks(cls, file_path: Path) -> Dict[str, Any]:
        """Parse raw PNG structure to inspect all chunks (IHDR, PLTE, IDAT, IEND, tEXt, and custom)."""
        chunks = []
        custom_chunks = []
        has_ihdr = False
        has_iend = False
        width, height = 0, 0
        bit_depth, color_type = 0, 0

        with open(file_path, "rb") as f:
            sig = f.read(8)
            if sig != b"\x89PNG\r\n\x1a\n":
                return {"is_png": False, "error": "Not a valid PNG signature"}

            while True:
                length_bytes = f.read(4)
                if not length_bytes or len(length_bytes) < 4:
                    break
                length = struct.unpack(">I", length_bytes)[0]
                chunk_type_bytes = f.read(4)
                if len(chunk_type_bytes) < 4:
                    break
                chunk_type = chunk_type_bytes.decode("latin1", errors="replace")

                data = f.read(length)
                crc_bytes = f.read(4)

                chunk_entry = {
                    "type": chunk_type,
                    "length": length,
                    "is_ancillary": chunk_type[0].islower(),
                    "is_private": chunk_type[1].islower(),
                }

                if chunk_type == "IHDR" and len(data) >= 13:
                    has_ihdr = True
                    w, h, bd, ct = struct.unpack(">IIBB", data[:10])
                    width, height, bit_depth, color_type = w, h, bd, ct
                    chunk_entry["dimensions"] = f"{w}x{h}"
                    chunk_entry["bit_depth"] = bd
                    chunk_entry["color_type"] = ct

                elif chunk_type in ("tEXt", "zTXt", "iTXt"):
                    chunk_entry["text_payload"] = data.decode("latin1", errors="replace")[:256]

                elif chunk_type not in ("IHDR", "PLTE", "IDAT", "IEND", "sRGB", "gAMA", "pHYs", "cHRM"):
                    custom_chunks.append({
                        "type": chunk_type,
                        "length": length,
                        "preview": data[:64].hex()
                    })

                if chunk_type == "IEND":
                    has_iend = True

                chunks.append(chunk_entry)

        return {
            "is_png": True,
            "dimensions": {"width": width, "height": height},
            "bit_depth": bit_depth,
            "color_type": color_type,
            "total_chunks": len(chunks),
            "custom_chunks": custom_chunks,
            "has_valid_structure": has_ihdr and has_iend,
            "chunks_summary": chunks[:25]
        }

    @classmethod
    def extract_lsb(cls, file_path: Path, max_bytes: int = 1024 * 1024) -> Dict[str, Any]:
        """Extract Least Significant Bits (LSB) across RGB and separate channels."""
        try:
            with Image.open(file_path) as img:
                img_rgb = img.convert("RGB")
                pixels = list(img_rgb.getdata())
        except Exception as e:
            return {"error": f"Image open failed: {str(e)}"}

        # Extract RGB interleaved LSB
        rgb_bits = []
        r_bits = []
        g_bits = []
        b_bits = []

        limit_pixels = min(len(pixels), max_bytes * 8 // 3)
        for r, g, b in pixels[:limit_pixels]:
            r_lsb = r & 1
            g_lsb = g & 1
            b_lsb = b & 1
            rgb_bits.extend([r_lsb, g_lsb, b_lsb])
            r_bits.append(r_lsb)
            g_bits.append(g_lsb)
            b_bits.append(b_lsb)

        def bits_to_bytes(bit_list: List[int]) -> bytes:
            byte_arr = bytearray()
            for i in range(0, len(bit_list) - 7, 8):
                byte_val = 0
                for bit in bit_list[i:i+8]:
                    byte_val = (byte_val << 1) | bit
                byte_arr.append(byte_val)
            return bytes(byte_arr)

        rgb_bytes = bits_to_bytes(rgb_bits)
        r_bytes = bits_to_bytes(r_bits)
        g_bytes = bits_to_bytes(g_bits)
        b_bytes = bits_to_bytes(b_bits)

        from ..engines.flag_finder import FlagFinder
        finder = FlagFinder()

        rgb_flags = finder.scan_binary(rgb_bytes, source_file="lsb_rgb")
        r_flags = finder.scan_binary(r_bytes, source_file="lsb_r")
        g_flags = finder.scan_binary(g_bytes, source_file="lsb_g")
        b_flags = finder.scan_binary(b_bytes, source_file="lsb_b")

        all_flags = rgb_flags + r_flags + g_flags + b_flags

        return {
            "pixels_inspected": limit_pixels,
            "rgb_bytes_extracted": len(rgb_bytes),
            "flags_found": all_flags,
            "rgb_preview": rgb_bytes[:64].hex(),
            "r_preview": r_bytes[:32].hex(),
            "g_preview": g_bytes[:32].hex(),
            "b_preview": b_bytes[:32].hex(),
        }

    @classmethod
    def compare_images(cls, img_path_a: Path, img_path_b: Path) -> Dict[str, Any]:
        """Compute visual and pixel differences between two challenge images."""
        try:
            with Image.open(img_path_a) as a, Image.open(img_path_b) as b:
                if a.size != b.size:
                    return {"identical": False, "error": f"Image dimensions differ: {a.size} vs {b.size}"}
                
                a_rgb = a.convert("RGB")
                b_rgb = b.convert("RGB")
                diff_count = 0
                total_pixels = a.size[0] * a.size[1]
                
                a_pixels = list(a_rgb.getdata())
                b_pixels = list(b_rgb.getdata())
                
                for p1, p2 in zip(a_pixels, b_pixels):
                    if p1 != p2:
                        diff_count += 1
                        
                diff_percent = (diff_count / total_pixels) * 100
                return {
                    "identical": diff_count == 0,
                    "total_pixels": total_pixels,
                    "different_pixels": diff_count,
                    "diff_percentage": round(diff_percent, 4)
                }
        except Exception as e:
            return {"error": str(e)}
