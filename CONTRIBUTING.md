# Contributing to CTF HUNTER X

We welcome community contributions, custom plugins, and improvements to analysis modules.

## Contribution Guidelines
1. **Evidence-Based Determinism**: Never submit code that fakes, simulates, or hardcodes discovered flags. Every finding must stem from true file inputs, explicit byte offsets, and cryptographic verification.
2. **Safety First**: Any module interacting with network resources or archives must adhere strictly to the SSRF and Zip-Slip protections defined in `docs/THREAT_MODEL.md`.
3. **Pure Python Fallbacks**: Native system tools (such as binwalk, tshark, exiftool) must always have an operational pure-Python fallback.

## Development Workflow
1. Install Python requirements: `pip install -r requirements.txt`
2. Run backend test suite: `pytest -v tests/`
3. Build frontend assets: `cd frontend && npm install && npm run build`
4. Verify all tests pass before submitting pull requests.
