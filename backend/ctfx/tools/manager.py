import os
import platform
import shutil
import subprocess
from typing import Dict, Any, List

TOOL_DEFINITIONS = [
    {
        "name": "python",
        "binary": "python",
        "description": "Python runtime environment & script execution",
        "category": "Core Runtime",
        "install_guidance": {
            "Windows": "Download installer from python.org or via winget: winget install Python.Python.3.11",
            "Linux": "sudo apt install python3 python3-pip",
            "Darwin": "brew install python3"
        }
    },
    {
        "name": "git",
        "binary": "git",
        "description": "Version control & repository analyzer",
        "category": "Version Control",
        "install_guidance": {
            "Windows": "winget install Git.Git",
            "Linux": "sudo apt install git",
            "Darwin": "brew install git"
        }
    },
    {
        "name": "7-Zip",
        "binary": "7z",
        "description": "High-ratio archive unpacker (7z, rar, iso, dmg)",
        "category": "Archive Extraction",
        "install_guidance": {
            "Windows": "winget install 7zip.7zip",
            "Linux": "sudo apt install p7zip-full",
            "Darwin": "brew install p7zip"
        }
    },
    {
        "name": "Binwalk",
        "binary": "binwalk",
        "description": "Firmware analysis tool & embedded file carver",
        "category": "Forensics & Stego",
        "install_guidance": {
            "Windows": "Install via WSL or python -m pip install binwalk",
            "Linux": "sudo apt install binwalk",
            "Darwin": "brew install binwalk"
        }
    },
    {
        "name": "ExifTool",
        "binary": "exiftool",
        "description": "Read and write image/media metadata and camera EXIF",
        "category": "OSINT & Forensics",
        "install_guidance": {
            "Windows": "winget install OliverBetz.ExifTool",
            "Linux": "sudo apt install libimage-exiftool-perl",
            "Darwin": "brew install exiftool"
        }
    },
    {
        "name": "TShark / Wireshark",
        "binary": "tshark",
        "description": "Terminal-based network packet capture and dissection engine",
        "category": "Network Forensics",
        "install_guidance": {
            "Windows": "winget install WiresharkFoundation.Wireshark",
            "Linux": "sudo apt install tshark",
            "Darwin": "brew install wireshark"
        }
    },
    {
        "name": "Nmap",
        "binary": "nmap",
        "description": "Network mapper and port auditor (authorized targets only)",
        "category": "Network Discovery",
        "install_guidance": {
            "Windows": "winget install Insecure.Nmap",
            "Linux": "sudo apt install nmap",
            "Darwin": "brew install nmap"
        }
    },
    {
        "name": "Ghidra",
        "binary": "ghidraRun",
        "description": "NSA software reverse engineering decompiler framework",
        "category": "Reverse Engineering",
        "install_guidance": {
            "Windows": "Download zip from ghidra-sre.org and set PATH or winget install Ghidra",
            "Linux": "sudo apt install ghidra or download release zip",
            "Darwin": "brew install --cask ghidra"
        }
    },
    {
        "name": "Radare2",
        "binary": "r2",
        "description": "Unix-like reverse engineering framework and hex editor",
        "category": "Reverse Engineering",
        "install_guidance": {
            "Windows": "winget install radareorg.radare2",
            "Linux": "sudo apt install radare2",
            "Darwin": "brew install radare2"
        }
    },
    {
        "name": "Rizin",
        "binary": "rizin",
        "description": "Fork of radare2 with focus on usability and security",
        "category": "Reverse Engineering",
        "install_guidance": {
            "Windows": "winget install dev.rizin",
            "Linux": "sudo apt install rizin",
            "Darwin": "brew install rizin"
        }
    },
    {
        "name": "Tesseract OCR",
        "binary": "tesseract",
        "description": "Optical Character Recognition engine for text inside images",
        "category": "Stego & OCR",
        "install_guidance": {
            "Windows": "winget install UB-Mannheim.TesseractOCR",
            "Linux": "sudo apt install tesseract-ocr",
            "Darwin": "brew install tesseract"
        }
    },
    {
        "name": "ImageMagick",
        "binary": "magick",
        "description": "Bitmap manipulation, image compare and format conversion",
        "category": "Steganography",
        "install_guidance": {
            "Windows": "winget install ImageMagick.ImageMagick",
            "Linux": "sudo apt install imagemagick",
            "Darwin": "brew install imagemagick"
        }
    },
    {
        "name": "FFmpeg",
        "binary": "ffmpeg",
        "description": "Complete audio and video streams processor and decoder",
        "category": "Audio / Video",
        "install_guidance": {
            "Windows": "winget install Gyan.FFmpeg",
            "Linux": "sudo apt install ffmpeg",
            "Darwin": "brew install ffmpeg"
        }
    },
    {
        "name": "Volatility 3",
        "binary": "vol",
        "description": "Memory forensics framework for RAM dump extraction",
        "category": "Memory Forensics",
        "install_guidance": {
            "Windows": "python -m pip install volatility3",
            "Linux": "python3 -m pip install volatility3",
            "Darwin": "brew install volatility3"
        }
    }
]

class ToolInventoryManager:
    """Detects available security tools on the host, checks version, and reports health and install guidance."""

    @classmethod
    def get_inventory(cls) -> List[Dict[str, Any]]:
        current_os = platform.system()  # 'Windows', 'Linux', 'Darwin'
        inventory = []

        for item in TOOL_DEFINITIONS:
            binary_name = item["binary"]
            resolved_path = shutil.which(binary_name)
            if not resolved_path and current_os == "Windows":
                # Check .exe extension
                resolved_path = shutil.which(f"{binary_name}.exe")

            is_installed = resolved_path is not None
            version_str = "Unavailable"

            if is_installed and resolved_path:
                try:
                    # Execute with short timeout to query version
                    proc = subprocess.run(
                        [resolved_path, "--version"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=2,
                        text=True,
                        shell=False
                    )
                    out = (proc.stdout or proc.stderr or "").strip().split("\n")[0]
                    version_str = out[:80] if out else "Installed (version string empty)"
                except Exception:
                    version_str = "Installed"

            guidance = item["install_guidance"].get(current_os, item["install_guidance"]["Linux"])

            inventory.append({
                "name": item["name"],
                "binary": item["binary"],
                "category": item["category"],
                "description": item["description"],
                "is_installed": is_installed,
                "version": version_str,
                "executable_path": resolved_path or "Not found in PATH",
                "install_guidance": guidance,
                "fallback_available": True,  # Python fallbacks exist for all core operations
            })

        return inventory
