#!/usr/bin/env bash
set -e

echo "=== CTF HUNTER X - Environment Setup Script ==="
OS="$(uname -s)"

echo "[*] Detected Operating System: $OS"

if [ "$OS" = "Linux" ]; then
    if [ -f /etc/debian_version ]; then
        echo "[*] Detected Debian/Ubuntu/Kali. Installing optional native tools..."
        sudo apt-get update || true
        sudo apt-get install -y python3-pip python3-venv p7zip-full binwalk tshark ffmpeg exiftool tesseract-ocr || true
    fi
elif [ "$OS" = "Darwin" ]; then
    echo "[*] Detected macOS. Installing dependencies via Homebrew..."
    brew install p7zip tshark ffmpeg exiftool tesseract || true
fi

echo "[*] Installing Python backend dependencies..."
python3 -m pip install -r requirements.txt
python3 -m pip install -e .

echo "[*] Building frontend assets..."
if command -v npm &> /dev/null; then
    cd frontend && npm install && npm run build && cd ..
else
    echo "[!] npm not detected. Serving in API-only or development mode."
fi

echo "[+] Setup completed successfully!"
