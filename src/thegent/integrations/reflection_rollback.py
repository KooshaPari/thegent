"""Reflection rollback command.

# @trace WL-185
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class RollbackEntry:
    """Represents a single rollback entry snapshot."""

    entry_id: str
    timestamp: datetime
    snapshot: dict[str, Any]


class ReflectionRollbackStore:
    """Store for managing rollback entries."""

    def __init__(self) -> None:
        """Initialize the rollback store."""
        self._entries: dict[str, RollbackEntry] = {}

    def record(self, entry_id: str, snapshot: dict[str, Any]) -> RollbackEntry:
        """Record a new rollback entry.

        Args:
            entry_id: Unique identifier for this rollback entry.
            snapshot: Dictionary containing the snapshot data.

        Returns:
            The created RollbackEntry.
        """
        entry = RollbackEntry(
            entry_id=entry_id,
            timestamp=datetime.now(timezone.utc),
            snapshot=snapshot.copy(),
        )
        self._entries[entry_id] = entry
        return entry

    def rollback_to(self, entry_id: str) -> dict[str, Any]:
        """Rollback to a previously recorded entry.

        Args:
            entry_id: Unique identifier of the entry to rollback to.

        Returns:
            The snapshot dictionary from that entry.

        Raises:
            KeyError: If the entry_id does not exist.
        """
        entry = self._entries[entry_id]
        return entry.snapshot.copy()

    def list_entries(self) -> list[RollbackEntry]:
        """Get all recorded rollback entries.

        Returns:
            List of RollbackEntry records in insertion order.
        """
        return list(self._entries.values())
