# Security Policy for CTF HUNTER X

## Authorized CTF Scope
CTF HUNTER X is designed solely for local analysis of authorized Capture The Flag (CTF) files, forensic captures, and educational lab challenges.

- **No Active Network Exploitation**: CTF HUNTER X performs no unsolicited scanning, exploitation, or attacking of remote infrastructure.
- **SSRF Defenses**: The web analysis module prohibits loopback (`127.0.0.0/8`), private networks (`RFC 1918`), and cloud instance metadata addresses (`169.254.169.254`).
- **Archive Isolation**: The archive extraction engine enforces path containment to prevent Zip-Slip vulnerabilities and decompression bombs.
- **Binary Execution Safety**: Executables (ELF, PE, Mach-O) are analyzed using static header parsers and disassembly heuristics. Binaries are never executed directly on the host operating system.

## Vulnerability Reporting
If you identify a security issue in CTF HUNTER X (such as a bypass to path traversal defenses or SSRF protections), please submit an issue via the repository's security advisory portal.
