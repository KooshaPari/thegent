"""Enhanced Python API generator (mkdocstrings-like)."""

import ast
from pathlib import Path
from typing import Any


class PythonAPIGenerator:
    """Generate Python API documentation from docstrings."""

    def __init__(self) -> None:
        """Initialize Python API generator."""
        self.modules: dict[str, Any] = {}

    def parse_module(self, module_path: Path) -> dict[str, Any]:
        """Parse a Python module.

        Args:
            module_path: Path to Python module

        Returns:
            Parsed module information
        """
        content = module_path.read_text()
        tree = ast.parse(content)

        classes = []
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(
                    {
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                    }
                )
            elif isinstance(node, ast.FunctionDef):
                functions.append(
                    {
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "args": [arg.arg for arg in node.args.args],
                    }
                )

        return {
            "path": str(module_path),
            "classes": classes,
            "functions": functions,
        }

    def generate_docs(self, module_info: dict[str, Any]) -> str:
        """Generate documentation from module info.

        Args:
            module_info: Module information dictionary

        Returns:
            Generated markdown documentation
        """
        lines = [f"# {Path(module_info['path']).stem}"]
        lines.append("")

        if module_info["classes"]:
            lines.append("## Classes")
            lines.append("")
            for cls in module_info["classes"]:
                lines.append(f"### {cls['name']}")
                if cls["docstring"]:
                    lines.append(cls["docstring"])
                lines.append("")

        if module_info["functions"]:
            lines.append("## Functions")
            lines.append("")
            for func in module_info["functions"]:
                lines.append(f"### {func['name']}")
                if func["docstring"]:
                    lines.append(func["docstring"])
                lines.append("")

        return "\n".join(lines)
