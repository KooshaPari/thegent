"""SQLite doc indexer — upsert frontmatter into the docs table.

# @trace FR-DOCS-002
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, UTC
from pathlib import Path

import orjson


class DocIndexer:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        schema_sql = (Path(__file__).parent / "schema.sql").read_text()
        with self._conn() as conn:
            conn.executescript(schema_sql)

    def upsert_doc(self, path: str, frontmatter: dict) -> None:
        now = datetime.now(UTC).isoformat()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO docs (path, type, status, title, layer, date, author,
                    session_id, git_commit, tags, relates_to, traces_to, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    type=excluded.type,
                    status=excluded.status,
                    title=excluded.title,
                    layer=excluded.layer,
                    date=excluded.date,
                    indexed_at=excluded.indexed_at,
                    tags=excluded.tags,
                    relates_to=excluded.relates_to,
                    traces_to=excluded.traces_to
                """,
                (
                    path,
                    frontmatter.get("type", ""),
                    frontmatter.get("status", "draft"),
                    frontmatter.get("title", ""),
                    frontmatter.get("layer", 0),
                    frontmatter.get("date", ""),
                    frontmatter.get("author", "agent"),
                    frontmatter.get("session_id", ""),
                    frontmatter.get("git_commit", ""),
                    orjson.dumps(frontmatter.get("tags", [])).decode(),
                    orjson.dumps(frontmatter.get("relates_to", [])).decode(),
                    orjson.dumps(frontmatter.get("traces_to", [])).decode(),
                    now,
                ),
            )
