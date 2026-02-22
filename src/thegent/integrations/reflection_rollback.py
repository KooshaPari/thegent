"""Reflection rollback manager for work stream snapshot and restore.

# @trace WL-185
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class RollbackSnapshot:
    """Snapshot of work stream state for rollback.

    Attributes:
        snapshot_id: Unique snapshot identifier.
        timestamp: When the snapshot was created (ISO 8601 format).
        work_stream_content: Full content of WORK_STREAM.md file.
        cycle_id: Associated cycle identifier.
    """

    snapshot_id: str
    timestamp: str
    work_stream_content: str
    cycle_id: str
    _created_at: Optional[datetime] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Parse timestamp into datetime for convenience."""
        try:
            self._created_at = datetime.fromisoformat(self.timestamp)
        except ValueError:
            self._created_at = None


class ReflectionRollbackManager:
    """Manager for work stream snapshots and rollback operations."""

    SNAPSHOTS_DIR = Path("docs/reference/rollback_snapshots")

    def __init__(self, snapshots_dir: Optional[Path] = None) -> None:
        """Initialize the rollback manager.

        Args:
            snapshots_dir: Directory where snapshots are stored. Defaults to
                          docs/reference/rollback_snapshots.
        """
        self._snapshots_dir = snapshots_dir or self.SNAPSHOTS_DIR

    def take_snapshot(self, work_stream_path: Path) -> RollbackSnapshot:
        """Create a snapshot of the current work stream content.

        Args:
            work_stream_path: Path to WORK_STREAM.md file.

        Returns:
            RollbackSnapshot object with snapshot metadata.

        Raises:
            FileNotFoundError: If work_stream_path does not exist.
        """
        if not work_stream_path.exists():
            raise FileNotFoundError(f"Work stream file not found: {work_stream_path}")

        content = work_stream_path.read_text(encoding="utf-8")
        snapshot_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now(timezone.utc).isoformat()
        cycle_id = ""  # Empty for now; can be set by caller

        snapshot = RollbackSnapshot(
            snapshot_id=snapshot_id,
            timestamp=timestamp,
            work_stream_content=content,
            cycle_id=cycle_id,
        )

        # Persist snapshot (exclude _created_at from serialization)
        self._snapshots_dir.mkdir(parents=True, exist_ok=True)
        snapshot_file = self._snapshots_dir / f"{snapshot_id}.json"
        snapshot_dict = {
            "snapshot_id": snapshot.snapshot_id,
            "timestamp": snapshot.timestamp,
            "work_stream_content": snapshot.work_stream_content,
            "cycle_id": snapshot.cycle_id,
        }
        snapshot_file.write_text(json.dumps(snapshot_dict, indent=2), encoding="utf-8")

        return snapshot

    def list_snapshots(self) -> list[RollbackSnapshot]:
        """List all available snapshots, sorted by timestamp (newest first).

        Returns:
            List of RollbackSnapshot objects.
        """
        if not self._snapshots_dir.exists():
            return []

        snapshots: list[RollbackSnapshot] = []
        for snapshot_file in self._snapshots_dir.glob("*.json"):
            try:
                data = json.loads(snapshot_file.read_text(encoding="utf-8"))
                snapshot = RollbackSnapshot(
                    snapshot_id=data["snapshot_id"],
                    timestamp=data["timestamp"],
                    work_stream_content=data["work_stream_content"],
                    cycle_id=data.get("cycle_id", ""),
                )
                snapshots.append(snapshot)
            except (json.JSONDecodeError, KeyError):
                # Skip invalid snapshots
                continue

        # Sort by timestamp, newest first
        snapshots.sort(key=lambda s: s.timestamp, reverse=True)
        return snapshots

    def rollback_to(self, snapshot_id: str, work_stream_path: Path) -> None:
        """Restore work stream to a specific snapshot state.

        Args:
            snapshot_id: ID of the snapshot to restore.
            work_stream_path: Path where to restore the file.

        Raises:
            FileNotFoundError: If snapshot does not exist.
        """
        snapshot_file = self._snapshots_dir / f"{snapshot_id}.json"
        if not snapshot_file.exists():
            raise FileNotFoundError(f"Snapshot not found: {snapshot_id}")

        data = json.loads(snapshot_file.read_text(encoding="utf-8"))
        work_stream_path.write_text(data["work_stream_content"], encoding="utf-8")

    def cleanup_old_snapshots(self, keep_last_n: int = 5) -> None:
        """Delete old snapshots, keeping only the N most recent.

        Args:
            keep_last_n: Number of recent snapshots to keep (default: 5).
        """
        snapshots = self.list_snapshots()
        if len(snapshots) <= keep_last_n:
            return

        # Remove oldest snapshots
        for snapshot in snapshots[keep_last_n:]:
            snapshot_file = self._snapshots_dir / f"{snapshot.snapshot_id}.json"
            snapshot_file.unlink(missing_ok=True)
