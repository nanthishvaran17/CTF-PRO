# CTF HUNTER X - Windows Launch Script
Write-Host "[*] Starting CTF HUNTER X Workstation on Windows..." -ForegroundColor Cyan

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Python 3.11+ is required but not found in PATH." -ForegroundColor Red
    exit 1
}

# Start backend server
Write-Host "[*] Launching API and Unified Workstation on http://127.0.0.1:8000 ..." -ForegroundColor Green
python -m uvicorn backend.ctfx.main:app --host 127.0.0.1 --port 8000 --reload
