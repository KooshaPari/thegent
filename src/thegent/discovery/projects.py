"""WP-11001: Cross-project discovery and context management."""

import contextlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


class ProjectRegistry:
    """Manages a registry of local projects using thegent."""

    def __init__(self, global_config_dir: Path) -> None:
        self.registry_file = global_config_dir / "project_registry.jsonl"
        self.global_config_dir = global_config_dir
        self.global_config_dir.mkdir(parents=True, exist_ok=True)

    def register_project(self, path: Path, name: str = "") -> None:
        """Register a project path."""
        path = path.resolve()
        entry = {"path": str(path), "name": name or path.name, "last_active": datetime.now(UTC).isoformat()}

        # Read existing to avoid duplicates
        projects = self.list_projects()
        if any(p["path"] == str(path) for p in projects):
            self.update_activity(path)
            return

        with self.registry_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def list_projects(self) -> list[dict[str, Any]]:
        """List all registered projects."""
        if not self.registry_file.exists():
            return []

        projects = []
        with self.registry_file.open("r", encoding="utf-8") as f:
            for line in f:
                self._parse_project_line(projects, line)
        return projects

    def _parse_project_line(self, projects: list[dict[str, Any]], line: str) -> None:
        """Parse a project registry line safely."""
        with contextlib.suppress(Exception):
            projects.append(json.loads(line))

    def update_activity(self, path: Path) -> None:
        """Update last active timestamp for a project."""
        path_str = str(path.resolve())
        projects = self.list_projects()
        updated = False
        for p in projects:
            if p["path"] == path_str:
                p["last_active"] = datetime.now(UTC).isoformat()
                updated = True

        if updated:
            with self.registry_file.open("w", encoding="utf-8") as f:
                for p in projects:
                    f.write(json.dumps(p) + "\n")


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
