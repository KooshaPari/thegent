"""Auto-generate architecture diagrams from code."""

from pathlib import Path
from typing import Any


class ArchitectureGenerator:
    """Generate architecture diagrams from code structure."""

    def __init__(self) -> None:
        """Initialize architecture generator."""
        self.components: list[dict[str, Any]] = []

    def analyze_structure(self, root_path: Path) -> dict[str, Any]:
        """Analyze code structure.

        Args:
            root_path: Root directory to analyze

        Returns:
            Structure analysis
        """
        packages = []
        modules = []

        for py_file in root_path.rglob("*.py"):
            if "__init__.py" in str(py_file):
                packages.append(str(py_file.parent))
            else:
                modules.append(str(py_file))

        return {
            "packages": packages,
            "modules": modules,
            "structure": self._build_structure(root_path),
        }

    def _build_structure(self, root_path: Path) -> dict[str, Any]:
        """Build structure tree.

        Args:
            root_path: Root directory

        Returns:
            Structure tree
        """
        structure = {}
        for item in root_path.iterdir():
            if item.is_dir() and not item.name.startswith("__"):
                structure[item.name] = self._build_structure(item)
            elif item.suffix == ".py":
                structure[item.stem] = "module"
        return structure

    def generate_mermaid(self, structure: dict[str, Any]) -> str:
        """Generate Mermaid diagram.

        Args:
            structure: Structure dictionary

        Returns:
            Mermaid diagram code
        """
        lines = ["graph TD"]

        def add_nodes(d: dict[str, Any], prefix: str = ""):
            for key, value in d.items():
                node_id = f"{prefix}_{key}" if prefix else key
                if isinstance(value, dict):
                    lines.append(f"    {node_id}[{key}]")
                    add_nodes(value, node_id)
                else:
                    lines.append(f"    {node_id}[{key}]")

        add_nodes(structure)
        return "\n".join(lines)
