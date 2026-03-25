"""VitePress sidebar generator.

# @trace FR-DOCS-007
"""

from __future__ import annotations

import json
from pathlib import Path

from thegent.infra.fast_yaml_parser import yaml_load


class SidebarGenerator:
    """Walk docs root, group by frontmatter type, emit sidebar-auto.ts."""

    def __init__(self, docs_root: Path) -> None:
        self._root = docs_root

    def generate(self) -> dict[str, list[dict[str, str]]]:
        """Return sidebar groups keyed by doc type (or directory name)."""
        groups: dict[str, list[dict[str, str]]] = {}
        if not self._root.exists():
            return groups
        for md in sorted(self._root.rglob("*.md")):
            entry = self._parse(md)
            key = entry["type"]
            groups.setdefault(key, []).append({"text": entry["title"], "link": self._link(md)})
        return groups

    def emit_typescript(self) -> str:
        """Return TypeScript source for sidebar-auto.ts."""
        groups = self.generate()
        items_json = json.dumps(
            {key: [{"text": e["text"], "link": e["link"]} for e in entries] for key, entries in groups.items()},
            indent=2,
        )
        return f"export const sidebar = {items_json};\n"

    def write(self, dest: Path) -> None:
        """Write sidebar-auto.ts to dest."""
        dest.write_text(self.emit_typescript())

    def _parse(self, md: Path) -> dict[str, str]:
        text = md.read_text()
        fm: dict[str, str] = {}
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                fm = yaml_load(parts[1]) or {}
        doc_type = str(fm.get("type", md.parent.name))
        title = str(fm.get("title", md.stem))
        return {"type": doc_type, "title": title}

    def _link(self, md: Path) -> str:
        rel = md.relative_to(self._root)
        return "/" + str(rel.with_suffix(""))
