"""WP-11001: Cross-project discovery and context management."""

import contextlib
import sqlite3
import json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


class ProjectRegistry:
    """Manages a registry of local projects using thegent."""

    def __init__(self, global_config_dir: Path) -> None:
        self.global_config_dir = global_config_dir
        self.global_config_dir.mkdir(parents=True, exist_ok=True)
        self.registry_file = global_config_dir / "project_registry.jsonl"
        self.registry_db = global_config_dir / "registry.db"
        self.global_config_dir = global_config_dir
        self._conn = sqlite3.connect(str(self.registry_db))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()
        self._migrate_from_jsonl()
        self._conn.commit()

    def _init_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                path TEXT NOT NULL UNIQUE,
                last_active TEXT NOT NULL
            )
            """
        )

    def _migrate_from_jsonl(self) -> None:
        if not self.registry_file.exists():
            return

        cur = self._conn.execute("SELECT COUNT(1) AS n FROM projects")
        row_count = int(cur.fetchone()["n"])
        cur.close()
        if row_count > 0:
            return

        with self.registry_file.open("r", encoding="utf-8") as f:
            for line in f:
                payload = self._safe_load_jsonl(line)
                if not payload:
                    continue

                project_id = payload.get("id") or self._new_project_id()
                path = str(Path(payload.get("path", "")).resolve())
                name = payload.get("name", Path(path).name)
                last_active = payload.get("last_active") or datetime.now(UTC).isoformat()

                if not path:
                    continue
                self._upsert_project(project_id, name, path, last_active)

    def _new_project_id(self) -> str:
        return uuid.uuid4().hex[:12]

    def _upsert_project(self, project_id: str, name: str, path: str, last_active: str) -> None:
        with contextlib.suppress(sqlite3.IntegrityError):
            self._conn.execute(
                "INSERT INTO projects (id, name, path, last_active) VALUES (?, ?, ?, ?)",
                (project_id, name, path, last_active),
            )

    def register_project(self, path: Path, name: str = "") -> None:
        """Register a project path."""
        path = path.resolve()
        projects = self.list_projects()
        if any(p["path"] == str(path) for p in projects):
            self.update_activity(path)
            return

        project_id = self._new_project_id()
        now = datetime.now(UTC).isoformat()
        self._conn.execute(
            "INSERT INTO projects (id, name, path, last_active) VALUES (?, ?, ?, ?)",
            (project_id, name or path.name, str(path), now),
        )
        self._conn.commit()

    def list_projects(self) -> list[dict[str, Any]]:
        """List all registered projects."""
        projects = [
            {"id": row["id"], "name": row["name"], "path": row["path"], "last_active": row["last_active"]}
            for row in self._conn.execute(
                "SELECT id, name, path, last_active FROM projects ORDER BY last_active DESC"
            ).fetchall()
        ]
        return projects

    def _parse_project_line(self, projects: list[dict[str, Any]], line: str) -> None:
        """Parse a project registry line safely."""
        with contextlib.suppress(Exception):
            payload = json.loads(line)
            if isinstance(payload, dict):
                projects.append(payload)

    def update_activity(self, path: Path) -> None:
        """Update last active timestamp for a project."""
        path_str = str(path.resolve())
        now = datetime.now(UTC).isoformat()
        self._conn.execute(
            "UPDATE projects SET last_active = ? WHERE path = ?",
            (now, path_str),
        )
        self._conn.commit()

    def _safe_load_jsonl(self, line: str) -> dict[str, Any] | None:
        with contextlib.suppress(Exception):
            payload = json.loads(line)
            if isinstance(payload, dict):
                return payload
        return None


class ContextBridger:
    """WP-11002: Bridges context (files, state) across projects."""

    def __init__(self, registry: ProjectRegistry) -> None:
        self.registry = registry

    def get_peer_context(self, project_name: str, file_pattern: str) -> list[Path]:
        """Find files in a peer project matching a pattern."""
        projects = self.registry.list_projects()
        peer = next((p for p in projects if p["name"] == project_name), None)
        if not peer:
            _log.warning(f"Peer project '{project_name}' not found in registry.")
            return []

        peer_path = Path(peer["path"])
        return list(peer_path.glob(file_pattern))
