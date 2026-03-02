"""Shadow audit Git log with secret scrubbing.

Tracks all git operations as immutable audit entries in SQLite, with
automatic secret scrubbing via the native secret scanner before storage.

Journal classes (GitJournal, GitJournalEnhanced, GitJournalAsync) are
defined in audit_journal.py and re-exported here for backward compatibility.

WBS: wp-71002-shadow-git
FR Traceability: FR-VER-003 (shadow audit log with secret scrubbing)
"""

from __future__ import annotations

import logging
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from thegent.audit.constants import DEFAULT_DB_PATH as _DEFAULT_DB_PATH
from thegent.audit.secret_scrubbing import scrub_secrets as _scrub_secrets

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def _now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()


class AuditEntry(BaseModel):
    """An immutable audit log entry for a git commit."""

    id: str = Field(default_factory=_new_id)
    project_id: str
    sha: str
    message: str
    diff: str
    created_at: str = Field(default_factory=_now_iso)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dict."""
        return self.model_dump()


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_AUDIT_SCHEMA_SQL = """\
CREATE TABLE IF NOT EXISTS audit_entries (
    id         TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    sha        TEXT NOT NULL,
    message    TEXT NOT NULL,
    diff       TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

# ---------------------------------------------------------------------------
# ShadowAuditGit
# ---------------------------------------------------------------------------


class ShadowAuditGit:
    """Tracks git operations as immutable audit entries with secret scrubbing.

    All commit messages and diffs are scrubbed for secrets before storage.
    Uses the same SQLite database as ProjectRegistry (shared DB path).

    Parameters
    ----------
    db_path:
        Path to the SQLite database file.  Defaults to ``~/.thegent/registry.db``.
    """

    def __init__(self, db_path: Path | str | None = None) -> None:
        import os

        if db_path is None:
            env_path = os.environ.get("THGENT_REGISTRY_DB")
            self._db_path = Path(env_path) if env_path else _DEFAULT_DB_PATH
        else:
            self._db_path = Path(db_path)

        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.row_factory = sqlite3.Row
        journal_mode_cursor = self._conn.execute("PRAGMA journal_mode=WAL")
        journal_mode_cursor.fetchone()
        journal_mode_cursor.close()
        foreign_keys_cursor = self._conn.execute("PRAGMA foreign_keys=ON")
        foreign_keys_cursor.close()
        self._conn.executescript(_AUDIT_SCHEMA_SQL)
        self._conn.commit()
        log.debug("shadow_audit_git.init db_path=%s", self._db_path)

    def record_commit(
        self,
        project_id: str,
        sha: str,
        message: str,
        diff: str,
    ) -> AuditEntry:
        """Record a git commit as an immutable audit entry.

        Both the message and diff are scrubbed for secrets before storage.
        """
        scrubbed_message = _scrub_secrets(message)
        scrubbed_diff = _scrub_secrets(diff)

        entry = AuditEntry(
            project_id=project_id,
            sha=sha,
            message=scrubbed_message,
            diff=scrubbed_diff,
        )
        self._conn.execute(
            "INSERT INTO audit_entries (id, project_id, sha, message, diff, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (entry.id, entry.project_id, entry.sha, entry.message, entry.diff, entry.created_at),
        )
        self._conn.commit()
        log.info("shadow_audit_git.record_commit sha=%s project=%s", sha, project_id)
        return entry

    def get_audit_log(self, project_id: str, limit: int | None = None) -> list[AuditEntry]:
        """Return audit entries for a project, ordered by creation time.

        Parameters
        ----------
        project_id:
            The project whose audit log to retrieve.
        limit:
            Maximum number of entries to return.  None means all.
        """
        query = (
            "SELECT id, project_id, sha, message, diff, created_at "
            "FROM audit_entries WHERE project_id = ? ORDER BY created_at"
        )
        params: list[Any] = [project_id]
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        rows = self._conn.execute(query, params).fetchall()
        return [
            AuditEntry(
                id=r["id"],
                project_id=r["project_id"],
                sha=r["sha"],
                message=r["message"],
                diff=r["diff"],
                created_at=r["created_at"],
            )
            for r in rows
        ]

    def export_audit(self, project_id: str, path: Path | str) -> None:
        """Export the audit log for a project to a JSON file."""
        import orjson as json

        entries = self.get_audit_log(project_id)
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(
            json.dumps([e.to_dict() for e in entries])
        )
        log.info("shadow_audit_git.export_audit project=%s path=%s", project_id, dest)


# ---------------------------------------------------------------------------
# Re-export journal classes for backward compatibility
# ---------------------------------------------------------------------------

from thegent.audit.audit_journal import (  # noqa: E402, F401
    GitJournal,
    GitJournalAsync,
    GitJournalEnhanced,
)
