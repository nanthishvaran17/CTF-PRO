#!/usr/bin/env bash
set -e

echo "[*] Starting CTF HUNTER X Workstation..."
if ! command -v python3 &> /dev/null; then
    echo "[!] python3 is required but not installed."
    exit 1
fi

echo "[*] Launching API and UI on http://127.0.0.1:8000 ..."
python3 -m uvicorn backend.ctfx.main:app --host 127.0.0.1 --port 8000 --reload
