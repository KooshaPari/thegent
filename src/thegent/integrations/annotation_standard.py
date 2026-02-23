"""Remote→Local Annotation Standard for cross-system annotation management.

WL-238: Remote→Local Annotation Standard
Provides a standard interface for storing, retrieving, and merging annotations
from remote sources into local annotation entries.

# @trace WL-238
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AnnotationEntry:
    """A single annotation entry with remote source and local annotations.

    Attributes:
        item_id: Unique identifier for the annotated item.
        source: Source system or service providing the annotations.
        annotations: Dictionary of annotation key-value pairs.
    """

    item_id: str
    source: str
    annotations: dict[str, str] = field(default_factory=dict)


class RemoteToLocalAnnotationStandard:
    """Manages annotations synced from remote sources to local storage."""

    def __init__(self) -> None:
        """Initialize an empty annotation store."""
        self._entries: dict[str, AnnotationEntry] = {}

    def annotate(self, item_id: str, source: str, annotations: dict[str, str]) -> AnnotationEntry:
        """Create or replace annotations for an item.

        Args:
            item_id: Unique identifier for the item.
            source: Source system providing the annotations.
            annotations: Dictionary of key-value annotation pairs.

        Returns:
            The created or updated AnnotationEntry.
        """
        entry = AnnotationEntry(item_id=item_id, source=source, annotations=annotations.copy())
        self._entries[item_id] = entry
        return entry

    def get(self, item_id: str) -> AnnotationEntry:
        """Retrieve annotations for an item by ID.

        Args:
            item_id: Unique identifier for the item.

        Returns:
            The AnnotationEntry for the item.

        Raises:
            KeyError: If no annotations exist for this item_id.
        """
        if item_id not in self._entries:
            raise KeyError(f"No annotations found for item_id: {item_id}")
        return self._entries[item_id]

    def get_annotation(self, item_id: str, key: str) -> str | None:
        """Get a single annotation value by item and key.

        Args:
            item_id: Unique identifier for the item.
            key: Annotation key to retrieve.

        Returns:
            The annotation value, or None if the key does not exist.
            Returns None if the item_id itself does not exist.
        """
        if item_id not in self._entries:
            return None
        return self._entries[item_id].annotations.get(key)

    def merge(self, item_id: str, new_annotations: dict[str, str]) -> AnnotationEntry:
        """Merge new annotations into existing annotations for an item.

        New keys are added; existing keys are overwritten by new values.

        Args:
            item_id: Unique identifier for the item.
            new_annotations: Dictionary of new/updated annotation pairs.

        Returns:
            The updated AnnotationEntry.

        Raises:
            KeyError: If no annotations exist for this item_id.
        """
        if item_id not in self._entries:
            raise KeyError(f"No annotations found for item_id: {item_id}")

        entry = self._entries[item_id]
        entry.annotations.update(new_annotations)
        return entry
