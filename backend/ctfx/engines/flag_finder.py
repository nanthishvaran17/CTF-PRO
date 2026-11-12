import re
from typing import List, Dict, Any, Optional, Set, Pattern

DEFAULT_FLAG_PATTERNS = [
    r"FLAG\{[A-Za-z0-9_\-\.\:\@\!\#\$\%\^\&\*\+\= ]+\}",
    r"flag\{[A-Za-z0-9_\-\.\:\@\!\#\$\%\^\&\*\+\= ]+\}",
    r"CTF\{[A-Za-z0-9_\-\.\:\@\!\#\$\%\^\&\*\+\= ]+\}",
    r"ctf\{[A-Za-z0-9_\-\.\:\@\!\#\$\%\^\&\*\+\= ]+\}",
    r"picoCTF\{[A-Za-z0-9_\-\.\:\@\!\#\$\%\^\&\*\+\= ]+\}",
    r"HTB\{[A-Za-z0-9_\-\.\:\@\!\#\$\%\^\&\*\+\= ]+\}",
    r"THM\{[A-Za-z0-9_\-\.\:\@\!\#\$\%\^\&\*\+\= ]+\}",
    r"DUCTF\{[A-Za-z0-9_\-\.\:\@\!\#\$\%\^\&\*\+\= ]+\}",
    r"[a-zA-Z0-9_\-]{2,20}\{[A-Za-z0-9_\-\.\:\@\!\#\$\%\^\&\*\+\= ]{4,120}\}",
]

class FlagFinder:
    """Detects flags using compiled regular expressions, custom prefixes, and description auto-detection."""

    def __init__(self, custom_regexes: Optional[List[str]] = None, case_sensitive: bool = True):
        self.case_sensitive = case_sensitive
        patterns = list(DEFAULT_FLAG_PATTERNS)
        if custom_regexes:
            patterns.extend(custom_regexes)

        flags = 0 if case_sensitive else re.IGNORECASE
        self.compiled_patterns: List[Pattern] = []
        for pat in patterns:
            try:
                self.compiled_patterns.append(re.compile(pat, flags))
            except re.error:
                continue

    @classmethod
    def auto_detect_format_from_text(cls, text: str) -> Optional[str]:
        """Detect flag pattern specification from challenge description or hints.
        e.g., 'Flag format: ctf{...}', 'flag format is hackme{...}', or 'format is team_name{hash}'
        """
        hint_patterns = [
            r"flags?\s+format\s+is[:\s]+([a-zA-Z0-9_\-]+)\{",
            r"flags?\s+(?:format|is|looks\s+like)[:\s]+([a-zA-Z0-9_\-]+)\{",
            r"format\s+is[:\s]+([a-zA-Z0-9_\-]+)\{",
            r"format[:\s]+([a-zA-Z0-9_\-]+)\{",
            r"flags?\s+are\s+of\s+the\s+form\s+([a-zA-Z0-9_\-]+)\{",
            r"([a-zA-Z0-9_\-]+)\{[^}]+\}",
        ]
        for hp in hint_patterns:
            m = re.search(hp, text, re.IGNORECASE)
            if m:
                prefix = re.escape(m.group(1))
                return rf"{prefix}\{{[A-Za-z0-9_\-\.\:\@\!\#\$\%\^\&\*\+\= ]+\}}"
        return None

    def scan_text(self, text: str, source_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Scan text and return matched flag candidates with character offsets."""
        candidates: List[Dict[str, Any]] = []
        seen_values: Set[str] = set()

        for pattern in self.compiled_patterns:
            for match in pattern.finditer(text):
                flag_str = match.group(0).strip()
                if flag_str in seen_values:
                    continue
                seen_values.add(flag_str)

                entry = {
                    "flag": flag_str,
                    "pattern": pattern.pattern,
                    "char_start": match.start(),
                    "char_end": match.end(),
                    "source_context": source_context or {},
                }
                candidates.append(entry)

        return candidates

    def scan_binary(self, raw_bytes: bytes, source_file: Optional[str] = None) -> List[Dict[str, Any]]:
        """Directly scan raw bytes for flag candidates and record exact byte offsets."""
        candidates: List[Dict[str, Any]] = []
        seen: Set[str] = set()

        for pattern in self.compiled_patterns:
            try:
                b_pattern = re.compile(pattern.pattern.encode("utf-8"), pattern.flags)
            except Exception:
                continue

            for match in b_pattern.finditer(raw_bytes):
                try:
                    flag_val = match.group(0).decode("utf-8", errors="replace").strip()
                except Exception:
                    continue

                if flag_val in seen:
                    continue
                seen.add(flag_val)

                candidates.append({
                    "flag": flag_val,
                    "pattern": pattern.pattern,
                    "byte_offset": match.start(),
                    "byte_end": match.end(),
                    "source_file": source_file,
                })

        return candidates
