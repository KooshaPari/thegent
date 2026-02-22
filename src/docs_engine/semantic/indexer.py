"""Nightly semantic knowledge extractor.

Reads conversation-dump markdown files, extracts decisions/findings/lessons
using section header + bullet point patterns, writes kb-extract docs.

# @trace FR-DOCS-011
"""

from __future__ import annotations

import re
from pathlib import Path

from docs_engine.capture.writer import DocWriter, _slugify
from docs_engine.schema.base import DocType


_SECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"#+\s*(?:decisions?|decision\s+made)\s*\n((?:\n|.*\n)*?)(?=#+|\Z)",
        re.IGNORECASE,
    ),
    re.compile(
        r"#+\s*(?:findings?|key\s+findings?)\s*\n((?:\n|.*\n)*?)(?=#+|\Z)",
        re.IGNORECASE,
    ),
    re.compile(
        r"#+\s*(?:lessons?\s*(?:learned)?|takeaways?)\s*\n((?:\n|.*\n)*?)(?=#+|\Z)",
        re.IGNORECASE,
    ),
]

_BULLET: re.Pattern[str] = re.compile(r"^\s*[-*]\s+(.+)", re.MULTILINE)


class SemanticIndexer:
    """Extract structured knowledge from conversation dumps."""

    def __init__(self, docs_root: Path, db_path: Path) -> None:
        self._root = docs_root
        self._writer = DocWriter(docs_root=docs_root, db_path=db_path)

    def extract(self) -> list[dict[str, str]]:
        """Return list of {title, body, source} dicts from all dumps."""
        items: list[dict[str, str]] = []
        dump_dir = self._root / "research"
        if not dump_dir.exists():
            return items
        for dump_file in sorted(dump_dir.glob("CONVERSATION_DUMP_*.md")):
            items.extend(self._extract_file(dump_file))
        return items

    def _extract_file(self, path: Path) -> list[dict[str, str]]:
        text = path.read_text()
        items: list[dict[str, str]] = []
        for pattern in _SECTION_PATTERNS:
            for match in pattern.finditer(text):
                body = match.group(1)
                for bullet in _BULLET.findall(body):
                    bullet = bullet.strip()
                    if len(bullet) < 5:
                        continue
                    items.append({"title": bullet[:120], "body": bullet, "source": path.name})
        return items

    def run(self) -> int:
        """Extract items and write new kb-extract docs. Returns count of new docs written."""
        items = self.extract()
        if not items:
            return 0
        kb_dir = self._root / "kb"
        kb_dir.mkdir(parents=True, exist_ok=True)
        existing_slugs = {f.stem for f in kb_dir.glob("*.md")}
        count = 0
        for item in items:
            slug = _slugify(item["title"])
            # Filenames are "{date}-{slug}.md", so stem contains slug as suffix after date.
            already_exists = any(stem.endswith(slug) for stem in existing_slugs)
            if already_exists:
                continue
            written_path = self._writer.new(
                DocType.KB_EXTRACT,
                title=item["title"],
                tags=[item["source"]],
            )
            existing_slugs.add(written_path.stem)
            count += 1
        return count
