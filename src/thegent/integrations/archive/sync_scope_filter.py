"""Sync scope filters.

# @trace WL-168
"""

from __future__ import annotations


class SyncScopeFilter:
    """Filters sync scope based on include and exclude patterns."""

    def __init__(
        self,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> None:
        """Initialize the sync scope filter.

        Args:
            include_patterns: List of substring patterns to include. If None or empty,
                              all items are considered included by default.
            exclude_patterns: List of substring patterns to exclude. Empty by default.
        """
        self._include_patterns = include_patterns or []
        self._exclude_patterns = exclude_patterns or []

    def matches(self, item_id: str) -> bool:
        """Check if an item matches the filter criteria.

        An item matches if:
        1. It matches any include pattern (or all if no includes specified), AND
        2. It does not match any exclude pattern.

        Uses simple substring matching (not regex).

        Args:
            item_id: The item identifier to check.

        Returns:
            True if the item matches the filter, False otherwise.
        """
        # If include patterns are specified, item must match at least one
        if self._include_patterns:
            included = any(pattern in item_id for pattern in self._include_patterns)
            if not included:
                return False

        # Item must not match any exclude pattern
        excluded = any(pattern in item_id for pattern in self._exclude_patterns)
        if excluded:
            return False

        return True

    def filter(self, items: list[str]) -> list[str]:
        """Filter a list of items based on the scope criteria.

        Args:
            items: List of item IDs to filter.

        Returns:
            Sublist of items that match the filter.
        """
        return [item for item in items if self.matches(item)]
