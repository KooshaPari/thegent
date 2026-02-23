"""Workstream Sorting and Normalization utilities.

WL-225: WL Sort/Normalize Command
Provides sorting, normalization, and deduplication for workstream records.

# @trace WL-225
"""

from __future__ import annotations

from typing import Any


class WLSortNormalizer:
    """Sorts, normalizes, and deduplicates workstream records."""

    def sort(self, items: list[dict[str, Any]], key: str = "id") -> list[dict[str, Any]]:
        """Sort a list of items by a specified key.

        Args:
            items: List of dictionary items to sort.
            key: The dictionary key to sort by. Defaults to "id".

        Returns:
            A new sorted list without modifying the original.
        """
        return sorted(items, key=lambda item: item.get(key, ""))

    def normalize_ids(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize "id" fields to uppercase string format like "WL-123".

        Args:
            items: List of items to normalize.

        Returns:
            A new list with normalized IDs.
        """
        result = []
        for item in items:
            normalized_item = dict(item)
            if "id" in normalized_item:
                id_value = normalized_item["id"]
                if isinstance(id_value, str):
                    normalized_item["id"] = id_value.upper()
                else:
                    normalized_item["id"] = str(id_value).upper()
            result.append(normalized_item)
        return result

    def deduplicate(self, items: list[dict[str, Any]], key: str = "id") -> list[dict[str, Any]]:
        """Remove duplicate items, keeping the first occurrence.

        Args:
            items: List of items to deduplicate.
            key: The dictionary key to check for duplicates. Defaults to "id".

        Returns:
            A new list with duplicates removed.
        """
        seen: set[Any] = set()
        result = []

        for item in items:
            key_value = item.get(key)
            if key_value not in seen:
                seen.add(key_value)
                result.append(item)

        return result
