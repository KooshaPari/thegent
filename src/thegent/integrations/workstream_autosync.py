"""Automatic Workstream Reflection (WL-160): GitHub Projects + Linear Bidirectional Sync.

Provides background synchronization that continuously reflects:
- local markdown updates (docs/reference/WORK_STREAM.md) -> GitHub Projects + Linear
- remote status updates in GitHub Projects/Linear -> local markdown status lines

Key Principles:
- Standalone-safe: No crash when disabled or credentials missing
- Config-driven: Enable/disable via environment variables
- Cycle runner: Background loop with configurable interval
- Adapters: Separate logic for GitHub and Linear platforms
- Reflection writer: Atomic updates to local markdown
"""

import asyncio
import base64
import hashlib
import orjson as json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from thegent.infra.identity_proxy import SSHIdentityProxy
from thegent.integrations.adapters import (
    ConnectorConfigAdapter,
    MetricsAdapter,
    StateAdapter,
    xor_encrypt,
    xor_decrypt,
    compute_artifact_key,
)
from thegent.integrations.capability_alerts import (
    CapabilityMismatchDetector,
    ConnectorCapabilityDiscovery,
    ConnectorSLAEvaluator,
    ConnectorSLAThresholds,
)
from thegent.integrations.connector_mapping_cache import ConnectorMappingCache
from thegent.integrations.error_budget import ErrorBudgetConfig, ErrorBudgetTracker
from thegent.integrations.gh_project_sync import (
    GHProjectConfig,
    GHProjectSyncError,
    close_or_comment_github_issue_refs,
    extract_github_issue_refs,
    sync_from_github as gh_sync_from_github,
    sync_to_github as gh_sync_to_github,
)
from thegent.integrations.idempotency_cache import IdempotencyCache
from thegent.integrations.reflection_event_log import ReflectionDecision, ReflectionEventLog
from thegent.integrations.linear_graphql import (
    LinearGraphQLAuthError,
    LinearGraphQLConfig,
    LinearGraphQLError,
    sync_from_linear as linear_sync_from,
    sync_to_linear as linear_sync_to,
)
from thegent.integrations.rate_limit_backoff import RateLimitBackoffManager, RateLimitConfig
from thegent.integrations.policy_checksum import verify_payload_checksum
from thegent.integrations.sync_provenance import (
    enrich_sync_metadata,
    propagate_owner_metadata,
)
from thegent.integrations.writer_lock import SingleWriterLock
from thegent.integrations.pipeline_percentiles import PipelinePercentileTracker
from thegent.observability.prometheus import get_metrics_collector
from thegent.execution import EscalationQueue
from research_engine.digest import build_hourly_change_digest
from thegent.utils.routing_impl.circuit_breaker import (
    CircuitOpenError,
    ProviderCircuitBreakerConfig,
    ProviderCircuitBreakerRegistry,
)

from thegent.integrations.workstream_autosync_shared import (
    ConnectorHealthProbeResult,
    FailureRecord,
    MaintenanceWindow,
    RemoteMissingItemPolicy,
    RetryClass,
    SyncCheckpoint,
    SyncCycleManifest,
    SyncDirection,
    SyncFailureQueue,
    SyncOperation,
    WorkstreamAutosyncAuthError,
    WorkstreamAutosyncConfig,
    WorkstreamAutosyncConfigError,
    WorkstreamAutosyncError,
    WorkstreamAutosyncMaintenanceError,
    WorkstreamDuplicateTitleError,
    WorkstreamItem,
    WorkstreamParser,
    WorkstreamPartition,
    build_owner_metadata,
    compute_adaptive_sync_interval,
    load_autosync_config_from_env,
    validate_env_profile_drift,
)

logger = logging.getLogger(__name__)

__all__ = [
    "ConnectorHealthProbeResult",
    "FailureRecord",
    "MaintenanceWindow",
    "RemoteMissingItemPolicy",
    "RetryClass",
    "SyncCheckpoint",
    "SyncCycleManifest",
    "SyncDirection",
    "SyncFailureQueue",
    "SyncOperation",
    "WorkstreamAutosyncAuthError",
    "WorkstreamAutosyncConfig",
    "WorkstreamAutosyncConfigError",
    "WorkstreamAutosyncError",
    "WorkstreamAutosyncMaintenanceError",
    "WorkstreamAutosyncRunner",
    "WorkstreamDuplicateTitleError",
    "WorkstreamItem",
    "WorkstreamParser",
    "WorkstreamPartition",
    "build_owner_metadata",
    "compute_adaptive_sync_interval",
    "load_autosync_config_from_env",
    "validate_env_profile_drift",
]

# Autosync Cycle Runner


class WorkstreamAutosyncRunner:
    """Background cycle runner for workstream autosync."""

    def __init__(self, config: WorkstreamAutosyncConfig):
        """Initialize the autosync runner.

        Args:
            config: Workstream autosync configuration
        """
        self.config = config
        self.is_running = False
        self._task: asyncio.Task[None] | None = None
        self.last_sync_time: datetime | None = None
        self.last_operation: SyncOperation | None = None
        self.total_cycles = 0
        self.last_error: str | None = None
        self._failure_queue = SyncFailureQueue(
            retention_seconds=self.config.failure_queue_retention_seconds,
        )
        self._load_failure_queue()
        self._checkpoint: SyncCheckpoint | None = None
        self._latest_blocker_digest: list[str] = []
        self._last_ignored_item_ids: list[str] = []
        self._last_scope_filtered_item_ids: list[str] = []
        self._last_connector_probe: list[ConnectorHealthProbeResult] = []
        self._next_cycle_interval_seconds = self.config.cycle_interval_seconds
        self._latest_incident_snapshot: dict[str, Any] | None = None
        self._idempotency_cache = IdempotencyCache()
        self._error_budget = ErrorBudgetTracker(
            ErrorBudgetConfig(
                max_consecutive_failures=self.config.error_budget_max_consecutive_failures,
                max_failure_rate=self.config.error_budget_max_failure_rate,
                escalation_after=self.config.error_budget_escalation_after,
            ),
        )

        # Initialize adapters
        self._metrics_adapter = MetricsAdapter(config)
        self._state_adapter = StateAdapter(config)
        self._connector_config_adapter = ConnectorConfigAdapter(config)

        self._metrics = get_metrics_collector()
        self._breaker_registry = ProviderCircuitBreakerRegistry.get_instance()
        self._current_run_correlation_id: str | None = None
        self._last_cycle_fingerprint: str | None = None
        self._slo_alerts: list[str] = []
        self._last_slo_escalation_signature: str | None = None
        self._connector_sla_thresholds: dict[str, ConnectorSLAThresholds] = dict(self.config.connector_sla_thresholds)
        self._connector_sla_evaluator = ConnectorSLAEvaluator()
        self._connector_latency_tracker = PipelinePercentileTracker()
        self._connector_error_budgets: dict[str, ErrorBudgetTracker] = {}
        self._cycle_failure_recorded = False
        self._cycle_change_events: list[dict[str, Any]] = []
        self._latest_change_digest: dict[str, Any] = {"bucket": "hourly", "hours": {}}
        self._local_orphan_report: dict[str, Any] = {
            "local_ids": [],
            "mapped_remote_ids": [],
            "local_orphan_ids": [],
            "orphan_count": 0,
        }
        self._reflection_event_log = ReflectionEventLog(log_path=self.config.reflection_event_log_path)
        self._no_op_summary: dict[str, Any] | None = None
        self._last_trend_sample: dict[str, Any] | None = None
        self._rate_limit_backoff = self._connector_config_adapter.create_rate_limiter()
        self._writer_lock = SingleWriterLock(lock_path=self._writer_lock_path())

    def _connector_breaker(self, connector: str) -> Any:
        return self._connector_config_adapter.get_connector_breaker(connector)

    def _connector_timeout_seconds(self, connector: str, direction: str) -> float:
        return self._connector_config_adapter.get_connector_timeout(connector, direction)

    def _autosync_metrics_export_path(self) -> Path:
        default_path = Path("docs/reference/workstream_autosync_metrics.prom")
        return self.config.autosync_prometheus_export_path or default_path

    def _cycle_metrics_path(self) -> Path:
        default_cycle_metrics_path = Path("docs/reference/workstream_autosync_cycle_metrics.jsonl")
        return self.config.cycle_metrics_path or default_cycle_metrics_path

    def _change_digest_path(self) -> Path:
        default_change_digest_path = Path("artifacts/workstream_autosync_change_digest.jsonl")
        return self.config.change_digest_path or default_change_digest_path

    def _writer_lock_path(self) -> Path:
        if self.config.writer_lock_path is not None:
            return self.config.writer_lock_path
        if self.config.work_stream_path is not None:
            return self.config.work_stream_path.parent / "autosync.lock"
        return SingleWriterLock.DEFAULT_LOCK_PATH

    def _writer_lock_owner(self) -> str:
        actor_id = self.config.actor_id.strip()
        if actor_id:
            return actor_id
        return f"pid-{os.getpid()}"

    def _requires_writer_lock(self) -> bool:
        return (
            self.config.writer_lock_enabled
            and not self.config.dry_run
            and not self.config.simulation_mode
            and (self.config.github_can_write() or self.config.linear_can_write())
        )

    def _escalation_session_dir(self) -> Path:
        status_path = self.config.status_file_path or Path("docs/reference/autosync_status.json")
        return status_path.parent

    def _latest_snapshot_age_seconds(self) -> int | None:
        status_path = self.config.status_file_path or Path("docs/reference/autosync_status.json")
        snapshot_candidates = sorted(status_path.parent.glob("autosync_snapshot_*.json"))
        if not snapshot_candidates:
            return None
        try:
            latest = max(snapshot_candidates, key=lambda path: path.stat().st_mtime)
            age_delta = datetime.now(timezone.utc) - datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
            return max(0, int(age_delta.total_seconds()))
        except OSError:
            return None

    def _evaluate_slo_state(self) -> list[str]:
        alerts: list[str] = []
        snapshot_age = self._latest_snapshot_age_seconds()
        if snapshot_age is not None and snapshot_age > self.config.autosync_stale_snapshot_seconds:
            alerts.append(f"autosync snapshot stale for {snapshot_age}s")

        if self._error_budget.should_escalate():
            alerts.append("autosync error budget escalation threshold reached")

        if self._error_budget.should_hard_fail():
            alerts.append("autosync error budget hard-fail threshold reached")

        for connector, thresholds in sorted(self._connector_sla_thresholds.items()):
            latency_summary = self._connector_latency_tracker.summary(connector)
            if latency_summary.get("count", 0) == 0:
                continue
            error_budget = self._connector_error_budget(connector)
            result = self._connector_sla_evaluator.evaluate(
                connector_name=connector,
                latency_summary=latency_summary,
                error_budget_stats=error_budget.get_stats(),
                thresholds=thresholds,
            )
            for breach in result.get("breaches", []):
                alerts.append(f"connector {connector} SLA breach: {breach}")

        return alerts

    def _connector_error_budget(self, connector: str) -> ErrorBudgetTracker:
        normalized = connector.lower()
        budget = self._connector_error_budgets.get(normalized)
        if budget is None:
            budget = ErrorBudgetTracker(
                ErrorBudgetConfig(
                    max_consecutive_failures=self.config.error_budget_max_consecutive_failures,
                    max_failure_rate=self.config.error_budget_max_failure_rate,
                    escalation_after=self.config.error_budget_escalation_after,
                ),
            )
            self._connector_error_budgets[normalized] = budget
        return budget

    def _record_connector_latency(self, connector: str, *, duration_seconds: float) -> None:
        duration_ms = max(0.0, float(duration_seconds) * 1000.0)
        cycle_id = self._current_run_correlation_id or "standalone"
        self._connector_latency_tracker.record(connector, duration_ms, cycle_id)

    def _maybe_enqueue_escalation(self, reason: str) -> None:
        if not reason or self.config.dry_run:
            return
        if not self._current_run_correlation_id:
            return
        signature = hashlib.sha1(f"{self._current_run_correlation_id}:{reason}".encode()).hexdigest()
        if signature == self._last_slo_escalation_signature:
            return

        escalation_queue = EscalationQueue(self._escalation_session_dir())
        escalation_queue.add(
            run_id=self._current_run_correlation_id,
            reason=reason,
            sla_minutes=max(1, int(self.config.autosync_stale_snapshot_seconds / 60)),
            owner=self.config.actor_id.strip() or None,
            agent="autosync",
            lane="autosync",
            priority=1,
        )
        self._last_slo_escalation_signature = signature
        logger.warning("Autosync SLO escalation queued: %s", reason)

    def _flush_prometheus_metrics(self) -> None:
        self._metrics.export_text_file(self._autosync_metrics_export_path())

    def _cycle_manifest_path(self) -> Path:
        default_cycle_manifest_path = Path("artifacts/workstream_autosync_cycle_manifest.jsonl")
        return self.config.cycle_manifest_path or default_cycle_manifest_path

    def _read_last_manifest_hash(self) -> str:
        path = self._cycle_manifest_path()
        if not path.exists():
            return ""
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines:
            return ""
        last_payload = json.loads(lines[-1])
        manifest_hash = last_payload.get("manifest_hash")
        if isinstance(manifest_hash, str):
            return manifest_hash
        return ""

    def _append_cycle_manifest(
        self,
        *,
        status: str,
        started_at: datetime,
        items: list[WorkstreamItem],
        decisions: dict[str, Any],
        outputs: dict[str, Any],
    ) -> None:
        manifest = SyncCycleManifest(
            cycle_number=self.total_cycles + 1,
            started_at=started_at.isoformat(),
            status=status,
            inputs={
                "item_count": len(items),
                "item_ids": sorted(item.item_id for item in items),
                "shadow_mode": self.config.shadow_mode,
                "run_id": self._current_run_correlation_id,
            },
            decisions=decisions,
            outputs=outputs,
            previous_manifest_hash=self._read_last_manifest_hash(),
        ).with_hash()
        path = self._cycle_manifest_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(manifest.to_dict().decode().decode(), sort_keys=True) + "\n")

    @staticmethod
    def _build_operation_id(platform: str, direction: str, items: list[WorkstreamItem]) -> str:
        """Build replay-safe deterministic operation IDs for sync batches."""
        item_key = ",".join(sorted(item.item_id for item in items))
        digest = hashlib.sha1(f"{platform}:{direction}:{item_key}".encode()).hexdigest()[:12]
        return f"{platform}-{direction}-{digest}"

    @staticmethod
    def _build_mutation_id(platform: str, item: WorkstreamItem) -> str:
        """Build a deterministic mutation identifier for one item write."""
        payload = f"{platform}:{item.item_id}:{item.status}:{item.priority}:{item.area}"
        digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]
        return f"{platform}-mutation-{item.item_id}-{digest}"

    @staticmethod
    def _normalize_for_checksum_payload(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Return a deterministic remote payload representation for checksum verification."""
        normalized = [{key: item[key] for key in sorted(item)} for item in payload]
        return sorted(normalized, key=lambda item: json.dumps(item, sort_keys=True).decode().decode())

    def _enforce_write_guards(self, *, connector: str, items: list[WorkstreamItem]) -> None:
        """Fail-fast guard for write-capable sync entrypoints."""
        if self.config.is_emergency_stop_active():
            raise WorkstreamAutosyncConfigError(
                "Emergency stop active; write-capable autosync entrypoint is disabled",
            )
        if self.config.require_actor_identity:
            payload = ",".join(sorted(item.item_id for item in items))
            SSHIdentityProxy.require_actor_identity(
                actor_id=self.config.actor_id,
                signature=self.config.actor_signature,
                payload=payload,
                signing_key=self.config.actor_signing_key,
            )
        required = self.config.required_connector_capabilities.get(connector, [])
        if required:
            discovery = ConnectorCapabilityDiscovery(
                lambda key: self.config.connector_capabilities.get(key, []),
            )
            available = discovery.discover(connector, refresh=True)
            missing = CapabilityMismatchDetector(required).check_connector(connector, available)
            if missing:
                raise WorkstreamAutosyncConfigError(
                    f"Connector capability mismatch for {connector}: missing {', '.join(missing)}",
                )
        if self.config.payload_checksum_enforced:
            checksum_payload = [item.to_dict() for item in items]
            verify_payload_checksum(checksum_payload, self.config.expected_payload_checksum)

    def _artifact_encryption_key(self) -> str:
        key = self.config.artifact_encryption_key or os.getenv("THGENT_AUTOSYNC_ARTIFACT_KEY", "")
        if self.config.artifact_encryption_enabled and not key:
            raise WorkstreamAutosyncConfigError(
                "Artifact encryption is enabled but no key is configured (THGENT_AUTOSYNC_ARTIFACT_KEY)."
            )
        return key

    def _serialize_artifact_payload(self, payload: Any) -> str:
        text = json.dumps(payload, indent=2).decode().decode()
        if not self.config.artifact_encryption_enabled:
            return text
        key = self._artifact_encryption_key()
        encrypted = {
            "encrypted": True,
            "algorithm": "xor-v1",
            "ciphertext_b64": xor_encrypt(text.encode("utf-8"), key),
        }
        return json.dumps(encrypted, indent=2).decode().decode()

    def _deserialize_artifact_payload(self, raw_text: str) -> Any:
        payload = json.loads(raw_text)
        if not isinstance(payload, dict) or payload.get("encrypted") is not True:
            return payload
        if payload.get("algorithm") != "xor-v1":
            raise WorkstreamAutosyncConfigError("Unsupported encrypted artifact algorithm.")
        ciphertext = payload.get("ciphertext_b64")
        if not isinstance(ciphertext, str):
            raise WorkstreamAutosyncConfigError("Encrypted artifact is missing ciphertext_b64.")
        key = self._artifact_encryption_key()
        decrypted_text = self._xor_decrypt(ciphertext, key)
        return json.loads(decrypted_text)

    def _compute_local_orphan_report(self, items: list[WorkstreamItem]) -> dict[str, Any]:
        local_ids = sorted(item.item_id for item in items)
        mapped_remote_ids: set[str] = set()
        for item in items:
            if item.board_id:
                mapped_remote_ids.add(item.item_id)

        mapping_path = self.config.connector_mapping_cache_path
        if mapping_path is None:
            mapping_path = Path("docs/reference/connector_mapping_cache.json")
        if mapping_path.exists():
            mapping_cache = ConnectorMappingCache(cache_file=mapping_path)
            mapped_remote_ids.update(mapping_cache.list_cached_wl_ids("github"))
            mapped_remote_ids.update(mapping_cache.list_cached_wl_ids("linear"))

        orphan_ids = sorted(set(local_ids) - mapped_remote_ids)
        return {
            "local_ids": local_ids,
            "mapped_remote_ids": sorted(mapped_remote_ids),
            "local_orphan_ids": orphan_ids,
            "orphan_count": len(orphan_ids),
        }

    def _build_remote_reflection_status_updates(
        self,
        *,
        local_items: list[WorkstreamItem],
        remote_status_updates: dict[str, str],
    ) -> dict[str, str]:
        """Apply remote archive/delete policy for local items absent in remote snapshots."""
        merged_updates = dict(remote_status_updates)
        if self.config.remote_missing_item_policy == RemoteMissingItemPolicy.IGNORE:
            return merged_updates

        local_ids = {item.item_id for item in local_items}
        remote_ids = set(remote_status_updates.keys())
        missing_ids = sorted(local_ids - remote_ids)
        if not missing_ids:
            return merged_updates

        policy_status = (
            "ARCHIVED" if self.config.remote_missing_item_policy == RemoteMissingItemPolicy.ARCHIVE else "DELETED"
        )
        for item_id in missing_ids:
            merged_updates[item_id] = policy_status
        return merged_updates

    @staticmethod
    def _classify_retry(message: str) -> RetryClass:
        lowered = message.lower()
        if "429" in lowered or "rate limit" in lowered or "quota" in lowered:
            return RetryClass.RATE_LIMIT
        if "timeout" in lowered or "temporar" in lowered or "network" in lowered or "connection reset" in lowered:
            return RetryClass.TRANSIENT
        return RetryClass.PERMANENT

    def _compute_cycle_fingerprint(self, items: list[WorkstreamItem]) -> str:
        canonical = "|".join(
            sorted(
                f"{item.item_id}:{item.status}:{item.priority}:{item.area}:{item.blocked_by or ''}" for item in items
            )
        )
        return hashlib.sha1(canonical.encode("utf-8")).hexdigest()

    def _trend_path(self) -> Path:
        return self.config.trend_file_path or Path("docs/reference/autosync_trend.jsonl")

    def _append_trend_sample(
        self,
        *,
        started_at: datetime,
        completed_at: datetime,
        item_count: int,
        no_op: bool,
        no_op_reason: str | None,
    ) -> None:
        sample = {
            "captured_at": completed_at.isoformat(),
            "duration_seconds": max(0.0, (completed_at - started_at).total_seconds()),
            "item_count": item_count,
            "failure_queue_size": len(self._failure_queue.snapshot()),
            "orphan_count": int(self._local_orphan_report.get("orphan_count", 0)),
            "no_op": no_op,
            "no_op_reason": no_op_reason,
            "correlation_id": self._current_run_correlation_id,
        }
        path = self._trend_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(sample, sort_keys=True).decode().decode() + "\n")
        self._last_trend_sample = sample

    def _record_change_event(
        self,
        *,
        connector: str,
        action: str,
        outcome: str,
        count: int,
    ) -> None:
        if count <= 0:
            return
        self._cycle_change_events.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "connector": connector,
                "action": action,
                "outcome": outcome,
                "count": count,
            }
        )

    def _refresh_change_digest(self) -> dict[str, Any]:
        self._latest_change_digest = build_hourly_change_digest(self._cycle_change_events)
        return self._latest_change_digest

    def _append_change_digest_snapshot(self) -> None:
        payload = {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "cycle_number": self.total_cycles,
            "cycle_id": self._current_run_correlation_id,
            "digest": self._refresh_change_digest(),
        }
        path = self._change_digest_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True).decode().decode() + "\n")

    def _finalize_change_digest(self) -> dict[str, Any]:
        """Finalize and persist the current cycle's digest."""
        self._refresh_change_digest()
        self._append_change_digest_snapshot()
        return self._latest_change_digest

    def _log_remote_reflection_events(
        self,
        *,
        connector: str,
        local_items: list[WorkstreamItem],
        status_updates: dict[str, str],
    ) -> None:
        if not status_updates:
            return

        local_status = {item.item_id: item.status for item in local_items}
        cycle_id = self._current_run_correlation_id or "unknown"

        for item_id, updated_status in status_updates.items():
            before_status = local_status.get(item_id, "")
            decision_type = "skip" if before_status == updated_status else "apply"
            self._reflection_event_log.log(
                ReflectionDecision(
                    wl_id=item_id,
                    decision_type=decision_type,
                    before_value=before_status,
                    after_value=updated_status,
                    connector=connector,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    cycle_id=cycle_id,
                    direction="remote_to_local",
                    mutation_id=f"{connector}:{item_id}:{cycle_id}",
                )
            )
            self._record_change_event(
                connector=connector,
                action="remote_to_local",
                outcome=decision_type,
                count=1,
            )

    def _record_local_reflection_events(self, *, connector: str, operation: SyncOperation) -> None:
        if operation.items_processed <= 0:
            return
        if operation.items_failed > 0 and operation.errors:
            self._record_change_event(
                connector=connector,
                action="local_to_remote",
                outcome="failure",
                count=operation.items_failed,
            )

        applied = max(0, operation.items_successful)
        skipped = max(0, operation.items_processed - operation.items_successful)
        if skipped > 0 and not operation.errors:
            self._record_change_event(
                connector=connector,
                action="local_to_remote",
                outcome="skip",
                count=skipped,
            )
        event_ts = (
            operation.completed_at.isoformat() if operation.completed_at else datetime.now(timezone.utc).isoformat()
        )
        cycle_id = self._current_run_correlation_id or "unknown"

        def _log_local_decision(
            *, decision_type: str, before_value: object, after_value: object, mutation_suffix: str
        ) -> None:
            self._reflection_event_log.log(
                ReflectionDecision(
                    wl_id=operation.operation_id,
                    decision_type=decision_type,
                    before_value=before_value,
                    after_value=after_value,
                    connector=connector,
                    timestamp=event_ts,
                    cycle_id=cycle_id,
                    direction="local_to_remote",
                    mutation_id=f"{connector}:{operation.operation_id}:{mutation_suffix}",
                )
            )

        if operation.items_failed > 0 and operation.errors:
            _log_local_decision(
                decision_type="failure",
                before_value=operation.items_processed,
                after_value=operation.items_successful,
                mutation_suffix="failure",
            )
            if operation.items_successful <= 0:
                return
        if skipped > 0 and not operation.errors:
            _log_local_decision(
                decision_type="skip",
                before_value=operation.items_processed,
                after_value=operation.items_processed - skipped,
                mutation_suffix="skip",
            )
        if applied > 0:
            _log_local_decision(
                decision_type="apply",
                before_value=operation.items_processed,
                after_value=applied,
                mutation_suffix="apply",
            )
            self._record_change_event(
                connector=connector,
                action="local_to_remote",
                outcome="apply",
                count=applied,
            )

    def _emit_cycle_metrics(
        self,
        *,
        started_at: datetime,
        completed_at: datetime,
        item_count: int,
        status: str,
        no_op: bool,
        no_op_reason: str | None,
    ) -> None:
        payload = {
            "captured_at": completed_at.isoformat(),
            "cycle_number": self.total_cycles,
            "status": status,
            "duration_seconds": max(0.0, (completed_at - started_at).total_seconds()),
            "item_count": item_count,
            "no_op": no_op,
            "no_op_reason": no_op_reason,
            "last_error": self.last_error,
            "failure_queue_size": len(self._failure_queue.snapshot()),
            "next_cycle_interval_seconds": self._next_cycle_interval_seconds,
            "connector_health": [probe.to_dict() for probe in self._last_connector_probe],
            "correlation_id": self._current_run_correlation_id,
        }
        path = self._cycle_metrics_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True).decode().decode() + "\n")

    def _compact_snapshots(self, status_path: Path) -> None:
        retention = max(1, int(self.config.snapshot_retention_count))
        snapshots = sorted(status_path.parent.glob("autosync_snapshot_*.json"))
        if len(snapshots) <= retention:
            return
        for snapshot in snapshots[: len(snapshots) - retention]:
            snapshot.unlink(missing_ok=True)

    @staticmethod
    def simulate_connector_chaos(
        connector: str,
        scenario: str,
        *,
        items_count: int,
    ) -> dict[str, Any]:
        """Deterministic chaos fixture for outage and partial-ack scenarios."""
        normalized = scenario.strip().lower()
        if normalized == "timeout":
            return {
                "connector": connector,
                "scenario": normalized,
                "items_attempted": items_count,
                "items_acked": 0,
                "retry_count": 3,
                "backoff_seconds": [1, 2, 4],
                "escalate": True,
                "outcome": "outage",
            }
        if normalized == "http_5xx":
            return {
                "connector": connector,
                "scenario": normalized,
                "items_attempted": items_count,
                "items_acked": 0,
                "retry_count": 2,
                "backoff_seconds": [1, 2],
                "escalate": True,
                "outcome": "server_error",
            }
        if normalized == "partial_ack":
            acked = 0 if items_count <= 1 else items_count - 1
            return {
                "connector": connector,
                "scenario": normalized,
                "items_attempted": items_count,
                "items_acked": acked,
                "retry_count": 1,
                "backoff_seconds": [1],
                "escalate": acked != items_count,
                "outcome": "partial",
            }
        raise ValueError(f"Unsupported chaos scenario: {scenario}")

    async def start(self) -> None:
        """Start the autosync cycle runner."""
        if self.is_running:
            logger.warning("Autosync already running")
            return

        if not self.config.is_valid():
            logger.warning(
                "Autosync not started: config invalid (enabled=%s, has_github=%s, has_linear=%s)",
                self.config.enabled,
                self.config.should_sync_github(),
                self.config.should_sync_linear(),
            )
            return

        self.is_running = True
        logger.info(
            "Starting workstream autosync (interval=%ds, github=%s, linear=%s)",
            self.config.cycle_interval_seconds,
            self.config.should_sync_github(),
            self.config.should_sync_linear(),
        )

        self._task = asyncio.create_task(self._run_cycle())

    async def stop(self) -> None:
        """Stop the autosync cycle runner."""
        if not self.is_running:
            return

        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                logger.debug("Autosync task cancelled during shutdown")

        logger.info("Workstream autosync stopped")

    async def _run_cycle(self) -> None:
        """Run the main sync cycle loop."""
        while self.is_running:
            try:
                await self._perform_sync_cycle()
                await asyncio.sleep(self._next_cycle_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in autosync cycle: %s", e, exc_info=True)
                await asyncio.sleep(min(self._next_cycle_interval_seconds, 60))

    def _probe_connectors(self) -> list[ConnectorHealthProbeResult]:
        """Probe connector health and return deterministic statuses."""
        probes: list[ConnectorHealthProbeResult] = []
        if self.config.should_sync_github():
            status = self.config.connector_health_states.get("github", "healthy").strip().lower()
            if status not in {"healthy", "degraded", "down"}:
                status = "healthy"
            probes.append(ConnectorHealthProbeResult(connector="github", status=status))
        if self.config.should_sync_linear():
            status = self.config.connector_health_states.get("linear", "healthy").strip().lower()
            if status not in {"healthy", "degraded", "down"}:
                status = "healthy"
            probes.append(ConnectorHealthProbeResult(connector="linear", status=status))
        return probes

    def _metadata_state(self) -> dict[str, Any]:
        """Compute metadata freshness state."""
        refreshed_at = self.config.metadata_last_refreshed_at
        if refreshed_at is None:
            return {"status": "fresh", "age_seconds": 0}
        now = datetime.now(timezone.utc)
        age_seconds = int((now - refreshed_at).total_seconds())
        stale = age_seconds > self.config.metadata_ttl_seconds
        return {
            "status": "stale" if stale else "fresh",
            "age_seconds": max(0, age_seconds),
        }

    def _build_incident_snapshot_bundle(
        self,
        *,
        items_count: int,
        metadata_state: dict[str, Any],
    ) -> dict[str, Any]:
        """Build immutable incident snapshot payload for the current cycle."""
        snapshot_age_seconds = self._latest_snapshot_age_seconds()
        snapshot_stale = (
            snapshot_age_seconds is not None and snapshot_age_seconds > self.config.autosync_stale_snapshot_seconds
        )
        slo_alerts = self._evaluate_slo_state()
        policy_hash = hashlib.sha1(
            json.dumps(
                {
                    "strict_tag_validation": self.config.strict_tag_validation,
                    "strict_title_validation": self.config.strict_title_validation,
                    "adaptive_interval_enabled": self.config.adaptive_interval_enabled,
                    "metadata_ttl_seconds": self.config.metadata_ttl_seconds,
                },
                sort_keys=True,
            ).encode("utf-8"),
        ).hexdigest()
        return {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "items_count": items_count,
            "snapshot_age_seconds": snapshot_age_seconds,
            "snapshot_stale": snapshot_stale,
            "correlation_id": self._current_run_correlation_id,
            "slo_alerts": slo_alerts,
            "error_budget": self._error_budget.get_stats(),
            "connector_sla": self._connector_sla_snapshot(),
            "policy_hash": policy_hash,
            "connector_health": [probe.to_dict() for probe in self._last_connector_probe],
            "metadata": metadata_state,
            "last_error": self.last_error,
            "failure_queue_size": len(self._failure_queue.snapshot()),
            "mutation_summary": self.last_operation.to_dict() if self.last_operation else None,
        }

    def _append_incident_snapshot(self, snapshot: dict[str, Any]) -> None:
        """Append snapshot bundle to incident artifact stream."""
        path = self.config.incident_bundle_path or Path("docs/reference/workstream_incident_snapshots.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(snapshot, sort_keys=True).decode().decode() + "\n")

    def _connector_sla_snapshot(self) -> dict[str, Any]:
        snapshot: dict[str, Any] = {}
        for connector, thresholds in sorted(self._connector_sla_thresholds.items()):
            latency_summary = self._connector_latency_tracker.summary(connector)
            error_budget = self._connector_error_budget(connector)
            if latency_summary.get("count", 0) == 0:
                snapshot[connector] = {
                    "latency": latency_summary,
                    "error_budget": error_budget.get_stats(),
                    "thresholds": {
                        "p95_latency_ms": thresholds.p95_latency_ms,
                        "max_failure_rate": thresholds.max_failure_rate,
                    },
                    "within_sla": None,
                    "breaches": [],
                }
                continue

            evaluation = self._connector_sla_evaluator.evaluate(
                connector_name=connector,
                latency_summary=latency_summary,
                error_budget_stats=error_budget.get_stats(),
                thresholds=thresholds,
            )
            snapshot[connector] = evaluation
        return snapshot

    def _finalize_incident_snapshot(self, *, items_count: int, metadata_state: dict[str, Any]) -> None:
        """Persist incident snapshot and act on SLO alerts."""
        self._latest_incident_snapshot = self._build_incident_snapshot_bundle(
            items_count=items_count,
            metadata_state=metadata_state,
        )
        self._append_incident_snapshot(self._latest_incident_snapshot)
        self._slo_alerts = list(self._latest_incident_snapshot.get("slo_alerts", []))
        for reason in self._slo_alerts:
            self._maybe_enqueue_escalation(reason)

    def _update_next_cycle_interval(self, *, items_count: int) -> None:
        """Compute and set next-cycle interval."""
        if not self.config.adaptive_interval_enabled:
            self._next_cycle_interval_seconds = self.config.cycle_interval_seconds
            return
        queue_size = len(self._failure_queue.snapshot())
        drift_rate = 1.0 if self._latest_blocker_digest else 0.0
        error_rate = 1.0 if self.last_error else 0.0
        load_factor = min(1.0, float(items_count + queue_size) / 200.0)
        self._next_cycle_interval_seconds = compute_adaptive_sync_interval(
            base_interval_seconds=self.config.cycle_interval_seconds,
            min_interval_seconds=self.config.adaptive_interval_min_seconds,
            max_interval_seconds=self.config.adaptive_interval_max_seconds,
            drift_rate=drift_rate,
            error_rate=error_rate,
            load_factor=load_factor,
        )

    async def _perform_sync_cycle(self) -> None:
        """Perform a single sync cycle."""
        cycle_started_at = datetime.now(timezone.utc)
        cycle_monotonic_started = time.perf_counter()
        no_op = False
        no_op_reason: str | None = None
        cycle_items: list[WorkstreamItem] = []
        cycle_change_digest: dict[str, Any] = {"bucket": "hourly", "hours": {}}
        self._cycle_failure_recorded = False
        writer_lock_owner: str | None = None
        writer_lock_acquired = False
        cycle_decisions: dict[str, Any] = {
            "github_enabled": self.config.should_sync_github(),
            "linear_enabled": self.config.should_sync_linear(),
            "shadow_mode": self.config.shadow_mode,
        }

        def _record_cycle_status(status: str) -> None:
            duration = time.perf_counter() - cycle_monotonic_started
            self._metrics.record_autosync_cycle_result(status=status, duration_seconds=duration)

        try:
            self._cycle_change_events = []
            if self._requires_writer_lock():
                writer_lock_owner = self._writer_lock_owner()
                if not self._writer_lock.acquire(writer_lock_owner):
                    current_owner = self._writer_lock.get_owner() or "unknown"
                    raise WorkstreamAutosyncError(
                        f"single-writer lock unavailable: held by {current_owner}",
                    )
                writer_lock_acquired = True
                cycle_decisions["writer_lock_owner"] = writer_lock_owner

            if self.config.is_emergency_stop_active():
                raise WorkstreamAutosyncConfigError(
                    "Emergency stop active; autosync external mutation is paused",
                )
            self._current_run_correlation_id = str(uuid4())
            self._no_op_summary = None

            work_stream_path = self.config.work_stream_path or Path("docs/reference/WORK_STREAM.md")
            raw_content = ""
            if work_stream_path.exists():
                raw_content = work_stream_path.read_text(encoding="utf-8")

            # Parse local items
            items = WorkstreamParser.parse_items(work_stream_path)
            ignore_set = set(self.config.normalized_wl_ignore_list)
            self._last_ignored_item_ids = sorted(item.item_id for item in items if item.item_id in ignore_set)
            if self._last_ignored_item_ids:
                items = [item for item in items if item.item_id not in ignore_set]
            self._last_scope_filtered_item_ids = sorted(
                item.item_id for item in items if not self.config.matches_scope_filters(item)
            )
            if self._last_scope_filtered_item_ids:
                items = [item for item in items if self.config.matches_scope_filters(item)]
            cycle_items = items
            self._local_orphan_report = self._compute_local_orphan_report(items)
            if not items:
                logger.debug("No work stream items to sync")
                self._clear_checkpoint()
                no_op = True
                no_op_reason = "no_workstream_items"
                self._no_op_summary = {
                    "no_op": True,
                    "reason": no_op_reason,
                    "skipped_connectors": int(self.config.should_sync_github()) + int(self.config.should_sync_linear()),
                }
                self.total_cycles += 1
                self.last_error = None
                self._error_budget.record_success()
                self._update_next_cycle_interval(items_count=0)
                self._finalize_incident_snapshot(
                    items_count=0,
                    metadata_state=self._metadata_state(),
                )
                self._metrics.record_autosync_cycle(
                    items_count=0,
                    ignored_count=len(self._last_ignored_item_ids),
                    had_error=False,
                )
                self._flush_prometheus_metrics()
                self._write_status_snapshot()
                self._append_trend_sample(
                    started_at=cycle_started_at,
                    completed_at=datetime.now(timezone.utc),
                    item_count=0,
                    no_op=no_op,
                    no_op_reason=no_op_reason,
                )
                cycle_change_digest = self._finalize_change_digest()
                self._emit_cycle_metrics(
                    started_at=cycle_started_at,
                    completed_at=datetime.now(timezone.utc),
                    item_count=0,
                    status="success",
                    no_op=no_op,
                    no_op_reason=no_op_reason,
                )
                self._append_cycle_manifest(
                    status="success",
                    started_at=cycle_started_at,
                    items=[],
                    decisions={**cycle_decisions, "reason": "no_items"},
                    outputs={"total_cycles": self.total_cycles, "change_digest": cycle_change_digest},
                )
                _record_cycle_status("success")
                return

            title_duplicates = WorkstreamParser.duplicate_titles(items)
            if title_duplicates and self.config.strict_title_validation:
                duplicates = ", ".join(title for title, _ in title_duplicates)
                raise WorkstreamDuplicateTitleError(
                    f"Duplicate workstream titles detected: {duplicates}",
                )

            _, invalid_tags = WorkstreamParser.validate_tags(
                items,
                allowed_tags=self.config.allowed_tags,
                strict=self.config.strict_tag_validation,
            )
            if invalid_tags and self.config.strict_tag_validation:
                raise WorkstreamAutosyncConfigError(
                    f"Invalid workstream tags detected: {', '.join(invalid_tags)}",
                )

            self._last_connector_probe = self._probe_connectors()
            unhealthy = [probe for probe in self._last_connector_probe if probe.status != "healthy"]
            if unhealthy:
                failed = ", ".join(f"{probe.connector}:{probe.status}" for probe in unhealthy)
                raise WorkstreamAutosyncError(f"Pre-apply connector health probe failed: {failed}")

            self.last_sync_time = datetime.now(timezone.utc)
            logger.debug("Performing sync cycle for %d items", len(items))
            self._failure_queue.prune_expired(self.last_sync_time)
            self._write_failure_queue()
            self._latest_blocker_digest = WorkstreamParser.open_blocker_digest(items)
            cycle_fingerprint = self._compute_cycle_fingerprint(items)
            if cycle_fingerprint == self._last_cycle_fingerprint:
                no_op = True
                no_op_reason = "unchanged_workstream_state"
                self._no_op_summary = {
                    "no_op": True,
                    "reason": no_op_reason,
                    "skipped_connectors": int(self.config.should_sync_github()) + int(self.config.should_sync_linear()),
                }
                self.total_cycles += 1
                self.last_error = None
                self._error_budget.record_success()
                self._update_next_cycle_interval(items_count=len(items))
                self._finalize_incident_snapshot(
                    items_count=len(items),
                    metadata_state=self._metadata_state(),
                )
                self._metrics.record_autosync_cycle(
                    items_count=len(items),
                    ignored_count=len(self._last_ignored_item_ids),
                    had_error=False,
                )
                self._flush_prometheus_metrics()
                self._write_status_snapshot()
                self._append_trend_sample(
                    started_at=cycle_started_at,
                    completed_at=datetime.now(timezone.utc),
                    item_count=len(items),
                    no_op=no_op,
                    no_op_reason=no_op_reason,
                )
                cycle_change_digest = self._finalize_change_digest()
                self._emit_cycle_metrics(
                    started_at=cycle_started_at,
                    completed_at=datetime.now(timezone.utc),
                    item_count=len(items),
                    status="success",
                    no_op=no_op,
                    no_op_reason=no_op_reason,
                )
                self._append_cycle_manifest(
                    status="success",
                    started_at=cycle_started_at,
                    items=items,
                    decisions={**cycle_decisions, "reason": no_op_reason},
                    outputs={"total_cycles": self.total_cycles, "no_op": True, "change_digest": cycle_change_digest},
                )
                _record_cycle_status("success")
                return
            cycle_decisions["open_blockers"] = list(self._latest_blocker_digest)
            metadata_state = self._metadata_state()

            updated_content = WorkstreamParser.sync_sla_annotations(raw_content, items=items)
            if updated_content != raw_content and not self.config.dry_run:
                work_stream_path.parent.mkdir(parents=True, exist_ok=True)
                work_stream_path.write_text(updated_content, encoding="utf-8")

            try:
                self._checkpoint = self._load_checkpoint()
                if self._checkpoint and self.last_sync_time - self._checkpoint.created_at > timedelta(
                    seconds=self.config.checkpoint_ttl_seconds,
                ):
                    logger.debug("Checkpoint expired; restarting from index 0")
                    self._checkpoint = None
            except (ValueError, KeyError, OSError) as exc:
                logger.debug("Checkpoint load failed, continuing without resume: %s", exc)
                self._checkpoint = None

            if self.config.simulation_mode:
                no_op_reason = "simulation_mode"
                no_op = True
                self._no_op_summary = {
                    "no_op": True,
                    "reason": "simulation_mode",
                    "skipped_connectors": int(self.config.should_sync_github()) + int(self.config.should_sync_linear()),
                }
            else:
                # Sync to GitHub if enabled
                if self.config.should_sync_github():
                    if self.config.is_maintenance_active("github", project=self.config.project_id):
                        logger.info("Skipping GitHub sync because connector is in maintenance window")
                        self._clear_checkpoint("github", "write")
                        self._clear_checkpoint("github", "read")
                    else:
                        await self._sync_in_partitions(
                            connector="github",
                            direction="write",
                            items=items,
                            sync_fn=self._sync_to_github,
                        )
                    if self.config.github_can_read():
                        await self._sync_in_partitions(
                            connector="github",
                            direction="read",
                            items=items,
                            sync_fn=lambda chunk: self._sync_from_github(chunk, work_stream_path),
                        )

                # Sync to Linear if enabled
                if self.config.should_sync_linear():
                    if self.config.is_maintenance_active("linear", project=self.config.project_id):
                        logger.info("Skipping Linear sync because connector is in maintenance window")
                        self._clear_checkpoint("linear", "write")
                        self._clear_checkpoint("linear", "read")
                    else:
                        await self._sync_in_partitions(
                            connector="linear",
                            direction="write",
                            items=items,
                            sync_fn=self._sync_to_linear,
                        )
                    if self.config.linear_can_read():
                        await self._sync_in_partitions(
                            connector="linear",
                            direction="read",
                            items=items,
                            sync_fn=lambda chunk: self._sync_from_linear(chunk, work_stream_path),
                        )

            self.total_cycles += 1
            self.last_error = None
            self._last_cycle_fingerprint = cycle_fingerprint
            if not self._cycle_failure_recorded:
                self._error_budget.record_success()
            self._update_next_cycle_interval(items_count=len(items))
            self._finalize_incident_snapshot(
                items_count=len(items),
                metadata_state=metadata_state,
            )
            self._metrics.record_autosync_cycle(
                items_count=len(items),
                ignored_count=len(self._last_ignored_item_ids),
                had_error=False,
            )
            self._flush_prometheus_metrics()
            self._write_status_snapshot()
            self._append_trend_sample(
                started_at=cycle_started_at,
                completed_at=datetime.now(timezone.utc),
                item_count=len(items),
                no_op=no_op,
                no_op_reason=no_op_reason,
            )
            cycle_change_digest = self._finalize_change_digest()
            self._emit_cycle_metrics(
                started_at=cycle_started_at,
                completed_at=datetime.now(timezone.utc),
                item_count=len(items),
                status="success",
                no_op=no_op,
                no_op_reason=no_op_reason,
            )
            self._append_cycle_manifest(
                status="success",
                started_at=cycle_started_at,
                items=items,
                decisions=cycle_decisions,
                outputs={
                    "total_cycles": self.total_cycles,
                    "last_operation": self.last_operation.to_dict() if self.last_operation else None,
                    "failure_queue_size": len(self._failure_queue.snapshot()),
                    "change_digest": cycle_change_digest,
                },
            )
            _record_cycle_status("success")

        except Exception as e:
            logger.error("Failed to perform sync cycle: %s", e, exc_info=True)
            self.total_cycles += 1
            self.last_error = str(e)
            if not self._cycle_failure_recorded:
                self._error_budget.record_failure()
                self._cycle_failure_recorded = True
            self._update_next_cycle_interval(items_count=0)
            self._finalize_incident_snapshot(
                items_count=0,
                metadata_state=self._metadata_state(),
            )
            self._metrics.record_autosync_cycle(
                items_count=0,
                ignored_count=len(self._last_ignored_item_ids),
                had_error=True,
            )
            self._flush_prometheus_metrics()
            self._write_status_snapshot()
            self._append_trend_sample(
                started_at=cycle_started_at,
                completed_at=datetime.now(timezone.utc),
                item_count=0,
                no_op=no_op,
                no_op_reason=no_op_reason,
            )
            cycle_change_digest = self._finalize_change_digest()
            self._emit_cycle_metrics(
                started_at=cycle_started_at,
                completed_at=datetime.now(timezone.utc),
                item_count=0,
                status="failed",
                no_op=no_op,
                no_op_reason=no_op_reason,
            )
            self._append_cycle_manifest(
                status="failed",
                started_at=cycle_started_at,
                items=cycle_items,
                decisions=cycle_decisions,
                outputs={
                    "total_cycles": self.total_cycles,
                    "last_error": self.last_error,
                    "change_digest": cycle_change_digest,
                },
            )
            _record_cycle_status("failed")
        finally:
            if writer_lock_acquired and writer_lock_owner:
                self._writer_lock.release(writer_lock_owner)

    def _write_status_snapshot(self) -> None:
        status_path = self.config.status_file_path or Path("docs/reference/autosync_status.json")
        payload = {
            "last_cycle_at": datetime.now(timezone.utc).isoformat(),
            "total_cycles": self.total_cycles,
            "last_error": self.last_error,
            "health": "degraded" if self.last_error else "ok",
            "runner": self.get_status(),
            "open_blockers": self._latest_blocker_digest,
            "failure_queue_size": len(self._failure_queue.snapshot()),
            "checkpoint": self._checkpoint.to_dict() if self._checkpoint else None,
            "connector_health": [probe.to_dict() for probe in self._last_connector_probe],
            "next_cycle_interval_seconds": self._next_cycle_interval_seconds,
            "incident_snapshot": self._latest_incident_snapshot,
            "correlation_id": self._current_run_correlation_id,
            "local_orphan_report": self._local_orphan_report,
            "ignored_wl_ids": self._last_ignored_item_ids,
            "scope_filtered_wl_ids": self._last_scope_filtered_item_ids,
            "no_op_summary": self._no_op_summary,
            "trend_sample": self._last_trend_sample,
            "change_digest": self._latest_change_digest,
        }
        try:
            status_path.parent.mkdir(parents=True, exist_ok=True)
            serialized = self._serialize_artifact_payload(payload)
            status_path.write_text(serialized, encoding="utf-8")
            snapshot_name = datetime.now(timezone.utc).strftime("autosync_snapshot_%Y%m%dT%H%M%S%fZ.json")
            snapshot_path = status_path.parent / snapshot_name
            snapshot_path.write_text(serialized, encoding="utf-8")
            self._compact_snapshots(status_path)
        except OSError as exc:
            logger.warning("Failed to write autosync status to %s: %s", status_path, exc)

    async def _sync_to_github(self, items: list[WorkstreamItem]) -> None:
        """Sync items to GitHub Projects.

        Args:
            items: Work stream items to sync
        """
        if not self.config.github_can_write():
            return
        self._enforce_write_guards(connector="github", items=items)

        op = SyncOperation(
            operation_id=self._build_operation_id("gh", "write", items),
            platform="github",
            direction="write",
            correlation_id=self._current_run_correlation_id,
        )

        try:
            op.items_processed = len(items)
            fallback_owner = self.config.actor_id.strip()
            enriched_items = []
            for item in items:
                metadata = enrich_sync_metadata(
                    item.to_dict(),
                    source_url=f"github://workstream/{item.item_id}",
                    source_tag="github",
                )
                owner = item.owner.strip() if item.owner else ""
                if not owner:
                    owner = fallback_owner
                if owner:
                    metadata = propagate_owner_metadata(metadata, owner=owner)
                enriched_items.append(metadata)
            if self.config.shadow_mode:
                logger.info("Shadow mode active: blocking %d GitHub mutations", len(items))
                op.items_successful = len(items)
                op.completed_at = datetime.now(timezone.utc)
                op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
                self._record_local_reflection_events(connector="github", operation=op)
                self.last_operation = op
                return
            if self._idempotency_cache.check(op.operation_id):
                op.items_successful = 0
                op.completed_at = datetime.now(timezone.utc)
                op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
                self._record_local_reflection_events(connector="github", operation=op)
                self.last_operation = op
                logger.info("Skipping replayed GitHub write operation: %s", op.operation_id)
                return

            if self.config.dry_run:
                logger.info(
                    "Dry-run: skip GitHub write sync (%d items to %s/%d)",
                    len(items),
                    self.config.github_owner,
                    self.config.effective_github_project_number(),
                )
                op.items_successful = len(items)
            else:
                gh_config = GHProjectConfig(
                    enabled=True,
                    owner=self.config.github_owner,
                    number=self.config.effective_github_project_number(),
                    direction=self.config.github_direction.value,
                    standalone_mode=self.config.standalone_mode,
                )
                result = await asyncio.to_thread(gh_sync_to_github, gh_config, enriched_items)
                created = int(result.get("items_created", 0))
                updated = int(result.get("items_updated", 0))
                op.items_successful = created + updated
                errors = result.get("errors", [])
                if isinstance(errors, list):
                    op.errors.extend(str(error) for error in errors)

                error_ids = {
                    str(error).split(":", 1)[0].strip()
                    for error in op.errors
                    if isinstance(error, str) and ":" in error
                }
                successful_items = [item for item in items if item.item_id not in error_ids]
                close_failures = 0
                if self.config.github_auto_close_issues:
                    completed_issue_refs: list[str] = []
                    for item in successful_items:
                        if item.status.upper() != "COMPLETED":
                            continue
                        completed_issue_refs.extend(
                            extract_github_issue_refs(
                                {
                                    "title": item.title,
                                    "body": item.raw_section or "",
                                }
                            )
                        )
                    if completed_issue_refs:
                        close_result = close_or_comment_github_issue_refs(
                            completed_issue_refs,
                            close_comment=self.config.github_auto_close_comment,
                        )
                        close_failures = len(close_result.get("errors", []))
                        if close_failures:
                            op.errors.extend(str(error) for error in close_result["errors"])
                for item in successful_items:
                    mutation_id = self._build_mutation_id("gh", item)
                    mutation_hash = hashlib.sha1(
                        f"{item.item_id}:{item.status}:{item.priority}:{item.area}".encode()
                    ).hexdigest()
                    if self._idempotency_cache.check_content("github", item.item_id, mutation_hash):
                        continue
                    self._idempotency_cache.record(
                        operation_id=mutation_id,
                        wl_id=item.item_id,
                        connector="github",
                        content_hash=mutation_hash,
                    )
                if successful_items:
                    self._idempotency_cache.record(
                        operation_id=op.operation_id,
                        wl_id=successful_items[0].item_id,
                        connector="github",
                        content_hash=hashlib.sha1(
                            ",".join(sorted(item.item_id for item in successful_items)).encode("utf-8")
                        ).hexdigest(),
                    )

            op.items_failed = max(0, op.items_processed - op.items_successful) + close_failures

            op.completed_at = datetime.now(timezone.utc)
            op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
            self._record_local_reflection_events(connector="github", operation=op)
            self.last_operation = op

        except (GHProjectSyncError, ValueError, TypeError) as e:
            logger.error("Failed to sync to GitHub: %s", e, exc_info=True)
            op.items_failed = max(0, op.items_processed - op.items_successful)
            op.errors.append(str(e))
            if self.config.standalone_mode:
                op.completed_at = datetime.now(timezone.utc)
                op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
                self._record_local_reflection_events(connector="github", operation=op)
                await self._record_failure(
                    connector="github",
                    direction="write",
                    item_id=op.operation_id,
                    message=str(e),
                )
                return
            raise
        except Exception as e:
            logger.error("Unexpected GitHub write sync failure: %s", e, exc_info=True)
            op.items_failed = max(0, op.items_processed - op.items_successful)
            op.errors.append(str(e))
            if self.config.standalone_mode:
                op.completed_at = datetime.now(timezone.utc)
                op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
                self._record_local_reflection_events(connector="github", operation=op)
                await self._record_failure(
                    connector="github",
                    direction="write",
                    item_id=op.operation_id,
                    message=str(e),
                )
                return
            raise

    async def _sync_from_github(self, items: list[WorkstreamItem], work_stream_path: Path) -> None:
        """Sync status updates from GitHub Projects back to local markdown.

        Args:
            items: Work stream items
            work_stream_path: Path to WORK_STREAM.md
        """
        if not self.config.github_can_read():
            return

        op = SyncOperation(
            operation_id=self._build_operation_id("gh", "read", items),
            platform="github",
            direction="read",
            correlation_id=self._current_run_correlation_id,
        )

        try:
            op.items_processed = len(items)
            local_status_by_id = {item.item_id: item.status.upper() for item in items}
            gh_status_updates: dict[str, str] = {}
            if self.config.dry_run:
                logger.info("Dry-run: skip GitHub read reflection (%d items)", len(items))
            else:
                gh_config = GHProjectConfig(
                    enabled=True,
                    owner=self.config.github_owner,
                    number=self.config.effective_github_project_number(),
                    direction=self.config.github_direction.value,
                    standalone_mode=self.config.standalone_mode,
                )
                result = await asyncio.to_thread(gh_sync_from_github, gh_config)
                remote_items = result.get("items", [])
                if self.config.payload_checksum_enforced:
                    if not isinstance(remote_items, list) or any(not isinstance(item, dict) for item in remote_items):
                        raise TypeError("Remote payload must be a list of objects for checksum verification")
                    verify_payload_checksum(
                        self._normalize_for_checksum_payload(remote_items),
                        self.config.expected_payload_checksum,
                    )
                target_ids = {item.item_id for item in items}
                remote_status_updates: dict[str, str] = {}
                close_failures = 0
                if isinstance(remote_items, list):
                    for remote_item in remote_items:
                        if not isinstance(remote_item, dict):
                            continue
                        remote_item_id = str(remote_item.get("item_id") or "").strip()
                        remote_status = str(remote_item.get("status") or "").strip().upper()
                        if remote_item_id in target_ids and remote_status:
                            remote_status_updates[remote_item_id] = remote_status
                            if remote_status == "COMPLETED" and local_status_by_id.get(remote_item_id) != "COMPLETED":
                                if self.config.github_auto_close_issues:
                                    issue_refs = extract_github_issue_refs(remote_item)
                                    if issue_refs:
                                        close_result = close_or_comment_github_issue_refs(
                                            issue_refs,
                                            close_comment=self.config.github_auto_close_comment,
                                        )
                                        close_errors = close_result.get("errors", [])
                                        if close_errors:
                                            close_failures += len(close_errors)
                                            op.errors.extend(str(error) for error in close_errors)

                gh_status_updates = self._build_remote_reflection_status_updates(
                    local_items=items,
                    remote_status_updates=remote_status_updates,
                )
                if gh_status_updates:
                    content = work_stream_path.read_text(encoding="utf-8")
                    updated_content = WorkstreamParser.sync_status_annotations(content, statuses=gh_status_updates)
                    if updated_content != content:
                        work_stream_path.write_text(updated_content, encoding="utf-8")
                op.items_successful = len(gh_status_updates)
                op.items_failed = max(0, op.items_processed - op.items_successful) + close_failures
                errors = result.get("errors", [])
                if isinstance(errors, list):
                    op.errors.extend(str(error) for error in errors)
            self._log_remote_reflection_events(
                connector="github",
                local_items=items,
                status_updates=gh_status_updates,
            )
            if self.config.standalone_mode and close_failures:
                await self._record_failure(
                    connector="github",
                    direction="read",
                    item_id=op.operation_id,
                    message="github auto-close issue update failed",
                )

            op.completed_at = datetime.now(timezone.utc)
            op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
            self.last_operation = op

        except (GHProjectSyncError, OSError, ValueError, TypeError) as e:
            logger.error("Failed to sync from GitHub: %s", e, exc_info=True)
            op.errors.append(str(e))
            if self.config.standalone_mode:
                op.completed_at = datetime.now(timezone.utc)
                op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
                await self._record_failure(
                    connector="github",
                    direction="read",
                    item_id=op.operation_id,
                    message=str(e),
                )
            if self.config.standalone_mode:
                return
            raise
        except Exception as e:
            logger.error("Unexpected GitHub read sync failure: %s", e, exc_info=True)
            op.errors.append(str(e))
            if self.config.standalone_mode:
                op.completed_at = datetime.now(timezone.utc)
                op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
                await self._record_failure(
                    connector="github",
                    direction="read",
                    item_id=op.operation_id,
                    message=str(e),
                )
            if self.config.standalone_mode:
                return
            raise

    async def _sync_to_linear(self, items: list[WorkstreamItem]) -> None:
        """Sync items to Linear.

        Args:
            items: Work stream items to sync
        """
        if not self.config.linear_can_write():
            return
        self._enforce_write_guards(connector="linear", items=items)

        op = SyncOperation(
            operation_id=self._build_operation_id("linear", "write", items),
            platform="linear",
            direction="write",
            correlation_id=self._current_run_correlation_id,
        )

        try:
            op.items_processed = len(items)
            fallback_owner = self.config.actor_id.strip()
            enriched_items = []
            for item in items:
                metadata = enrich_sync_metadata(
                    item.to_dict(),
                    source_url=f"linear://workstream/{item.item_id}",
                    source_tag="linear",
                )
                owner = item.owner.strip() if item.owner else ""
                if not owner:
                    owner = fallback_owner
                if owner:
                    metadata = propagate_owner_metadata(metadata, owner=owner)
                enriched_items.append(metadata)
            if self.config.shadow_mode:
                logger.info("Shadow mode active: blocking %d Linear mutations", len(items))
                op.items_successful = len(items)
                op.completed_at = datetime.now(timezone.utc)
                op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
                self._record_local_reflection_events(connector="linear", operation=op)
                self.last_operation = op
                return
            if self._idempotency_cache.check(op.operation_id):
                op.items_successful = 0
                op.completed_at = datetime.now(timezone.utc)
                op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
                self._record_local_reflection_events(connector="linear", operation=op)
                self.last_operation = op
                logger.info("Skipping replayed Linear write operation: %s", op.operation_id)
                return

            if self.config.dry_run:
                logger.info(
                    "Dry-run: skip Linear write sync (%d items to team %s)", len(items), self.config.linear_team_key
                )
                op.items_successful = len(items)
            else:
                linear_config = LinearGraphQLConfig(
                    api_key=self.config.linear_api_key,
                    team_key=self.config.linear_team_key,
                    timeout_seconds=self.config.linear_write_timeout_seconds,
                )
                result = await asyncio.to_thread(linear_sync_to, linear_config, enriched_items)
                created = int(result.get("items_created", 0))
                updated = int(result.get("items_updated", 0))
                op.items_successful = created + updated
                errors = result.get("errors", [])
                if isinstance(errors, list):
                    op.errors.extend(str(error) for error in errors)

                error_ids = {
                    str(error).split(":", 1)[0].strip()
                    for error in op.errors
                    if isinstance(error, str) and ":" in error
                }
                successful_items = [item for item in items if item.item_id not in error_ids]
                for item in successful_items:
                    mutation_id = self._build_mutation_id("linear", item)
                    mutation_hash = hashlib.sha1(
                        f"{item.item_id}:{item.status}:{item.priority}:{item.area}".encode()
                    ).hexdigest()
                    if self._idempotency_cache.check_content("linear", item.item_id, mutation_hash):
                        continue
                    self._idempotency_cache.record(
                        operation_id=mutation_id,
                        wl_id=item.item_id,
                        connector="linear",
                        content_hash=mutation_hash,
                    )
                if successful_items:
                    self._idempotency_cache.record(
                        operation_id=op.operation_id,
                        wl_id=successful_items[0].item_id,
                        connector="linear",
                        content_hash=hashlib.sha1(
                            ",".join(sorted(item.item_id for item in successful_items)).encode("utf-8")
                        ).hexdigest(),
                    )

            op.items_failed = max(0, op.items_processed - op.items_successful)

            op.completed_at = datetime.now(timezone.utc)
            op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
            self._record_local_reflection_events(connector="linear", operation=op)
            self.last_operation = op

        except (LinearGraphQLAuthError, LinearGraphQLError, ValueError, TypeError) as e:
            logger.error("Failed to sync to Linear: %s", e, exc_info=True)
            op.items_failed = max(0, op.items_processed - op.items_successful)
            op.errors.append(str(e))
            if self.config.standalone_mode:
                op.completed_at = datetime.now(timezone.utc)
                op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
                self._record_local_reflection_events(connector="linear", operation=op)
                return
            raise
        except Exception as e:
            logger.error("Unexpected Linear write sync failure: %s", e, exc_info=True)
            op.items_failed = max(0, op.items_processed - op.items_successful)
            op.errors.append(str(e))
            if self.config.standalone_mode:
                op.completed_at = datetime.now(timezone.utc)
                op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
                self._record_local_reflection_events(connector="linear", operation=op)
                return
            raise

    async def _sync_from_linear(self, items: list[WorkstreamItem], work_stream_path: Path) -> None:
        """Sync status updates from Linear back to local markdown.

        Args:
            items: Work stream items
            work_stream_path: Path to WORK_STREAM.md
        """
        if not self.config.linear_can_read():
            return

        op = SyncOperation(
            operation_id=self._build_operation_id("linear", "read", items),
            platform="linear",
            direction="read",
            correlation_id=self._current_run_correlation_id,
        )

        try:
            op.items_processed = len(items)
            linear_status_updates: dict[str, str] = {}
            if self.config.dry_run:
                logger.info("Dry-run: skip Linear read reflection (%d items)", len(items))
            else:
                linear_config = LinearGraphQLConfig(
                    api_key=self.config.linear_api_key,
                    team_key=self.config.linear_team_key,
                    timeout_seconds=self.config.linear_read_timeout_seconds,
                )
                result = await asyncio.to_thread(linear_sync_from, linear_config)
                remote_items = result.get("items", [])
                if self.config.payload_checksum_enforced:
                    if not isinstance(remote_items, list) or any(not isinstance(item, dict) for item in remote_items):
                        raise TypeError("Remote payload must be a list of objects for checksum verification")
                    verify_payload_checksum(
                        self._normalize_for_checksum_payload(remote_items),
                        self.config.expected_payload_checksum,
                    )
                target_ids = {item.item_id for item in items}
                remote_status_updates: dict[str, str] = {}
                if isinstance(remote_items, list):
                    for remote_item in remote_items:
                        if not isinstance(remote_item, dict):
                            continue
                        remote_item_id = str(remote_item.get("item_id") or "").strip()
                        remote_status = str(remote_item.get("status") or "").strip().upper()
                        if remote_item_id in target_ids and remote_status:
                            remote_status_updates[remote_item_id] = remote_status

                linear_status_updates = self._build_remote_reflection_status_updates(
                    local_items=items,
                    remote_status_updates=remote_status_updates,
                )
                if linear_status_updates:
                    content = work_stream_path.read_text(encoding="utf-8")
                    updated_content = WorkstreamParser.sync_status_annotations(
                        content,
                        statuses=linear_status_updates,
                    )
                    if updated_content != content:
                        work_stream_path.write_text(updated_content, encoding="utf-8")
                op.items_successful = len(linear_status_updates)
                errors = result.get("errors", [])
                if isinstance(errors, list):
                    op.errors.extend(str(error) for error in errors)
            self._log_remote_reflection_events(
                connector="linear",
                local_items=items,
                status_updates=linear_status_updates,
            )
            op.items_failed = max(0, op.items_processed - op.items_successful)

            op.completed_at = datetime.now(timezone.utc)
            op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
            self.last_operation = op

        except (LinearGraphQLAuthError, LinearGraphQLError, OSError, ValueError, TypeError) as e:
            logger.error("Failed to sync from Linear: %s", e, exc_info=True)
            op.errors.append(str(e))
            if self.config.standalone_mode:
                return
            raise
        except Exception as e:
            logger.error("Unexpected Linear read sync failure: %s", e, exc_info=True)
            op.errors.append(str(e))
            if self.config.standalone_mode:
                return
            raise

    async def _sync_in_partitions(
        self,
        *,
        connector: str,
        direction: str,
        items: list[WorkstreamItem],
        sync_fn,
    ) -> None:
        """Run a sync function over dynamic partitions with checkpoint resume."""
        breaker = self._connector_breaker(connector)
        timeout_seconds = self._connector_timeout_seconds(connector, direction)
        partitions = WorkstreamParser.split_items(items, self.config.effective_partition_size)
        start_index = self._checkpoint_start(connector, direction, len(partitions))

        if start_index >= len(partitions):
            self._clear_checkpoint(connector, direction)
            return

        for partition_index in range(start_index, len(partitions)):
            logger.debug("Running %s/%s partition %d/%d", connector, direction, partition_index + 1, len(partitions))
            self._checkpoint = SyncCheckpoint(
                connector=connector,
                direction=direction,
                start_index=partition_index,
                total_partitions=len(partitions),
                partition_size=self.config.effective_partition_size,
                created_at=datetime.now(timezone.utc),
            )
            self._write_checkpoint()
            partition_attempt = 0
            while True:
                try:
                    partition = partitions[partition_index]
                    started_at = time.monotonic()

                    async def _run_partition_sync(partition_items: list[WorkstreamItem] = partition) -> None:
                        await asyncio.wait_for(sync_fn(partition_items), timeout=timeout_seconds)

                    try:
                        await breaker.call_async(_run_partition_sync)
                    except asyncio.TimeoutError as exc:
                        duration_seconds = max(0.0, time.monotonic() - started_at)
                        self._record_connector_latency(connector, duration_seconds=duration_seconds)
                        self._metrics.record_autosync_connector_operation(
                            connector=connector,
                            direction=direction,
                            result="timeout",
                            duration_seconds=duration_seconds,
                        )
                        self._metrics.set_circuit_breaker(connector, breaker.state == "open")
                        raise WorkstreamAutosyncError(
                            f"{connector}/{direction} timed out after {timeout_seconds:.3f}s",
                        ) from exc
                    except CircuitOpenError as exc:
                        duration_seconds = max(0.0, time.monotonic() - started_at)
                        self._record_connector_latency(connector, duration_seconds=duration_seconds)
                        self._metrics.record_autosync_circuit_open(connector=connector, direction=direction)
                        self._metrics.record_autosync_connector_operation(
                            connector=connector,
                            direction=direction,
                            result="circuit_open",
                            duration_seconds=duration_seconds,
                        )
                        self._metrics.set_circuit_breaker(connector, True)
                        raise WorkstreamAutosyncError(
                            f"{connector}/{direction} blocked by open connector circuit breaker",
                        ) from exc
                    except Exception:
                        duration_seconds = max(0.0, time.monotonic() - started_at)
                        self._record_connector_latency(connector, duration_seconds=duration_seconds)
                        self._metrics.record_autosync_connector_operation(
                            connector=connector,
                            direction=direction,
                            result="error",
                            duration_seconds=duration_seconds,
                        )
                        self._metrics.set_circuit_breaker(connector, breaker.state == "open")
                        raise
                    else:
                        duration_seconds = max(0.0, time.monotonic() - started_at)
                        self._record_connector_latency(connector, duration_seconds=duration_seconds)
                        self._connector_error_budget(connector).record_success()
                        self._metrics.record_autosync_connector_operation(
                            connector=connector,
                            direction=direction,
                            result="success",
                            duration_seconds=duration_seconds,
                        )
                        self._metrics.set_circuit_breaker(connector, breaker.state == "open")
                        break
                except Exception as exc:
                    retry_class = await self._record_failure(
                        connector=connector,
                        direction=direction,
                        item_id=f"partition:{partition_index}",
                        message=str(exc),
                    )
                    self._checkpoint = SyncCheckpoint(
                        connector=connector,
                        direction=direction,
                        start_index=partition_index,
                        total_partitions=len(partitions),
                        partition_size=self.config.effective_partition_size,
                        created_at=datetime.now(timezone.utc),
                    )
                    self._write_checkpoint()
                    if not self.config.standalone_mode:
                        raise
                    if retry_class == RetryClass.PERMANENT:
                        self._clear_checkpoint(connector, direction)
                        return

                    partition_attempt += 1
                    if partition_attempt > self._rate_limit_backoff.config.max_retries:
                        logger.error(
                            "Partition sync exhausted retries for connector=%s direction=%s partition=%d: %s",
                            connector,
                            direction,
                            partition_index,
                            exc,
                        )
                        return

                    backoff_seconds = self._rate_limit_backoff.compute_wait(partition_attempt)
                    logger.warning(
                        "Retrying %s/%s partition=%d attempt=%d/%d in %.3fs after %s",
                        connector,
                        direction,
                        partition_index,
                        partition_attempt,
                        self._rate_limit_backoff.config.max_retries,
                        backoff_seconds,
                        retry_class.value,
                    )
                    await asyncio.sleep(backoff_seconds)

            self._checkpoint = SyncCheckpoint(
                connector=connector,
                direction=direction,
                start_index=partition_index + 1,
                total_partitions=len(partitions),
                partition_size=self.config.effective_partition_size,
                created_at=datetime.now(timezone.utc),
            )
            self._write_checkpoint()

        self._clear_checkpoint(connector, direction)

    def _failure_queue_path(self) -> Path:
        """Get failure queue persistence path."""
        default_failure_queue_path = Path("docs/reference/workstream_autosync_failures.json")
        return self.config.failure_queue_path or default_failure_queue_path

    def _load_failure_queue(self) -> None:
        """Load persisted failure queue entries."""
        path = self._failure_queue_path()
        if not path.exists():
            return
        try:
            payload = self._deserialize_artifact_payload(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        if not isinstance(payload, list):
            return

        entries: list[FailureRecord] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            try:
                occurred_at = item["occurred_at"]
                occurred_at_dt = (
                    datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
                    if isinstance(occurred_at, str)
                    else occurred_at
                )
                entries.append(
                    FailureRecord(
                        operation_id=item["operation_id"],
                        connector=item["connector"],
                        item_id=item["item_id"],
                        message=item["message"],
                        occurred_at=occurred_at_dt,
                        retry_class=str(item.get("retry_class", RetryClass.PERMANENT.value)),
                        correlation_id=(
                            str(item["correlation_id"]) if item.get("correlation_id") is not None else None
                        ),
                    ),
                )
            except (KeyError, ValueError, TypeError):
                logger.debug("Skipping malformed failure queue entry: %s", item)
                continue

        self._failure_queue = SyncFailureQueue(
            retention_seconds=self.config.failure_queue_retention_seconds,
        )
        self._failure_queue.replace_records(entries)

    def _write_failure_queue(self) -> None:
        """Persist failure queue state."""
        path = self._failure_queue_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._serialize_artifact_payload(self._failure_queue.to_dict_list()), encoding="utf-8")

    def _checkpoint_start(self, connector: str, direction: str, partition_count: int) -> int:
        """Compute start partition index for resume."""
        if not self._checkpoint:
            return 0
        if (
            self._checkpoint.connector == connector
            and self._checkpoint.direction == direction
            and self._checkpoint.total_partitions == partition_count
            and self._checkpoint.partition_size == self.config.effective_partition_size
        ):
            return min(self._checkpoint.start_index, partition_count)
        return 0

    def _checkpoint_path(self) -> Path:
        """Get checkpoint persistence path."""
        default_checkpoint_path = Path("docs/reference/workstream_autosync_checkpoint.json")
        return self.config.checkpoint_file_path or default_checkpoint_path

    def _checkpoint_key(self) -> Path:
        """Compatibility alias for checkpoint naming."""
        return self._checkpoint_path()

    def _load_checkpoint(self) -> SyncCheckpoint | None:
        """Load checkpoint from disk."""
        path = self._checkpoint_path()
        if not path.exists():
            return None

        payload = self._deserialize_artifact_payload(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Checkpoint payload must be an object.")
        return SyncCheckpoint.from_dict(payload)

    def _write_checkpoint(self) -> None:
        """Persist current checkpoint state."""
        if not self._checkpoint:
            return
        path = self._checkpoint_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._serialize_artifact_payload(self._checkpoint.to_dict()), encoding="utf-8")

    def _clear_checkpoint(self, connector: str | None = None, direction: str | None = None) -> None:
        """Clear checkpoint state for requested scope."""
        if connector is None or direction is None:
            self._checkpoint = None
            path = self._checkpoint_path()
            if path.exists():
                path.unlink()
            return

        if self._checkpoint and self._checkpoint.connector == connector and self._checkpoint.direction == direction:
            self._checkpoint = None
            path = self._checkpoint_path()
            if path.exists():
                path.unlink()

    async def _record_failure(
        self,
        *,
        connector: str,
        direction: str,
        item_id: str,
        message: str,
    ) -> RetryClass:
        """Record a failure and prune stale entries."""
        digest = hashlib.sha1(f"{connector}:{direction}:{item_id}:{message}".encode()).hexdigest()[:12]
        operation_id = f"{connector}-{direction}-{item_id}-{digest}"
        retry_class = self._classify_retry(message)
        self._error_budget.record_failure()
        self._connector_error_budget(connector).record_failure()
        self._cycle_failure_recorded = True
        self._failure_queue.push(
            operation_id=operation_id,
            connector=connector,
            item_id=item_id,
            message=message,
            retry_class=retry_class,
            correlation_id=self._current_run_correlation_id,
        )
        self._write_failure_queue()
        self.last_error = message
        return retry_class

    def get_status(self) -> dict[str, Any]:
        """Get current autosync status.

        Returns:
            Status dictionary
        """
        return {
            "enabled": self.config.enabled,
            "is_running": self.is_running,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "github_enabled": self.config.should_sync_github(),
            "linear_enabled": self.config.should_sync_linear(),
            "last_operation": self.last_operation.to_dict() if self.last_operation else None,
            "open_blockers": self._latest_blocker_digest,
            "failure_queue_size": len(self._failure_queue.snapshot()),
            "next_cycle_interval_seconds": self._next_cycle_interval_seconds,
            "connector_health": [probe.to_dict() for probe in self._last_connector_probe],
            "metadata": self._metadata_state(),
            "correlation_id": self._current_run_correlation_id,
            "local_orphan_report": self._local_orphan_report,
            "ignored_wl_ids": self._last_ignored_item_ids,
            "scope_filtered_wl_ids": self._last_scope_filtered_item_ids,
            "no_op_summary": self._no_op_summary,
            "trend_sample": self._last_trend_sample,
        }


# ---------------------------------------------------------------------------
