"""Auto-generate sidebar from directory structure."""

from pathlib import Path
from typing import Any


class AutoSidebarGenerator:
    """Generate sidebar automatically from directory structure."""

    def __init__(self, docs_root: Path) -> None:
        """Initialize auto-sidebar generator.

        Args:
            docs_root: Root directory of documentation
        """
        self.docs_root = docs_root

    def scan_structure(self) -> dict[str, Any]:
        """Scan directory structure.

        Returns:
            Structure dictionary
        """
        structure = {}

        for item in sorted(self.docs_root.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                structure[item.name] = self._scan_directory(item)
            elif item.suffix in [".md", ".mdx"]:
                structure[item.stem] = {"type": "file", "path": str(item)}

        return structure

    def _scan_directory(self, directory: Path) -> dict[str, Any]:
        """Scan a directory recursively.

        Args:
            directory: Directory to scan

        Returns:
            Directory structure
        """
        result = {"type": "directory", "children": {}}

        for item in sorted(directory.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                result["children"][item.name] = self._scan_directory(item)
            elif item.suffix in [".md", ".mdx"]:
                result["children"][item.stem] = {
                    "type": "file",
                    "path": str(item),
                }

        return result

    def generate_sidebar_config(self) -> list[dict[str, Any]]:
        """Generate sidebar configuration.

        Returns:
            Sidebar configuration list
        """
        structure = self.scan_structure()
        sidebar = []

        for key, value in structure.items():
            sidebar.append(self._build_sidebar_item(key, value))

        return sidebar

    def _build_sidebar_item(self, name: str, item: dict[str, Any]) -> dict[str, Any]:
        """Build a sidebar item.

        Args:
            name: Item name
            item: Item structure

        Returns:
            Sidebar item dictionary
        """
        if item.get("type") == "file":
            return {
                "text": name.replace("_", " ").title(),
                "link": item["path"],
            }

        result = {
            "text": name.replace("_", " ").title(),
            "collapsed": False,
            "items": [],
        }

        for child_name, child_item in item.get("children", {}).items():
            result["items"].append(self._build_sidebar_item(child_name, child_item))

        return result
