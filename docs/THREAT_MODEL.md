# CTF HUNTER X - Threat Model & Security Posture

## 1. Operating Scope & Intended Target
CTF HUNTER X is specifically engineered for authorized Capture The Flag (CTF) challenges, security educational labs, and forensic challenges. 
**Prohibitions**:
- No active automated network scanning against unauthorized third-party infrastructure.
- No arbitrary remote exploit payloads or malicious agent generation.
- No blind internet scraping.

## 2. Threat Actors & Attack Vectors

| Attack Vector | Threat Scenario | Mitigation Strategy |
|---|---|---|
| **Malicious Archive Upload (Zip-Slip)** | An uploaded ZIP/TAR contains path traversal characters (`../../etc/passwd`) designed to overwrite system files upon extraction. | Absolute path resolution check. Reject or normalize any entry resolving outside target extraction sandbox. Refuse symlinks pointing outside sandbox. |
| **Archive Decompression Bomb** | A tiny archive (e.g., zip bomb) that decompresses to hundreds of gigabytes, exhausting host disk and memory. | Hard caps on: total uncompressed byte size (default 250MB per file), max file count (10,000), max compression ratio (100:1), and recursive depth (max 5 layers). |
| **Server-Side Request Forgery (SSRF)** | In Web analysis mode, a user or crafted payload directs the fetcher to inspect internal cloud metadata (`169.254.169.254`), localhost (`127.0.0.1`), or private subnets (`10.0.0.0/8`, `192.168.0.0/16`). | Strict IP validation prior to socket connection. Resolve DNS and verify that resolved IP is NOT in `IPv4Network` / `IPv6Network` private, loopback, link-local, or multicast ranges. Disallow file:// and gopher:// schemes. |
| **Arbitrary Binary Execution** | In Reverse Engineering mode, a user submits an unknown or malicious ELF/PE executable. | Never execute uploaded binaries directly on the host. Execution is strictly disallowed in standard analysis. Static disassembly and header parsing only. Sandbox hooks require container isolation with dropped capabilities and no network. |
| **Host Path & Secret Leakage** | Backend exception traces or file responses leaking absolute system paths, host usernames, or environment variables. | Sanitized API error handlers returning structured RFC 7807 problem details with relative paths only. No environment secrets in error dumps. |
| **Denial of Service via Infinite Decodes** | An endless cycle of base64/hex transformations creating memory exhaustion. | Graph cycle detection using SHA-256 state tracking; hard ceiling on decode recursion depth (default max 10 steps); maximum output buffer cap per step (10MB). |
| **Unauthorized Access (Remote Mode)** | Multiple users sharing an instance where unauthenticated users can view challenge flags or tamper with verification. | Dual Mode architecture: `LOCAL` mode (zero auth friction, loopback-only) vs `REMOTE` mode (Argon2id/Bcrypt password hashing, JWT bearer tokens, CSRF tokens on mutating requests, role-based access, and immutable audit logs). |

## 3. Sandboxing & Fallback Safety
- **Pure Python Fallbacks**: Where native host tools (e.g. `binwalk`, `exiftool`, `tshark`, `radare2`) are absent, the application gracefully degrades to verified, secure pure-Python parsers.
- **Read-Only Original Files**: Intake files are stored in content-addressed storage with read-only permissions (`0o444`). All analysis operations treat originals as strictly immutable.
