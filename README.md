# CTF HUNTER X - Evidence-Based CTF Analysis Workstation

CTF HUNTER X is a local-first, evidence-anchored Capture The Flag (CTF) analysis and flag discovery platform. Built for security researchers, students, and competitive teams, it ensures that every discovered flag is backed by deterministic cryptographic provenance (source SHA-256, true magic byte type, exact file offset, and reproducible transformation chains).

---

## Architecture Overview

```
Frontend (React 19, TypeScript, Vite, Tailwind CSS)
    |--- 3-Panel Workspace: Files Tree | Hex & Multi-Tab Inspector | Candidate & Provenance
    |--- Interactive Hex Viewer with byte-range slicing and candidate deep-linking
    |--- Evidence Provenance Directed Acyclic Graph (DAG)
    |--- 15 Cyberpunk Dark-themed Views
    |
REST API & Event Bus (FastAPI, Python 3.11+, SQLite Async WAL, SSE)
    |--- Streaming Content-Addressed Vault (SHA-256, 0o444 Read-Only Storage)
    |--- Universal Flag Discovery Engine (Regex, Case-folding, Multiline, Custom Formats)
    |--- Multi-Layer Recursive Cyclic-Safe Decoder (Base64/32/16, Hex, ROT13, Caesar, XOR)
    |--- Safe Archive Extractor (Zip-Slip and Decompression Bomb Protection)
    |--- Modular Analyzers:
           * Stego: PNG chunks, LSB bit planes, visual diff
           * Forensics: PCAP stream reassembly, HTTP extraction, basic auth credentials
           * Crypto: Caesar 25-shift chi-squared scoring, Atbash, Vigenere, Hash ID, weak RSA
           * Web: SSRF-guarded fetcher, static JS analysis, endpoint/JWT auditing
           * Reverse Engineering: ELF, PE, Mach-O header parsing, section & symbol analysis
           * OSINT: EXIF camera metadata, GPS DMS to decimal coordinates converter
    |--- Candidate Verifier (7-state lifecycle, decoy classifier, authoritative oracle logs)
    |--- Tool Manager (Native host tool detection with pure-Python fallbacks)
    |--- Report & Writeup Generator (HTML, JSON, CSV, PDF, Markdown, Repro Script)
```

---

## Quickstart & Launching

### Option 1: Native Run (Backend + Embedded Frontend)
Ensure Python 3.11+ and Node.js 18+ are available.

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install -e .

# 2. Build frontend assets
cd frontend
npm install
npm run build
cd ..

# 3. Launch application
python -m uvicorn backend.ctfx.main:app --host 127.0.0.1 --port 8000
```
Open your browser to `http://127.0.0.1:8000`.

### Option 2: Docker & Docker Compose
```bash
docker compose up --build
```
Navigate to `http://localhost:8000`.

---

## Command Line Interface (`ctfx`)

CTF HUNTER X includes a native CLI utility:

```bash
# Analyze suspect file for hidden strings, trailing bytes, and flags
ctfx analyze /path/to/suspect_challenge_file

# Check health and versions of host security tools
ctfx tools
```

---

## Verification Lifecycle & Statuses

Flags transition strictly through 7 distinct states:
1. `DISCOVERED`: Matched string or pattern token identified in target.
2. `CANDIDATE`: Validated candidate format.
3. `EVIDENCE-SUPPORTED`: Anchored to immutable source SHA-256 and byte offset.
4. `VALIDATION-PENDING`: Queued for scoreboard submission or analyst verification.
5. `VERIFIED-BY-CHALLENGE`: Authoritative confirmation received from challenge platform or organizer.
6. `REJECTED`: Explicitly rejected by validation oracle or failed format constraints.
7. `UNRESOLVED`: Incomplete decode path or unknown cryptographic scheme.

---

## Honest Limitations

In strict adherence to the project's zero-simulation policy:
1. **No Native Binary Execution on Host**: Untrusted binaries (ELF, PE, Mach-O) are analyzed purely through static header parsing, section inspection, and string extraction. Live debugging or dynamic tracing requires an isolated container sandbox.
2. **Deterministic Cryptanalysis Scope**: The built-in cryptography suite targets classical ciphers (Caesar, Atbash, Vigenere, single-byte XOR), standard hashing algorithms, and known educational RSA vulnerabilities (small public exponent $e=3$, Fermat factorization of close primes). Ciphers with high-entropy unkeyed ciphertext are reported honestly as `UNRESOLVED`.
3. **SSRF Guard Restrictions**: The web analyzer strictly blocks private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.1`), and cloud metadata (`169.254.169.254`). Active port scanning and network fuzzing are prohibited.
4. **Tool Dependency Fallbacks**: When native external binaries (e.g., `binwalk`, `tshark`, `exiftool`) are not installed on the host system, the platform displays their status as `UNAVAILABLE` and runs verified pure-Python implementations.
