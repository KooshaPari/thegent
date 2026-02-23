"""Orphan detection for workstream autosync.

Extracts orphan detection logic.
"""

from typing import Any

from thegent.integrations.workstream_autosync_shared import WorkstreamItem


class OrphanDetector:
    """Detects orphan items in workstream."""
    
    def __init__(self, config: Any):
        self.config = config
    
    def compute_local_orphan_report(
        self,
        items: list[WorkstreamItem],
        remote_ids: list[str],
    ) -> dict[str, Any]:
        """Compute which local items don't exist remotely."""
        local_ids = {item.item_id for item in items}
        remote_id_set = set(remote_ids)
        
        local_orphans = local_ids - remote_id_set
        mapped_remote = local_ids & remote_id_set
        
        return {
            "local_ids": sorted(local_ids),
            "mapped_remote_ids": sorted(mapped_remote),
            "local_orphan_ids": sorted(local_orphans),
            "orphan_count": len(local_orphans),
        }
    
    def filter_orphans(
        self,
        items: list[WorkstreamItem],
        remote_ids: list[str],
    ) -> list[WorkstreamItem]:
        """Filter out orphan items from sync."""
        remote_id_set = set(remote_ids)
        return [item for item in items if item.item_id in remote_id_set]


__all__ = ["OrphanDetector"]
