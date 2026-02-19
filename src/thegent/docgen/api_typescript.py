"""TypeScript/JavaScript API generator."""

from pathlib import Path
from typing import Any


class TypeScriptAPIGenerator:
    """Generate TypeScript/JavaScript API documentation."""

    def __init__(self):
        """Initialize TypeScript API generator."""
        self.interfaces: list[dict[str, Any]] = []
        self.functions: list[dict[str, Any]] = []

    def parse_file(self, file_path: Path) -> dict[str, Any]:
        """Parse a TypeScript/JavaScript file.
        
        Args:
            file_path: Path to TS/JS file
            
        Returns:
            Parsed file information
        """
        content = file_path.read_text()
        
        # Simple parsing - would use proper TS parser in production
        interfaces = []
        functions = []
        
        # Extract interfaces
        import re
        interface_pattern = r"interface\s+(\w+)\s*\{"
        for match in re.finditer(interface_pattern, content):
            interfaces.append({"name": match.group(1)})
        
        # Extract functions
        func_pattern = r"(?:export\s+)?(?:async\s+)?function\s+(\w+)"
        for match in re.finditer(func_pattern, content):
            functions.append({"name": match.group(1)})
        
        return {
            "path": str(file_path),
            "interfaces": interfaces,
            "functions": functions,
        }

    def generate_docs(self, file_info: dict[str, Any]) -> str:
        """Generate documentation from file info.
        
        Args:
            file_info: File information dictionary
            
        Returns:
            Generated markdown documentation
        """
        lines = [f"# {Path(file_info['path']).stem}"]
        lines.append("")
        
        if file_info["interfaces"]:
            lines.append("## Interfaces")
            lines.append("")
            for iface in file_info["interfaces"]:
                lines.append(f"### {iface['name']}")
                lines.append("")
        
        if file_info["functions"]:
            lines.append("## Functions")
            lines.append("")
            for func in file_info["functions"]:
                lines.append(f"### {func['name']}")
                lines.append("")
        
        return "\n".join(lines)
