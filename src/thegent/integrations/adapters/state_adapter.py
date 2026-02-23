"""State management adapter for workstream autosync.

Handles local state persistence, checkpoints, and trends.
"""

import orjson as json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class StateAdapter:
    """Adapter for state management operations."""
    
    def __init__(self, config: Any):
        self.config = config
        self._status_path = config.status_file_path or Path("docs/reference/autosync_status.json")
        self._trend_path = config.trend_path or Path("docs/reference/workstream_autosync_trend.jsonl")
    
    def get_latest_snapshot_age_seconds(self) -> int | None:
        """Get age of latest snapshot in seconds."""
        snapshot_candidates = sorted(self._status_path.parent.glob("autosync_snapshot_*.json"))
        if not snapshot_candidates:
            return None
        try:
            latest = max(snapshot_candidates, key=lambda p: p.stat().st_mtime)
            age = datetime.now(timezone.utc) - datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
            return max(0, int(age.total_seconds()))
        except OSError:
            return None
    
    def get_checkpoint_path(self, checkpoint_id: str) -> Path:
        """Get path for checkpoint file."""
        return self._status_path.parent / f"autosync_checkpoint_{checkpoint_id}.json"
    
    def get_snapshot_path(self) -> Path:
        """Get path for snapshot file."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return self._status_path.parent / f"autosync_snapshot_{timestamp}.json"
    
    def append_trend_sample(self, sample: dict[str, Any]) -> None:
        """Append trend sample to file."""
        try:
            self._trend_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._trend_path, "a") as f:
                f.write(json.dumps(sample).decode().decode() + "\n")
        except Exception:
            pass
    
    def read_last_manifest_hash(self) -> str:
        """Read last manifest hash from status."""
        try:
            if self._status_path.exists():
                data = json.loads(self._status_path.read_text())
                return data.get("last_manifest_hash", "")
        except Exception:
            pass
        return ""
    
    def write_status(self, status: dict[str, Any]) -> None:
        """Write status to file."""
        try:
            self._status_path.parent.mkdir(parents=True, exist_ok=True)
            self._status_path.write_text(json.dumps(status, indent=2).decode().decode())
        except Exception:
            pass


__all__ = ["StateAdapter"]
