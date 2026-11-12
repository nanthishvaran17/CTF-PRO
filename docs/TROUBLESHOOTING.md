# CTF HUNTER X - Troubleshooting Guide

## Common Issues & Solutions

### 1. Port 8000 Already in Use
If another process occupies port 8000:
```bash
python -m uvicorn backend.ctfx.main:app --port 8080
```
Update `frontend/src/api/client.ts` to reflect the custom port if running in split frontend development mode.

### 2. Missing Native Tools (TShark, ExifTool, Binwalk)
CTF HUNTER X detects whether tools exist in PATH. If unavailable:
- The Tool Manager marks them as `UNAVAILABLE` and provides OS installation guidance.
- The core engine automatically activates built-in pure-Python fallbacks.

### 3. File Permissions on Windows or Linux
Ingested files in `data/uploads/` are marked read-only (`0o444`). To remove temporary test data:
```bash
# On Linux/macOS
rm -rf data/uploads/* data/artifacts/*
# On Windows PowerShell
Remove-Item -Recurse -Force data/uploads/*, data/artifacts/*
```
