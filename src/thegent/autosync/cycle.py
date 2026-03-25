"""Autosync cycle execution and connector operations."""

from __future__ import annotations

import asyncio
import hashlib
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Iterable

import orjson

from thegent.integrations.policy_checksum import verify_payload_checksum
from thegent.integrations.sync_provenance import enrich_sync_metadata, new_run_correlation_id, propagate_owner_metadata
from thegent.integrations.workstream_autosync_shared import (
    RetryClass,
    SyncCheckpoint,
    SyncCycleManifest,
    SyncOperation,
    WorkstreamAutosyncConfigError,
    WorkstreamAutosyncError,
    WorkstreamItem,
    WorkstreamParser,
)
from thegent.utils.routing_impl.circuit_breaker import CircuitOpenError

CONNECTOR_DIFF_WORKFLOW = {"dry_run_diff_artifact_path": "artifacts/workstream_autosync_dry_run_diff.txt"}
_public_module = sys.modules.get("thegent.integrations.workstream_autosync")
if _public_module is not None and not hasattr(_public_module, "asyncio"):
    _public_module.asyncio = asyncio


def _public_api() -> Any:
    from thegent.integrations import workstream_autosync as public_api

    if not hasattr(public_api, "asyncio"):
        public_api.asyncio = asyncio
    return public_api


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(orjson.dumps(payload).decode("utf-8") + "\n")


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS))


def _status_path(self: Any) -> Path:
    return self.config.status_file_path or self._state_adapter.get_status_path()


def _manifest_path(self: Any) -> Path:
    return self.config.cycle_manifest_path or self._state_adapter.get_cycle_manifest_path()


def _failure_queue_path(self: Any) -> Path | None:
    return self.config.failure_queue_path or self._state_adapter.get_failure_queue_path()


def _checkpoint_path(self: Any) -> Path | None:
    return self.config.checkpoint_file_path


def _issue_retry_class(message: str) -> RetryClass:
    lowered = message.lower()
    if "429" in lowered or "rate limit" in lowered:
        return RetryClass.RATE_LIMIT
    if "timeout" in lowered or "tempor" in lowered:
        return RetryClass.TRANSIENT
    return RetryClass.PERMANENT


def _operation_id(self: Any, platform: str, direction: str, items: list[WorkstreamItem]) -> str:
    raw = self._sync_adapter.build_operation_id(platform, direction, items)
    return raw.replace("github-", "gh-", 1)


def _payload_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(orjson.dumps(payload, option=orjson.OPT_SORT_KEYS)).hexdigest()


def _metadata_state(self: Any) -> dict[str, Any]:
    refreshed = self.config.metadata_last_refreshed_at
    if refreshed is None:
        return {"status": "fresh", "age_seconds": 0}
    age = int((datetime.now(UTC) - refreshed).total_seconds())
    return {"status": "stale" if age > self.config.metadata_ttl_seconds else "fresh", "age_seconds": age}


def _filter_items(self: Any, items: Iterable[WorkstreamItem]) -> list[WorkstreamItem]:
    ignored = set(self.config.normalized_wl_ignore_list)
    return [item for item in items if item.item_id.upper() not in ignored and self.config.matches_scope_filters(item)]


def _build_payload_item(item: WorkstreamItem, source_tag: str) -> dict[str, Any]:
    payload = item.to_dict()
    if item.owner:
        payload = propagate_owner_metadata(payload, item.owner)
    return enrich_sync_metadata(payload, source_url=f"{source_tag}://workstream/{item.item_id}", source_tag=source_tag)


def _persist_failure_queue(self: Any) -> None:
    path = _failure_queue_path(self)
    if path is not None:
        _write_json(path, self._failure_queue.to_dict_list())


def _persist_checkpoint(self: Any) -> None:
    path = _checkpoint_path(self)
    if path is None:
        return
    if self._checkpoint is None:
        if path.exists():
            path.unlink()
        return
    _write_json(path, self._checkpoint.to_dict())


def _write_status(self: Any, status: str, items: list[WorkstreamItem]) -> None:
    status_path = _status_path(self)
    payload = {
        "enabled": self.config.enabled,
        "status": status,
        "last_error": self.last_error,
        "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
        "total_cycles": self.total_cycles,
        "item_count": len(items),
        "ignored_wl_ids": self.config.normalized_wl_ignore_list,
        "last_operation": self.last_operation.to_dict() if self.last_operation else None,
        "connector_diff_workflow": CONNECTOR_DIFF_WORKFLOW,
    }
    _write_json(status_path, payload)
    _write_json(status_path.parent / f"autosync_snapshot_{self.total_cycles:04d}.json", payload)


def _write_prometheus_export(self: Any, status: str) -> None:
    path = self.config.autosync_prometheus_export_path or self._state_adapter.get_autosync_metrics_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"thegent_autosync_cycles_total {self.total_cycles}",
        f'thegent_autosync_cycle_outcomes_total{{status="success"}} {self._outcome_counts.get("success", 0)}',
        f'thegent_autosync_cycle_outcomes_total{{status="failure"}} {self._outcome_counts.get("failure", 0)}',
        f"thegent_autosync_cycle_duration_seconds_count {self._cycle_duration_count}",
        f"thegent_autosync_connector_operations_total {self._connector_operation_count}",
        f"thegent_autosync_cycle_health {1 if status == 'success' else 0}",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _acquire_writer_lock(self: Any) -> bool:
    if not self.config.writer_lock_enabled:
        return True
    return self._writer_lock.acquire(self._current_run_correlation_id or self._runner_id)


def _release_writer_lock(self: Any) -> None:
    if self.config.writer_lock_enabled:
        self._writer_lock.release(self._current_run_correlation_id or self._runner_id)


def _remote_status_map(remote_items: list[dict[str, Any]]) -> dict[str, str]:
    return {
        str(item["item_id"]): str(item["status"]) for item in remote_items if item.get("item_id") and item.get("status")
    }


def _completion_transition(local_items: list[WorkstreamItem], remote_item: dict[str, Any]) -> bool:
    wl_id = str(remote_item.get("item_id") or "")
    next_status = str(remote_item.get("status") or "")
    current = next((item.status for item in local_items if item.item_id == wl_id), None)
    return current not in {"COMPLETED", "DONE", "CLOSED"} and next_status in {"COMPLETED", "DONE", "CLOSED"}


def _sleep_impl() -> Callable[[float], Any]:
    return _public_api().asyncio.sleep


async def run_sync_cycle(runner: Any) -> dict[str, Any]:
    return await runner._perform_sync_cycle()


async def _perform_sync_cycle(self: Any) -> dict[str, Any]:
    started_at = datetime.now(UTC)
    self.total_cycles += 1
    self.last_error = None
    self._no_op_summary = None
    self._throttle_retry_attempts = 0
    self._throttle_wait_seconds = 0.0
    self._current_run_correlation_id = new_run_correlation_id()
    items: list[WorkstreamItem] = []
    status = "success"
    outputs: dict[str, Any] = {"connector_diff_workflow": CONNECTOR_DIFF_WORKFLOW}
    decisions: dict[str, Any] = {
        "github_enabled": self.config.github_enabled,
        "linear_enabled": self.config.linear_enabled,
    }
    try:
        if not _acquire_writer_lock(self):
            raise WorkstreamAutosyncError("single-writer lock unavailable")
        if self.config.is_emergency_stop_active():
            raise WorkstreamAutosyncConfigError("Emergency stop active")
        if self.config.work_stream_path:
            items = _filter_items(self, WorkstreamParser.parse_items(self.config.work_stream_path))
        fingerprint = self._compute_cycle_fingerprint(items) if items else ""
        if self.config.simulation_mode:
            self._no_op_summary = {"no_op": True, "reason": "simulation_mode"}
            outputs["no_op_reason"] = "simulation_mode"
        elif not items:
            self._no_op_summary = {"no_op": True, "reason": "no_workstream_items"}
            outputs["no_op_reason"] = "no_workstream_items"
        elif self._last_cycle_fingerprint == fingerprint:
            self._no_op_summary = {"no_op": True, "reason": "unchanged_workstream_state"}
            outputs["no_op_reason"] = "unchanged_workstream_state"
        else:
            if self.config.github_can_write() and not self.config.is_maintenance_active("github"):
                await self._sync_in_partitions("github", "write", items, self._sync_to_github)
            if self.config.linear_can_write() and not self.config.is_maintenance_active("linear"):
                await self._sync_in_partitions("linear", "write", items, self._sync_to_linear)
            if (
                self.config.github_can_read()
                and self.config.work_stream_path
                and not self.config.is_maintenance_active("github")
            ):
                await self._sync_from_github(items, self.config.work_stream_path)
            if (
                self.config.linear_can_read()
                and self.config.work_stream_path
                and not self.config.is_maintenance_active("linear")
            ):
                await self._sync_from_linear(items, self.config.work_stream_path)
            self._last_cycle_fingerprint = fingerprint
        self._error_budget.record_success()
    except Exception as exc:
        status = "failure"
        self.last_error = str(exc)
        self._error_budget.record_failure()
    finally:
        completed_at = datetime.now(UTC)
        self.last_sync_time = completed_at
        self._outcome_counts[status] = self._outcome_counts.get(status, 0) + 1
        self._cycle_duration_count += 1
        outputs.setdefault("last_operation", self.last_operation.to_dict() if self.last_operation else None)
        self._append_cycle_manifest(status, started_at, items, decisions, outputs)
        self._emit_cycle_metrics(
            started_at,
            completed_at,
            len(items),
            status,
            bool(self._no_op_summary),
            None if not self._no_op_summary else self._no_op_summary.get("reason"),
        )
        _write_status(self, status, items)
        _write_prometheus_export(self, status)
        self._finalize_incident_snapshot(len(items), _metadata_state(self))
        self._compact_snapshots(_status_path(self))
        _release_writer_lock(self)
    return {"status": status, "items": len(items)}


async def _sync_in_partitions(
    self: Any,
    connector: str,
    direction: str,
    items: list[WorkstreamItem],
    sync_fn: Callable[[list[WorkstreamItem]], Any],
) -> None:
    partitions = WorkstreamParser.split_items(items, self.config.effective_partition_size)
    timeout = self._connector_config.get_connector_timeout(connector, direction)
    breaker = self._connector_config.get_connector_breaker(connector)
    backoff = self._connector_config.create_rate_limiter()
    for index, partition in enumerate(partitions):
        self._checkpoint = SyncCheckpoint(
            connector, direction, index, len(partitions), self.config.effective_partition_size, datetime.now(UTC)
        )
        _persist_checkpoint(self)
        attempt = 0
        while True:
            try:

                async def _invoke(partition_items: list[WorkstreamItem] = partition) -> None:
                    await asyncio.wait_for(sync_fn(partition_items), timeout=timeout)

                await breaker.call_async(_invoke)
                self._connector_error_budget(connector).record_success()
                self._connector_operation_count += 1
                self._checkpoint = None
                _persist_checkpoint(self)
                break
            except CircuitOpenError as exc:
                self._checkpoint = None
                _persist_checkpoint(self)
                raise WorkstreamAutosyncError(f"open connector circuit breaker for {connector}") from exc
            except asyncio.TimeoutError as exc:
                self._connector_error_budget(connector).record_failure()
                self._checkpoint = None
                _persist_checkpoint(self)
                error = WorkstreamAutosyncError(f"{connector} {direction} partition timed out after {timeout:.3f}s")
                if self.config.standalone_mode:
                    self.last_error = str(error)
                    return
                raise error from exc
            except Exception as exc:
                self._connector_error_budget(connector).record_failure()
                message = str(exc)
                if _issue_retry_class(message) == RetryClass.RATE_LIMIT and attempt < backoff.config.max_retries:
                    attempt += 1
                    wait_seconds = backoff.compute_wait(attempt)
                    self._throttle_retry_attempts += 1
                    self._throttle_wait_seconds += wait_seconds
                    await _sleep_impl()(wait_seconds)
                    continue
                await self._record_failure(connector, direction, partition[0].item_id if partition else "", message)
                self._checkpoint = None
                _persist_checkpoint(self)
                if self.config.standalone_mode:
                    self.last_error = message
                    return
                raise


async def _sync_to_github(self: Any, items: list[WorkstreamItem]) -> None:
    if self.config.is_emergency_stop_active():
        raise WorkstreamAutosyncConfigError("Emergency stop active")
    required = set(self.config.required_connector_capabilities.get("github", []))
    available = set(self.config.connector_capabilities.get("github", []))
    missing = sorted(required - available)
    if missing:
        raise WorkstreamAutosyncConfigError(f"Connector capability mismatch for github: missing {missing[0]}")
    public_api = _public_api()
    payload = [_build_payload_item(item, "github") for item in items]
    if self.config.require_actor_identity:
        public_api.SSHIdentityProxy.require_actor_identity(
            actor_id=self.config.actor_id,
            signature=self.config.actor_signature,
            payload=payload,
            signing_key=self.config.actor_signing_key,
        )
    operation_id = _operation_id(self, "github", "write", items)
    pending = [
        item
        for item in payload
        if not self._idempotency_cache.check_content("github", item["item_id"], _payload_hash(item))
    ]
    operation = SyncOperation(
        operation_id, "github", "write", len(items), len(pending), 0, correlation_id=self._current_run_correlation_id
    )
    if not self.config.shadow_mode and pending:
        result = public_api.gh_sync_to_github(self.config, pending)
        operation.errors = list(result.get("errors", [])) if isinstance(result, dict) else []
    for item in pending:
        self._idempotency_cache.record(operation_id, item["item_id"], "github", _payload_hash(item))
    if self.config.github_auto_close_issues:
        refs: list[str] = []
        for item in items:
            if item.status == "COMPLETED":
                refs.extend(public_api.extract_github_issue_refs({"title": item.title, "body": item.raw_section or ""}))
        if refs:
            public_api.close_or_comment_github_issue_refs(refs, close_comment=self.config.github_auto_close_comment)
    operation.completed_at = datetime.now(UTC)
    operation.duration_seconds = max(0.0, (operation.completed_at - operation.started_at).total_seconds())
    self.last_operation = operation
    self._record_connector_latency("github", operation.duration_seconds)
    self._record_local_reflection_events("github", operation)


async def _sync_from_github(self: Any, items: list[WorkstreamItem], work_stream_path: Path) -> None:
    public_api = _public_api()
    result = public_api.gh_sync_from_github(self.config, items)
    remote_items = list(result.get("items", [])) if isinstance(result, dict) else []
    if self.config.payload_checksum_enforced:
        verify_payload_checksum(remote_items, self.config.expected_payload_checksum)
    updates = self._build_remote_reflection_status_updates(items, _remote_status_map(remote_items))
    text = work_stream_path.read_text(encoding="utf-8")
    work_stream_path.write_text(WorkstreamParser.sync_status_annotations(text, statuses=updates), encoding="utf-8")
    if self.config.github_auto_close_issues:
        for remote_item in remote_items:
            if _completion_transition(items, remote_item):
                refs = public_api.extract_github_issue_refs(remote_item)
                if refs:
                    public_api.close_or_comment_github_issue_refs(
                        refs, close_comment=self.config.github_auto_close_comment
                    )
    operation = SyncOperation(
        _operation_id(self, "github", "read", items),
        "github",
        "read",
        len(remote_items),
        len(remote_items),
        0,
        correlation_id=self._current_run_correlation_id,
    )
    operation.completed_at = datetime.now(UTC)
    operation.duration_seconds = max(0.0, (operation.completed_at - operation.started_at).total_seconds())
    self.last_operation = operation
    self._record_connector_latency("github", operation.duration_seconds)
    self._log_remote_reflection_events("github", items, updates)


async def _sync_to_linear(self: Any, items: list[WorkstreamItem]) -> None:
    if self.config.is_emergency_stop_active():
        raise WorkstreamAutosyncConfigError("Emergency stop active")
    public_api = _public_api()
    payload = [_build_payload_item(item, "linear") for item in items]
    operation_id = _operation_id(self, "linear", "write", items)
    pending = [
        item
        for item in payload
        if not self._idempotency_cache.check_content("linear", item["item_id"], _payload_hash(item))
    ]
    if not self.config.shadow_mode and pending:
        public_api.linear_sync_to(self.config, pending)
    for item in pending:
        self._idempotency_cache.record(operation_id, item["item_id"], "linear", _payload_hash(item))
    operation = SyncOperation(
        operation_id, "linear", "write", len(items), len(pending), 0, correlation_id=self._current_run_correlation_id
    )
    operation.completed_at = datetime.now(UTC)
    operation.duration_seconds = max(0.0, (operation.completed_at - operation.started_at).total_seconds())
    self.last_operation = operation
    self._record_connector_latency("linear", operation.duration_seconds)
    self._record_local_reflection_events("linear", operation)


async def _sync_from_linear(self: Any, items: list[WorkstreamItem], work_stream_path: Path) -> None:
    public_api = _public_api()
    result = public_api.linear_sync_from(self.config)
    remote_items = list(result.get("items", [])) if isinstance(result, dict) else []
    if self.config.payload_checksum_enforced:
        verify_payload_checksum(remote_items, self.config.expected_payload_checksum)
    updates = self._build_remote_reflection_status_updates(items, _remote_status_map(remote_items))
    text = work_stream_path.read_text(encoding="utf-8")
    work_stream_path.write_text(WorkstreamParser.sync_status_annotations(text, statuses=updates), encoding="utf-8")
    operation = SyncOperation(
        _operation_id(self, "linear", "read", items),
        "linear",
        "read",
        len(remote_items),
        len(remote_items),
        0,
        correlation_id=self._current_run_correlation_id,
    )
    operation.completed_at = datetime.now(UTC)
    operation.duration_seconds = max(0.0, (operation.completed_at - operation.started_at).total_seconds())
    self.last_operation = operation
    self._record_connector_latency("linear", operation.duration_seconds)
    self._log_remote_reflection_events("linear", items, updates)


async def _record_failure(self: Any, connector: str, direction: str, item_id: str, message: str) -> RetryClass:
    retry_class = _issue_retry_class(message)
    self._failure_queue.push(
        f"{connector}-{direction}-{item_id or 'unknown'}",
        connector,
        item_id or "unknown",
        message,
        retry_class=retry_class,
        correlation_id=self._current_run_correlation_id,
    )
    _persist_failure_queue(self)
    return retry_class


def _append_cycle_manifest(
    self: Any,
    status: str,
    started_at: datetime,
    items: list[WorkstreamItem],
    decisions: dict[str, Any],
    outputs: dict[str, Any],
) -> None:
    manifest = SyncCycleManifest(
        cycle_number=self.total_cycles,
        started_at=started_at.isoformat(),
        status=status,
        inputs={
            "run_id": self._current_run_correlation_id,
            "item_ids": [item.item_id for item in items],
            "item_count": len(items),
        },
        decisions=decisions,
        outputs={**outputs, "connector_diff_workflow": CONNECTOR_DIFF_WORKFLOW},
        previous_manifest_hash=self._manifest_prev_hash,
    ).with_hash()
    self._manifest_prev_hash = manifest.manifest_hash
    _append_jsonl(_manifest_path(self), manifest.to_dict())


def _emit_cycle_metrics(
    self: Any,
    started_at: datetime,
    completed_at: datetime,
    item_count: int,
    status: str,
    no_op: bool,
    no_op_reason: str | None,
) -> None:
    payload = {
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat(),
        "duration_seconds": max(0.0, (completed_at - started_at).total_seconds()),
        "item_count": item_count,
        "status": status,
        "no_op": no_op,
        "no_op_reason": no_op_reason,
        "throttle_retry_attempts": self._throttle_retry_attempts,
        "throttle_wait_seconds": self._throttle_wait_seconds,
    }
    self._metrics_adapter.append_cycle_metrics(payload)


def _compute_cycle_fingerprint(self: Any, items: list[WorkstreamItem]) -> str:
    return self._sync_adapter.compute_cycle_fingerprint(items)


__all__ = [
    "_append_cycle_manifest",
    "_compute_cycle_fingerprint",
    "_emit_cycle_metrics",
    "_perform_sync_cycle",
    "_record_failure",
    "_sync_from_github",
    "_sync_from_linear",
    "_sync_in_partitions",
    "_sync_to_github",
    "_sync_to_linear",
    "run_sync_cycle",
]
