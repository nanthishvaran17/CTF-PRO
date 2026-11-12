import base64
import binascii
import hashlib
import html
import re
import urllib.parse
from typing import List, Dict, Any, Optional, Set, Tuple
from .flag_finder import FlagFinder

class CyclicDecodeError(Exception):
    pass

class MultiLayerDecoder:
    """Recursive multi-layer decoder with cycle prevention and provenance tracking."""

    def __init__(self, max_depth: int = 8, max_buffer_size: int = 10 * 1024 * 1024):
        self.max_depth = max_depth
        self.max_buffer_size = max_buffer_size
        self.flag_finder = FlagFinder()

    @staticmethod
    def _is_mostly_printable(text: str, threshold: float = 0.85) -> bool:
        if not text:
            return False
        printable = sum(1 for c in text if c.isprintable() or c in "\r\n\t")
        return (printable / len(text)) >= threshold

    # --- Decoders ---

    @staticmethod
    def decode_base64(data: str) -> Optional[str]:
        cleaned = re.sub(r"\s+", "", data)
        if len(cleaned) < 4 or len(cleaned) % 4 != 0:
            # Try adding padding if 1-2 '=' are missing
            missing = (4 - len(cleaned) % 4) % 4
            if missing and missing != 3:
                cleaned += "=" * missing
            else:
                return None
        if not re.fullmatch(r"[A-Za-z0-9+/=]+", cleaned):
            return None
        try:
            raw = base64.b64decode(cleaned.encode("ascii"), validate=True)
            text = raw.decode("utf-8")
            if MultiLayerDecoder._is_mostly_printable(text):
                return text
        except Exception:
            pass
        return None

    @staticmethod
    def decode_base32(data: str) -> Optional[str]:
        cleaned = re.sub(r"\s+", "", data).upper()
        if len(cleaned) < 8 or not re.fullmatch(r"[A-Z2-7=]+", cleaned):
            return None
        missing = (8 - len(cleaned) % 8) % 8
        if missing in (1, 3, 4, 6):
            cleaned += "=" * missing
        try:
            raw = base64.b32decode(cleaned.encode("ascii"))
            text = raw.decode("utf-8")
            if MultiLayerDecoder._is_mostly_printable(text):
                return text
        except Exception:
            pass
        return None

    @staticmethod
    def decode_hex(data: str) -> Optional[str]:
        cleaned = re.sub(r"[\s:]+", "", data)
        # Check if starts with 0x
        if cleaned.startswith("0x") or cleaned.startswith("0X"):
            cleaned = cleaned[2:]
        if len(cleaned) < 4 or len(cleaned) % 2 != 0:
            return None
        if not re.fullmatch(r"[0-9a-fA-F]+", cleaned):
            return None
        try:
            raw = bytes.fromhex(cleaned)
            text = raw.decode("utf-8")
            if MultiLayerDecoder._is_mostly_printable(text):
                return text
        except Exception:
            pass
        return None

    @staticmethod
    def decode_url(data: str) -> Optional[str]:
        if "%" not in data:
            return None
        try:
            decoded = urllib.parse.unquote(data)
            if decoded != data and MultiLayerDecoder._is_mostly_printable(decoded):
                return decoded
        except Exception:
            pass
        return None

    @staticmethod
    def decode_html_entities(data: str) -> Optional[str]:
        if "&" not in data or ";" not in data:
            return None
        decoded = html.unescape(data)
        if decoded != data and MultiLayerDecoder._is_mostly_printable(decoded):
            return decoded
        return None

    @staticmethod
    def decode_rot13(data: str) -> Optional[str]:
        import codecs
        decoded = codecs.decode(data, "rot_13")
        if decoded != data and MultiLayerDecoder._is_mostly_printable(decoded):
            return decoded
        return None

    @staticmethod
    def decode_binary_str(data: str) -> Optional[str]:
        cleaned = re.sub(r"\s+", "", data)
        if len(cleaned) >= 8 and len(cleaned) % 8 == 0 and re.fullmatch(r"[01]+", cleaned):
            try:
                byte_vals = [int(cleaned[i:i+8], 2) for i in range(0, len(cleaned), 8)]
                text = bytes(byte_vals).decode("utf-8")
                if MultiLayerDecoder._is_mostly_printable(text):
                    return text
            except Exception:
                pass
        return None

    @staticmethod
    def decode_ascii_decimal(data: str) -> Optional[str]:
        parts = re.split(r"[\s,]+", data.strip())
        if len(parts) >= 3 and all(p.isdigit() for p in parts if p):
            try:
                nums = [int(p) for p in parts if p]
                if all(0 <= n <= 255 for n in nums):
                    text = bytes(nums).decode("utf-8")
                    if MultiLayerDecoder._is_mostly_printable(text):
                        return text
            except Exception:
                pass
        return None

    @staticmethod
    def decode_unicode_escapes(data: str) -> Optional[str]:
        if "\\u" in data or "\\x" in data:
            try:
                decoded = data.encode("utf-8").decode("unicode_escape")
                if decoded != data and MultiLayerDecoder._is_mostly_printable(decoded):
                    return decoded
            except Exception:
                pass
        return None

    @staticmethod
    def solve_single_byte_xor(data_bytes: bytes) -> List[Tuple[int, str, float]]:
        """Try all 255 single-byte XOR keys and return candidates that score as English/printable."""
        results = []
        for key in range(1, 256):
            xored = bytes(b ^ key for b in data_bytes)
            try:
                text = xored.decode("utf-8")
                printable_cnt = sum(1 for c in text if c.isprintable() or c in "\r\n\t")
                ratio = printable_cnt / len(text)
                if ratio > 0.85:
                    results.append((key, text, ratio))
            except Exception:
                continue
        results.sort(key=lambda x: x[2], reverse=True)
        return results

    # --- Recursive Orchestrator ---

    def decode_chain(
        self,
        initial_input: str,
        visited_hashes: Optional[Set[str]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
        depth: int = 0
    ) -> List[Dict[str, Any]]:
        """Recursively explore decodings with loop detection and branch capping."""
        if visited_hashes is None:
            visited_hashes = set()
        if history is None:
            history = []

        if depth >= self.max_depth or len(initial_input) > self.max_buffer_size:
            return []

        input_hash = hashlib.sha256(initial_input.encode("utf-8", errors="ignore")).hexdigest()
        if input_hash in visited_hashes:
            return []
        visited_hashes.add(input_hash)

        # Check if flag is directly visible in current text
        discovered = []
        flags = self.flag_finder.scan_text(initial_input)
        for f in flags:
            discovered.append({
                "flag": f["flag"],
                "depth": depth,
                "history": list(history),
                "final_text": initial_input,
                "match_pattern": f["pattern"],
            })

        # List candidate decoder functions
        decoders = [
            ("base64", self.decode_base64),
            ("hex", self.decode_hex),
            ("url", self.decode_url),
            ("html", self.decode_html_entities),
            ("rot13", self.decode_rot13),
            ("base32", self.decode_base32),
            ("binary_str", self.decode_binary_str),
            ("ascii_decimal", self.decode_ascii_decimal),
            ("unicode_escapes", self.decode_unicode_escapes),
        ]

        for name, dec_func in decoders:
            try:
                res = dec_func(initial_input)
                if res and res != initial_input:
                    step_entry = {
                        "step": depth + 1,
                        "method": name,
                        "input_preview": (initial_input[:40] + "...") if len(initial_input) > 40 else initial_input,
                        "output_preview": (res[:40] + "...") if len(res) > 40 else res,
                        "output_len": len(res),
                        "output_sha256": hashlib.sha256(res.encode("utf-8")).hexdigest()
                    }
                    new_history = history + [step_entry]
                    sub_findings = self.decode_chain(res, visited_hashes.copy(), new_history, depth + 1)
                    discovered.extend(sub_findings)
            except Exception:
                continue

        # Single-byte XOR trial if input looks like hex or raw bytes
        if len(initial_input) >= 8 and len(initial_input) <= 4096:
            try:
                cleaned_hex = re.sub(r"[\s:]+", "", initial_input)
                if len(cleaned_hex) % 2 == 0 and re.fullmatch(r"[0-9a-fA-F]+", cleaned_hex):
                    raw = bytes.fromhex(cleaned_hex)
                    xor_candidates = self.solve_single_byte_xor(raw)
                    for key, xor_text, score in xor_candidates[:3]:
                        step_entry = {
                            "step": depth + 1,
                            "method": f"xor_key_0x{key:02x}",
                            "input_preview": initial_input[:40],
                            "output_preview": xor_text[:40],
                            "output_len": len(xor_text),
                            "score": score
                        }
                        new_history = history + [step_entry]
                        sub_findings = self.decode_chain(xor_text, visited_hashes.copy(), new_history, depth + 1)
                        discovered.extend(sub_findings)
            except Exception:
                pass

        return discovered
