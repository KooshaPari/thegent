"""Hourly Change Digest for change tracking and reporting.

# @trace WL-237
Provides hourly aggregation and digestion of changes across local and remote systems,
enabling compact hourly change summaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ChangeEntry:
    """A change entry with type, item ID, and hourly timestamp."""

    item_id: str
    change_type: str
    hour: str


class HourlyChangeDigest:
    """Aggregates and summarizes changes by hour."""

    def __init__(self) -> None:
        """Initialize the hourly change digest."""
        self._by_hour: dict[str, list[ChangeEntry]] = {}

    def record(self, item_id: str, change_type: str) -> ChangeEntry:
        """Record a change with current timestamp.

        Derives the hour from the current UTC time as "YYYY-MM-DDTHH".

        Args:
            item_id: The item ID that changed.
            change_type: Type of change (e.g., 'created', 'updated', 'deleted').

        Returns:
            The created ChangeEntry.
        """
        now = datetime.now(timezone.utc)
        hour = now.strftime("%Y-%m-%dT%H")
        entry = ChangeEntry(item_id=item_id, change_type=change_type, hour=hour)
        if hour not in self._by_hour:
            self._by_hour[hour] = []
        self._by_hour[hour].append(entry)
        return entry

    def get_hour(self, hour: str) -> list[ChangeEntry]:
        """Get all changes for a specific hour.

        Args:
            hour: Hour in format "YYYY-MM-DDTHH".

        Returns:
            List of ChangeEntries for that hour, or empty list if no entries.
        """
        return self._by_hour.get(hour, [])

    def digest(self, hour: str) -> dict[str, int]:
        """Get a summary digest of changes by type for a specific hour.

        Args:
            hour: Hour in format "YYYY-MM-DDTHH".

        Returns:
            Dictionary mapping change_type to count of changes of that type.
        """
        entries = self.get_hour(hour)
        digest: dict[str, int] = {}
        for entry in entries:
            if entry.change_type not in digest:
                digest[entry.change_type] = 0
            digest[entry.change_type] += 1
        return digest
