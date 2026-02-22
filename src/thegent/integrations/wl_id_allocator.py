"""Work-stream ID (WL-*) reservation and allocation tracking.

Manages reservations of WL ID ranges to prevent collisions and track allocations
across the system.

FR traceability: WL-307 (WL ID Reservation Allocator)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WLRange:
    """Represents a reserved range of WL IDs.

    Attributes:
        start: Starting WL ID (inclusive).
        end: Ending WL ID (inclusive).
        label: Human-readable label for the range.
        reserved_by: Name/identifier of the entity reserving the range.
    """

    start: int
    end: int
    label: str
    reserved_by: str


class WLIdAllocator:
    """Manages WL ID ranges and allocations."""

    def __init__(self) -> None:
        """Initialize the allocator with empty ranges."""
        self._ranges: list[WLRange] = []

    def reserve_range(self, start: int, end: int, label: str, reserved_by: str) -> WLRange:
        """Reserve a range of WL IDs.

        Args:
            start: Starting WL ID (inclusive).
            end: Ending WL ID (inclusive).
            label: Human-readable label for the range.
            reserved_by: Name/identifier of the entity making the reservation.

        Returns:
            The WLRange object that was created.

        Raises:
            ValueError: If the range overlaps any existing reservation.
        """
        if start > end:
            raise ValueError(f"start ({start}) must be <= end ({end})")

        if self.check_overlap(start, end):
            raise ValueError(
                f"Range [{start}, {end}] overlaps with existing reservations"
            )

        wl_range = WLRange(start=start, end=end, label=label, reserved_by=reserved_by)
        self._ranges.append(wl_range)
        logger.debug(
            f"Reserved WL range [{start}, {end}] labeled '{label}' "
            f"by {reserved_by}"
        )
        return wl_range

    def next_available(self, after: int = 0) -> int:
        """Find the next available (unreserved) WL ID.

        Args:
            after: Start search after this ID (default: 0).

        Returns:
            The lowest unreserved WL ID greater than after.
        """
        candidate = after + 1

        # Check for collisions with any reserved range
        while True:
            if not any(r.start <= candidate <= r.end for r in self._ranges):
                return candidate
            candidate += 1

    def is_reserved(self, wl_id: int) -> bool:
        """Check if a WL ID is within any reserved range.

        Args:
            wl_id: The WL ID to check.

        Returns:
            True if the ID is reserved, False otherwise.
        """
        return any(r.start <= wl_id <= r.end for r in self._ranges)

    def list_ranges(self) -> list[WLRange]:
        """Get all reserved ranges, sorted by start ID.

        Returns:
            Sorted list of WLRange objects.
        """
        return sorted(self._ranges, key=lambda r: r.start)

    def check_overlap(self, start: int, end: int) -> bool:
        """Check if a range overlaps with any existing reservation.

        Args:
            start: Starting ID (inclusive).
            end: Ending ID (inclusive).

        Returns:
            True if the range overlaps any existing reservation, False otherwise.
        """
        # Ranges overlap if: new_start <= existing_end AND new_end >= existing_start
        return any(start <= r.end and end >= r.start for r in self._ranges)
