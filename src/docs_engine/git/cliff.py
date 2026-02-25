"""git-cliff changelog runner and SQLite indexer.

# @trace FR-DOCS-010
"""

from __future__ import annotations

import subprocess
from datetime import datetime, UTC
from pathlib import Path

from docs_engine.db.indexer import DocIndexer


class CliffRunner:
    """Run git-cliff and index the resulting CHANGELOG in SQLite."""

    def __init__(self, repo_root: Path, db_path: Path) -> None:
        self._root = repo_root
        self._db_path = db_path

    def _build_command(self, output: Path) -> list[str]:
        return ["git-cliff", "--output", str(output)]

    def run(self, output: Path | None = None) -> Path:
        """Run git-cliff, write CHANGELOG, index result. Raises RuntimeError on failure."""
        if output is None:
            output = self._root / "CHANGELOG.md"
        cmd = self._build_command(output)
        result = subprocess.run(cmd, cwd=self._root, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"git-cliff failed: {result.stderr}")
        self._index(output)
        return output

    def _index(self, changelog: Path) -> None:
        indexer = DocIndexer(self._db_path)
        indexer.init_schema()
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        indexer.upsert_doc(
            path=str(changelog),
            frontmatter={
                "type": "changelog",
                "status": "published",
                "title": "CHANGELOG",
                "layer": 3,
                "date": today,
            },
        )
