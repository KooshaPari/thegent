"""Field mapping bootstrap wizard for first-time connector setup.

Provides interactive guidance for mapping source fields to target fields with
optional transform functions, enabling safe field projection during initial sync.

# @trace WL-265
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FieldMappingEntry:
    """Represents a single field mapping with optional transformation.

    Attributes:
        source_field: Name of the field in the source connector.
        target_field: Name of the field in the target connector.
        transform: Transformation function name; defaults to identity (no-op).
    """

    source_field: str
    target_field: str
    transform: str = "identity"


class FieldMappingWizard:
    """Interactive wizard for bootstrapping field mappings.

    Manages a collection of field mappings and provides methods to add, retrieve,
    and apply transformations to field values.
    """

    def __init__(self):
        """Initialize the field mapping wizard with an empty mapping registry."""
        self._mappings: dict[str, FieldMappingEntry] = {}

    def add(
        self, source_field: str, target_field: str, transform: str = "identity"
    ) -> FieldMappingEntry:
        """Add a new field mapping to the wizard.

        Args:
            source_field: Name of the source field.
            target_field: Name of the target field.
            transform: Optional transformation function name; defaults to "identity".

        Returns:
            The created FieldMappingEntry.
        """
        entry = FieldMappingEntry(
            source_field=source_field, target_field=target_field, transform=transform
        )
        self._mappings[source_field] = entry
        logger.debug(
            f"Added field mapping: {source_field} -> {target_field} (transform: {transform})"
        )
        return entry

    def get(self, source_field: str) -> FieldMappingEntry:
        """Retrieve a field mapping by source field name.

        Args:
            source_field: Name of the source field to look up.

        Returns:
            The FieldMappingEntry for the source field.

        Raises:
            KeyError: If the source field is not in the mapping registry.
        """
        if source_field not in self._mappings:
            raise KeyError(f"Field mapping for '{source_field}' not found")
        return self._mappings[source_field]

    def apply(self, source_field: str, value: str) -> str:
        """Apply the mapped transformation to a value.

        Currently implements the "identity" transform (returns value unchanged).
        Additional transforms can be added as needed.

        Args:
            source_field: Name of the source field.
            value: The value to transform.

        Returns:
            The transformed value.

        Raises:
            KeyError: If the source field is not in the mapping registry.
        """
        entry = self.get(source_field)  # Raises KeyError if not found

        # Apply the transformation based on the transform name
        if entry.transform == "identity":
            return value
        # Extensible: add more transforms as needed
        logger.warning(f"Unknown transform '{entry.transform}'; returning value unchanged")
        return value

    def all_mappings(self) -> list[FieldMappingEntry]:
        """Return all configured field mappings.

        Returns:
            A list of all FieldMappingEntry objects in the wizard.
        """
        return list(self._mappings.values())
