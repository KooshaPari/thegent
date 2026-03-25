"""WP-22003: Global Agent State Sync (SyncLoop).
Federated agent state synchronization across multiple registered projects.
Ensures context continuity in cross-project multi-agent teams.
"""

import orjson as json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from thegent.discovery.projects import ProjectRegistry

_log = logging.getLogger(__name__)


class SyncPayload(BaseModel):
    timestamp: str
    active_teams: list[dict[str, Any]]
    recent_handoffs: list[dict[str, Any]]


class SyncLoop:
    """Manages periodic state synchronization across project boundaries."""

    def __init__(self, registry: ProjectRegistry, sync_dir: Path) -> None:
        self.registry = registry
        self.sync_dir = sync_dir
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        self.last_sync_ts = self._load_last_sync()

    def _load_last_sync(self) -> float:
        """Load the timestamp of the last successful synchronization."""
        ts_file = self.sync_dir / "last_sync_ts"
        if ts_file.exists():
            try:
                return float(ts_file.read_text().strip())
            except Exception:
                return 0.0
        return 0.0

    def _save_last_sync(self):
        """Save the current timestamp as the last successful synchronization."""
        ts_file = self.sync_dir / "last_sync_ts"
        ts_file.write_text(str(datetime.now(UTC).timestamp()))

    async def sync_all(self, local_project_id: str):
        """Perform a full synchronization cycle across all registered projects."""
        projects = self.registry.list_projects()
        local_project = next((p for p in projects if p["id"] == local_project_id), None)

        if not local_project:
            _log.error("Local project %s not found in registry", local_project_id)
            return

        _log.info("Starting global state sync for project: %s", local_project_id)

        # 1. Collect local state (e.g. recent runs, team tasks, handoffs)
        local_state = self._collect_local_state(Path(local_project["path"]))

        # 2. Push/Pull to/from peers
        for peer in projects:
            if peer["id"] == local_project_id:
                continue

            _log.info("Syncing state with peer: %s", peer["id"])
            peer_path = Path(peer["path"])
            self._push_state_to_peer(peer_path, local_project_id, local_state)

        self._save_last_sync()
        _log.info("Global state sync complete.")

    def _collect_local_state(self, project_path: Path) -> dict[str, Any]:
        """Collect the state that needs to be synchronized from the local project."""
        teams = self._load_active_teams(project_path)
        handoffs = self._load_recent_handoffs(project_path)
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "active_teams": teams,
            "recent_handoffs": handoffs,
        }

    def _push_state_to_peer(self, peer_path: Path, source_id: str, state: dict[str, Any]):
        """Push local state to a peer project's sync inbox."""
        payload = self._validate_payload(state)
        peer_sync_inbox = peer_path / ".thegent" / "sync_inbox"
        peer_sync_inbox.mkdir(parents=True, exist_ok=True)

        sync_file = peer_sync_inbox / f"{source_id}_state.json"
        try:
            sync_file.write_bytes(json.dumps(payload, option=json.OPT_INDENT_2))
        except Exception as e:
            _log.error("Failed to push state to peer %s: %s", source_id, e)

    def _validate_payload(self, state: dict[str, Any]) -> dict[str, Any]:
        try:
            return SyncPayload.model_validate(state).model_dump()
        except ValidationError as exc:
            raise ValueError(f"Invalid sync payload: {exc}") from exc

    def _load_active_teams(self, project_path: Path) -> list[dict[str, Any]]:
        candidates = [
            project_path / ".thegent" / "team_registry.json",
            project_path / "team_registry.json",
        ]
        for path in candidates:
            if not path.exists():
                continue
            data = self._read_json_file(path)
            teams = data.get("teams", data) if isinstance(data, dict) else data
            if not isinstance(teams, list):
                raise ValueError(f"Malformed team registry at {path}: expected list")
            active: list[dict[str, Any]] = []
            for entry in teams:
                if not isinstance(entry, dict):
                    continue
                if entry.get("active", True):
                    active.append(entry)
            return active
        return []

    def _load_recent_handoffs(self, project_path: Path, limit: int = 25) -> list[dict[str, Any]]:
        candidates = [
            project_path / ".thegent" / "handoff_registry.jsonl",
            project_path / "handoff_registry.jsonl",
        ]
        for path in candidates:
            if not path.exists():
                continue
            records: list[dict[str, Any]] = []
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    payload = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Malformed handoff registry line {line_no} in {path}") from exc
                if isinstance(payload, dict):
                    records.append(payload)
            return records[-limit:]
        return []

    def _read_json_file(self, path: Path) -> Any:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON in {path}") from exc
