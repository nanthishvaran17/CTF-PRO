from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional
import importlib.util
import logging

logger = logging.getLogger(__name__)

class AnalyzerPlugin(ABC):
    """Base class for all CTF HUNTER X user-defined analyzer plugins."""

    name: str = "BaseAnalyzer"
    version: str = "1.0.0"
    author: str = "Anonymous"
    description: str = "Analyzer plugin description"
    supported_types: List[str] = ["*"]

    @abstractmethod
    def analyze(self, file_path: Path, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform analysis on target file and return structured results."""
        pass


class PluginManager:
    """Discovers and runs third-party plugins in the plugins/ folder."""

    def __init__(self, plugins_dir: Path):
        self.plugins_dir = plugins_dir
        self.loaded_plugins: Dict[str, AnalyzerPlugin] = {}

    def discover_and_load(self) -> Dict[str, AnalyzerPlugin]:
        """Scan plugins directory for Python modules implementing AnalyzerPlugin."""
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_plugins.clear()

        for py_file in self.plugins_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue

            try:
                module_name = f"ctfx_plugin_{py_file.stem}"
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)

                    for attr_name in dir(mod):
                        attr = getattr(mod, attr_name)
                        if isinstance(attr, type) and issubclass(attr, AnalyzerPlugin) and attr is not AnalyzerPlugin:
                            instance = attr()
                            self.loaded_plugins[instance.name] = instance
                            logger.info(f"Loaded plugin: {instance.name} v{instance.version}")
            except Exception as e:
                logger.error(f"Failed loading plugin from {py_file}: {e}")

        return self.loaded_plugins

    def get_plugin_list(self) -> List[Dict[str, Any]]:
        """Return metadata list of all loaded plugins for UI."""
        return [
            {
                "name": p.name,
                "version": p.version,
                "author": p.author,
                "description": p.description,
                "supported_types": p.supported_types
            }
            for p in self.loaded_plugins.values()
        ]

    def run_plugins_for_file(self, file_path: Path, file_type: str) -> List[Dict[str, Any]]:
        """Execute all relevant plugins matching file type."""
        results = []
        for name, plugin in self.loaded_plugins.items():
            if "*" in plugin.supported_types or file_type in plugin.supported_types:
                try:
                    res = plugin.analyze(file_path, {"file_type": file_type})
                    results.append({
                        "plugin_name": name,
                        "success": True,
                        "data": res
                    })
                except Exception as e:
                    results.append({
                        "plugin_name": name,
                        "success": False,
                        "error": str(e)
                    })
        return results
