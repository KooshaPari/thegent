"""Runtime autosync runner with thin lifecycle wiring."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import orjson

from thegent.execution.resilience import EscalationQueue
from thegent.integrations.adapters import ConnectorConfigAdapter, MetricsAdapter, StateAdapter
from thegent.integrations.adapters.sync_adapter import SyncAdapter
from thegent.integrations.connector_mapping_cache import ConnectorMappingCache
from thegent.integrations.error_budget import ErrorBudgetConfig, ErrorBudgetTracker
from thegent.integrations.idempotency_cache import IdempotencyCache
from thegent.integrations.reflection_event_log import ReflectionDecision, ReflectionEventLog
from thegent.integrations.workstream_autosync_shared import (
    FailureRecord,
    RemoteMissingItemPolicy,
    SyncCheckpoint,
    SyncFailureQueue,
    WorkstreamAutosyncConfig,
    WorkstreamAutosyncConfigError,
)
from thegent.integrations.writer_lock import SingleWriterLock

logger = logging.getLogger(__name__)

_public_module = sys.modules.get("thegent.integrations.workstream_autosync")
if _public_module is not None and not hasattr(_public_module, "asyncio"):
    _public_module.asyncio = asyncio


def _load_failure_queue(config: WorkstreamAutosyncConfig, queue: SyncFailureQueue) -> None:
    path = config.failure_queue_path
    if not path or not path.exists():
        return
    try:
        payload = orjson.loads(path.read_bytes())
        records = [
            FailureRecord(
                operation_id=str(entry["operation_id"]),
                connector=str(entry["connector"]),
                item_id=str(entry["item_id"]),
                message=str(entry["message"]),
                occurred_at=datetime.fromisoformat(str(entry["occurred_at"])),
                retry_class=str(entry.get("retry_class", "permanent")),
                correlation_id=entry.get("correlation_id"),
            )
            for entry in payload
        ]
        queue.replace_records(records)
    except Exception as exc:
        logger.warning("failed loading autosync failure queue: %s", exc)


def _load_checkpoint(config: WorkstreamAutosyncConfig) -> SyncCheckpoint | None:
    path = config.checkpoint_file_path
    if not path or not path.exists():
        return None
    try:
        return SyncCheckpoint.from_dict(orjson.loads(path.read_bytes()))
    except Exception as exc:
        logger.warning("failed loading autosync checkpoint: %s", exc)
        return None


class WorkstreamAutosyncRunner:
    """Autosync runtime owner for cycle execution and local state."""

    def __init__(self, config: WorkstreamAutosyncConfig):
        self.config = config
        if not hasattr(self.config, "trend_path"):
            self.config.trend_path = self.config.trend_file_path
        self.is_running = False
        self._task: asyncio.Task[None] | None = None
        self.last_sync_time: datetime | None = None
        self.total_cycles = 0
        self.last_error: str | None = None
        self._last_operation = None
        self._no_op_summary: dict[str, Any] | None = None
        self._latest_incident_snapshot: dict[str, Any] | None = None
        self._current_run_correlation_id: str | None = None
        self._last_cycle_fingerprint: str | None = None
        self._throttle_retry_attempts = 0
        self._throttle_wait_seconds = 0.0
        self._manifest_prev_hash = ""
        self._connector_latency_samples: dict[str, list[float]] = {}
        self._connector_operation_count = 0
        self._outcome_counts: dict[str, int] = {"success": 0, "failure": 0}
        self._cycle_duration_count = 0
        self._runner_id = f"autosync-{id(self):x}"
        self._state_adapter = StateAdapter(config)
        self._connector_config = ConnectorConfigAdapter(config)
        self._metrics_adapter = MetricsAdapter(config)
        self._sync_adapter = SyncAdapter(config)
        self._failure_queue = SyncFailureQueue(config.failure_queue_retention_seconds)
        _load_failure_queue(config, self._failure_queue)
        self._checkpoint = _load_checkpoint(config)
        idempotency_path = (config.status_file_path or Path("docs/reference/autosync_status.json")).parent / "idempotency_cache.json"
        self._idempotency_cache = IdempotencyCache(idempotency_path)
        self._mapping_cache = ConnectorMappingCache(config.connector_mapping_cache_path)
        self._reflection_event_log = ReflectionEventLog(config.reflection_event_log_path)
        self._writer_lock = SingleWriterLock(config.writer_lock_path)
        self._error_budget = ErrorBudgetTracker(
            ErrorBudgetConfig(
                max_consecutive_failures=config.error_budget_max_consecutive_failures,
                max_failure_rate=config.error_budget_max_failure_rate,
                escalation_after=config.error_budget_escalation_after,
            )
        )

    async def start(self) -> None:
        if self.is_running or not self.config.is_valid():
            return
        self.is_running = True
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        self.is_running = False
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass

    async def _run_loop(self) -> None:
        while self.is_running:
            await self._perform_sync_cycle()
            await asyncio.sleep(max(1, self.config.cycle_interval_seconds))

    def get_status(self) -> dict[str, Any]:
        return {
            "enabled": self.config.enabled,
            "is_running": self.is_running,
            "github_enabled": self.config.github_enabled,
            "linear_enabled": self.config.linear_enabled,
            "total_cycles": self.total_cycles,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "last_error": self.last_error,
            "last_operation": self.last_operation.to_dict() if self.last_operation else None,
            "ignored_wl_ids": self.config.normalized_wl_ignore_list,
            "no_op_summary": self._no_op_summary,
            "connector_diff_workflow": {
                "dry_run_diff_artifact_path": "artifacts/workstream_autosync_dry_run_diff.txt"
            },
        }

    @property
    def last_operation(self) -> Any:
        return self._last_operation

    @last_operation.setter
    def last_operation(self, value: Any) -> None:
        self._last_operation = value

    def _build_incident_snapshot_bundle(self, items_count: int, metadata_state: dict[str, Any]) -> dict[str, Any]:
        return {
            "correlation_id": self._current_run_correlation_id,
            "cycle_number": self.total_cycles,
            "items_count": items_count,
            "metadata_state": metadata_state,
            "last_error": self.last_error,
            "slo_alerts": self._evaluate_slo_state(),
            "connector_diff_workflow": {
                "dry_run_diff_artifact_path": "artifacts/workstream_autosync_dry_run_diff.txt"
            },
        }

    def _finalize_incident_snapshot(self, items_count: int, metadata_state: dict[str, Any]) -> None:
        snapshot = self._build_incident_snapshot_bundle(items_count, metadata_state)
        self._latest_incident_snapshot = snapshot
        if self.config.incident_bundle_path:
            self.config.incident_bundle_path.parent.mkdir(parents=True, exist_ok=True)
            with self.config.incident_bundle_path.open("a", encoding="utf-8") as handle:
                handle.write(orjson.dumps(snapshot).decode("utf-8") + "\n")
        alerts = snapshot.get("slo_alerts", [])
        if alerts:
            queue = EscalationQueue((self.config.status_file_path or self._state_adapter.get_status_path()).parent)
            for alert in alerts:
                queue.add(str(self._current_run_correlation_id), str(alert), lane="autosync")

    def _evaluate_slo_state(self) -> list[str]:
        alerts: list[str] = []
        status_dir = (self.config.status_file_path or self._state_adapter.get_status_path()).parent
        snapshots = sorted(status_dir.glob("autosync_snapshot_*.json"))
        if snapshots:
            age_seconds = int(datetime.now(UTC).timestamp() - snapshots[-1].stat().st_mtime)
            if age_seconds > self.config.autosync_stale_snapshot_seconds:
                alerts.append(f"autosync snapshot stale: age_seconds={age_seconds}")
        stats = self._error_budget.get_stats()
        if self._error_budget.should_escalate():
            alerts.append(f"error budget escalation: failures={stats['failure_count']}")
        if self._error_budget.should_hard_fail():
            alerts.append("error budget hard-fail threshold reached")
        for connector, threshold in self.config.connector_sla_thresholds.items():
            latencies = sorted(self._connector_latency_samples.get(connector, []))
            if latencies:
                p95_index = min(len(latencies) - 1, max(0, round((len(latencies) - 1) * 0.95)))
                p95_ms = latencies[p95_index] * 1000
                if p95_ms > threshold.p95_latency_ms:
                    alerts.append(f"connector {connector} latency breach: p95_ms={p95_ms:.1f}")
            connector_stats = self._connector_error_budget(connector).get_stats()
            if connector_stats["current_failure_rate"] > threshold.max_failure_rate:
                alerts.append(
                    f"connector {connector} failure rate breach: rate={connector_stats['current_failure_rate']:.2f}"
                )
        return alerts

    def _record_local_reflection_events(self, connector: str, operation: Any) -> None:
        self._reflection_event_log.log(
            ReflectionDecision(
                wl_id=operation.operation_id,
                decision_type="apply",
                before_value=None,
                after_value=operation.to_dict(),
                connector=connector,
                timestamp=(operation.completed_at or datetime.now(UTC)).isoformat(),
                cycle_id=self._current_run_correlation_id or operation.operation_id,
                direction="local_to_remote",
                mutation_id=operation.operation_id,
            )
        )

    def _log_remote_reflection_events(
        self,
        connector: str,
        local_items: list[Any],
        status_updates: dict[str, str],
    ) -> None:
        by_id = {item.item_id: item for item in local_items}
        for wl_id, remote_status in status_updates.items():
            local = by_id.get(wl_id)
            if local is not None and local.status == remote_status:
                continue
            self._reflection_event_log.log(
                ReflectionDecision(
                    wl_id=wl_id,
                    decision_type="apply",
                    before_value=None if local is None else local.status,
                    after_value=remote_status,
                    connector=connector,
                    timestamp=datetime.now(UTC).isoformat(),
                    cycle_id=self._current_run_correlation_id or wl_id,
                    direction="remote_to_local",
                    mutation_id=f"{connector}:{wl_id}",
                )
            )

    def _build_remote_reflection_status_updates(
        self,
        local_items: list[Any],
        remote_status_updates: dict[str, str],
    ) -> dict[str, str]:
        updates = dict(remote_status_updates)
        if self.config.remote_missing_item_policy == RemoteMissingItemPolicy.ARCHIVE:
            for item in local_items:
                if item.item_id not in updates:
                    updates[item.item_id] = "ARCHIVED"
        return updates

    def _compact_snapshots(self, status_path: Path) -> None:
        snapshots = sorted(status_path.parent.glob("autosync_snapshot_*.json"))
        while len(snapshots) > self.config.snapshot_retention_count:
            snapshots.pop(0).unlink(missing_ok=True)

    def _serialize_artifact_payload(self, payload: dict[str, Any]) -> str:
        if not self.config.artifact_encryption_enabled:
            return orjson.dumps(payload).decode("utf-8")
        key = self.config.artifact_encryption_key
        if not key:
            raise WorkstreamAutosyncConfigError("Artifact encryption is enabled but no key is configured")
        raw = orjson.dumps(payload)
        secret = hashlib.sha256(key.encode("utf-8")).digest()
        encrypted = bytes(byte ^ secret[index % len(secret)] for index, byte in enumerate(raw))
        return orjson.dumps({"encrypted": True, "payload": base64.b64encode(encrypted).decode("ascii")}).decode(
            "utf-8"
        )

    def _deserialize_artifact_payload(self, serialized: str) -> dict[str, Any]:
        payload = orjson.loads(serialized)
        if not payload.get("encrypted"):
            return payload
        key = self.config.artifact_encryption_key
        if not key:
            raise WorkstreamAutosyncConfigError("Artifact encryption is enabled but no key is configured")
        data = base64.b64decode(payload["payload"])
        secret = hashlib.sha256(key.encode("utf-8")).digest()
        decrypted = bytes(byte ^ secret[index % len(secret)] for index, byte in enumerate(data))
        return orjson.loads(decrypted)

    def _compute_local_orphan_report(self, items: list[Any]) -> dict[str, list[str]]:
        cached = set(self._mapping_cache.list_cached_wl_ids("github")) | set(
            self._mapping_cache.list_cached_wl_ids("linear")
        )
        mapped = sorted(item.item_id for item in items if item.item_id in cached)
        orphaned = sorted(item.item_id for item in items if item.item_id not in cached)
        return {"mapped_remote_ids": mapped, "local_orphan_ids": orphaned}

    def _record_connector_latency(self, connector: str, duration_seconds: float) -> None:
        self._connector_latency_samples.setdefault(connector, []).append(max(0.0, duration_seconds))
        self._metrics_adapter.record_connector_latency(connector, duration_seconds)

    def _connector_error_budget(self, connector: str) -> Any:
        return self._connector_config.get_error_budget(connector)

    @staticmethod
    def simulate_connector_chaos(connector: str, scenario: str, items_count: int) -> dict[str, Any]:
        if scenario == "timeout":
            return {"connector": connector, "scenario": scenario, "items_attempted": items_count, "items_acked": 0, "retry_count": 3, "outcome": "outage", "escalate": True}
        if scenario == "partial_ack":
            return {"connector": connector, "scenario": scenario, "items_attempted": items_count, "items_acked": max(items_count - 1, 0), "retry_count": 0, "outcome": "partial", "escalate": True}
        if scenario == "http_5xx":
            return {"connector": connector, "scenario": scenario, "items_attempted": items_count, "items_acked": 0, "retry_count": 0, "outcome": "server_error", "escalate": True}
        raise ValueError("Unsupported chaos scenario")


from thegent.autosync import cycle as _cycle

for _name in (
    "_perform_sync_cycle",
    "_sync_in_partitions",
    "_sync_to_github",
    "_sync_from_github",
    "_sync_to_linear",
    "_sync_from_linear",
    "_record_failure",
    "_append_cycle_manifest",
    "_emit_cycle_metrics",
    "_compute_cycle_fingerprint",
):
    setattr(WorkstreamAutosyncRunner, _name, getattr(_cycle, _name))


__all__ = ["WorkstreamAutosyncRunner"]
