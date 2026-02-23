from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OrphanRecord:
    """Record of an orphaned remote item."""

    item_id: str
    source: str
    reason: str = ""


class RemoteOrphanDetector:
    """Detects remote items that lack local workstream representation.

    # @trace WL-248
    """

    def detect(
        self,
        remote_ids: set[str],
        local_ids: set[str],
        source: str = "remote",
    ) -> list[OrphanRecord]:
        """Detect remote items not present in local workstream.

        Args:
            remote_ids: Set of IDs from remote tracker
            local_ids: Set of IDs in local workstream
            source: Source label for the orphan records

        Returns:
            List of OrphanRecord objects for items in remote_ids not in local_ids
        """
        orphaned = remote_ids - local_ids
        return [OrphanRecord(item_id=item_id, source=source) for item_id in sorted(orphaned)]

    def filter_known(
        self,
        orphans: list[OrphanRecord],
        known_ids: set[str],
    ) -> list[OrphanRecord]:
        """Filter out orphans that are in the known IDs set.

        Args:
            orphans: List of OrphanRecord objects to filter
            known_ids: Set of IDs to exclude

        Returns:
            Filtered list containing only orphans not in known_ids
        """
        return [o for o in orphans if o.item_id not in known_ids]
