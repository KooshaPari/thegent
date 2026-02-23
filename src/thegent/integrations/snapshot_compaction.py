"""Snapshot Compaction (WL-253): Track and compact snapshot storage.

Manages snapshot registration, compaction tracking, and storage savings
calculation. Useful for monitoring and optimizing snapshot storage usage
across the system.

# @trace WL-253
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Snapshot Entry
# ---------------------------------------------------------------------------


@dataclass
class SnapshotEntry:
    """A snapshot and its compaction status.

    Attributes:
        snapshot_id: Unique identifier for the snapshot.
        size_bytes: Size of the snapshot in bytes (original or compacted).
        compacted: Whether the snapshot has been compacted.
    """

    snapshot_id: str
    """Unique snapshot identifier."""

    size_bytes: int
    """Size in bytes (original or compacted)."""

    compacted: bool = False
    """Whether the snapshot has been compacted."""

    _original_size_bytes: int = 0
    """Original size before compaction (for calculating savings)."""

    def __post_init__(self) -> None:
        """Validate snapshot entry."""
        if not self.snapshot_id:
            raise ValueError("snapshot_id cannot be empty")
        if self.size_bytes < 0:
            raise ValueError(f"size_bytes must be >= 0, got {self.size_bytes}")
        # Track original size if not yet set
        if self._original_size_bytes == 0:
            self._original_size_bytes = self.size_bytes


# ---------------------------------------------------------------------------
# Snapshot Compactor
# ---------------------------------------------------------------------------


class SnapshotCompactor:
    """Manages snapshot registration and compaction tracking.

    Tracks snapshot sizes, compaction status, and calculates storage
    savings achieved through compaction.

    Example:
        >>> compactor = SnapshotCompactor()
        >>> compactor.register("snap-1", 1000)
        SnapshotEntry(snapshot_id="snap-1", size_bytes=1000, compacted=False)
        >>> compactor.compact("snap-1", 600)
        SnapshotEntry(snapshot_id="snap-1", size_bytes=600, compacted=True)
        >>> compactor.savings_bytes()
        400
    """

    def __init__(self) -> None:
        """Initialize the snapshot compactor."""
        self._snapshots: dict[str, SnapshotEntry] = {}
        logger.debug("SnapshotCompactor initialized")

    def register(self, snapshot_id: str, size_bytes: int) -> SnapshotEntry:
        """Register a snapshot.

        Creates a new entry or overwrites an existing one.

        Args:
            snapshot_id: Unique snapshot identifier.
            size_bytes: Initial size in bytes.

        Returns:
            The registered SnapshotEntry.

        Raises:
            ValueError: If snapshot_id or size_bytes is invalid.

        Example:
            >>> compactor = SnapshotCompactor()
            >>> entry = compactor.register("snap-1", 1000)
            >>> entry.snapshot_id
            "snap-1"
            >>> entry.compacted
            False
        """
        entry = SnapshotEntry(
            snapshot_id=snapshot_id,
            size_bytes=size_bytes,
            compacted=False,
        )
        self._snapshots[snapshot_id] = entry
        logger.debug(
            "Registered snapshot: snapshot_id=%r, size_bytes=%d",
            snapshot_id,
            size_bytes,
        )
        return entry

    def compact(self, snapshot_id: str, compacted_size: int) -> SnapshotEntry:
        """Mark a snapshot as compacted and update its size.

        Args:
            snapshot_id: The snapshot to compact.
            compacted_size: The new size after compaction (in bytes).

        Returns:
            The updated SnapshotEntry.

        Raises:
            KeyError: If snapshot_id is not registered.
            ValueError: If compacted_size is invalid.

        Example:
            >>> compactor = SnapshotCompactor()
            >>> compactor.register("snap-1", 1000)
            >>> entry = compactor.compact("snap-1", 600)
            >>> entry.compacted
            True
            >>> entry.size_bytes
            600
        """
        if snapshot_id not in self._snapshots:
            raise KeyError(f"Snapshot {snapshot_id!r} not registered")

        if compacted_size < 0:
            raise ValueError(f"compacted_size must be >= 0, got {compacted_size}")

        entry = self._snapshots[snapshot_id]
        original_size = entry._original_size_bytes
        entry.compacted = True
        entry.size_bytes = compacted_size

        savings = original_size - compacted_size
        logger.debug(
            "Compacted snapshot: snapshot_id=%r, original=%d, compacted=%d, savings=%d",
            snapshot_id,
            original_size,
            compacted_size,
            savings,
        )
        return entry

    def savings_bytes(self) -> int:
        """Calculate total storage savings from compaction.

        Returns the sum of (original_size - compacted_size) for all
        compacted snapshots.

        Returns:
            Total bytes saved across all compacted snapshots.

        Example:
            >>> compactor = SnapshotCompactor()
            >>> compactor.register("snap-1", 1000)
            >>> compactor.register("snap-2", 2000)
            >>> compactor.compact("snap-1", 600)
            >>> compactor.compact("snap-2", 1500)
            >>> compactor.savings_bytes()
            900
        """
        total_savings = 0
        for entry in self._snapshots.values():
            if entry.compacted:
                savings = entry._original_size_bytes - entry.size_bytes
                total_savings += max(savings, 0)
        return total_savings

    def uncompacted(self) -> list[SnapshotEntry]:
        """Get all snapshots that have not been compacted.

        Returns:
            List of uncompacted SnapshotEntry objects.

        Example:
            >>> compactor = SnapshotCompactor()
            >>> compactor.register("snap-1", 1000)
            >>> compactor.register("snap-2", 2000)
            >>> compactor.compact("snap-1", 600)
            >>> uncompacted = compactor.uncompacted()
            >>> len(uncompacted)
            1
            >>> uncompacted[0].snapshot_id
            "snap-2"
        """
        result = [e for e in self._snapshots.values() if not e.compacted]
        logger.debug("Fetched uncompacted snapshots: count=%d", len(result))
        return result
