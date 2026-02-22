"""Read-only query layer over the docs SQLite index.

# @trace FR-DOCS-002
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


class DocQueries:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_by_type(self, doc_type: str) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM docs WHERE type=? ORDER BY date DESC",
                (doc_type,),
            ).fetchall()
        return [dict(r) for r in rows]

    def get_by_status(self, status: str) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM docs WHERE status=? ORDER BY date DESC",
                (status,),
            ).fetchall()
        return [dict(r) for r in rows]

    def search(self, query: str) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM docs WHERE title LIKE ? ORDER BY date DESC",
                (f"%{query}%",),
            ).fetchall()
        return [dict(r) for r in rows]
