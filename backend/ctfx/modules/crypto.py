import collections
import math
import re
from typing import Dict, Any, List, Optional, Tuple

ENGLISH_FREQ = {
    'a': 0.08167, 'b': 0.01492, 'c': 0.02782, 'd': 0.04253, 'e': 0.12702,
    'f': 0.02228, 'g': 0.02015, 'h': 0.06094, 'i': 0.06966, 'j': 0.00153,
    'k': 0.00772, 'l': 0.04025, 'm': 0.02406, 'n': 0.06749, 'o': 0.07507,
    'p': 0.01929, 'q': 0.00095, 'r': 0.05987, 's': 0.06327, 't': 0.09056,
    'u': 0.02758, 'v': 0.00978, 'w': 0.02360, 'x': 0.00150, 'y': 0.01974,
    'z': 0.00074
}

class CryptoAnalyzer:
    """Cryptographic analysis suite for classic ciphers, frequency analysis, hash ID, and weak RSA."""

    @classmethod
    def chi_squared_score(cls, text: str) -> float:
        """Calculate chi-squared score comparing text letter frequency to natural English (lower is better)."""
        counts = collections.Counter(c.lower() for c in text if c.isalpha())
        total_letters = sum(counts.values())
        if total_letters == 0:
            return 999999.0

        chi_sq = 0.0
        for char, expected_ratio in ENGLISH_FREQ.items():
            expected_count = expected_ratio * total_letters
            actual_count = counts.get(char, 0)
            chi_sq += ((actual_count - expected_count) ** 2) / expected_count
        return round(chi_sq, 2)

    @classmethod
    def solve_caesar(cls, text: str) -> List[Dict[str, Any]]:
        """Try all 25 Caesar shifts, evaluate with Chi-Squared and flag detector."""
        results = []
        from ..engines.flag_finder import FlagFinder
        finder = FlagFinder()

        for shift in range(1, 26):
            shifted = []
            for char in text:
                if 'a' <= char <= 'z':
                    shifted.append(chr((ord(char) - ord('a') - shift) % 26 + ord('a')))
                elif 'A' <= char <= 'Z':
                    shifted.append(chr((ord(char) - ord('A') - shift) % 26 + ord('A')))
                else:
                    shifted.append(char)
            candidate_str = "".join(shifted)
            score = cls.chi_squared_score(candidate_str)
            flags = finder.scan_text(candidate_str)

            results.append({
                "shift": shift,
                "text": candidate_str,
                "chi_squared": score,
                "flags_found": [f["flag"] for f in flags]
            })

        results.sort(key=lambda x: (len(x["flags_found"]) == 0, x["chi_squared"]))
        return results

    @classmethod
    def solve_atbash(cls, text: str) -> str:
        """Apply Atbash substitution cipher (A<->Z, B<->Y)."""
        res = []
        for char in text:
            if 'a' <= char <= 'z':
                res.append(chr(ord('z') - (ord(char) - ord('a'))))
            elif 'A' <= char <= 'Z':
                res.append(chr(ord('Z') - (ord(char) - ord('A'))))
            else:
                res.append(char)
        return "".join(res)

    @classmethod
    def solve_vigenere(cls, text: str, key: str) -> str:
        """Decrypt Vigenere cipher using a known or hypothesized key."""
        clean_key = [c.lower() for c in key if c.isalpha()]
        if not clean_key:
            return text
        res = []
        key_idx = 0
        for char in text:
            if char.isalpha():
                shift = ord(clean_key[key_idx % len(clean_key)]) - ord('a')
                if 'a' <= char <= 'z':
                    res.append(chr((ord(char) - ord('a') - shift) % 26 + ord('a')))
                elif 'A' <= char <= 'Z':
                    res.append(chr((ord(char) - ord('A') - shift) % 26 + ord('A')))
                key_idx += 1
            else:
                res.append(char)
        return "".join(res)

    @classmethod
    def analyze_frequencies(cls, text: str) -> Dict[str, Any]:
        """Compute letter frequency counts and percentage distribution."""
        letters = [c.lower() for c in text if c.isalpha()]
        total = len(letters)
        if total == 0:
            return {"total_letters": 0, "frequencies": {}}

        counts = collections.Counter(letters)
        freq_dict = {
            char: {
                "count": counts[char],
                "percentage": round((counts[char] / total) * 100, 2),
                "expected_english": round(ENGLISH_FREQ.get(char, 0) * 100, 2)
            }
            for char in "abcdefghijklmnopqrstuvwxyz"
        }
        return {
            "total_letters": total,
            "frequencies": freq_dict,
            "top_characters": "".join([pair[0] for pair in counts.most_common(10)])
        }

    @classmethod
    def identify_hash(cls, hash_str: str) -> List[Dict[str, str]]:
        """Identify potential hash algorithms based on string length, character set, and salt format."""
        cleaned = hash_str.strip()
        candidates = []

        if cleaned.startswith("$2a$") or cleaned.startswith("$2b$") or cleaned.startswith("$2y$"):
            candidates.append({"algorithm": "bcrypt", "format": "Modular Crypt Format (bcrypt)"})
        elif cleaned.startswith("$argon2"):
            candidates.append({"algorithm": "Argon2", "format": "Argon2 Password Hash"})
        elif cleaned.startswith("$6$"):
            candidates.append({"algorithm": "SHA-512 Crypt", "format": "Unix SHA-512 ($6$)"})
        elif cleaned.startswith("$1$"):
            candidates.append({"algorithm": "MD5 Crypt", "format": "Unix MD5 ($1$)"})

        if re.fullmatch(r"[0-9a-fA-F]+", cleaned):
            l = len(cleaned)
            if l == 32:
                candidates.extend([
                    {"algorithm": "MD5", "format": "Hex 128-bit"},
                    {"algorithm": "NTLM", "format": "Windows NTLM Hash"},
                    {"algorithm": "MD4", "format": "Hex 128-bit"},
                ])
            elif l == 40:
                candidates.extend([
                    {"algorithm": "SHA-1", "format": "Hex 160-bit"},
                    {"algorithm": "RIPEMD-160", "format": "Hex 160-bit"},
                ])
            elif l == 64:
                candidates.extend([
                    {"algorithm": "SHA-256", "format": "Hex 256-bit"},
                    {"algorithm": "HMAC-SHA256", "format": "Hex 256-bit"},
                ])
            elif l == 128:
                candidates.extend([
                    {"algorithm": "SHA-512", "format": "Hex 512-bit"},
                    {"algorithm": "Whirlpool", "format": "Hex 512-bit"},
                ])

        return candidates

    @classmethod
    def rsa_cube_root_attack(cls, c: int, e: int = 3) -> Optional[int]:
        """Solve RSA message when public exponent e is small (e.g. 3) and message m^e < n."""
        # Integer n-th root
        low = 0
        high = c
        while low <= high:
            mid = (low + high) // 2
            mid_pow = mid ** e
            if mid_pow == c:
                return mid
            elif mid_pow < c:
                low = mid + 1
            else:
                high = mid - 1
        return None

    @classmethod
    def fermat_factorization(cls, n: int, max_iterations: int = 100000) -> Optional[Tuple[int, int]]:
        """Factor RSA modulus n when prime factors p and q are close to sqrt(n)."""
        import math
        a = math.isqrt(n)
        if a * a < n:
            a += 1

        for _ in range(max_iterations):
            b2 = a * a - n
            if b2 >= 0:
                b = math.isqrt(b2)
                if b * b == b2:
                    p = a - b
                    q = a + b
                    if p * q == n and p > 1 and q > 1:
                        return (p, q)
            a += 1
        return None
