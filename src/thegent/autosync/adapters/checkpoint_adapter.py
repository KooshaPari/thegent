"""Checkpoint and failure queue adapter for workstream autosync.

Handles checkpoint persistence and failure queue management.
"""

import json
from pathlib import Path
from typing import Any

from thegent.integrations.workstream_autosync_shared import SyncCheckpoint, SyncFailureQueue


class CheckpointAdapter:
    """Adapter for checkpoint and failure queue operations."""
    
    def __init__(self, config: Any, failure_queue: SyncFailureQueue):
        self.config = config
        self._failure_queue = failure_queue
    
    def get_failure_queue_path(self) -> Path:
        return self.config.failure_queue_path or Path("docs/reference/workstream_autosync_failures.json")
    
    def get_checkpoint_path(self) -> Path:
        return self.config.checkpoint_file_path or Path("docs/reference/workstream_autosync_checkpoint.json")
    
    def load_checkpoint(self) -> SyncCheckpoint | None:
        """Load checkpoint from disk."""
        path = self.get_checkpoint_path()
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            return SyncCheckpoint.from_dict(data)
        except Exception:
            return None
    
    def save_checkpoint(self, checkpoint: SyncCheckpoint) -> None:
        """Save checkpoint to disk."""
        path = self.get_checkpoint_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(checkpoint.to_dict()))
    
    def clear_checkpoint(self) -> None:
        """Clear checkpoint file."""
        path = self.get_checkpoint_path()
        if path.exists():
            path.unlink()
    
    def load_failure_queue(self) -> None:
        """Load failure queue from disk."""
        path = self.get_failure_queue_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self._failure_queue.from_dict(data)
            except Exception:
                pass
    
    def save_failure_queue(self) -> None:
        """Save failure queue to disk."""
        path = self.get_failure_queue_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._failure_queue.to_dict()))


__all__ = ["CheckpointAdapter"]
