# CTF HUNTER X - Plugin Authoring Guide

CTF HUNTER X supports drop-in analyzer plugins. Any Python file placed in the `plugins/` directory that inherits from `AnalyzerPlugin` is automatically discovered and surfaced in the application.

## Creating a Plugin
1. Create a new file in `plugins/my_custom_plugin.py`.
2. Subclass `backend.ctfx.plugins.base.AnalyzerPlugin`.
3. Implement `analyze(self, file_path: Path, context: Optional[Dict[str, Any]]) -> Dict[str, Any]`.

## Example Plugin Implementation
```python
from pathlib import Path
from typing import Dict, Any, Optional
from backend.ctfx.plugins.base import AnalyzerPlugin

class CustomKeywordScanner(AnalyzerPlugin):
    name = "CustomKeywordScanner"
    version = "1.0.0"
    author = "Analyst"
    description = "Scans small text files for secret keywords"
    supported_types = ["TXT", "CSV", "*"]

    def analyze(self, file_path: Path, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        with open(file_path, "rb") as f:
            data = f.read(2048)
        
        has_secret = b"SECRET" in data
        return {
            "has_keyword": has_secret,
            "bytes_examined": len(data)
        }
```

The plugin manager loads the class upon execution without restarting the server.
