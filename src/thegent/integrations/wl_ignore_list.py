"""WL ignore list.

Maintains a set of workload IDs that should be skipped during sync operations.

# @trace WL-189
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class WLIgnoreList:
    """Manages a list of workload IDs to ignore during operations."""

    def __init__(self) -> None:
        """Initialize the ignore list."""
        self._ignored: set[str] = set()
        logger.debug("Initialized WLIgnoreList")

    def add(self, wl_id: str) -> None:
        """Add a workload ID to the ignore list.

        Args:
            wl_id: The workload ID to ignore.
        """
        self._ignored.add(wl_id)
        logger.debug(f"Added {wl_id} to ignore list (total: {len(self._ignored)})")

    def remove(self, wl_id: str) -> None:
        """Remove a workload ID from the ignore list.

        Args:
            wl_id: The workload ID to remove.
        """
        self._ignored.discard(wl_id)
        logger.debug(f"Removed {wl_id} from ignore list (total: {len(self._ignored)})")

    def is_ignored(self, wl_id: str) -> bool:
        """Check if a workload ID is in the ignore list.

        Args:
            wl_id: The workload ID to check.

        Returns:
            True if the ID is ignored, False otherwise.
        """
        return wl_id in self._ignored

    def all_ignored(self) -> list[str]:
        """Get all ignored workload IDs.

        Returns:
            Sorted list of all ignored workload IDs.
        """
        return sorted(self._ignored)

    def filter(self, wl_ids: list[str]) -> list[str]:
        """Filter out ignored IDs from a list.

        Args:
            wl_ids: List of workload IDs to filter.

        Returns:
            List containing only the non-ignored IDs from the input.
        """
        result = [wl_id for wl_id in wl_ids if wl_id not in self._ignored]
        logger.debug(f"Filtered {len(wl_ids)} IDs: {len(result)} remaining after removing {len(wl_ids) - len(result)} ignored")
        return result
