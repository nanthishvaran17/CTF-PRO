from pathlib import Path
from typing import Dict, Any, Optional
from backend.ctfx.plugins.base import AnalyzerPlugin

class CustomXorDetectorPlugin(AnalyzerPlugin):
    name = "CustomXorDetector"
    version = "1.0.0"
    author = "CTF HUNTER X Community"
    description = "Scans small binary blocks for single-byte XOR obfuscated flag headers"
    supported_types = ["BINARY", "TXT", "*"]

    def analyze(self, file_path: Path, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        with open(file_path, "rb") as f:
            sample = f.read(4096)

        matches = []
        # Target signature: "FLAG{" xor'd with key
        flag_prefix = b"FLAG{"
        for key in range(1, 256):
            xored_sig = bytes(b ^ key for b in flag_prefix)
            if xored_sig in sample:
                matches.append({
                    "key_hex": f"0x{key:02x}",
                    "key_int": key,
                    "target_pattern": "FLAG{",
                    "note": f"Found XOR'd flag signature matching key 0x{key:02x}"
                })

        return {
            "bytes_scanned": len(sample),
            "xor_candidates_found": len(matches),
            "matches": matches
        }
