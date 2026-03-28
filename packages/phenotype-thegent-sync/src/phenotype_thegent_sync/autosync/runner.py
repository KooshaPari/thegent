"""Main autosync runner - thin orchestration layer.

This is the main entry point. Delegates to specialized modules.
Target: Under 800 LOC.
"""

import asyncio
import logging
from datetime import datetime, UTC
from typing import Any

from phenotype_thegent_sync.autosync.adapters import (
    ConnectorConfigAdapter,
    MetricsAdapter,
    StateAdapter,
)
from phenotype_thegent_sync.integrations.workstream_autosync_shared import (
    SyncCheckpoint,
    SyncFailureQueue,
    WorkstreamAutosyncConfig,
)

logger = logging.getLogger(__name__)


class WorkstreamAutosyncRunner:
    """Main runner - thin orchestration delegating to modules."""

    # Initialize with composition - delegate to modules
    def __init__(self, config: WorkstreamAutosyncConfig):
        self.config = config
        self.is_running = False
        self._task: asyncio.Task[None] | None = None
        self.last_sync_time: datetime | None = None
        self.total_cycles = 0
        self.last_error: str | None = None

        # Initialize adapters
        self._state_adapter = StateAdapter(config)
        self._connector_config = ConnectorConfigAdapter(config)
        self._metrics_adapter = MetricsAdapter(config)

        # Legacy attributes for compatibility - will be migrated
        self._failure_queue = SyncFailureQueue(
            retention_seconds=config.failure_queue_retention_seconds,
        )
        self._checkpoint: SyncCheckpoint | None = None

    # Lifecycle methods - keep here (small)
    async def start(self) -> None:
        """Start the autosync runner."""
        if self.is_running:
            return
        self.is_running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Autosync runner started")

    async def stop(self) -> None:
        """Stop the autosync runner."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Autosync runner stopped")

    async def _run_loop(self) -> None:
        """Main run loop."""
        while self.is_running:
            try:
                await self._run_cycle()
            except Exception as e:
                logger.error(f"Cycle error: {e}")
                self.last_error = str(e)
            await asyncio.sleep(self.config.cycle_interval_seconds)

    async def _run_cycle(self) -> None:
        """Execute one cycle - delegates to specialized methods."""
        self.total_cycles += 1
        self.last_sync_time = datetime.now(UTC)

        # Delegate to cycle module
        from phenotype_thegent_sync.autosync.cycle import run_sync_cycle

        result = await run_sync_cycle(self)

        if result.get("error"):
            self.last_error = result["error"]

    # Status methods - simple delegates
    def get_status(self) -> dict[str, Any]:
        """Get runner status."""
        return {
            "is_running": self.is_running,
            "total_cycles": self.total_cycles,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "last_error": self.last_error,
        }

    # Property accessors for backward compatibility
    @property
    def last_operation(self):
        return getattr(self, "_last_operation", None)

    @last_operation.setter
    def last_operation(self, value):
        self._last_operation = value


__all__ = ["WorkstreamAutosyncRunner"]
