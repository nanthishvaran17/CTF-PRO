import re
from pathlib import Path
from typing import Generator, Dict, Any, List

class StringsExtractor:
    """Extracts strings from raw files across multiple encodings with exact byte offsets."""

    ASCII_PATTERN = re.compile(rb"[\x20-\x7e]{4,}")
    # UTF-16LE: printable ASCII byte followed by 0x00, repeated >= 4 times
    UTF16LE_PATTERN = re.compile(rb"(?:[\x20-\x7e]\x00){4,}")
    # UTF-16BE: 0x00 followed by printable ASCII byte, repeated >= 4 times
    UTF16BE_PATTERN = re.compile(rb"(?:\x00[\x20-\x7e]){4,}")

    @classmethod
    def scan_file(
        cls,
        file_path: Path,
        min_length: int = 4,
        max_strings: int = 20000,
        chunk_size: int = 1024 * 1024,
        overlap: int = 1024
    ) -> List[Dict[str, Any]]:
        """Streaming scanner recording exact file offsets and encodings."""
        results: List[Dict[str, Any]] = []
        file_size = file_path.stat().st_size
        offset = 0

        with open(file_path, "rb") as f:
            carry_over = b""
            carry_offset = 0

            while offset < file_size:
                f.seek(offset)
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                combined = carry_over + chunk
                base_offset = offset - len(carry_over)

                # 1. ASCII scan
                for match in cls.ASCII_PATTERN.finditer(combined):
                    if len(results) >= max_strings:
                        break
                    val = match.group(0)
                    if len(val) >= min_length:
                        s_offset = base_offset + match.start()
                        e_offset = base_offset + match.end()
                        try:
                            text = val.decode("ascii")
                            results.append({
                                "offset": s_offset,
                                "end_offset": e_offset,
                                "length": len(text),
                                "encoding": "ascii",
                                "value": text,
                                "method": "strings:ascii"
                            })
                        except Exception:
                            pass

                # 2. UTF-16LE scan
                for match in cls.UTF16LE_PATTERN.finditer(combined):
                    if len(results) >= max_strings:
                        break
                    val = match.group(0)
                    if len(val) >= min_length * 2:
                        s_offset = base_offset + match.start()
                        e_offset = base_offset + match.end()
                        try:
                            text = val.decode("utf-16le")
                            results.append({
                                "offset": s_offset,
                                "end_offset": e_offset,
                                "length": len(text),
                                "encoding": "utf-16le",
                                "value": text,
                                "method": "strings:utf-16le"
                            })
                        except Exception:
                            pass

                # 3. UTF-16BE scan
                for match in cls.UTF16BE_PATTERN.finditer(combined):
                    if len(results) >= max_strings:
                        break
                    val = match.group(0)
                    if len(val) >= min_length * 2:
                        s_offset = base_offset + match.start()
                        e_offset = base_offset + match.end()
                        try:
                            text = val.decode("utf-16be")
                            results.append({
                                "offset": s_offset,
                                "end_offset": e_offset,
                                "length": len(text),
                                "encoding": "utf-16be",
                                "value": text,
                                "method": "strings:utf-16be"
                            })
                        except Exception:
                            pass

                if len(results) >= max_strings:
                    break

                # Prepare carry over for next chunk
                if len(chunk) >= overlap:
                    carry_over = chunk[-overlap:]
                else:
                    carry_over = chunk
                offset += len(chunk)

        # De-duplicate entries by (offset, encoding)
        seen = set()
        unique_results = []
        for r in results:
            key = (r["offset"], r["encoding"])
            if key not in seen:
                seen.add(key)
                unique_results.append(r)

        return unique_results
