"""SQLite-backed project registry for hierarchical versioning.

Tracks projects and episodes (atomic units of agent work) in a local
SQLite database with WAL mode for concurrent-safe atomic writes.

WBS: wp-71001-registry-db
FR Traceability: FR-VER-001 (project registry and episode tracking)
"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_DB_PATH = Path.home() / ".thegent" / "registry.db"
_SCHEMA_VERSION = 1

_TERMINAL_STATUSES = frozenset({"completed", "failed"})

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class EpisodeStatus(StrEnum):
    """Lifecycle status for an agent episode."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SUSPENDED = "suspended"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


class ProjectRecord(BaseModel):
    """A registered project in the hierarchy."""

    id: str = Field(default_factory=_new_id)
    name: str
    path: str
    created_at: str = Field(default_factory=_now_iso)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EpisodeRecord(BaseModel):
    """An episode: one atomic unit of agent work."""

    id: str = Field(default_factory=_new_id)
    project_id: str
    agent_id: str
    started_at: str = Field(default_factory=_now_iso)
    ended_at: str | None = None
    status: EpisodeStatus = EpisodeStatus.RUNNING
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """\
CREATE TABLE IF NOT EXISTS projects (
    id         TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    path       TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata   TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS episodes (
    id         TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    agent_id   TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at   TEXT,
    status     TEXT NOT NULL DEFAULT 'running',
    metadata   TEXT NOT NULL DEFAULT '{}'
);
"""

_SCHEMA_VERSION_SQL = """\
CREATE TABLE IF NOT EXISTS schema_version (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    version    INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class ProjectRegistry:
    """SQLite-backed registry for projects and episodes.

    Uses WAL journal mode for safe concurrent reads/writes.

    Parameters
    ----------
    db_path:
        Path to the SQLite database file.  Parent directories are created
        automatically.  Defaults to ``~/.thegent/registry.db`` or the value
        of the ``THGENT_REGISTRY_DB`` environment variable.
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
        self._init_schema()
        self._conn.commit()
        log.debug("project_registry.init", db_path=str(self._db_path))

    def _init_schema(self) -> None:
        """Initialize or migrate schema to the current version."""
        self._conn.execute(_SCHEMA_VERSION_SQL)
        current_version = self._current_schema_version()
        if current_version >= _SCHEMA_VERSION:
            return

        for next_version in range(current_version + 1, _SCHEMA_VERSION + 1):
            if next_version == 1:
                self._migrate_v0_to_v1()
            else:
                raise ValueError(f"Unsupported registry schema migration target: v{next_version}")
            self._conn.execute("INSERT INTO schema_version (version) VALUES (?)", (next_version,))

    def _current_schema_version(self) -> int:
        cursor = self._conn.execute(
            "SELECT version FROM schema_version ORDER BY id DESC LIMIT 1",
        )
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return 0
        return int(row["version"])

    def _migrate_v0_to_v1(self) -> None:
        """Initialize baseline project/episode tables for schema v1."""
        self._conn.executescript(_SCHEMA_SQL)

    # ------------------------------------------------------------------
    # Project operations
    # ------------------------------------------------------------------

    def register_project(
        self,
        name: str,
        path: str,
        metadata: dict[str, Any] | None = None,
    ) -> ProjectRecord:
        """Register a new project and persist it."""
        record = ProjectRecord(name=name, path=path, metadata=metadata or {})
        self._conn.execute(
            "INSERT INTO projects (id, name, path, created_at, metadata) VALUES (?, ?, ?, ?, ?)",
            (record.id, record.name, record.path, record.created_at, json.dumps(record.metadata)),
        )
        self._conn.commit()
        log.info("project_registry.register_project", project_id=record.id, name=name)
        return record

    def get_project(self, project_id: str) -> ProjectRecord | None:
        """Retrieve a project by ID, or None if not found."""
        row = self._conn.execute(
            "SELECT id, name, path, created_at, metadata FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()
        if row is None:
            return None
        return ProjectRecord(
            id=row["id"],
            name=row["name"],
            path=row["path"],
            created_at=row["created_at"],
            metadata=json.loads(row["metadata"]),
        )

    def list_projects(self) -> list[ProjectRecord]:
        """Return all registered projects."""
        rows = self._conn.execute(
            "SELECT id, name, path, created_at, metadata FROM projects ORDER BY created_at"
        ).fetchall()
        return [
            ProjectRecord(
                id=r["id"],
                name=r["name"],
                path=r["path"],
                created_at=r["created_at"],
                metadata=json.loads(r["metadata"]),
            )
            for r in rows
        ]

    def update_project_metadata(
        self,
        project_id: str,
        metadata: dict[str, Any],
    ) -> ProjectRecord | None:
        """Merge *metadata* into the project's existing metadata.

        Returns the updated record, or None if the project does not exist.
        """
        row = self._conn.execute(
            "SELECT id, name, path, created_at, metadata FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()
        if row is None:
            return None

        current_metadata = json.loads(row["metadata"])
        new_metadata = {**current_metadata, **metadata}
        self._conn.execute(
            "UPDATE projects SET metadata = ? WHERE id = ?",
            (json.dumps(new_metadata), project_id),
        )
        self._conn.commit()
        return ProjectRecord(
            id=row["id"],
            name=row["name"],
            path=row["path"],
            created_at=row["created_at"],
            metadata=new_metadata,
        )

    # ------------------------------------------------------------------
    # Episode operations
    # ------------------------------------------------------------------

    def create_episode(
        self,
        project_id: str,
        agent_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> EpisodeRecord:
        """Create a new running episode for the given project."""
        record = EpisodeRecord(
            project_id=project_id,
            agent_id=agent_id,
            metadata=metadata or {},
        )
        self._conn.execute(
            "INSERT INTO episodes (id, project_id, agent_id, started_at, ended_at, status, metadata) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                record.id,
                record.project_id,
                record.agent_id,
                record.started_at,
                record.ended_at,
                record.status.value,
                json.dumps(record.metadata),
            ),
        )
        self._conn.commit()
        log.info(
            "project_registry.create_episode",
            episode_id=record.id,
            project_id=project_id,
            agent_id=agent_id,
        )
        return record

    def update_episode(
        self,
        episode_id: str,
        status: EpisodeStatus | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> EpisodeRecord | None:
        """Update an episode's status and/or metadata.

        Returns the updated record, or None if the episode does not exist.
        For terminal statuses (completed, failed), ``ended_at`` is set automatically.
        """
        row = self._conn.execute(
            "SELECT id, project_id, agent_id, started_at, ended_at, status, metadata FROM episodes WHERE id = ?",
            (episode_id,),
        ).fetchone()
        if row is None:
            return None

        current_status = row["status"]
        current_metadata = json.loads(row["metadata"])
        current_ended_at = row["ended_at"]

        new_status = status.value if status is not None else current_status
        new_metadata = {**current_metadata, **(metadata or {})}
        new_ended_at = current_ended_at
        if new_status in _TERMINAL_STATUSES and current_ended_at is None:
            new_ended_at = _now_iso()

        self._conn.execute(
            "UPDATE episodes SET status = ?, metadata = ?, ended_at = ? WHERE id = ?",
            (new_status, json.dumps(new_metadata), new_ended_at, episode_id),
        )
        self._conn.commit()

        log.info(
            "project_registry.update_episode",
            episode_id=episode_id,
            status=new_status,
        )

        return EpisodeRecord(
            id=row["id"],
            project_id=row["project_id"],
            agent_id=row["agent_id"],
            started_at=row["started_at"],
            ended_at=new_ended_at,
            status=EpisodeStatus(new_status),
            metadata=new_metadata,
        )

    def get_episodes_for_project(self, project_id: str) -> list[EpisodeRecord]:
        """Return all episodes for a given project, ordered by start time."""
        rows = self._conn.execute(
            "SELECT id, project_id, agent_id, started_at, ended_at, status, metadata "
            "FROM episodes WHERE project_id = ? ORDER BY started_at",
            (project_id,),
        ).fetchall()
        return [
            EpisodeRecord(
                id=r["id"],
                project_id=r["project_id"],
                agent_id=r["agent_id"],
                started_at=r["started_at"],
                ended_at=r["ended_at"],
                status=EpisodeStatus(r["status"]),
                metadata=json.loads(r["metadata"]),
            )
            for r in rows
        ]
