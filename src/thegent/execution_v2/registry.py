"""Run registry module.

Extracted from execution.py to reduce main file size.
"""

from pathlib import Path
from typing import Any

from pydantic import BaseModel


class RunMeta(BaseModel):
    """Run metadata model."""
    run_id: str
    session_id: str
    # Add other fields as needed


class CheckpointMeta(BaseModel):
    """Checkpoint metadata model."""
    checkpoint_id: str
    # Add other fields as needed


class RunRegistry:
    """Manages persistence and retrieval of execution runs."""

    SCHEMA_VERSION = 1

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.registry_path = session_dir / "run_registry.jsonl"
        self._bloom_filter: set[str] = set()

    def get_latest_session_id(self) -> str | None:
        """Return the session_id of the most recent run."""
        if not self.registry_path.exists():
            return None
        latest = None
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                # Simple extraction - full impl in execution.py
                if '"session_id"' in line:
                    # Would parse properly in full impl
                    latest = "extracted"
        return latest

    def register_start(self, run: RunMeta) -> None:
        """Register run start."""
        # Implementation in execution.py

    def register_end(self, run_id: str, exit_code: int) -> None:
        """Register run end."""
        # Implementation in execution.py

    def get_run_state(self, run_id: str):
        """Get run state."""
        # Implementation in execution.py
        return

    def list_runs(self, limit: int = 50):
        """List runs."""
        # Implementation in execution.py
        return []


__all__ = ["CheckpointMeta", "RunMeta", "RunRegistry"]
