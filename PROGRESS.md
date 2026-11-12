# CTF HUNTER X - PROGRESS TRACKER

This document tracks autonomous progress across all milestones towards the Definition of Done.
Statuses: `TODO` | `DOING` | `DONE` | `BLOCKED`

---

## 1. Foundation & Architecture
- [x] Initialize Git repository & baseline `.gitignore` <!-- id: 1.1 -->
- [x] Create PROGRESS.md & project directory layout <!-- id: 1.2 -->
- [x] Create `docs/ARCHITECTURE.md` (System design, data flow, repo tree) <!-- id: 1.3 -->
- [x] Create `docs/THREAT_MODEL.md` (Asset boundaries, SSRF prevention, zip-slip, sandbox) <!-- id: 1.4 -->

## 2. Core Engine & File Intake
- [ ] Safe file storage & content-addressed hashing (SHA-256, chunked streaming) <!-- id: 2.1 -->
- [ ] True magic-byte file type detection (30+ formats, recursive fallback) <!-- id: 2.2 -->
- [ ] Archive unpacker with zip-slip, symlink, and bomb protection <!-- id: 2.3 -->
- [ ] High-performance string extractor (ASCII, UTF-8, UTF-16LE/BE, null-delimited, byte offsets) <!-- id: 2.4 -->
- [ ] Universal Flag Discovery Engine (regex, case-folding, custom formats, auto-detect) <!-- id: 2.5 -->
- [ ] Multi-layer Recursive Decoder (Base64/32/16, Hex, URL, HTML, ROT13, Caesar, XOR, cyclic guard, provenance tracking) <!-- id: 2.6 -->

## 3. Specialized Analysis Modules
- [ ] Stego Analyzer (PNG chunks, LSB extraction, bit planes, channels, entropy, palette, OCR/QR fallback) <!-- id: 3.1 -->
- [ ] Audio/Video Analyzer (metadata, spectrogram generation, waveform, frequency view, ffmpeg fallback) <!-- id: 3.2 -->
- [ ] Forensics Analyzer (PCAP/PCAPNG TCP stream reassembly, HTTP/DNS/TLS extraction, credentials, log normalization) <!-- id: 3.3 -->
- [ ] Cryptography Analyzer (Caesar, Atbash, Vigenere, XOR/repeating XOR, frequency analysis, hash identification, RSA/AES helpers) <!-- id: 3.4 -->
- [ ] Web Analyzer (Safe URL parser, HTTP client with private IP SSRF-guard, header/cookie inspection, static JS extraction) <!-- id: 3.5 -->
- [ ] Reverse Engineering Analyzer (ELF/PE/Mach-O header parsing, sections, imports/exports, symbols, disasm fallback) <!-- id: 3.6 -->
- [ ] OSINT Helper (Metadata extraction, EXIF GPS coordinates, domain/DNS lookup, clue correlation) <!-- id: 3.7 -->

## 4. Verification Engine & Signature Features
- [ ] Candidate Flag lifecycle state machine (7 statuses: DISCOVERED, CANDIDATE, EVIDENCE-SUPPORTED, VALIDATION-PENDING, VERIFIED-BY-CHALLENGE, REJECTED, UNRESOLVED) <!-- id: 4.1 -->
- [ ] Decoy classifier (heuristics for documentation examples, placeholders, test data with explainable reasons) <!-- id: 4.2 -->
- [ ] Interactive Evidence Graph builder (File -> Extraction -> Transform -> Candidate) <!-- id: 4.3 -->
- [ ] Reproduce Script Generator (Python & Shell reproduction commands) <!-- id: 4.4 -->
- [ ] Auto Writeup Generator (Markdown report from verified evidence chain) <!-- id: 4.5 -->
- [ ] Smart Triage Engine (next steps recommendation based on file type & clues) <!-- id: 4.6 -->
- [ ] Plugin System (Auto-discovery of `plugins/*.py` implementing `AnalyzerPlugin`) <!-- id: 4.7 -->

## 5. Tool Manager & AI Advisory
- [ ] System Tool Inventory & Health Checker (Python, Git, 7z, Binwalk, Exiftool, Wireshark/TShark, Ghidra, Radare2, FFmpeg, etc.) <!-- id: 5.1 -->
- [ ] Optional AI Assistant Interface (Ollama / Open-compatible / Offline mode; strictly marked as "Hypothesis") <!-- id: 5.2 -->

## 6. Database & REST API
- [ ] Database Schema with SQLAlchemy 2 (challenges, files, hashes, jobs, flags, evidence, decodes, verification_events, audit) <!-- id: 6.1 -->
- [ ] FastAPI Application with `/api/v1` routes (REST endpoints, pagination, OpenAPI docs) <!-- id: 6.2 -->
- [ ] Background Job Execution Queue (cancellation, status reporting, SSE/event streaming) <!-- id: 6.3 -->
- [ ] Local vs Remote Mode Support (Auth, JWT, CSRF, rate-limiting, audit log) <!-- id: 6.4 -->
- [ ] Multi-format Report Exporter (HTML, JSON, CSV, PDF) <!-- id: 6.5 -->
- [ ] CLI Interface (`ctfx analyze`, `ctfx report`, `ctfx tools`) <!-- id: 6.6 -->

## 7. Frontend User Interface
- [ ] React + Vite + TypeScript + Tailwind CSS project setup <!-- id: 7.1 -->
- [ ] Cyberpunk / Modern Dark UI Theme (#0B0F1A, #121829, #22D3EE cyan accent, WCAG AA contrast) <!-- id: 7.2 -->
- [ ] 3-Panel Workspace (File & Evidence Tree, Center multi-tab viewer, Right Candidate inspector) <!-- id: 7.3 -->
- [ ] Interactive Hex Viewer with byte-range highlight & deep-linking <!-- id: 7.4 -->
- [ ] Interactive Evidence Graph Canvas & Tree visualization <!-- id: 7.5 -->
- [ ] All 15 Required Navigation Views & Dashboard widgets <!-- id: 7.6 -->
- [ ] Keyboard Shortcuts (Ctrl+K palette, '/', 'g+h', 'g+e', 'g+r') <!-- id: 7.7 -->

## 8. Real Test Fixtures & Test Suite
- [ ] Real Fixture Generation: LSB PNG, Nested Zip, Base64/Hex/Rot13 chain, PCAP HTTP capture, ELF binary <!-- id: 8.1 -->
- [ ] Unit & Integration Test Suite (`pytest`) <!-- id: 8.2 -->
- [ ] Security Verification Tests (Zip-slip, Bomb, SSRF, Path Traversal) <!-- id: 8.3 -->
- [ ] Frontend Test Suite / verification <!-- id: 8.4 -->

## 9. Deployment, Packaging & Documentation
- [ ] Dockerfile & docker-compose.yml <!-- id: 9.1 -->
- [ ] Cross-platform launch scripts (`scripts/run_windows.ps1`, `scripts/run_linux.sh`, `scripts/setup.sh`) <!-- id: 9.2 -->
- [ ] Comprehensive Documentation (README.md with honest limitations, USER_GUIDE.md, DEVELOPER_GUIDE.md, SECURITY.md, LICENSE) <!-- id: 9.3 -->
- [ ] Final Verification against Definition of Done checklist <!-- id: 9.4 -->
