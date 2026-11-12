# CTF-PRO (CTF HUNTER X)
### *Next-Generation Autonomous, Evidence-Based CTF Analysis & Flag Discovery Platform*

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0%2B-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Tests: 24 Passed](https://img.shields.io/badge/Tests-24%2F24%20Passed-10B981?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![Security: SSRF Protected](https://img.shields.io/badge/Security-SSRF%20%26%20Zip--Slip%20Safe-blueviolet?style=for-the-badge&logo=shield)](docs/THREAT_MODEL.md)

---

## 🌟 Executive Summary

**CTF-PRO** (powered by the **CTF HUNTER X Engine**) is a local-first, evidence-anchored cybersecurity analysis workstation engineered for competitive CTF teams, digital forensics analysts, and security researchers.

Unlike conventional heuristic tools that guess or simulate findings, **CTF-PRO operates on a strict zero-simulation rule**: every candidate flag, decoded artifact, and carved stream is backed by immutable cryptographic provenance (source SHA-256, magic-byte true type, exact file byte offset, and reproducible transformation chains).

---

## 🚀 Key Value Propositions

- 🛡️ **Zero Fake Flags & Real Execution**: No mock or hardcoded flags. If an external tool is missing, CTF-PRO automatically falls back to hardened pure-Python parsers.
- 🔗 **Deep-Linked Hex & Evidence DAG**: Click any candidate flag to immediately jump to its exact byte offset in the interactive Hex Viewer.
- 🔄 **Recursive Cyclic-Safe Decoder**: Unravels multi-layer obfuscation (Base64, Base32, Hex, ROT13, Caesar, XOR, URL, HTML, ASCII decimal) with hash loop prevention and strict memory bounds.
- 🗄️ **Safe Archive Unpacker**: Built-in Zip-Slip path traversal defense, symlink trap rejection, and decompression bomb caps.
- 🌐 **SSRF-Guarded Web Auditing**: Strict IP validation disallows loopback (`127.0.0.1`), RFC 1918 private subnets, and cloud instance metadata endpoints (`169.254.169.254`).
- 📊 **Enterprise Reporting**: One-click generation of audit reports in **HTML**, **JSON**, **CSV**, and **PDF**, plus auto-generated GitHub Flavored Markdown writeups and standalone Python reproduction scripts.

---

## 🏛️ System Architecture

```
                                  +---------------------------------------+
                                  |     React 19 + TypeScript Frontend    |
                                  |  - 3-Panel Cybersecurity Workspace    |
                                  |  - Interactive Slicing Hex Viewer     |
                                  |  - Provenance Directed Acyclic Graph  |
                                  |  - 15 Modular Analysis Views          |
                                  +-------------------+-------------------+
                                                      | REST API & SSE (/api/v1)
                                  +-------------------v-------------------+
                                  |    FastAPI Async Engine & Queue       |
                                  |  - Local / Remote Dual Security Modes |
                                  |  - Asynchronous Background Pipeline   |
                                  +---------+-------------------+---------+
                                            |                   |
                    +-----------------------v---+           +---v-----------------------+
                    |  Modular Analysis Engines |           |    Storage & Persistence  |
                    |  - True Magic-Byte Intake |           |  - SQLite (WAL Async)     |
                    |  - High-Perf Strings      |           |  - Read-Only Vault (0o444)|
                    |  - Multi-Layer Decoder    |           |  - Immutable File Hashes  |
                    +-------------+-------------+           +---------------------------+
                                  |
    +-----------------------------v-------------------------------------------------------+
    |                             Specialized Domain Modules                              |
    |  +--------------------+  +--------------------+  +--------------------+             |
    |  | Steganography      |  | Network Forensics  |  | Cryptanalysis      |             |
    |  | - PNG Chunk Audit  |  | - PCAP TCP Streams |  | - Caesar / ROT /   |             |
    |  | - LSB RGB Bitplanes|  | - HTTP Carving     |  |   Vigenere         |             |
    |  | - Visual Difference|  | - Credentials Hunt |  | - XOR Key Bruter   |             |
    |  | - Trailing Bytes   |  | - Log Normalizer   |  | - Weak RSA (e=3)   |             |
    |  +--------------------+  +--------------------+  +--------------------+             |
    |  +--------------------+  +--------------------+  +--------------------+             |
    |  | Reverse Engineering|  | Web (SSRF-Safe)    |  | OSINT / Media      |             |
    |  | - ELF / PE Headers |  | - Static JS Audit  |  | - EXIF GPS -> Coords|            |
    |  | - Section Audit    |  | - JWT Discovery    |  | - WAV Envelope &   |             |
    |  | - Suspicious APIs  |  | - HTML Secrets     |  |   Spectrum FFT     |             |
    |  +--------------------+  +--------------------+  +--------------------+             |
    +-------------------------------------------------------------------------------------+
```

---

## 🚦 Candidate Flag Lifecycle

Flags transition strictly through 7 distinct states. A flag is **never** marked `VERIFIED` without authoritative confirmation from the target oracle or scoreboard:

| Status Badge | State Description | Promotion Criteria |
|---|---|---|
| `DISCOVERED` | Initial Token Match | Extracted regex token matching target format. |
| `CANDIDATE` | Format Validated | Passed string sanity and entropy checks. |
| `EVIDENCE-SUPPORTED` | Cryptographically Anchored | Linked to source file SHA-256, byte offset, and deterministic decode steps. |
| `VALIDATION-PENDING` | Submission Queued | Dispatched to scoreboard verification oracle or organizer hook. |
| `VERIFIED-BY-CHALLENGE` | Authoritatively Confirmed | Scoreboard or organizer returned confirmed acceptance (logged in verification events). |
| `REJECTED` | Invalidated | Explicitly rejected by oracle or violates challenge constraints. |
| `UNRESOLVED` | Cryptographically Incomplete | Unkeyed high-entropy cipher or missing decoding stage. |

---

## 💻 Quick Start & Deployment

### Method 1: Local Native Workstation (Recommended)

**Prerequisites**: Python 3.11+ and Node.js 18+

```bash
# 1. Clone repository
git clone https://github.com/nanthishvaran17/CTF-PRO.git
cd CTF-PRO

# 2. Install Python backend dependencies
pip install -r requirements.txt
pip install -e .

# 3. Build frontend production distribution
cd frontend
npm install
npm run build
cd ..

# 4. Start Unified Workstation
python -m uvicorn backend.ctfx.main:app --host 127.0.0.1 --port 8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

---

### Method 2: Docker & Container Orchestration

Run backend and frontend unified inside an isolated, containerized environment:

```bash
docker compose up --build
```
Navigate to **`http://localhost:8000`**.

---

### Method 3: Cross-Platform Launch Scripts

- **Windows PowerShell**:
  ```powershell
  .\scripts\run_windows.ps1
  ```
- **Linux / macOS / Kali**:
  ```bash
  chmod +x scripts/run_linux.sh scripts/setup.sh
  ./scripts/setup.sh
  ./scripts/run_linux.sh
  ```

---

## ⚡ Command Line Interface (`ctfx`)

CTF-PRO exposes a high-performance CLI for rapid file inspection and system health auditing:

```bash
# 1. Deep-analyze a challenge file for hidden strings, trailing bytes, and multi-layer flags
ctfx analyze /path/to/suspect_challenge_file

# 2. Check health, versions, and paths of host security tools
ctfx tools
```

**Real Execution Sample:**
```
[*] Ingesting target: trailing_payload.png
    - SHA-256: 88d8e58fb16c30e20e177d061459ba6fd0e52e2d1e4114278f8ba736282bfa27
    - Size: 122 bytes
    - True Magic Type: PNG (PNG binary file)
    - Entropy: 5.3735/8.0
    [!] Anomaly: Found 32 trailing bytes beyond boundary!

[*] Scanning printable strings with exact byte offsets...
    - Extracted 5 strings.

[+] Flag Discovery Complete. Discovered candidates:
    #1 Flag: FLAG{trailing_iend_detected} (offset: 92, method: direct_strings)
    #2 Flag: FLAG{trailing_iend_detected} (offset: 92, method: multilayer_decode)
```

---

## 🧩 Plugin System

CTF-PRO features an auto-discovery plugin architecture. Any `.py` file placed in the `plugins/` directory subclassing `AnalyzerPlugin` is loaded dynamically without restarting the server:

```python
from pathlib import Path
from typing import Dict, Any, Optional
from backend.ctfx.plugins.base import AnalyzerPlugin

class CustomKeywordScanner(AnalyzerPlugin):
    name = "CustomKeywordScanner"
    version = "1.0.0"
    author = "Analyst"
    description = "Scans small text files for secret keywords"
    supported_types = ["TXT", "CSV", "*"]

    def analyze(self, file_path: Path, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        with open(file_path, "rb") as f:
            data = f.read(2048)
        return {
            "found_secret": b"SECRET" in data,
            "bytes_examined": len(data)
        }
```

---

## 🧪 Comprehensive Verification Suite

Run all 24 unit, integration, and security boundary tests:

```bash
python -m pytest tests/ -v
```

```
tests/test_api.py::test_full_api_workflow PASSED                         [  4%]
tests/test_core_engines.py::test_file_intake_magic_and_entropy PASSED    [  8%]
tests/test_core_engines.py::test_strings_extractor_with_offsets PASSED   [ 12%]
tests/test_core_engines.py::test_multilayer_decoder_chains PASSED        [ 16%]
tests/test_core_engines.py::test_archive_zip_slip_and_bomb_protection PASSED [ 20%]
tests/test_core_engines.py::test_flag_finder_and_verifier PASSED         [ 25%]
tests/test_core_engines.py::test_repro_script_and_writeup PASSED         [ 29%]
tests/test_fixtures_suite.py::test_clean_file_reports_nothing_found PASSED [ 33%]
tests/test_fixtures_suite.py::test_planted_multilayer_encoded_flag PASSED [ 37%]
tests/test_fixtures_suite.py::test_planted_lsb_stego_png PASSED          [ 41%]
tests/test_fixtures_suite.py::test_trailing_bytes_png PASSED             [ 45%]
tests/test_fixtures_suite.py::test_nested_zip_extraction PASSED          [ 50%]
tests/test_fixtures_suite.py::test_pcap_http_stream_reconstruction PASSED [ 54%]
tests/test_fixtures_suite.py::test_elf_binary_strings_and_architecture PASSED [ 58%]
tests/test_modules.py::test_stego_png_and_lsb PASSED                     [ 62%]
tests/test_modules.py::test_forensics_pcap_reconstruction PASSED         [ 66%]
tests/test_modules.py::test_crypto_analysis PASSED                       [ 70%]
tests/test_modules.py::test_web_ssrf_blocking PASSED                     [ 75%]
tests/test_modules.py::test_reverse_engineering_elf PASSED               [ 79%]
tests/test_modules.py::test_plugin_discovery_and_execution PASSED        [ 83%]
tests/test_modules.py::test_tool_inventory_detection PASSED              [ 87%]
tests/test_security_bounds.py::test_zip_slip_absolute_and_relative_traversal PASSED [ 91%]
tests/test_security_bounds.py::test_archive_bomb_limits PASSED           [ 95%]
tests/test_security_bounds.py::test_ssrf_protection_subnets PASSED       [100%]
======================= 24 passed in 2.06s ========================
```

---

## 🔒 Security Posture & Honest Limitations

1. **Host Binary Execution Policy**: Uploaded binaries (ELF, PE, Mach-O) are strictly inspected via static header parsers and disassembly heuristics. Executables are never run natively on the host machine.
2. **SSRF Guard**: The web client resolves target domain names and verifies that the destination IP does not belong to loopback (`127.0.0.0/8`), RFC 1918 private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), or cloud metadata IPs (`169.254.169.254`).
3. **Deterministic Crypto Scope**: Classical ciphers (Caesar, Atbash, Vigenere, single-byte XOR), standard hash recognition, and small-exponent RSA ($e=3$) are solved deterministically. Unknown high-entropy ciphertexts without keys are reported honestly as `UNRESOLVED`.
4. **Tool Fallbacks**: If native system utilities (`binwalk`, `tshark`, `exiftool`) are missing, the UI flags them as `UNAVAILABLE` and runs verified pure-Python implementations.

---

## 📚 Documentation & Technical References

- 📖 [Architecture Specification](docs/ARCHITECTURE.md)
- 🛡️ [Threat Model & Defense Posture](docs/THREAT_MODEL.md)
- 📘 [User Guide & Shortcuts](docs/USER_GUIDE.md)
- 💻 [Developer Guide](docs/DEVELOPER_GUIDE.md)
- 🔌 [Plugin Authoring Guide](docs/PLUGIN_GUIDE.md)
- 📡 [REST API Reference](docs/API_DOCS.md)
- 🔧 [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

---

## 📄 License & Credits

- **Author**: [Nanthishvaran](https://github.com/nanthishvaran17)
- **License**: Released under the [MIT License](LICENSE).
