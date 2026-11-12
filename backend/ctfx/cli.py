import argparse
import asyncio
import sys
from pathlib import Path
from .engines.intake import FileIntakeEngine
from .engines.strings import StringsExtractor
from .engines.flag_finder import FlagFinder
from .engines.decoder import MultiLayerDecoder
from .tools.manager import ToolInventoryManager
from .reporting.exporter import ReportExporter

def run_analyze(path_str: str, custom_regex: str = None):
    p = Path(path_str)
    if not p.exists():
        print(f"[!] Error: File '{path_str}' does not exist.")
        sys.exit(1)

    print(f"[*] Ingesting target: {p.name}")
    sha256, size = FileIntakeEngine.compute_sha256_and_size(p)
    f_type = FileIntakeEngine.detect_file_type(p)
    entropy = FileIntakeEngine.compute_entropy(p)
    trailing = FileIntakeEngine.detect_trailing_bytes(p, f_type["type"])

    print(f"    - SHA-256: {sha256}")
    print(f"    - Size: {size:,} bytes")
    print(f"    - True Magic Type: {f_type['type']} ({f_type['description']})")
    print(f"    - Entropy: {entropy}/8.0")
    if trailing:
        print(f"    [!] Anomaly: Found {trailing['trailing_byte_count']} trailing bytes beyond boundary!")

    print("\n[*] Scanning printable strings with exact byte offsets...")
    strings = StringsExtractor.scan_file(p, min_length=4)
    print(f"    - Extracted {len(strings)} strings.")

    finder = FlagFinder(custom_regexes=[custom_regex] if custom_regex else None)
    flags_found = []

    for s in strings:
        matches = finder.scan_text(s["value"])
        for m in matches:
            flags_found.append({
                "flag": m["flag"],
                "offset": s["offset"],
                "encoding": s["encoding"],
                "method": "direct_strings"
            })

    # Try multi-layer decoder on sampled strings
    decoder = MultiLayerDecoder()
    for s in strings[:1000]:
        val = s["value"]
        if 8 <= len(val) <= 2048:
            dec_res = decoder.decode_chain(val)
            for d in dec_res:
                flags_found.append({
                    "flag": d["flag"],
                    "offset": s["offset"],
                    "encoding": s["encoding"],
                    "method": "multilayer_decode",
                    "history": d["history"]
                })

    print(f"\n[+] Flag Discovery Complete. Discovered {len(flags_found)} candidates:")
    for idx, f in enumerate(flags_found, 1):
        print(f"    #{idx} Flag: {f['flag']} (offset: {f['offset']}, method: {f['method']})")
        if f.get("history"):
            steps = " -> ".join(h["method"] for h in f["history"])
            print(f"        Decoding Chain: {steps}")

def run_tools():
    print("[*] CTF HUNTER X - Security Tools Inventory:\n")
    tools = ToolInventoryManager.get_inventory()
    for t in tools:
        status_symbol = "[+] INSTALLED" if t["is_installed"] else "[-] MISSING  "
        print(f"{status_symbol} {t['name']:<20} | Version: {t['version']:<30} | {t['category']}")
        if not t["is_installed"]:
            print(f"    Install guidance: {t['install_guidance']}")

def main():
    parser = argparse.ArgumentParser(prog="ctfx", description="CTF HUNTER X CLI Workstation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # analyze
    p_analyze = subparsers.add_parser("analyze", help="Analyze target file for hidden flags")
    p_analyze.add_argument("path", help="Path to file")
    p_analyze.add_argument("--regex", help="Custom flag regex pattern", default=None)

    # tools
    subparsers.add_parser("tools", help="List status of installed security tools")

    args = parser.parse_args()
    if args.command == "analyze":
        run_analyze(args.path, args.regex)
    elif args.command == "tools":
        run_tools()

if __name__ == "__main__":
    main()
