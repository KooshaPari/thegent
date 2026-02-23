"""Ownership metadata propagation for multi-system sync.

Propagate per-item ownership metadata across local, GitHub, and Linear.

# @trace WL-245
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OwnershipRecord:
    """Record representing ownership metadata for an item."""

    item_id: str
    owner: str
    team: str = ""


class OwnershipMetadataPropagator:
    """Manages ownership metadata propagation across systems."""

    def __init__(self) -> None:
        """Initialize the ownership metadata propagator."""
        self._ownership: dict[str, OwnershipRecord] = {}
        logger.debug("Initialized ownership metadata propagator")

    def assign(self, item_id: str, owner: str, team: str = "") -> OwnershipRecord:
        """Assign ownership metadata to an item.

        Args:
            item_id: Identifier for the item.
            owner: The owner's identifier or name.
            team: Optional team identifier.

        Returns:
            The created OwnershipRecord.
        """
        record = OwnershipRecord(item_id=item_id, owner=owner, team=team)
        self._ownership[item_id] = record
        logger.debug(f"Assigned ownership: {item_id} -> {owner} (team={team})")
        return record

    def propagate(self, source_id: str, target_ids: list[str]) -> list[OwnershipRecord]:
        """Propagate ownership from a source item to target items.

        Args:
            source_id: The source item to copy ownership from.
            target_ids: List of target item IDs to propagate ownership to.

        Returns:
            List of OwnershipRecord objects created for the targets.

        Raises:
            KeyError: If the source item has no ownership record.
        """
        if source_id not in self._ownership:
            raise KeyError(f"No ownership record found for {source_id}")

        source = self._ownership[source_id]
        propagated: list[OwnershipRecord] = []

        for target_id in target_ids:
            record = self.assign(target_id, source.owner, source.team)
            propagated.append(record)
            logger.debug(f"Propagated ownership from {source_id} to {target_id}")

        return propagated

    def get(self, item_id: str) -> OwnershipRecord:
        """Get the ownership record for an item.

        Args:
            item_id: The item identifier.

        Returns:
            The OwnershipRecord.

        Raises:
            KeyError: If no record exists for the item.
        """
        if item_id not in self._ownership:
            raise KeyError(f"No ownership record found for {item_id}")
        return self._ownership[item_id]

    def by_owner(self, owner: str) -> list[OwnershipRecord]:
        """Get all ownership records for a specific owner.

        Args:
            owner: The owner identifier to filter by.

        Returns:
            List of OwnershipRecord objects owned by the specified owner.
        """
        owned = [r for r in self._ownership.values() if r.owner == owner]
        logger.debug(f"Found {len(owned)} items owned by {owner}")
        return owned
