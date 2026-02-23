"""Workstream cycle orchestration.

Extracts cycle logic from workstream_autosync.py to reach target LOC.
"""

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from thegent.integrations.workstream_autosync_shared import (
    SyncCheckpoint,
    SyncDirection,
    SyncFailureQueue,
    SyncOperation,
    WorkstreamItem,
    WorkstreamParser,
)

logger = logging.getLogger(__name__)


class WorkstreamCycle:
    """Main cycle orchestration - extracted to reduce main file size."""
    
    def __init__(self, runner: Any):
        self.runner = runner  # Reference to main runner for access
    
    async def run_cycle(self) -> dict[str, Any]:
        """Execute one complete sync cycle."""
        result = {
            "started_at": datetime.now(timezone.utc),
            "items_synced": 0,
            "errors": [],
        }
        
        try:
            # Load workstream items
            items = await self._load_items()
            if not items:
                result["skipped"] = "no_items"
                return result
            
            # Determine sync direction
            direction = self._determine_direction(items)
            
            # Run sync based on direction
            if direction == SyncDirection.LOCAL_TO_REMOTE:
                await self._sync_to_remote(items)
            elif direction == SyncDirection.REMOTE_TO_LOCAL:
                await self._sync_from_remote(items)
            else:
                await self._sync_bidirectional(items)
            
            result["items_synced"] = len(items)
            
        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Cycle error: {e}")
        
        result["completed_at"] = datetime.now(timezone.utc)
        return result
    
    async def _load_items(self) -> list[WorkstreamItem]:
        """Load items from local workstream file."""
        workstream_path = self.runner.config.work_stream_path
        if not workstream_path or not workstream_path.exists():
            return []
        
        try:
            parser = WorkstreamParser()
            return parser.parse_file(workstream_path)
        except Exception as e:
            logger.error(f"Failed to load items: {e}")
            return []
    
    def _determine_direction(self, items: list[WorkstreamItem]) -> SyncDirection:
        """Determine sync direction based on config."""
        if self.runner.config.github_enabled and self.runner.config.linear_enabled:
            return SyncDirection.BIDIRECTIONAL
        elif self.runner.config.github_enabled:
            return SyncDirection.LOCAL_TO_REMOTE
        return SyncDirection.NONE
    
    async def _sync_to_remote(self, items: list[WorkstreamItem]) -> None:
        """Sync local items to remote."""
        if self.runner.config.github_enabled:
            await self.runner._sync_to_github(items)
        if self.runner.config.linear_enabled:
            await self.runner._sync_to_linear(items)
    
    async def _sync_from_remote(self, items: list[WorkstreamItem]) -> None:
        """Sync remote items to local."""
        workstream_path = self.runner.config.work_stream_path
        if self.runner.config.github_enabled:
            remote_items = await self.runner._sync_from_github(items, workstream_path)
            # Merge with local
        if self.runner.config.linear_enabled:
            remote_items = await self.runner._sync_from_linear(items, workstream_path)
    
    async def _sync_bidirectional(self, items: list[WorkstreamItem]) -> None:
        """Sync in both directions."""
        await self._sync_to_remote(items)
        await self._sync_from_remote(items)
    
    async def perform_sync_with_partitions(
        self,
        items: list[WorkstreamItem],
        partition_size: int = 50,
    ) -> dict[str, Any]:
        """Sync items in partitions for rate limiting."""
        results = {"success": 0, "failed": 0, "errors": []}
        
        for i in range(0, len(items), partition_size):
            partition = items[i:i + partition_size]
            try:
                await self._sync_partition(partition)
                results["success"] += len(partition)
            except Exception as e:
                results["failed"] += len(partition)
                results["errors"].append(str(e))
        
        return results
    
    async def _sync_partition(self, items: list[WorkstreamItem]) -> None:
        """Sync a single partition."""
        if self.runner.config.github_enabled:
            await self.runner._sync_to_github(items)
        if self.runner.config.linear_enabled:
            await self.runner._sync_to_linear(items)
    
    def checkpoint_start(self, connector: str, direction: str, partition_count: int) -> int:
        """Start checkpoint for partitioned sync."""
        self.runner._checkpoint = SyncCheckpoint(
            connector=connector,
            direction=direction,
            start_index=0,
            partition_size=partition_count,
            partition_count=partition_count,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        self.runner._write_checkpoint()
        return 0
    
    def checkpoint_advance(self, index: int) -> None:
        """Advance checkpoint to next partition."""
        if self.runner._checkpoint:
            self.runner._checkpoint.start_index = index
            self.runner._write_checkpoint()
    
    def checkpoint_complete(self) -> None:
        """Mark checkpoint as complete."""
        if self.runner._checkpoint:
            self.runner._checkpoint.completed_at = datetime.now(timezone.utc).isoformat()
            self.runner._write_checkpoint()
            self.runner._clear_checkpoint()


__all__ = ["WorkstreamCycle"]
