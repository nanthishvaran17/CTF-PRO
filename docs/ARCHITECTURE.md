# CTF HUNTER X - System Architecture

## 1. High-Level Overview
CTF HUNTER X is an evidence-first, local-first CTF analysis and flag discovery workstation. Every piece of intelligence, candidate flag, and extracted artifact is strictly anchored to immutable cryptographic provenance (source file hash, exact byte offset, transformation chain, and tool invocation metadata).

```
                      +---------------------------------------+
                      |       Web Frontend (Vite/React/TS)    |
                      |  3-Panel Workspace / Hex / Graph View |
                      +-------------------+-------------------+
                                          | REST / SSE / WS
                      +-------------------v-------------------+
                      |      FastAPI Backend Core (/api/v1)   |
                      |   Authentication & Session Control    |
                      +---------+-------------------+---------+
                                |                   |
        +-----------------------v---+           +---v-----------------------+
        |   Orchestrator & Queue    |           |   Storage & DB Layer      |
        | - Analysis Job Pipeline   |           | - SQLite (Local) / PG     |
        | - Process Isolation Worker|           | - Content-Addressed Vault |
        +-------------+-------------+           +---------------------------+
                      |
    +-----------------v---------------------------------------------------+
    |                   Analysis & Verification Engines                   |
    |  +--------------------+  +--------------------+  +----------------+ |
    |  | File Intake & Type |  | Strings & Decoder  |  | Stego / Vision | |
    |  +--------------------+  +--------------------+  +----------------+ |
    |  | Forensics & PCAP   |  | Cryptanalysis      |  | Reverse Eng    | |
    |  +--------------------+  +--------------------+  +----------------+ |
    |  | Web (SSRF-Safe)    |  | OSINT Metadata     |  | Plugin Host    | |
    |  +--------------------+  +--------------------+  +----------------+ |
    |                                                                     |
    |  Verification Engine: 7-State Candidate Lifecycle & Decoy Classifier|
    |  Artifact & Evidence Graph Builder -> Repro Script -> Auto-Writeup  |
    +---------------------------------------------------------------------+
```

## 2. Directory Tree
```
e:\CTF Pro1\
|-- .github/workflows/          # CI/CD Workflows (test, lint, security audit)
|-- backend/                    # FastAPI backend, analyzers, engines, CLI
|   |-- alembic/                # DB Migrations
|   |-- ctfx/                   # Python package
|   |   |-- api/                # FastAPI router endpoints (/api/v1)
|   |   |   |-- v1/             # Challenges, files, analysis, flags, tools, reports
|   |   |-- core/               # App configuration, security, job queue, events
|   |   |-- db/                 # SQLAlchemy 2 models, session management
|   |   |-- engines/            # Core computational engines
|   |   |   |-- intake.py       # Magic bytes, hash streaming, safe extraction
|   |   |   |-- strings.py      # Unicode/ASCII strings with exact byte offsets
|   |   |   |-- decoder.py      # Multi-layer recursive cyclic-safe decoder
|   |   |   |-- flag_finder.py  # Regex/custom pattern detector & auto-detector
|   |   |   |-- verifier.py     # 7-status lifecycle, decoy filter, evidence link
|   |   |-- modules/            # Specialized security domains
|   |   |   |-- stego.py        # LSB, bitplanes, PNG chunks, image compare
|   |   |   |-- forensics.py    # PCAP/PCAPNG streams, credentials, logs
|   |   |   |-- crypto.py       # Caesar, XOR, frequency analysis, weak RSA
|   |   |   |-- web.py          # SSRF-safe URL/HTML/JS analyzer
|   |   |   |-- re.py           # ELF/PE/Mach-O static headers & disassembly
|   |   |   |-- osint.py        # EXIF, metadata, GPS geolocation clues
|   |   |-- reporting/          # HTML, JSON, CSV, PDF, Markdown writeup & repro
|   |   |-- tools/              # Tool inventory detector & OS installer guidance
|   |   |-- plugins/            # Plugin loader interface
|   |   |-- cli.py              # `ctfx` command-line entrypoint
|-- frontend/                   # React + TypeScript + Vite + Tailwind PWA
|   |-- src/
|   |   |-- api/                # Typed REST client & SSE listeners
|   |   |-- components/         # 3-panel workspace, Hex Viewer, Evidence Graph
|   |   |-- pages/              # 15 distinct navigation views
|   |   |-- theme/              # Cyberpunk dark / light design tokens
|-- plugins/                    # Drop-in user plugins (*.py)
|-- tests/                      # Fixtures, unit, integration, and security tests
|-- docs/                       # Architecture, Threat Model, Guides
|-- docker/                     # Container definitions & compose manifests
|-- scripts/                    # Platform launch scripts (Windows, Linux, macOS)
```

## 3. Data Pipeline & Provenance
1. **Intake**: A file is ingested via upload or CLI. It is streamed into storage, never loaded wholly into memory. Its SHA-256 and true magic-byte signature are computed.
2. **Analysis**: Analysis jobs run through the modular engine. Each discovery creates an `EvidenceNode` recording:
   - Source File UUID & SHA-256
   - Byte offset (start and end)
   - Encoding & transformation steps
   - Tool/Fallback utilized
3. **Candidate Promotion**: Discovered tokens matching flag patterns are added as `CANDIDATE`. Heuristic evaluation checks for decoys/placeholders. Only explicit organizer/platform responses mark a candidate `VERIFIED-BY-CHALLENGE`.
4. **Synthesis**: The evidence chain forms a directed acyclic graph (DAG) exported to Markdown writeups and executable shell/python reproduction scripts.
