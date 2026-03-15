"""Compatibility surface for workstream autosync."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from typing import Awaitable, Callable

import orjson as json

from thegent_sync.integrations.workstream_autosync_shared import (
    ConnectorSLAThresholds,
    MaintenanceWindow,
    RemoteMissingItemPolicy,
    RetryClass,
    SyncOperation,
    SyncDirection,
    WorkstreamAutosyncConfig,
    WorkstreamAutosyncConfigError,
    WorkstreamAutosyncError,
    WorkstreamItem,
    WorkstreamParser,
    load_autosync_config_from_env,
)
from thegent_sync.integrations.rate_limit_backoff import RateLimitBackoffManager, RateLimitConfig
from thegent_sync.integrations.writer_lock import SingleWriterLock


class WorkstreamAutosyncRunner:
    """Package-backed runner retaining the legacy test contract."""

    def __init__(self, config: WorkstreamAutosyncConfig):
        self.config = config
        self.is_running = False
        self.last_sync_time: datetime | None = None
        self.total_cycles = 0
        self.last_error: str | None = None
        lock_path = config.writer_lock_path
        if lock_path is None and config.status_file_path is not None:
            lock_path = Path(config.status_file_path).parent / "autosync.lock"
        self._writer_lock = SingleWriterLock(lock_path)
        self._rate_limiter = RateLimitBackoffManager(
            RateLimitConfig(
                max_retries=max(0, int(config.rate_limit_max_retries)),
                initial_wait=max(0.01, float(config.rate_limit_initial_wait)),
                max_wait=max(0.01, float(config.rate_limit_max_wait)),
                multiplier=max(1.0, float(config.rate_limit_multiplier)),
            )
        )

    async def start(self) -> None:
        self.is_running = True

    async def stop(self) -> None:
        self.is_running = False

    async def _perform_sync_cycle(self) -> dict[str, object]:
        """Run one sync cycle and persist the cycle metric record."""
        self.total_cycles += 1
        self.last_sync_time = datetime.now(UTC)
        owner_id = f"autosync-cycle-{self.total_cycles}"

        if self.config.writer_lock_enabled and not self._writer_lock.acquire(owner_id):
            self.last_error = "single-writer lock unavailable"
            record = self._cycle_record(status="failed", item_count=0, error=self.last_error)
            self._append_cycle_metric(record)
            return record

        try:
            items = self._load_local_items()
            record = self._cycle_record(status="success", item_count=len(items))
            self._append_cycle_metric(record)
            self.last_error = None
            return record
        except Exception as exc:
            self.last_error = str(exc)
            record = self._cycle_record(status="failed", item_count=0, error=self.last_error)
            self._append_cycle_metric(record)
            return record
        finally:
            if self.config.writer_lock_enabled:
                self._writer_lock.release(owner_id)

    async def _sync_in_partitions(
        self,
        *,
        connector: str,
        direction: str,
        items: list[WorkstreamItem],
        sync_fn: Callable[[list[WorkstreamItem]], Awaitable[None]],
    ) -> SyncOperation:
        """Run a sync function against item partitions with bounded rate-limit retries."""
        operation = SyncOperation(
            operation_id=f"{connector}:{direction}:{datetime.now(UTC).isoformat()}",
            platform=connector,
            direction=direction,
            items_processed=len(items),
        )
        partitions = WorkstreamParser.split_items(items, self.config.effective_partition_size)

        for partition in partitions:
            attempts = 0
            while True:
                try:
                    await sync_fn(partition)
                    operation.items_successful += len(partition)
                    break
                except Exception as exc:
                    message = str(exc)
                    if "429" in message and attempts < self.config.rate_limit_max_retries:
                        attempts += 1
                        await asyncio.sleep(self._rate_limiter.compute_wait(attempts))
                        continue

                    operation.items_failed += len(partition)
                    operation.errors.append(message)
                    self.last_error = message
                    break

        operation.completed_at = datetime.now(UTC)
        operation.duration_seconds = max(
            0.0,
            (operation.completed_at - operation.started_at).total_seconds(),
        )
        return operation

    def get_status(self) -> dict[str, object]:
        return {
            "is_running": self.is_running,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "total_cycles": self.total_cycles,
            "last_error": self.last_error,
        }

    def _load_local_items(self) -> list[WorkstreamItem]:
        work_stream_path = self.config.work_stream_path
        if work_stream_path is None or not work_stream_path.exists():
            return []
        return WorkstreamParser.parse_items(work_stream_path)

    def _append_cycle_metric(self, record: dict[str, object]) -> None:
        path = self.config.cycle_metrics_path
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("ab") as handle:
                handle.write(json.dumps(record))
                handle.write(b"\n")

    def _cycle_record(self, *, status: str, item_count: int, error: str | None = None) -> dict[str, object]:
        return {
            "status": status,
            "item_count": item_count,
            "error": error,
            "timestamp": datetime.now(UTC).isoformat(),
        }


__all__ = [
    "ConnectorSLAThresholds",
    "MaintenanceWindow",
    "RemoteMissingItemPolicy",
    "RetryClass",
    "SyncDirection",
    "SyncOperation",
    "WorkstreamAutosyncConfig",
    "WorkstreamAutosyncConfigError",
    "WorkstreamAutosyncError",
    "WorkstreamAutosyncRunner",
    "WorkstreamItem",
    "WorkstreamParser",
    "load_autosync_config_from_env",
]
