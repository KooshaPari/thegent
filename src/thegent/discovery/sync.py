"""WP-22003: Global Agent State Sync (SyncLoop).
Federated agent state synchronization across multiple registered projects.
Ensures context continuity in cross-project multi-agent teams.
"""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from thegent.discovery.projects import ProjectRegistry

_log = logging.getLogger(__name__)


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
        # Simple local state collection (mocking file reads)
        state = {"timestamp": datetime.now(UTC).isoformat(), "active_teams": [], "recent_handoffs": []}

        # In a real system, this would read from team_registry.json, handoff_registry.jsonl, etc.
        return state

    def _push_state_to_peer(self, peer_path: Path, source_id: str, state: dict[str, Any]):
        """Push local state to a peer project's sync inbox."""
        peer_sync_inbox = peer_path / ".thegent" / "sync_inbox"
        peer_sync_inbox.mkdir(parents=True, exist_ok=True)

        sync_file = peer_sync_inbox / f"{source_id}_state.json"
        try:
            sync_file.write_text(json.dumps(state, indent=2))
        except Exception as e:
            _log.error("Failed to push state to peer %s: %s", source_id, e)
