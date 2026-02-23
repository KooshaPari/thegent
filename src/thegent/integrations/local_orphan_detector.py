from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LocalOrphanRecord:
    """Record of an orphaned local item."""

    item_id: str
    reason: str = ""


class LocalOrphanDetector:
    """Detects local workstream items lacking remote tracker representation.

    # @trace WL-249
    """

    def detect(
        self,
        local_ids: set[str],
        remote_ids: set[str],
    ) -> list[LocalOrphanRecord]:
        """Detect local items not present in remote tracker.

        Args:
            local_ids: Set of IDs in local workstream
            remote_ids: Set of IDs from remote tracker

        Returns:
            List of LocalOrphanRecord objects for items in local_ids not in remote_ids
        """
        orphaned = local_ids - remote_ids
        return [LocalOrphanRecord(item_id=item_id) for item_id in sorted(orphaned)]

    def filter_known(
        self,
        orphans: list[LocalOrphanRecord],
        known_ids: set[str],
    ) -> list[LocalOrphanRecord]:
        """Filter out orphans that are in the known IDs set.

        Args:
            orphans: List of LocalOrphanRecord objects to filter
            known_ids: Set of IDs to exclude

        Returns:
            Filtered list containing only orphans not in known_ids
        """
        return [o for o in orphans if o.item_id not in known_ids]
