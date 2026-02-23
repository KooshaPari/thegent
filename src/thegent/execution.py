"""Execution run metadata and registry for thegent orchestration."""

import contextlib
import hashlib
import json
import logging
import os
import socket
import time
import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field, ValidationError

from thegent.config import ThegentSettings
from thegent.execution_coercion_helpers import as_bool as _as_bool_impl
from thegent.execution_coercion_helpers import as_float as _as_float_impl
from thegent.execution_coercion_helpers import as_int as _as_int_impl
from thegent.execution_event_builders import (
    build_feedback_event,
    build_finish_event,
    build_pause_event,
    build_resume_event,
    build_schema_marker_event,
)
from thegent.execution_hash_helpers import calculate_stable_record_hash
from thegent.execution_jsonl_parsers import parse_checkpoint_by_id as _parse_checkpoint_by_id_impl
from thegent.execution_jsonl_parsers import parse_checkpoint_line as _parse_checkpoint_line_impl
from thegent.execution_jsonl_parsers import parse_circuit_failure as _parse_circuit_failure_impl
from thegent.execution_jsonl_parsers import parse_dlq_item as _parse_dlq_item_impl
from thegent.execution_jsonl_parsers import parse_fatigue_line as _parse_fatigue_line_impl
from thegent.execution_jsonl_parsers import parse_override_unexpired as _parse_override_unexpired_impl
from thegent.execution_jsonl_parsers import process_dlq_line as _process_dlq_line_impl
from thegent.execution_run_scan_helpers import check_session_id as _check_session_id_impl
from thegent.execution_run_scan_helpers import extract_domain_tag as _extract_domain_tag_impl
from thegent.execution_run_scan_helpers import extract_run_id as _extract_run_id_impl
from thegent.execution_run_scan_helpers import extract_session_id as _extract_session_id_impl
from thegent.execution_run_scan_helpers import filter_expired_record as _filter_expired_record_impl
from thegent.execution_run_scan_helpers import process_calibration_entry as _process_calibration_entry_impl
from thegent.execution_run_scan_helpers import process_run_entry as _process_run_entry_impl
from thegent.execution_run_scan_helpers import process_token_match as _process_token_match_impl
from thegent.execution_run_scan_helpers import update_run_state as _update_run_state_impl

_log = logging.getLogger(__name__)
_EXECUTION_WARNING_LIMIT = 3
_execution_warning_count = 0
_admission_import_warning_once: set[str] = set()
_execution_diagnostics: dict[str, Any] = {
    "optional_gate_import_failures": 0,
    "optional_gate_last_error_type": None,
    "optional_gate_last_error_message": None,
    "deadline_unregister": {
        "import_failures": 0,
        "runtime_failures": 0,
        "last_error_type": None,
        "last_error_message": None,
    },
    "message_parse": {
        "invalid_rows": 0,
        "non_pending_rows": 0,
        "last_error_type": None,
        "last_error_message": None,
    },
}


def _warn_bounded(message: str, *args: object) -> None:
    global _execution_warning_count
    _execution_warning_count += 1
    if _execution_warning_count <= _EXECUTION_WARNING_LIMIT:
        _log.warning(message, *args)


def get_execution_diagnostics() -> dict[str, Any]:
    """Return diagnostics snapshot for execution-path degradation."""
    return {
        "optional_gate_import_failures": _execution_diagnostics["optional_gate_import_failures"],
        "optional_gate_last_error_type": _execution_diagnostics["optional_gate_last_error_type"],
        "optional_gate_last_error_message": _execution_diagnostics["optional_gate_last_error_message"],
        "deadline_unregister": dict(_execution_diagnostics["deadline_unregister"]),
        "message_parse": dict(_execution_diagnostics["message_parse"]),
    }


def reset_execution_diagnostics() -> None:
    """Reset execution diagnostics (test helper)."""
    global _execution_warning_count
    _execution_warning_count = 0
    _admission_import_warning_once.clear()
    _execution_diagnostics["optional_gate_import_failures"] = 0
    _execution_diagnostics["optional_gate_last_error_type"] = None
    _execution_diagnostics["optional_gate_last_error_message"] = None
    _execution_diagnostics["deadline_unregister"] = {
        "import_failures": 0,
        "runtime_failures": 0,
        "last_error_type": None,
        "last_error_message": None,
    }
    _execution_diagnostics["message_parse"] = {
        "invalid_rows": 0,
        "non_pending_rows": 0,
        "last_error_type": None,
        "last_error_message": None,
    }


def _as_float(value: Any, default: float) -> float:
    """Coerce arbitrary values to float with a safe default."""
    return _as_float_impl(value, default)


def _as_int(value: Any, default: int) -> int:
    """Coerce arbitrary values to int with a safe default."""
    return _as_int_impl(value, default)


def _as_bool(value: Any, default: bool) -> bool:
    """Coerce arbitrary values to bool with a safe default."""
    return _as_bool_impl(value, default)


class RunState(StrEnum):
    """Run lifecycle state for state-aware orchestration (G-KD-03)."""

    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class MAIFArtifact(BaseModel):
    """WP-3002: Model AI Information Format (MAIF) for signed artifacts."""

    version: str = "1.0"
    run_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    agent: str
    model: str | None = None
    prompt_hash: str
    output_hash: str | None = None
    signature: str
    policy_result: str | None = None


class IdempotencyManager:
    """WP-1003: Ensures idempotent execution using 4-tuple keys."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir

    def generate_key(self, run_id: str, step_index: int, action_type: str, content: str) -> str:
        """Generate a 4-tuple idempotency key (run_id, step, action, hash)."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"{run_id}:{step_index}:{action_type}:{content_hash}"

    def check_and_record(self, registry: "RunRegistry", key: str) -> bool:
        """Check if key exists in registry; return True if already executed."""
        run = registry.find_by_token(key)
        return run is not None and run.get("status") == "completed"


class ContinuityPacket(BaseModel):
    """Compressed essence of session progress for cross-session handoffs (L3/L4).

    # @trace FR-HAX-004
    """

    intent: str
    """High-level goal of the session."""

    decisions: list[str] = Field(default_factory=list)
    """Key decisions made during the session."""

    risks: list[str] = Field(default_factory=list)
    """Identified risks or blockers."""

    context_hashes: dict[str, str] = Field(default_factory=dict)
    """SHA-256 hashes of referenced context files keyed by path string."""

    token_count: int = 0
    """Approximate token count (rough estimate)."""

    session_id: str = Field(default_factory=lambda: "")
    """Session ID this packet belongs to."""

    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    """ISO-8601 timestamp when the packet was created."""


class ConcurrencyController:
    """WP-5001: Advanced resource-based adaptive concurrency controller.

    Features:
    - Extended resource indices (CPU, memory, FD, network, disk, GPU, etc.)
    - Prediction engine for forecasting resource needs
    - Harness card modeling (codex/claude/droid usage profiles)
    - Bottleneck detection and analysis
    - Speculative execution strategies
    - Work chunking and parallelization
    - Per-owner usage tracking for fairness enforcement (swarm-usage-tracking)
    """

    def __init__(
        self,
        session_dir: Path,
        max_concurrency: int = 5,
        use_load_based: bool = True,
        critical_lane_slots: int | None = None,
    ) -> None:
        self.session_dir = session_dir
        self.max_concurrency = max_concurrency  # Fallback if load-based disabled
        self.use_load_based = use_load_based
        self.lock_file = session_dir / "concurrency.lock"
        # Critical lane reservation: slots kept exclusively for critical-priority runs.
        # Standard runs are limited to slots 0..(max_slots - critical_lane_slots - 1).
        # Resolved from: explicit arg → settings.critical_lane_slots → default 2.
        if critical_lane_slots is not None:
            self.critical_lane_slots = max(0, critical_lane_slots)
        else:
            try:
                settings = ThegentSettings()
                configured_slots = settings.critical_lane_slots
            except Exception:
                configured_slots = _as_int(os.environ.get("THGENT_CRITICAL_LANE_SLOTS"), 2)
            self.critical_lane_slots = max(0, configured_slots if configured_slots is not None else 2)

        # Per-owner usage tracker (module-level singleton, shared across instances).
        from thegent.orchestration.resource.load_based_limits import get_usage_tracker

        self._usage_tracker = get_usage_tracker()

        # Initialize advanced features (if available)
        if use_load_based:
            try:
                from thegent.orchestration.resource.resource_management import (
                    BottleneckDetector,
                    ResourcePredictionEngine,
                    create_harness_cards,
                )

                self.prediction_engine = ResourcePredictionEngine(session_dir / "resource_history.jsonl")
                self.bottleneck_detector = BottleneckDetector()
                self.harness_cards = create_harness_cards()
            except ImportError:
                # Advanced features not available, use basic resource-based limits
                self.prediction_engine = None
                self.bottleneck_detector = None
                self.harness_cards = None

    def acquire(
        self,
        lane: str = "standard",
        harness_type: str | None = None,
        priority: str = "standard",
        owner: str = "unknown",
        run_id: str = "",
        soft_deadline_s: float | None = None,
        warn_at_pct: float = 0.8,
        speculative: bool = False,
    ) -> bool:
        """Acquire a concurrency slot using advanced resource-based limits.

        Uses:
        - Extended resource monitoring (CPU, memory, FD, network, disk, etc.)
        - Prediction engine for forecasting
        - Harness card modeling for harness-specific limits
        - Bottleneck detection
        - 5% minimum buffer (hard limit, prevents crashes)
        - 15% discretionary buffer (soft limit, allows scaling)
        - Critical lane reservation: standard runs are blocked from the top
          ``critical_lane_slots`` slots so that critical runs always find room.
        - Per-owner usage tracking: records start when admitted.
        - Soft deadline monitoring: registers a preferred completion time with
          the :class:`DeadlineMonitor` when ``soft_deadline_s`` is provided.
          Past-deadline runs are logged but never cancelled.

        Args:
            lane: Lane name (``"standard"``, ``"critical"``, etc.).
            harness_type: Optional harness type for capacity modeling.
            priority: ``"critical"`` or ``"standard"`` (default).  A run is
                treated as critical when ``priority="critical"`` OR when
                ``lane="critical"``.  Critical runs may use all available
                slots; standard runs are limited to
                ``effective_limit - critical_lane_slots``.
            owner: Identifier for the owning agent/user/project (for fairness tracking).
            run_id: Unique run identifier (for tracing in usage logs).
            soft_deadline_s: Optional preferred completion budget in seconds.
                When provided and the run is admitted, a soft deadline is
                registered with the module-level :class:`DeadlineMonitor`.
                Violations emit WARNING (at ``warn_at_pct * soft_deadline_s``)
                and ERROR (at ``soft_deadline_s``) but do NOT cancel the run.
            warn_at_pct: Fraction of ``soft_deadline_s`` at which to warn
                (default 0.8 → 80 %).  Only used when ``soft_deadline_s`` is set.
        """
        is_critical = priority == "critical" or (lane or "").lower() == "critical"
        from thegent.cli.commands.impl import ps_impl
        from thegent.config import ThegentSettings

        sessions = ps_impl(all=True)
        running_count = sum(1 for s in sessions if s.get("status") == "running")

        # Use resource-based limits if enabled (default)
        settings = ThegentSettings()
        if self.use_load_based and (True):  # Default to True
            from thegent.orchestration.resource.load_based_limits import (
                LimitGateConfig,
                compute_dynamic_limit,
                sample_resources,
            )

            # Sample current resources
            snapshot = sample_resources()

            # Compute base dynamic limit (uses 5% min buffer, 15% discretionary buffer)
            config = LimitGateConfig.from_dict(settings.model_dump())
            effective_limit, details = compute_dynamic_limit(snapshot, config)

            # Log per-gate details (swarm-per-gate-logging)
            gate_values = {
                "cpu": details.get("cpu_slots", 999),
                "fd": details.get("fd_slots", 999),
                "mem": details.get("mem_slots", 999),
                "load": details.get("load_slots", 999),
            }
            limiting_gate = min(gate_values, key=lambda k: gate_values[k])
            _log.info(
                f"concurrency admission: effective_limit={effective_limit} "
                f"limiting_gate={limiting_gate} details={gate_values} "
                f"running={running_count} run_id={run_id}"
            )

            # Advanced features (if available)
            try:
                from thegent.orchestration.resource.resource_management import sample_extended_resources

                extended_snapshot = sample_extended_resources()

                # Record for prediction engine
                if self.prediction_engine:
                    self.prediction_engine.record(extended_snapshot)

                    # WP-5001: Predictive Throttling for Speculative Runs
                    if speculative and self.prediction_engine.should_throttle_speculative():
                        _log.info(f"gate blocked: gate=speculative_throttle value=1.0 limit=0.0 run_id={run_id}")
                        return False
                    _log.info(f"gate passed: gate=speculative_throttle run_id={run_id}")

                # Apply harness card modeling if harness type specified
                if harness_type and self.harness_cards:
                    card = self.harness_cards.get(harness_type)
                    if card:
                        # Estimate resources for current + 1 session (use p95 for conservative planning)
                        estimated = card.estimate_resources(running_count + 1, isolated=False, use_p95=True)
                        # Extract p95 memory estimate (or fallback to avg)
                        mem_estimate = estimated["memory_mb"].get("p95", estimated["memory_mb"].get("avg", 0))
                        # Adjust limit based on harness capacity
                        harness_limit = int((snapshot.mem_available_mb - mem_estimate) / config.mem_mb_per_slot)
                        old_limit = effective_limit
                        effective_limit = min(effective_limit, max(1, harness_limit))
                        if effective_limit < old_limit:
                            _log.info(
                                f"gate passed: gate=harness_card type={harness_type} limit={effective_limit} (reduced from {old_limit}) run_id={run_id}"
                            )
                        else:
                            _log.info(
                                f"gate passed: gate=harness_card type={harness_type} limit={effective_limit} run_id={run_id}"
                            )

                # Apply prediction adjustments
                if self.prediction_engine:
                    prediction = self.prediction_engine.predict_next_interval(60)
                    if prediction.get("confidence", 0) > 0.5:
                        # Adjust based on predicted trends
                        pred_mem = prediction.get("prediction", {}).get("mem_rss_mb", {})
                        if pred_mem and pred_mem.get("trend", 0) > 0:
                            # Memory trending up, reduce limit slightly
                            old_limit = effective_limit
                            effective_limit = int(effective_limit * 0.95)
                            _log.info(
                                f"gate passed: gate=prediction trend=up limit={effective_limit} (reduced from {old_limit}) run_id={run_id}"
                            )

                # Check for bottlenecks
                if self.bottleneck_detector:
                    contentions = self.bottleneck_detector.detect_resource_contention(
                        extended_snapshot, self.harness_cards or {}
                    )
                    if contentions:
                        # Reduce limit if resource contention detected
                        high_severity = sum(1 for c in contentions if c.get("severity") == "high")
                        if high_severity > 0:
                            old_limit = effective_limit
                            effective_limit = int(effective_limit * 0.9)
                            _log.info(
                                f"gate passed: gate=bottleneck severity=high limit={effective_limit} (reduced from {old_limit}) run_id={run_id}"
                            )
            except ImportError as exc:
                # Advanced features not available, use basic resource-based limits.
                mod = "thegent.orchestration.resource.resource_management"
                _execution_diagnostics["optional_gate_import_failures"] = (
                    int(_execution_diagnostics["optional_gate_import_failures"]) + 1
                )
                _execution_diagnostics["optional_gate_last_error_type"] = type(exc).__name__
                _execution_diagnostics["optional_gate_last_error_message"] = str(exc)
                if mod not in _admission_import_warning_once:
                    _admission_import_warning_once.add(mod)
                    _warn_bounded(
                        "Concurrency admission degraded: optional module %s unavailable; advanced gates skipped",
                        mod,
                    )

            # Apply critical lane reservation (swarm-critical-lane).
            # Critical runs can use all slots (no cap adjustment).
            # Standard runs are capped at effective_limit - critical_lane_slots
            # to keep dedicated headroom available for critical runs.
            old_limit = effective_limit
            slot_limit = effective_limit if is_critical else max(1, effective_limit - self.critical_lane_slots)
            if not is_critical and self.critical_lane_slots > 0:
                _log.info(
                    f"gate passed: gate=critical_lane_reservation slots={self.critical_lane_slots} "
                    f"limit={slot_limit} (reduced from {old_limit}) run_id={run_id}"
                )
            else:
                _log.debug(
                    f"gate passed: gate=critical_lane_reservation is_critical={is_critical} limit={slot_limit} run_id={run_id}"
                )

            admitted = running_count < slot_limit
            _log.info(
                "gate %s: gate=slots value=%d limit=%d run_id=%s lane=%s",
                "passed" if admitted else "blocked",
                running_count,
                slot_limit,
                run_id,
                lane,
            )
            if admitted:
                _log.info("run admitted: slots=%d/%d run_id=%s owner=%s", running_count, slot_limit, run_id, owner)
                self._usage_tracker.record_start(owner, run_id)
                if soft_deadline_s is not None and soft_deadline_s > 0:
                    from thegent.orchestration.resource.load_based_limits import get_deadline_monitor

                    get_deadline_monitor().register(
                        run_id=run_id or owner,
                        deadline_ts=soft_deadline_s,
                        warn_at_pct=warn_at_pct,
                    )
            else:
                _log.warning(
                    "run blocked: reason=slots count=%d limit=%d run_id=%s owner=%s",
                    running_count,
                    slot_limit,
                    run_id,
                    owner,
                )
            return admitted

        # Fallback to fixed limit (if load-based disabled).
        # Apply the same critical lane reservation against max_concurrency.
        old_limit = self.max_concurrency
        slot_limit = self.max_concurrency if is_critical else max(1, self.max_concurrency - self.critical_lane_slots)
        if not is_critical and self.critical_lane_slots > 0:
            _log.debug(
                f"gate passed: gate=critical_lane_reservation slots={self.critical_lane_slots} limit={slot_limit} (reduced from {old_limit})"
            )

        admitted = running_count < slot_limit
        _log.debug(
            "gate %s: gate=slots value=%.2f limit=%.2f",
            "passed" if admitted else "blocked",
            float(running_count),
            float(slot_limit),
        )
        if admitted:
            _log.info("run admitted: slots=%d/%d run_id=%s owner=%s (fixed)", running_count, slot_limit, run_id, owner)
            self._usage_tracker.record_start(owner, run_id)
            if soft_deadline_s is not None and soft_deadline_s > 0:
                from thegent.orchestration.resource.load_based_limits import get_deadline_monitor

                get_deadline_monitor().register(
                    run_id=run_id or owner,
                    deadline_ts=soft_deadline_s,
                    warn_at_pct=warn_at_pct,
                )
        else:
            _log.warning(
                "run blocked: reason=slots count=%d limit=%d run_id=%s owner=%s (fixed)",
                running_count,
                slot_limit,
                run_id,
                owner,
            )
        return admitted

    def release(self, owner: str = "unknown", run_id: str = "", elapsed_ms: float = 0.0) -> None:
        """Record the completion of a run for per-owner usage tracking.

        Also unregisters any soft deadline that was associated with this run so
        that the :class:`DeadlineMonitor` stops checking it.

        Call this after a run finishes (succeeded or failed) to decrement the
        owner's active count and accumulate elapsed time statistics.

        Args:
            owner:      Identifier used in the corresponding :meth:`acquire` call.
            run_id:     Run identifier used in the corresponding :meth:`acquire` call.
            elapsed_ms: Wall-clock duration of the run in milliseconds.
        """
        self._usage_tracker.record_end(owner, run_id, elapsed_ms)
        # Unregister any soft deadline for this run (no-op if none registered).
        try:
            from thegent.orchestration.resource.load_based_limits import get_deadline_monitor

            get_deadline_monitor().unregister(run_id or owner)
        except ImportError as exc:
            deadline = _execution_diagnostics["deadline_unregister"]
            deadline["import_failures"] = int(deadline["import_failures"]) + 1
            deadline["last_error_type"] = type(exc).__name__
            deadline["last_error_message"] = str(exc)
            _warn_bounded(
                "ResourceCoordinator.release: deadline monitor import unavailable; unregister skipped (%s)",
                type(exc).__name__,
            )
        except Exception as exc:
            deadline = _execution_diagnostics["deadline_unregister"]
            deadline["runtime_failures"] = int(deadline["runtime_failures"]) + 1
            deadline["last_error_type"] = type(exc).__name__
            deadline["last_error_message"] = str(exc)
            _warn_bounded(
                "ResourceCoordinator.release: deadline monitor unregister failed (%s)",
                type(exc).__name__,
            )

    def get_usage_stats(self) -> dict[str, Any]:
        """Return per-owner usage statistics as a serializable dict.

        Returns a mapping of ``{owner: stats_dict}`` suitable for CLI/MCP display.
        Each value is the output of :meth:`OwnerStats.to_dict`.
        """
        all_stats = self._usage_tracker.get_all_stats()
        return {owner: stats.to_dict() for owner, stats in all_stats.items()}

    def get_bottlenecks(self) -> dict[str, Any]:
        """Get current bottlenecks and slow points."""
        if self.bottleneck_detector is None:
            return {
                "detector_available": False,
                "reason": "bottleneck_detector_unavailable",
            }

        slow_points = self.bottleneck_detector.identify_slow_points()
        from thegent.orchestration.resource.resource_management import sample_extended_resources

        snapshot = sample_extended_resources()
        harness_cards = self.harness_cards if self.harness_cards is not None else {}
        contentions = self.bottleneck_detector.detect_resource_contention(snapshot, harness_cards)

        return {
            "slow_points": slow_points,
            "resource_contention": contentions,
        }


def _parse_checkpoint_by_id(line: str, checkpoint_id: str) -> dict[str, Any] | None:
    """Parse a checkpoint line and check if ID matches. WP-P2: Fix PERF203."""
    return _parse_checkpoint_by_id_impl(line, checkpoint_id)


def _parse_circuit_failure(
    line: str, target: str, category: str, now: datetime, window_s: int
) -> tuple[int, datetime | None]:
    """Parse a circuit breaker failure line. WP-P2: Fix PERF203."""
    return _parse_circuit_failure_impl(line, target, category, now, window_s)


def _parse_override_unexpired(line: str, owner: str, now: datetime) -> bool:
    """Parse an override line and check if it's unexpired. WP-P2: Fix PERF203."""
    return _parse_override_unexpired_impl(line, owner, now)


def _parse_fatigue_line(line: str, now: datetime, window_s: int) -> int:
    """Parse a fatigue interruption line. WP-P2: Fix PERF203."""
    return _parse_fatigue_line_impl(line, now, window_s)


class InterruptionTracker:
    """WP-4004: Fatigue tracking and interruption controls."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.path = session_dir / "interruption_tracker.jsonl"

    def record_interruption(self, run_id: str, severity: str = "medium") -> None:
        """Record an agent interruption event."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "run_id": run_id,
            "severity": severity,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def get_fatigue_score(self, window_s: int = 3600) -> float:
        """Calculate fatigue score based on recent interruptions (0.0-1.0)."""
        if not self.path.exists():
            return 0.0
        now = datetime.now(UTC)
        count = 0
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                count += _parse_fatigue_line(line, now, window_s)
        # Heuristic: 10+ interruptions per hour is high fatigue
        return min(1.0, count / 10.0)


class FreshnessValidator:
    """WP-4005: Detects stale state and enforces refresh logic."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir

    def is_stale(self, path: Path, max_age_s: int = 300) -> bool:
        """Check if a file or registry is stale."""
        if not path.exists():
            return True
        import time

        age = time.time() - path.stat().st_mtime
        return age > max_age_s

    def validate_action(self, context_files: list[Path]) -> list[str]:
        """Validate if the action is safe to perform based on context freshness."""
        issues = []
        for f in context_files:
            if self.is_stale(f):
                issues.append(f"Context file is stale: {f.name}")
        return issues


class HandoffManager:
    """WP-4006/9004: Manages shift handoffs and continuity snapshots with enforcement."""

    def __init__(
        self,
        session_dir: Path,
        warning_threshold: float | None = None,
        escalation_threshold: float | None = None,
    ) -> None:
        self.session_dir = session_dir
        self.path = session_dir / "handoff_registry.jsonl"
        self._confirmed_handoffs: set[str] = set()
        configured_warning = warning_threshold
        if configured_warning is None:
            configured_warning = _as_float(os.environ.get("THGENT_HANDOFF_WARNING_THRESHOLD"), 0.8)
        configured_escalation = escalation_threshold
        if configured_escalation is None:
            configured_escalation = _as_float(os.environ.get("THGENT_HANDOFF_ESCALATION_THRESHOLD"), 0.6)
        self.warning_threshold = min(max(configured_warning, 0.0), 1.0)
        self.escalation_threshold = min(max(configured_escalation, 0.0), self.warning_threshold)

    def create_snapshot(self, owner: str, run_ids: list[str]) -> str:
        """Create a continuity snapshot for a handoff."""
        snapshot_id = f"snap_{uuid.uuid4().hex[:8]}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        event = {
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "owner": owner,
            "run_ids": run_ids,
            "confirmed": False,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
        return snapshot_id

    def confirm_handoff(self, snapshot_id: str, incoming_owner: str, confidence: float = 1.0) -> bool:
        """WP-9004/12005: Incoming owner confirms handoff completeness with confidence."""
        if not self.verify_integrity(snapshot_id):
            self.session_dir.mkdir(parents=True, exist_ok=True)
            invalid_event = {
                "snapshot_id": snapshot_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "incoming_owner": incoming_owner,
                "confidence": confidence,
                "event_type": "handoff_invalid_snapshot",
                "reason": "snapshot_not_found",
            }
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(invalid_event) + "\n")
            return False

        if confidence < 0.0 or confidence > 1.0:
            self.session_dir.mkdir(parents=True, exist_ok=True)
            invalid_event = {
                "snapshot_id": snapshot_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "incoming_owner": incoming_owner,
                "confidence": confidence,
                "event_type": "handoff_invalid_snapshot",
                "reason": "confidence_out_of_range",
            }
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(invalid_event) + "\n")
            return False

        snapshot = self.get_snapshot(snapshot_id)
        if not isinstance(snapshot, dict) or not isinstance(snapshot.get("run_ids"), list):
            self.session_dir.mkdir(parents=True, exist_ok=True)
            invalid_event = {
                "snapshot_id": snapshot_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "incoming_owner": incoming_owner,
                "confidence": confidence,
                "event_type": "handoff_invalid_snapshot",
                "reason": "invalid_snapshot_shape",
            }
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(invalid_event) + "\n")
            return False

        confidence_state = "high"
        if confidence < self.warning_threshold:
            confidence_state = "low_warning"
            event_type = "handoff_low_confidence_warning"
            if confidence < self.escalation_threshold:
                confidence_state = "low_escalated"
                event_type = "handoff_low_confidence_escalation"
            low_confidence_event = {
                "snapshot_id": snapshot_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "incoming_owner": incoming_owner,
                "confidence": confidence,
                "event_type": event_type,
                "confidence_state": confidence_state,
                "warning_threshold": self.warning_threshold,
                "escalation_threshold": self.escalation_threshold,
                "run_count": len(snapshot.get("run_ids", [])),
            }
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(low_confidence_event) + "\n")

        self._confirmed_handoffs.add(snapshot_id)
        # Update registry record (simplified: append confirmation event)
        event = {
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "incoming_owner": incoming_owner,
            "confidence": confidence,
            "event_type": "handoff_confirmed",
            "confidence_state": confidence_state,
            "warning_threshold": self.warning_threshold,
            "escalation_threshold": self.escalation_threshold,
            "continuity_envelope_version": "v2.0",  # WP-12005
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
        return True

    def get_snapshot(self, snapshot_id: str) -> dict[str, Any] | None:
        """Retrieve a specific handoff snapshot by ID."""
        if not self.path.exists():
            return None
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                if data.get("snapshot_id") == snapshot_id and data.get("event_type") != "handoff_confirmed":
                    return data
        return None

    def list_pending_snapshots(self, limit: int = 10) -> list[dict[str, Any]]:
        """List pending (unconfirmed) handoff snapshots."""
        if not self.path.exists():
            return []
        snapshots: list[dict[str, Any]] = []
        confirmed: set[str] = set()
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                if data.get("event_type") == "handoff_confirmed":
                    confirmed.add(data["snapshot_id"])
                elif "snapshot_id" in data:
                    snapshots.append(data)
        pending = [s for s in snapshots if s["snapshot_id"] not in confirmed]
        return pending[:limit]

    def is_handoff_enforced(self) -> bool:
        """WP-9004: Check if a run is blocked by a pending handoff confirmation."""
        # Simplified: if any snapshot contains this run_id and is not confirmed
        # (This would need more state tracking in a real impl)
        return False

    def verify_integrity(self, snapshot_id: str) -> bool:
        """Verify the integrity of a handoff snapshot."""
        if not self.path.exists():
            return False
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                if f'"snapshot_id": "{snapshot_id}"' in line:
                    return True
        return False


class LoadClassifier:
    """WP-5002: Classifies system load and detects burst conditions."""

    def __init__(
        self,
        session_dir: Path,
        spike_threshold: int | None = None,
        surge_threshold: int | None = None,
    ) -> None:
        self.session_dir = session_dir
        self._spike = spike_threshold
        self._surge = surge_threshold

    def get_running_count(self) -> int:
        """Return count of currently running sessions."""
        from thegent.cli.commands.impl import ps_impl

        sessions = ps_impl(all=True)
        return sum(1 for s in sessions if s.get("status") == "running")

    def get_load_level(self) -> str:
        """Return current load level: normal, high, burst.

        Uses resource-based thresholds when load-based limits are enabled:
        - Normal: Below 70% of resource-based limit
        - High: 70-95% of resource-based limit (15% discretionary buffer)
        - Burst: Above 95% of resource-based limit (5% minimum buffer)
        """
        from thegent.config import ThegentSettings

        running = self.get_running_count()
        settings = ThegentSettings()

        # Use resource-based limits if enabled
        if settings.concurrency_load_based:
            from thegent.orchestration.resource.load_based_limits import (
                LimitGateConfig,
                compute_dynamic_limit,
                sample_resources,
            )

            snapshot = sample_resources()
            config = LimitGateConfig.from_dict(settings.model_dump())
            effective_limit, _ = compute_dynamic_limit(snapshot, config)

            # Thresholds based on resource-based limit with buffers
            surge = int(effective_limit * 0.95)  # 95% = 5% minimum buffer
            spike = int(effective_limit * 0.85)  # 85% = 15% discretionary buffer

            if running > surge:
                return "burst"
            if running > spike:
                return "high"
            return "normal"

        # Fallback to fixed thresholds if load-based disabled
        max_concurrency = settings.max_concurrency
        surge = self._surge if self._surge is not None else max_concurrency
        spike = self._spike if self._spike is not None else int(max_concurrency * 0.7)

        if running > surge:
            return "burst"
        if running > spike:
            return "high"
        return "normal"

    def is_safe_mode_active(self) -> bool:
        """Return True if system is in safe-mode (burst load)."""
        return self.get_load_level() == "burst"

    def get_traffic_shape(self) -> str:
        """Return current traffic shape (normal, shaped, restricted)."""
        level = self.get_load_level()
        if level == "burst":
            return "restricted"
        if level == "high":
            return "shaped"
        return "normal"


class DeferralQueue:
    """WP-5004: Manages non-critical tasks deferred during burst load."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.path = session_dir / "deferral_queue.jsonl"

    def defer(self, run_id: str, reason: str, eta_s: int = 300) -> None:
        """Defer a task with an estimated time to resume."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        event = {
            "run_id": run_id,
            "reason": reason,
            "deferred_at": datetime.now(UTC).isoformat(),
            "eta_utc": (datetime.now(UTC) + timedelta(seconds=eta_s)).isoformat(),
            "status": "deferred",
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def list_deferred(self) -> list[dict[str, Any]]:
        """List all currently deferred tasks."""
        if not self.path.exists():
            return []
        items: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                if data.get("status") == "deferred":
                    items.append(data)
        return items

    def resume(self, run_id: str) -> bool:
        """Resume a deferred task by marking it as resumed."""
        if not self.path.exists():
            return False
        lines: list[str] = []
        found = False
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    lines.append(line)
                    continue
                data = json.loads(stripped)
                if data.get("run_id") == run_id and data.get("status") == "deferred":
                    data["status"] = "resumed"
                    found = True
                lines.append(json.dumps(data) + "\n")
        if found:
            with self.path.open("w", encoding="utf-8") as f:
                f.writelines(lines)
        return found


class ContinuityWatchdog:
    """WP-5005: Background watchdog for stale ownership and automatic handoffs.

    ROB-012: Continuity watchdog with escalation on stale ownership - No orphaned critical tasks.
    """

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir

    def scan_stale_sessions(self, max_idle_s: int = 3600) -> list[str]:
        """Scan for sessions with no activity for max_idle_s."""
        from thegent.cli.commands.impl import ps_impl

        sessions = ps_impl(all=True)
        stale = []
        now = time.time()
        for s in sessions:
            if s.get("status") == "running":
                # ROB-012: Check mtime of session log/meta for actual staleness
                session_id = s.get("session_id")
                if session_id:
                    meta_path = self.session_dir / session_id / "meta.json"
                    if meta_path.exists():
                        mtime = meta_path.stat().st_mtime
                        idle_s = now - mtime
                        if idle_s > max_idle_s:
                            stale.append(session_id)
                    else:
                        # No metadata file - consider stale
                        stale.append(session_id)
        return stale

    def trigger_auto_handoff(self) -> bool:
        """Automatically trigger a handoff for a stale session (WP-5006)."""
        # Logic to update session owner in metadata
        return True

    def check_and_escalate_stale_critical(self, max_idle_s: int = 3600) -> list[dict[str, Any]]:
        """ROB-012: Check for stale critical tasks and escalate if needed.

        Returns list of escalated sessions.
        """
        from thegent.cli.commands.impl import ps_impl

        sessions = ps_impl(all=True)
        escalated = []
        now = time.time()

        for s in sessions:
            session_id = s.get("session_id")
            lane = s.get("lane", "standard")
            status = s.get("status", "")

            # ROB-012: Only escalate critical lane tasks that are stale
            if lane == "critical" and status == "running":
                if session_id is None:
                    raise RuntimeError(f"ROB-012: session entry missing session_id: {s!r}")
                meta_path = self.session_dir / session_id / "meta.json"
                if meta_path.exists():
                    mtime = meta_path.stat().st_mtime
                    idle_s = now - mtime
                    if idle_s > max_idle_s:
                        # ROB-012: Escalate stale critical task
                        try:
                            from thegent.governance.escalation import EscalationPriority, EscalationQueue

                            run_id = s.get("run_id") or session_id
                            esc_queue = EscalationQueue(self.session_dir)
                            esc_queue.escalate(
                                run_id=run_id,
                                prompt=s.get("prompt", ""),
                                reason=f"ROB-012: Critical task stale (idle {int(idle_s)}s > {max_idle_s}s)",
                                agent=s.get("agent", "unknown"),
                                priority=EscalationPriority.HIGH,
                                sla_minutes=30,  # Escalate after 30 minutes
                                metadata={"owner": s.get("owner", "unknown"), "lane": lane},
                            )
                            escalated.append(
                                {
                                    "session_id": session_id,
                                    "run_id": s.get("run_id"),
                                    "idle_seconds": int(idle_s),
                                    "escalated": True,
                                }
                            )
                        except Exception as e:
                            _log.warning("Failed to escalate stale critical task %s: %s", session_id, e)

        return escalated


def _parse_dlq_item(line: str, status: str | None, run_id: str | None) -> dict[str, Any] | None:
    """Parse a single DLQ item. WP-P2: Fix PERF203."""
    return _parse_dlq_item_impl(line, status, run_id)


def _process_dlq_line(line: str, run_id: str, resolution: str) -> tuple[str, bool]:
    """Process a single line in the DLQ. WP-P2: Fix PERF203."""
    return _process_dlq_line_impl(line, run_id, resolution)


class DLQManager:
    """WP-Y2: Dead-Letter Queue (DLQ) for permanently failing items."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.path = session_dir / "dlq_registry.jsonl"

    def enqueue(self, run_meta: "RunMeta", error: str) -> None:
        """Add a failing run to the DLQ."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        event = {
            "run_id": run_meta.run_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "agent": run_meta.agent,
            "prompt": run_meta.prompt,
            "error": error,
            "status": "pending_review",
            "poison_pill_count": 0,
        }
        # Check for poison pill (repeated failures of same task)
        existing = self.list_items(run_id=run_meta.run_id)
        if existing:
            event["poison_pill_count"] = existing[0].get("poison_pill_count", 0) + 1

        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

        # WP-3008: Integrate EscalationQueue with DLQ (Option C)
        try:
            # Check for infinite loops (don't escalate if it's an expired escalation)
            if "Escalation EXPIRED" in error:
                _log.info("Not re-escalating expired escalation for %s", run_meta.run_id)
            else:
                # Use governance escalation queue for unified tracking
                from thegent.governance.escalation import EscalationPriority
                from thegent.governance.escalation import EscalationQueue as GovEscalationQueue

                eq = GovEscalationQueue(self.session_dir)
                eq.escalate(
                    run_id=run_meta.run_id,
                    prompt=run_meta.prompt or "",
                    reason=f"DLQ Enqueue: {error}",
                    agent=run_meta.agent or "unknown",
                    priority=EscalationPriority.NORMAL,
                    sla_minutes=30,
                    metadata={"owner": run_meta.owner, "dlq_source": True},
                )
        except Exception as e:
            _log.error("Failed to auto-escalate DLQ item %s: %s", run_meta.run_id, e)

    def list_items(self, status: str | None = None, run_id: str | None = None) -> list[dict[str, Any]]:
        """List items in the DLQ with optional filtering."""
        if not self.path.exists():
            return []
        items = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                data = _parse_dlq_item(line, status, run_id)
                if data:
                    items.append(data)
        return items[::-1]  # Newest first

    def resolve(self, run_id: str, resolution: str) -> bool:
        """Mark a DLQ item as resolved (e.g. replayed, fixed)."""
        if not self.path.exists():
            return False
        lines = self.path.read_text(encoding="utf-8").splitlines()
        new_lines = []
        updated = False
        for line in lines:
            new_line, was_updated = _process_dlq_line(line, run_id, resolution)
            if was_updated:
                updated = True
            new_lines.append(new_line)
        if updated:
            self.path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return updated


class ReplayManager:
    """WP-4007/9003/9006: Decision replay and rationale snapshots with sandbox and what-if support."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self._sandbox_mode: bool = False

    def enable_sandbox(self) -> None:
        """WP-9003: Enable read-only sandbox mode for replay."""
        self._sandbox_mode = True

    def get_replay_chain(self, run_id: str) -> list[dict[str, Any]]:
        """Fetch the sequence of events for a run from the registry."""
        from thegent.execution import RunRegistry

        registry = RunRegistry(self.session_dir)
        runs = registry.list_runs(limit=1000)

        # Filter all events related to this run
        chain = [r for r in runs if r.get("run_id") == run_id or r.get("correlation_id") == run_id]
        return sorted(chain, key=lambda x: x.get("started_at_utc", ""))

    def simulate_policy_change(self, run_meta: "RunMeta", new_settings: Any) -> tuple[str, str]:
        """WP-4007: Pre-flight simulation of a different policy."""
        from thegent.execution import PolicyEngine

        engine = PolicyEngine(new_settings)
        return engine.evaluate(run_meta)

    def what_if_branch(
        self, run_id: str, branch_point_index: int, new_params: dict[str, Any], approved: bool = False
    ) -> dict[str, Any]:
        """WP-9006/12004: Simulate an alternate outcome with branch governance."""
        # WP-12004: Branch governance
        if not approved:
            return {
                "status": "pending_approval",
                "reason": "Branch simulation requires explicit governance approval.",
                "run_id": run_id,
                "branch_point": branch_point_index,
            }

        chain = self.get_replay_chain(run_id)
        if not chain or branch_point_index >= len(chain):
            return {"error": "Invalid branch point"}

        base_event = chain[branch_point_index]
        sim_event = base_event.copy()
        sim_event.update(new_params)
        sim_event["is_simulation"] = True
        sim_event["sim_id"] = f"sim_{run_id}_{branch_point_index}"

        # WP-12003: Sandbox hardening (ensure it's marked as non-mutating)
        sim_event["sandbox_mode"] = True
        sim_event["read_only"] = True

        return sim_event


class KPIManager:
    """WP-Y7: TRAFFIC KPI framework (10-metric)."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir

    def get_kpis(self) -> dict[str, Any]:
        """Calculate the 10 core KPIs for the dashboard."""
        from thegent.contracts.telemetry import ContractTelemetry
        from thegent.execution import RunRegistry

        registry = RunRegistry(self.session_dir)
        runs = registry.list_runs(limit=1000)
        ct = ContractTelemetry(self.session_dir)
        stats = ct.get_stats(limit=100)
        now = datetime.now(UTC)
        run_count = len(runs)
        finished_runs = [r for r in runs if r.get("status") in {"completed", "failed", "timed_out"}]
        success_runs = [r for r in finished_runs if r.get("status") == "completed"]
        confidence_values = [float(r.get("confidence", 0.0)) for r in runs if r.get("confidence") is not None]
        cost_values = [float(r.get("cost_usd", 0.0)) for r in runs if r.get("cost_usd") is not None]
        recent_runs = []
        for run in runs:
            started = run.get("started_at_utc")
            if not started:
                continue
            try:
                ts = datetime.fromisoformat(str(started))
            except ValueError:
                continue
            if (now - ts.astimezone(UTC)).total_seconds() <= 86400:
                recent_runs.append(run)

        throughput = run_count
        routing_accuracy = (len(success_runs) / len(finished_runs)) if finished_runs else 0.0
        accuracy = (
            sum(confidence_values) / len(confidence_values)
            if confidence_values
            else float(stats.get("avg_confidence", 0.0) or 0.0)
        )
        freshness = (len(recent_runs) / run_count) if run_count else 0.0
        fallback_rate = float(stats.get("fallback_rate", 0.0) or 0.0)
        interruption_rate = float(stats.get("interruption_rate", 0.0) or 0.0)
        cost_per_run = (sum(cost_values) / len(cost_values)) if cost_values else 0.0
        knowledge_coverage = sum(1 for r in runs if r.get("agent") and r.get("model")) / run_count if run_count else 0.0
        rollback_sla = routing_accuracy
        continuity_score = max(0.0, min(1.0, (freshness + (1.0 - interruption_rate) + rollback_sla) / 3.0))
        coverage_points = {
            "runs_total": run_count,
            "finished_runs": len(finished_runs),
            "telemetry_events": int(stats.get("total", 0) or 0),
            "confidence_samples": len(confidence_values),
            "cost_samples": len(cost_values),
        }
        data_availability = "full" if run_count >= 10 and int(stats.get("total", 0) or 0) >= 10 else "sparse"
        confidence_score = min(
            1.0,
            (
                (1.0 if coverage_points["runs_total"] >= 5 else coverage_points["runs_total"] / 5.0)
                + (1.0 if coverage_points["telemetry_events"] >= 5 else coverage_points["telemetry_events"] / 5.0)
            )
            / 2.0,
        )
        return {
            "throughput": throughput,
            "routing_accuracy": routing_accuracy,
            "accuracy": accuracy,
            "freshness": freshness,
            "fallback_rate": fallback_rate,
            "interruption_rate": interruption_rate,
            "cost_per_run": cost_per_run,
            "knowledge_coverage": knowledge_coverage,
            "rollback_sla": rollback_sla,
            "continuity_score": continuity_score,
            "data_availability": data_availability,
            "kpi_confidence": confidence_score,
            "coverage_points": coverage_points,
        }


class ProviderScorer:
    """WP-Y8/11008: Continuous scoring and learning loop with policy guardrails."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.path = session_dir / "provider_scores.json"

    def get_scores(self) -> dict[str, dict[str, float]]:
        """Return provider scores categorized by prompt characteristics."""
        if not self.path.exists():
            return {
                "coding": {"codex": 0.95, "claude": 0.90, "gemini": 0.85},
                "research": {"gemini": 0.98, "claude": 0.92, "codex": 0.70},
                "orchestration": {"claude": 0.96, "gemini": 0.88, "codex": 0.80},
            }
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def update_score(
        self, provider: str, characteristic: str, quality_score: float, approved: bool = False
    ) -> dict[str, Any]:
        """WP-11008: Update score with policy guardrails (e.g. requires approval for large changes)."""
        scores = self.get_scores()
        if characteristic not in scores:
            scores[characteristic] = {}

        current = scores[characteristic].get(provider, 0.8)
        delta = quality_score - current
        # Guardrail: if delta is large (> 0.2), require approval
        if abs(delta) > 0.2 and not approved:
            return {
                "status": "pending_approval",
                "reason": f"Significant score drift detected for {provider}/{characteristic} (delta {delta:.2f}).",
                "current": current,
                "proposed": quality_score,
            }

        # EMA update (0.1 alpha)
        scores[characteristic][provider] = (current * 0.9) + (quality_score * 0.1)

        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(scores, indent=2), encoding="utf-8")
        return {"status": "updated", "new_score": scores[characteristic][provider]}


class EvidenceLinter:
    """WP-2007: Checks evidence struct completeness and consistency."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir

    def lint(self, csm: Any) -> list[str]:
        """Verify CSM evidence is complete based on phase."""
        issues = []
        evidence = getattr(csm, "evidence", {})

        # Mandatory fields for all phases
        required = ["timestamp", "model", "agent"]
        for f in required:
            if not evidence.get(f):
                issues.append(f"Missing mandatory evidence field: {f}")

        # Phase-specific checks
        phase = getattr(csm, "phase", "execution")
        if phase == "routing":
            if not evidence.get("route_contract"):
                issues.append("Routing phase evidence missing route_contract")
        elif phase == "execution":
            if not evidence.get("stdout_hash") and not evidence.get("result"):
                issues.append("Execution phase evidence missing result/hash")
        elif phase == "promotion":
            if not evidence.get("policy_signature"):
                issues.append("Promotion phase evidence missing policy_signature")

        return issues


class AgentSource(StrEnum):
    """Source of the agent process for session registry (WP-9001)."""

    THEGENT_RUN = "thegent-run"
    THEGENT_DROID = "thegent-droid"
    THEGENT_SUBAGENT = "thegent-subagent"
    IDE_MANAGED = "ide-managed"
    USER_SPAWNED = "user-spawned"
    DISCOVERED = "discovered"
    MCP_PROXY = "mcp-proxy"


class InteractivityMode(StrEnum):
    """Interactivity mode of the session (WP-9002)."""

    PTY = "pty"
    TMUX = "tmux"
    HEADLESS_LOGS = "headless-logs"
    HEADLESS_HOLDPTY = "headless-holdpty"
    READ_ONLY = "read-only"


class RunMeta(BaseModel):
    """Metadata for a single agent/droid execution run."""

    run_id: str = Field(default_factory=lambda: f"run_{uuid.uuid4().hex[:8]}")
    correlation_id: str | None = None
    source: AgentSource = AgentSource.THEGENT_RUN
    interactivity: InteractivityMode = InteractivityMode.HEADLESS_LOGS

    # Attachment details
    attach_target: dict[str, Any] | None = None
    message_endpoint: str | None = None

    # Paths (managed sessions only)
    stdout_path: str | None = None
    stderr_path: str | None = None
    chat_path: str | None = None
    messages_path: str | None = None
    audit_path: str | None = None

    agent: str
    model: str | None = None
    mode: str = "write"
    prompt: str
    cwd: str
    owner: str
    started_at_utc: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    ended_at_utc: str | None = None
    duration_s: float | None = None
    exit_code: int | None = None
    status: str = "started"  # started, running, completed, failed, timed_out
    error_class: str | None = None  # usage_limit, timeout, logic_error, api_error
    signature: str | None = None
    policy_result: str | None = None  # allow, deny, warn
    policy_reason: str | None = None
    override_reason: str | None = None
    override_by: str | None = None
    rationale: str | None = None  # WP-4002/4007: Full explanation
    feedback_score: float | None = None  # WP-4008
    feedback_note: str | None = None
    host: str = Field(default_factory=socket.gethostname)
    pid: int = Field(default_factory=os.getpid)
    is_background: bool = False
    lane: str = "standard"  # standard, critical, recovery
    idempotency_token: str | None = None
    confidence: float | None = None
    arbitration: str | None = None  # leader, follower, consensus
    freshness_timestamp: str | None = Field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )  # ROB-011: Timestamp for stale-state detection

    # Audit trail chaining (WP-3004)
    prev_hash: str | None = None
    hash: str | None = None

    # Optional routing contract context
    route_contract: dict[str, Any] | None = None
    route_request: dict[str, Any] | None = None

    # Task routing metadata (Terminal Bench 2.0 Pareto frontier)
    task_category: str | None = None  # fast/normal/complex/high_complex
    task_complexity_score: int | None = None  # 0-100 complexity score
    estimated_cost_usd: float | None = None  # Estimated cost for this task
    estimated_duration_s: float | None = None  # Estimated duration
    constraint_violations: list[str] | None = None  # Hard constraint failures
    routing_reason: str | None = None  # Routing decision explanation

    # WP-3006: Compliance evidence retention — domain tagging for tiered retention
    domain_tag: str | None = None  # e.g. project-id, compliance-domain, lane

    # XA4: Contract version in task/run metadata for negotiation
    contract_version: str | None = None

    # WP-16002: Teammate delegation linkage
    task_id: str | None = None
    task_metadata: dict[str, Any] | None = None


class CheckpointMeta(BaseModel):
    """Metadata for a DAG/state checkpoint."""

    checkpoint_id: str = Field(default_factory=lambda: f"ckpt_{uuid.uuid4().hex[:8]}")
    created_at_utc: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    reason: str
    dag_content: str
    session_dir: str
    owner: str


class CalibrationRegistry:
    """WP-4008: Persists calibration factors and curves for agents (G-GP-09)."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.path = session_dir / "calibration_registry.json"

    def get_factor(self, agent: str) -> float:
        """Return the persisted calibration factor for an agent."""
        if not self.path.exists():
            return 1.0
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data.get(agent, {}).get("factor", 1.0)
        except Exception:
            return 1.0

    def update_agent(self, agent: str, factor: float, sample_size: int) -> None:
        """Persist a new calibration factor for an agent."""
        data = {}
        if self.path.exists():
            with contextlib.suppress(Exception):
                data = json.loads(self.path.read_text(encoding="utf-8"))
        data[agent] = {
            "factor": factor,
            "sample_size": sample_size,
            "updated_at_utc": datetime.now(UTC).isoformat(),
        }
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")


class LaneController:
    """WP-1002: Priority and urgency lane model for task management."""

    def __init__(self, session_dir: Path, capacity: int = 10) -> None:
        self.session_dir = session_dir
        self.capacity = capacity
        self.registry = RunRegistry(session_dir)

    def get_lane_priority(self, lane: str) -> int:
        """Return numeric priority for a lane (lower is higher priority)."""
        priorities = {
            "critical": 0,
            "standard": 10,
            "recovery": 20,
            "background": 100,
        }
        return priorities.get(lane.lower(), 50)

    def sort_tasks(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Sort tasks by lane priority and then by creation time."""
        return sorted(
            tasks,
            key=lambda x: (
                self.get_lane_priority(x.get("lane", "standard")),
                x.get("started_at_utc", ""),
            ),
        )

    def check_capacity(self, lane: str) -> bool:
        """Check if a lane has capacity to run (starvation prevention)."""
        runs = self.registry.list_runs(limit=100)
        active_runs = [r for r in runs if r.get("status") == "started"]

        # Reserved capacity for critical lane
        if lane == "critical":
            return True

        # Standard lane uses remaining capacity but leaves 2 slots for critical
        if len(active_runs) >= self.capacity - 2:
            return False

        return True


def _extract_session_id(line: str) -> str | None:
    """Extract session ID from a registry line. WP-P2: Fix PERF203."""
    return _extract_session_id_impl(line)


def _extract_run_id(line: str) -> str | None:
    """Extract run ID from a registry line. WP-P2: Fix PERF203."""
    return _extract_run_id_impl(line)


def _update_run_state(line: str, run_id: str, current_state: RunState | None) -> RunState | None:
    """Update run state from a registry line. WP-P2: Fix PERF203."""
    return _update_run_state_impl(line, run_id, current_state, RunState)


def _process_run_entry(line: str, runs: dict[str, dict[str, Any]]) -> None:
    """Process a run entry and update the runs dict. WP-P2: Fix PERF203."""
    _process_run_entry_impl(line, runs)


def _check_session_id(line: str, session_id: str) -> bool:
    """Check if a line matches the session ID. WP-P2: Fix PERF203."""
    return _check_session_id_impl(line, session_id)


def _process_token_match(line: str, token: str, best: dict[str, Any] | None) -> dict[str, Any] | None:
    """Process a line for idempotency token matching. WP-P2: Fix PERF203."""
    return _process_token_match_impl(line, token, best)


def _process_calibration_entry(line: str, agent: str, runs: dict[str, dict[str, Any]]) -> None:
    """Process an entry for calibration calculation. WP-P2: Fix PERF203."""
    _process_calibration_entry_impl(line, agent, runs)


def _extract_domain_tag(line: str) -> tuple[str | None, str | None]:
    """Extract run_id and domain_tag. WP-P2: Fix PERF203."""
    return _extract_domain_tag_impl(line)


def _filter_expired_record(
    line: str,
    now: datetime,
    run_domains: dict[str, str],
    default_days: int,
    by_domain: dict[str, int],
) -> tuple[bool, str]:
    """Check if a record is expired. Returns (is_expired, line). WP-P2: Fix PERF203."""
    return _filter_expired_record_impl(line, now, run_domains, default_days, by_domain)


def _parse_checkpoint_line(line: str) -> dict[str, Any] | None:
    """Parse a checkpoint registry line. WP-P2: Fix PERF203."""
    return _parse_checkpoint_line_impl(line)


def _parse_chat_line(line: str) -> "ChatEntry | None":
    """Parse a chat history line. WP-P2: Fix PERF203."""
    if not line.strip():
        return None
    try:
        return ChatEntry.model_validate_json(line)
    except Exception:
        return None


def _parse_message_line(line: str) -> "MessageEntry | None":
    """Parse a message registry line. WP-P2: Fix PERF203."""
    if not line.strip():
        return None
    try:
        msg = MessageEntry.model_validate_json(line)
        if msg.status == "pending":
            return msg
        message_parse = _execution_diagnostics["message_parse"]
        message_parse["non_pending_rows"] = int(message_parse["non_pending_rows"]) + 1
    except (ValidationError, json.JSONDecodeError, ValueError, TypeError) as exc:
        message_parse = _execution_diagnostics["message_parse"]
        message_parse["invalid_rows"] = int(message_parse["invalid_rows"]) + 1
        message_parse["last_error_type"] = type(exc).__name__
        message_parse["last_error_message"] = str(exc)
        _warn_bounded(
            "_parse_message_line: malformed message registry row ignored (%s)",
            type(exc).__name__,
        )
    return None


class RunRegistry:
    """Manages persistence and retrieval of execution runs.

    OPT-019: Uses bloom filter for fast negative lookups on session_id (O(1) session existence checks).
    """

    SCHEMA_VERSION = 1

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.registry_path = session_dir / "run_registry.jsonl"
        # OPT-019: Set-based fast negative lookups (O(1) session existence checks)
        self._bloom_filter: set[str] = set()
        self._last_hash_status: dict[str, Any] = {"status": "uninitialized", "error_type": None, "error_message": None}
        self._ensure_version_marker()

    def get_latest_session_id(self) -> str | None:
        """Return the correlation_id (or run_id) of the most recent started run."""
        if not self.registry_path.exists():
            return None
        latest: str | None = None
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                latest = _extract_session_id(line) or latest
        return latest

    def get_latest_run_id(self) -> str | None:
        """Return the run_id of the most recent run."""
        if not self.registry_path.exists():
            return None
        latest: str | None = None
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                latest = _extract_run_id(line) or latest
        return latest

    def _ensure_version_marker(self) -> None:
        """Write a version marker if the file is new."""
        if not self.registry_path.exists():
            self.session_dir.mkdir(parents=True, exist_ok=True)
            marker = build_schema_marker_event(self.SCHEMA_VERSION)
            marker["hash"] = self._calculate_hash(marker)
            with self.registry_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(marker) + "\n")

    def _get_last_hash(self) -> str | None:
        """Return the hash of the last record in the registry."""
        if not self.registry_path.exists():
            self._last_hash_status = {
                "status": "empty_registry",
                "error_type": None,
                "error_message": None,
            }
            return None

        try:
            with self.registry_path.open("r", encoding="utf-8") as f:
                last_line = None
                for line in f:
                    if line.strip():
                        last_line = line
                if not last_line:
                    self._last_hash_status = {
                        "status": "empty_chain",
                        "error_type": None,
                        "error_message": None,
                    }
                    return None

                data = json.loads(last_line)
                if not isinstance(data, dict):
                    self._last_hash_status = {
                        "status": "invalid_record_type",
                        "error_type": "TypeError",
                        "error_message": f"expected object, got {type(data).__name__}",
                    }
                    _warn_bounded("RunRegistry._get_last_hash: invalid trailing record type=%s", type(data).__name__)
                    return None

                hash_value = data.get("hash")
                if hash_value is None:
                    self._last_hash_status = {
                        "status": "missing_hash",
                        "error_type": "KeyError",
                        "error_message": "trailing record missing hash",
                    }
                    return None

                self._last_hash_status = {
                    "status": "ok",
                    "error_type": None,
                    "error_message": None,
                }
                return str(hash_value)
        except json.JSONDecodeError as exc:
            self._last_hash_status = {
                "status": "malformed_record",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
            _warn_bounded("RunRegistry._get_last_hash: malformed trailing record (%s)", type(exc).__name__)
            return None
        except OSError as exc:
            self._last_hash_status = {
                "status": "io_error",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
            _warn_bounded("RunRegistry._get_last_hash: read failed (%s)", type(exc).__name__)
            return None
        return None

    def get_last_hash_status(self) -> dict[str, Any]:
        """Return status metadata for the last _get_last_hash call."""
        return dict(self._last_hash_status)

    def _calculate_hash(self, data: dict[str, Any]) -> str:
        """Calculate a stable hash for a record, excluding the hash itself."""
        return calculate_stable_record_hash(data)

    def register_start(self, run: RunMeta) -> None:
        """Record the start of a run with hash chaining."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        run.prev_hash = self._get_last_hash()
        data = run.model_dump()
        run.hash = self._calculate_hash(data)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(run.model_dump_json() + "\n")
        # OPT-019: Add session_id to set for fast negative lookups
        session_id = run.correlation_id or run.run_id
        if session_id:
            self._bloom_filter.add(session_id)

    def register_end(
        self,
        run_id: str,
        exit_code: int,
        status: str,
        ended_at_utc: str,
        duration_s: float,
        error_class: str | None = None,
        cost_usd: float | None = None,
        event_details: dict[str, Any] | None = None,
    ) -> None:
        """Update a run with completion metadata and hash chaining. G-GP-06: cost_usd optional."""
        event = build_finish_event(
            run_id=run_id,
            exit_code=exit_code,
            status=status,
            ended_at_utc=ended_at_utc,
            duration_s=duration_s,
            error_class=error_class,
            prev_hash=self._get_last_hash(),
            cost_usd=cost_usd,
            event_details=event_details,
        )
        event["hash"] = self._calculate_hash(event)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def register_feedback(self, run_id: str, score: float, note: str | None = None) -> None:
        """Record operator feedback for a run with hash chaining."""
        event = build_feedback_event(
            run_id=run_id,
            score=score,
            note=note,
            prev_hash=self._get_last_hash(),
        )
        event["hash"] = self._calculate_hash(event)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def register_pause(
        self,
        run_id: str,
        reason: str,
        continuity_snapshot: dict[str, Any] | None = None,
    ) -> None:
        """Record run pause for state-aware orchestration (G-KD-03)."""
        event = build_pause_event(
            run_id=run_id,
            reason=reason,
            continuity_snapshot=continuity_snapshot,
            prev_hash=self._get_last_hash(),
        )
        event["hash"] = self._calculate_hash(event)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def register_resume(self, run_id: str) -> None:
        """Record run resume for state-aware orchestration (G-KD-03)."""
        event = build_resume_event(run_id=run_id, prev_hash=self._get_last_hash())
        event["hash"] = self._calculate_hash(event)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def get_run_state(self, run_id: str) -> RunState | None:
        """Return current run state from registry events (G-KD-03)."""
        if not self.registry_path.exists():
            return None
        state: RunState | None = None
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                state = _update_run_state(line, run_id, state)
        return state

    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        """List recent runs by parsing the registry."""
        if not self.registry_path.exists():
            return []

        runs: dict[str, dict[str, Any]] = {}
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                _process_run_entry(line, runs)

        # Sort by started_at_utc desc
        sorted_runs = sorted(runs.values(), key=lambda x: x.get("started_at_utc", ""), reverse=True)
        return sorted_runs[:limit]

    def session_exists(self, session_id: str) -> bool:
        """OPT-019: Fast negative lookup using bloom filter (O(1) session existence checks).

        Returns False if session definitely doesn't exist (bloom filter negative).
        Returns True if session might exist (requires full registry scan for confirmation).
        """
        # OPT-019: Fast negative lookup - if not in set, definitely doesn't exist
        if session_id not in self._bloom_filter:
            return False  # Definitely doesn't exist (set negative)
        # If in set, confirm with full registry scan
        return self._session_exists_in_registry(session_id)

    def _session_exists_in_registry(self, session_id: str) -> bool:
        """Check if session exists by scanning registry."""
        if not self.registry_path.exists():
            return False
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                if _check_session_id(line, session_id):
                    return True
        return False

    def find_by_token(self, token: str) -> dict[str, Any] | None:
        """Find the most recent run with a given idempotency token."""
        if not self.registry_path.exists():
            return None

        best: dict[str, Any] | None = None
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                best = _process_token_match(line, token, best)
        return best

    def get_calibration_factor(self, agent: str) -> float:
        """
        Calculate calibration factor (avg feedback / avg confidence) for an agent.
        G-GP-09: Checks CalibrationRegistry first for persisted factor.
        """
        cal = CalibrationRegistry(self.session_dir)
        factor = cal.get_factor(agent)
        if factor != 1.0:
            return factor

        if not self.registry_path.exists():
            return 1.0

        runs: dict[str, dict[str, Any]] = {}
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                _process_calibration_entry(line, agent, runs)

        relevant_runs = [r for r in runs.values() if r.get("feedback_score") is not None]
        if not relevant_runs:
            return 1.0

        avg_feedback = sum(float(r["feedback_score"]) for r in relevant_runs) / len(relevant_runs)
        avg_confidence = sum(float(r.get("confidence") or 0.5) for r in relevant_runs) / len(relevant_runs)
        if avg_confidence == 0:
            return 1.0
        return min(2.0, max(0.5, avg_feedback / avg_confidence))

    def purge_expired(
        self,
        default_days: int,
        by_domain: dict[str, int],
        dry_run: bool = True,
    ) -> dict[str, int]:
        """
        WP-3006: Tiered retention purge (G-GP-07).
        Removes records exceeding retention period. Returns counts of kept/purged.
        """
        if not self.registry_path.exists():
            return {"kept": 0, "purged": 0}

        now = datetime.now(UTC)
        run_domains: dict[str, str] = {}
        kept_lines = []
        purged_count = 0

        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                rid, domain = _extract_domain_tag(line)
                if rid and domain:
                    run_domains[rid] = domain

        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                is_expired, checked_line = _filter_expired_record(line, now, run_domains, default_days, by_domain)
                if is_expired:
                    purged_count += 1
                else:
                    kept_lines.append(checked_line)

        if not dry_run and purged_count > 0:
            self.registry_path.write_text("".join(kept_lines), encoding="utf-8")

        return {"kept": len(kept_lines), "purged": purged_count}


class ChatEntry(BaseModel):
    """Structured chat message for session history (WP-9003)."""

    ts: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    role: str  # user, assistant, system, tool
    content: str
    tool_name: str | None = None
    tool_input: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatHistory:
    """Manages structured conversation history for a session (WP-9003)."""

    def __init__(self, chat_path: Path) -> None:
        self.chat_path = chat_path

    def append(self, entry: ChatEntry) -> None:
        """Append a new chat entry to the session log."""
        self.chat_path.parent.mkdir(parents=True, exist_ok=True)
        with self.chat_path.open("a", encoding="utf-8") as f:
            f.write(entry.model_dump_json() + "\n")

    def load(self, limit: int | None = None) -> list[ChatEntry]:
        """Load chat history from the session log."""
        if not self.chat_path.exists():
            return []
        entries = []
        with self.chat_path.open("r", encoding="utf-8") as f:
            for line in f:
                entry = _parse_chat_line(line)
                if entry:
                    entries.append(entry)
        if limit:
            return entries[-limit:]
        return entries


class MessageEntry(BaseModel):
    """Pending message in the session queue (WP-9004)."""

    id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}")
    ts: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    type: str = "reprompt"  # reprompt, command, system, interrupt
    sender: str = "user"
    content: str
    status: str = "pending"  # pending, delivered, processed, failed
    metadata: dict[str, Any] = Field(default_factory=dict)


class MessageRegistry:
    """Manages the pending message queue for a session (WP-9004)."""

    def __init__(self, messages_path: Path) -> None:
        self.messages_path = messages_path

    def push(self, entry: MessageEntry) -> None:
        """Add a message to the queue."""
        self.messages_path.parent.mkdir(parents=True, exist_ok=True)
        with self.messages_path.open("a", encoding="utf-8") as f:
            f.write(entry.model_dump_json() + "\n")

    def list_pending(self) -> list[MessageEntry]:
        """List all pending messages in the queue."""
        if not self.messages_path.exists():
            return []
        entries = []
        with self.messages_path.open("r", encoding="utf-8") as f:
            for line in f:
                msg = _parse_message_line(line)
                if msg:
                    entries.append(msg)
        return entries

    def mark_processed(self, msg_id: str, status: str = "processed") -> None:
        """Mark a message as processed (appends an update event)."""
        # Since it's a JSONL queue, we append the update event
        # A more robust implementation would rewrite the file or use a separate state file
        update = {
            "id": msg_id,
            "status": status,
            "updated_at": datetime.now(UTC).isoformat(),
            "event": "update",
        }
        with self.messages_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(update) + "\n")


class AuditEntry(BaseModel):
    """Audit trail entry for session actions (WP-9005)."""

    ts: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    action: str  # view, send, attach, stop, pause, resume
    actor: str
    session_id: str
    details: dict[str, Any] = Field(default_factory=dict)
    result: str = "success"  # success, denied, error


class AuditRegistry:
    """Manages the session audit trail (WP-9005)."""

    def __init__(self, audit_path: Path) -> None:
        self.audit_path = audit_path

    def record(self, entry: AuditEntry) -> None:
        """Record an action in the audit trail."""
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        with self.audit_path.open("a", encoding="utf-8") as f:
            f.write(entry.model_dump_json() + "\n")


_LAST_POLL_MESSAGES_META: dict[str, Any] = {"status": "not_checked"}


def poll_session_messages(
    session_id: str | None = None,
    *,
    include_meta: bool = False,
) -> list[MessageEntry] | dict[str, Any]:
    """Poll for pending messages for the current session (WP-9004).

    If session_id is None, tries to read from THGENT_SESSION_ID env var (runtime value, not a setting).
    """
    global _LAST_POLL_MESSAGES_META  # noqa: PLW0603
    if session_id is None:
        # session_id is a runtime value, not a configuration setting
        # Keep using os.environ for runtime values that change per execution
        import os

        session_id = os.environ.get("THGENT_SESSION_ID")

    if not session_id:
        _LAST_POLL_MESSAGES_META = {"status": "missing_session_id"}
        missing_payload: dict[str, Any] = {"messages": [], "meta": dict(_LAST_POLL_MESSAGES_META)}
        return missing_payload if include_meta else []

    from thegent.cli.commands.impl import _find_session_meta
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
        msg_path = meta_path.parent / f"{session_id}.messages.jsonl"
        registry = MessageRegistry(msg_path)
        messages = registry.list_pending()
        _LAST_POLL_MESSAGES_META = {
            "status": "ok",
            "session_id": session_id,
            "pending_count": len(messages),
            "messages_path": str(msg_path),
        }
        ok_payload: dict[str, Any] = {"messages": messages, "meta": dict(_LAST_POLL_MESSAGES_META)}
        return ok_payload if include_meta else messages
    except FileNotFoundError as exc:
        _LAST_POLL_MESSAGES_META = {
            "status": "meta_missing",
            "session_id": session_id,
            "error_type": type(exc).__name__,
            "detail": str(exc)[:200],
        }
    except PermissionError as exc:
        _LAST_POLL_MESSAGES_META = {
            "status": "unreadable_messages",
            "session_id": session_id,
            "error_type": type(exc).__name__,
            "detail": str(exc)[:200],
        }
    except ValueError as exc:
        _LAST_POLL_MESSAGES_META = {
            "status": "parser_failure",
            "session_id": session_id,
            "error_type": type(exc).__name__,
            "detail": str(exc)[:200],
        }
    except OSError as exc:
        _LAST_POLL_MESSAGES_META = {
            "status": "io_failure",
            "session_id": session_id,
            "error_type": type(exc).__name__,
            "detail": str(exc)[:200],
        }

    empty_payload: dict[str, Any] = {"messages": [], "meta": dict(_LAST_POLL_MESSAGES_META)}
    return empty_payload if include_meta else []


def get_last_poll_session_messages_meta() -> dict[str, Any]:
    """Return diagnostics metadata for the latest poll_session_messages call."""
    return dict(_LAST_POLL_MESSAGES_META)


class CheckpointRegistry:
    """Manages persistence and retrieval of state checkpoints."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.registry_path = session_dir / "checkpoint_registry.jsonl"

    def create_checkpoint(self, reason: str, dag_content: str, owner: str) -> CheckpointMeta:
        """Record a new checkpoint."""
        ckpt = CheckpointMeta(
            reason=reason,
            dag_content=dag_content,
            session_dir=str(self.session_dir),
            owner=owner,
        )
        self.session_dir.mkdir(parents=True, exist_ok=True)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(ckpt.model_dump_json() + "\n")
        return ckpt

    def list_checkpoints(self, limit: int = 20) -> list[dict[str, Any]]:
        """List recent checkpoints."""
        if not self.registry_path.exists():
            return []

        ckpts = []
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                ckpt = _parse_checkpoint_line(line)
                if ckpt:
                    ckpts.append(ckpt)

        return sorted(ckpts, key=lambda x: x.get("created_at_utc", ""), reverse=True)[:limit]

    def get_checkpoint(self, checkpoint_id: str) -> dict[str, Any] | None:
        """Retrieve a specific checkpoint."""
        if not self.registry_path.exists():
            return None

        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                data = _parse_checkpoint_by_id(line, checkpoint_id)
                if data:
                    return data
        return None


class PolicyEngine:
    """Evaluates execution requests against governance policies."""

    def __init__(self, settings: Any) -> None:
        self.settings = settings

    def _emit_await_approval(
        self,
        run: RunMeta,
        reason: str,
        policy: str = "require_human_approval.policy_gate",
    ) -> None:
        """Append await_approval governance event to JSONL audit log."""
        session_dir = Path(getattr(self.settings, "session_dir", "~/.thegent/sessions")).expanduser().resolve()
        path = session_dir / "governance_events.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "event_type": "await_approval",
            "event_id": f"hitl_{uuid.uuid4().hex[:8]}",
            "run_id": run.run_id,
            "policy": policy,
            "owner": run.owner,
            "agent": run.agent,
            "lane": run.lane,
            "reason": reason,
            "checkpoint": "pre_execution",
            "environment": getattr(self.settings, "environment", "development"),
            "status": "pending",
            "emitted_at_utc": datetime.now(UTC).isoformat(),
        }
        try:
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(event, sort_keys=True))
                fh.write("\n")
        except OSError as exc:
            _log.warning("failed to write governance await_approval event: %s", exc)

    @staticmethod
    def _requires_human_approval(run: RunMeta) -> bool:
        """Detect explicit HITL requirement from run metadata/contracts."""
        if run.constraint_violations and any(v == "require_human_approval" for v in run.constraint_violations):
            return True
        if run.task_metadata and bool(run.task_metadata.get("require_human_approval")):
            return True
        return False

    def _query_opa(self, run: RunMeta) -> tuple[str, str] | None:
        """
        G-GP-01: Optional OPA integration. POST to /v1/data/thegent/allow.
        Returns (result, reason) or None if OPA not configured or unreachable.
        """
        raw_opa_url = getattr(self.settings, "opa_url", "")
        if not isinstance(raw_opa_url, str):
            opa_url = ""
        else:
            opa_url = raw_opa_url.strip().rstrip("/")
        if not opa_url:
            return None
        url = f"{opa_url}/v1/data/thegent/allow"
        timeout_ms = _as_float(getattr(self.settings, "opa_timeout_ms", 500), 500.0)
        timeout_s = max(0.1, timeout_ms / 1000.0)
        environment = getattr(self.settings, "environment", "development")
        if not isinstance(environment, str) or not environment:
            environment = "development"
        trust_score_threshold = _as_float(getattr(self.settings, "trust_score_threshold", 0.8), 0.8)
        payload = {
            "input": {
                "run_meta": run.model_dump(mode="json"),
                "context": {
                    "environment": environment,
                    "trust_score_threshold": trust_score_threshold,
                },
            },
        }
        try:
            response = httpx.post(url, json=payload, timeout=timeout_s)
            response.raise_for_status()
            data = response.json()
            raw: object = data.get("result") or {}
            result: dict[str, Any] = dict(raw) if isinstance(raw, dict) else {}
            allow = result.get("allow", False)
            reason = result.get("reason", "OPA decision")
            return ("allow", reason) if allow else ("deny", reason)
        except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError, OSError) as e:
            _log.warning("OPA query failed (%s): %s", url, e)
            return None

    def evaluate(self, run: RunMeta, registry: RunRegistry | None = None) -> tuple[str, str]:
        """
        Evaluate a run against active policies.
        Returns (result, reason) where result is 'allow', 'deny', or 'warn'.
        G-GP-01: When THGENT_OPA_URL is set, delegates to OPA first; falls back to Python logic on failure.
        """
        # G-GP-05: Explicit HITL gate from task/contract metadata.
        if self._requires_human_approval(run):
            reason = "Run requires explicit human approval."
            self._emit_await_approval(run, reason, policy="require_human_approval.metadata")
            return "pause", reason

        # WP-9007: Confidence escalation thresholds
        confidence = run.confidence if run.confidence is not None else 0.5
        threshold = _as_float(getattr(self.settings, "confidence_escalation_threshold", 0.4), 0.4)
        if confidence < threshold:
            reason = f"Confidence {confidence:.2f} below escalation threshold {threshold:.2f}. Manual review required."
            self._emit_await_approval(run, reason, policy="require_human_approval.low_confidence")
            return (
                "pause",
                reason,
            )

        # G-GP-02: Input Guardrails (NeMo-style)
        if _as_bool(getattr(self.settings, "input_guardrails_enabled", False), False):
            from thegent.governance.input_guardrails import guardrails_from_env

            rails = guardrails_from_env()
            res = rails.check(prompt=run.prompt, agent=run.agent, model=run.model, cwd=run.cwd)
            if not res.passed:
                return "deny", f"Input guardrail '{res.rail_id}' failed: {res.reason}. {res.remediation}"

        # Policy 0: Circuit Breakers (G-KD-05 / G-GP-04)
        if _as_bool(getattr(self.settings, "circuit_breaker_enabled", True), True):
            cb = CircuitBreakerRegistry(
                self.settings.session_dir,
                threshold=_as_int(getattr(self.settings, "circuit_breaker_threshold", 5), 5),
                window_s=_as_int(getattr(self.settings, "circuit_breaker_window_s", 300), 300),
                recovery_s=_as_int(getattr(self.settings, "circuit_breaker_recovery_s", 60), 60),
            )
            if cb.is_open(run.agent, category="agent"):
                return "deny", f"Circuit breaker is OPEN for agent '{run.agent}'. Repeated failures detected."
            if run.model and cb.is_open(run.model, category="model"):
                return "deny", f"Circuit breaker is OPEN for model '{run.model}'. Repeated failures detected."

        raw_opa_url = getattr(self.settings, "opa_url", None)
        opa_url = raw_opa_url.strip() if isinstance(raw_opa_url, str) else ""
        if opa_url:
            opa_result = self._query_opa(run)
            if opa_result is not None:
                return opa_result
            fallback_allow = _as_bool(getattr(self.settings, "opa_fallback_allow", False), False)
            if fallback_allow:
                return "allow", "OPA unreachable; fallback allow per config"
            return "deny", "OPA unreachable; fallback deny per config (set THGENT_OPA_FALLBACK_ALLOW=1 to allow)"

        env = str(getattr(self.settings, "environment", "development")).lower()

        # WP-0004/WP-4008: Trust Score Calibration
        # Adjust confidence based on historical performance if registry provided
        if registry and run.confidence is not None:
            cal_factor = registry.get_calibration_factor(run.agent)
            if cal_factor != 1.0:
                run.confidence = min(1.0, max(0.0, run.confidence * cal_factor))
                # We don't return here, we just adjust and continue to other checks

        # Policy 1: Critical lane requires high confidence
        if run.lane == "critical" and (run.confidence is not None and run.confidence < 0.9):
            return "deny", f"Critical lane requires confidence >= 0.9 (current: {run.confidence})"

        # Policy 2: Prevent use of unknown agents in critical/prod
        if (run.lane == "critical" or env == "production") and run.agent == "unknown":
            return "deny", f"Unknown agents are blocked in {env} / {run.lane} lane."

        # Policy 2b (XC2): Block critical lane when contract drift exceeds budget
        if run.lane == "critical":
            from thegent.contracts.telemetry import ContractTelemetry

            ct = ContractTelemetry(self.settings.session_dir)
            budget = ct.get_drift_budget_status(structural_budget_pct=5.0, semantic_budget_pct=10.0)
            if not budget.get("within_budget", True):
                return "deny", (
                    f"Critical lane blocked: contract drift exceeds budget "
                    f"(structural: {budget.get('structural_rate_pct', 0)}% > {budget.get('structural_budget_pct', 5)}%, "
                    f"semantic: {budget.get('semantic_rate_pct', 0)}% > {budget.get('semantic_budget_pct', 10)}%). "
                    "Run `thegent observe drift` to investigate."
                )

        # Policy 3: Warn if no confidence score provided for recovery/critical
        if run.lane in ("recovery", "critical") and run.confidence is None:
            if getattr(self.settings, "hitl_enabled", False) and "pre_execution" in getattr(
                self.settings, "hitl_checkpoints", []
            ):
                reason = f"{run.lane.capitalize()} action requires HITL approval due to missing confidence."
                self._emit_await_approval(run, reason, policy="require_human_approval.missing_confidence")
                return "pause", reason
            return "warn", f"{run.lane.capitalize()} actions should ideally carry a confidence score."

        # Policy 4: Trust Score Gate for Production
        if env == "production":
            threshold = _as_float(getattr(self.settings, "trust_score_threshold", 0.8), 0.8)
            conf = run.confidence if run.confidence is not None else 0.5
            if conf < threshold:
                return (
                    "deny",
                    f"Production environment requires trust score >= {threshold} (current: {conf}). Provide --override to proceed.",
                )

        # Policy 5: Cost Budget Enforcement (G-GP-06)
        if getattr(self.settings, "cost_tracking_enabled", False):
            from thegent.cost.aggregator import CostAggregator

            agg = CostAggregator(self.settings.session_dir)

            # Global MTD budget check
            mtd_total = agg.get_mtd_total()
            cost_budget = float(getattr(self.settings, "cost_budget_mtd", 100.0))
            if mtd_total >= cost_budget:
                return "deny", f"Monthly budget exceeded (${mtd_total:.2f} >= ${cost_budget:.2f})."

            # Per-category budget check (if routing enabled and category provided)
            if run.task_category and getattr(self.settings, "routing_enabled", False):
                category_budgets: dict[str, float] = getattr(self.settings, "cost_budget_by_category", {}) or {}
                category_limit = category_budgets.get(run.task_category.lower(), 0.0)

                if category_limit > 0.0:
                    category_mtd = agg.get_category_mtd_total(run.task_category.lower())
                    estimated_cost = run.estimated_cost_usd or 0.0
                    utilization = (category_mtd + estimated_cost) / category_limit

                    # Block at 100% utilization
                    if utilization >= 1.0:
                        return "deny", (
                            f"Category '{run.task_category}' budget exhausted: "
                            f"${category_mtd:.2f} + ${estimated_cost:.4f} >= ${category_limit:.2f}"
                        )

                    # Warn at 80% utilization
                    warning_threshold = float(getattr(self.settings, "routing_budget_warning_threshold", 0.80))
                    if utilization >= warning_threshold:
                        _log.warning(
                            "Category '%s' budget at %.0f%% utilization ($%.2f + $%.4f / $%.2f)",
                            run.task_category,
                            utilization * 100,
                            category_mtd,
                            estimated_cost,
                            category_limit,
                        )
                        # Continue (warn, don't deny)

        return "allow", "All policies passed."


class TrustBoundaryValidator:
    """WP-3007: Validates environment transitions (e.g. staging→production)."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.state_path = session_dir / "env_transition_state.json"

    def get_last_environment(self) -> str | None:
        """Return the last recorded environment from a run."""
        if not self.state_path.exists():
            return None
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
            return data.get("last_environment")
        except Exception:
            return None

    def record_environment(self, env: str) -> None:
        """Record current environment after successful run."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        data = {"last_environment": env, "updated_at": datetime.now(UTC).isoformat()}
        self.state_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def validate_transition(self, from_env: str | None, to_env: str) -> tuple[bool, str]:
        """
        Validate transition from from_env to to_env.
        Returns (allowed, reason). Promotions (dev→staging→prod) may require audit.
        """
        if not from_env:
            return True, "No prior environment"
        order = ["development", "staging", "production"]
        try:
            from_idx = order.index(from_env.lower())
            to_idx = order.index(to_env.lower())
        except ValueError:
            return True, "Unknown env; no transition check"
        if to_idx <= from_idx:
            return True, "Same or downgrade"
        if to_idx - from_idx > 1:
            return False, f"Skip-level promotion {from_env}→{to_env} requires explicit audit"
        return True, f"Valid promotion {from_env}→{to_env}"


class Auditor:
    """Provides integrity verification for the run registry."""

    def __init__(self, registry_path: Path) -> None:
        self.registry_path = registry_path
        # WP-3002: Rust MAIF Manager integration
        from thegent.maif.rust_manager import RustMAIFManager

        binary_path = Path("target-maif/release/thegent-maif")
        session_dir = registry_path.parent
        keys_dir = session_dir / "keys"
        self.maif_manager = RustMAIFManager(
            binary_path=binary_path,
            private_key_path=keys_dir / "maif_private.pem",
            public_key_path=keys_dir / "maif_public.pem",
        )

    def _calculate_hash(self, data: dict[str, Any]) -> str:
        """Calculate a stable hash for a record, excluding the hash field."""
        return calculate_stable_record_hash(data)

    def sign_run(self, run: RunMeta) -> str:
        """Generate a cryptographic signature for a run record."""
        # Keep signatures deterministic for stable verification and tests.
        data = f"{run.run_id}|{run.started_at_utc}|{run.owner}|{run.prompt}"
        return hashlib.sha256(data.encode()).hexdigest()

    def generate_maif_artifact(self, run: RunMeta, output: str | None = None) -> Any:
        """Generate a signed MAIF artifact for a run (WP-3002)."""
        # WP-3002: Use Rust MAIF binary for artifact generation
        try:
            artifact_path = self.registry_path.parent / "artifacts" / f"{run.run_id}.maif.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "prompt": run.prompt,
                "output": output,
                "policy_result": run.policy_result,
                "policy_reason": run.policy_reason,
            }
            return self.maif_manager.create_artifact(
                action="run_complete",
                payload=payload,
                agent=run.agent or "unknown",
                session=run.run_id,
                output_path=artifact_path,
            )
        except Exception as e:
            _log.debug(f"MAIF generation failed: {e}; falling back to Pydantic model")
            prompt_hash = hashlib.sha256(run.prompt.encode()).hexdigest()
            output_hash = hashlib.sha256(output.encode()).hexdigest() if output else None
            signature = self.sign_run(run)

            return MAIFArtifact(
                run_id=run.run_id,
                agent=run.agent,
                model=run.model,
                prompt_hash=prompt_hash,
                output_hash=output_hash,
                signature=signature,
                policy_result=run.policy_result,
            )

    def persist_maif_artifact(self, session_dir: Path, artifact: Any) -> Path:
        """Persist a MAIF artifact to the artifacts directory (WP-3002)."""
        artifacts_dir = session_dir / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        run_id = artifact.get("session_id") if isinstance(artifact, dict) else artifact.run_id
        path = artifacts_dir / f"{run_id}.maif.json"

        if isinstance(artifact, dict):
            path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
        else:
            path.write_text(artifact.model_dump_json(indent=2), encoding="utf-8")
        return path

    def verify_registry(self) -> dict[str, Any]:
        """Verify the integrity of all records in the registry, including the hash chain.

        ROB-006: Hash chain integrity verification on audit read - Detect tampered audit logs.
        """
        if not self.registry_path.exists():
            return {"status": "empty", "valid_count": 0, "corrupt_count": 0, "chain_broken": False, "issues": []}

        valid = 0
        corrupt = 0
        issues = []
        last_hash = None
        chain_broken = False

        with self.registry_path.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    rid = data.get("run_id", "unknown")
                    stored_hash = data.get("hash")
                    prev_hash = data.get("prev_hash")

                    # Chain check against prior record hash (first line has no chain expectation).
                    if last_hash is not None and prev_hash != last_hash:
                        chain_broken = True
                        issues.append(
                            f"ROB-006: Hash chain broken at line {i + 1} (run_id: {rid}). "
                            f"Expected prev_hash: {last_hash}, got: {prev_hash}"
                        )

                    if not stored_hash:
                        corrupt += 1
                        issues.append(f"Line {i + 1}: Missing hash field (run_id: {rid})")
                        continue

                    computed_hash = self._calculate_hash(data)
                    if stored_hash != computed_hash:
                        corrupt += 1
                        issues.append(
                            f"ROB-006: Hash mismatch at line {i + 1} (run_id: {rid}). "
                            f"Stored: {stored_hash[:16]}..., computed: {computed_hash[:16]}..."
                        )
                        continue

                    stored_sig = data.get("signature")
                    if stored_sig and data.get("event") != "finish":
                        raw_data = (
                            f"{data.get('run_id')}|{data.get('started_at_utc')}|"
                            f"{data.get('owner')}|{data.get('prompt')}"
                        )
                        expected_sig = hashlib.sha256(raw_data.encode()).hexdigest()
                        if stored_sig != expected_sig:
                            corrupt += 1
                            issues.append(f"Line {i + 1}: Signature mismatch for {rid}")
                            continue

                    valid += 1
                    last_hash = stored_hash
                except Exception as e:
                    corrupt += 1
                    issues.append(f"Line {i + 1}: JSON decode error: {e}")

        return {
            "status": "passed" if (corrupt == 0 and not chain_broken) else "failed",
            "valid_count": valid,
            "corrupt_count": corrupt,
            "chain_broken": chain_broken,
            "issues": issues,
        }


class CircuitBreakerRegistry:
    """Tracks failures and manages circuit states for models/agents.

    ROB-003: Poison pill detection for repeated identical failures - Stop infinite retry loops.
    """

    def __init__(self, session_dir: Path, threshold: int = 5, window_s: int = 300, recovery_s: int = 60) -> None:
        self.session_dir = session_dir
        self.registry_path = session_dir / "circuit_breakers.jsonl"
        self.threshold = threshold
        self.window_s = window_s
        self.recovery_s = recovery_s
        # ROB-003: Track identical failures for poison pill detection
        self._poison_pill_tracker: dict[str, list[tuple[str, float]]] = {}  # target -> [(error_hash, timestamp), ...]

    def record_failure(self, target: str, category: str = "agent", error_message: str | None = None) -> None:
        """Record a failure for a target in a specific category.

        ROB-003: Detects poison pills (repeated identical failures) and prevents infinite retry loops.
        """
        self.session_dir.mkdir(parents=True, exist_ok=True)
        error_hash = None
        if error_message:
            # ROB-003: Hash error message to detect identical failures
            error_hash = hashlib.sha256(error_message.encode()).hexdigest()[:16]
            key = f"{target}:{category}"
            now = time.time()

            # Track identical failures
            if key not in self._poison_pill_tracker:
                self._poison_pill_tracker[key] = []

            # Remove old entries outside window
            self._poison_pill_tracker[key] = [
                (eh, ts) for eh, ts in self._poison_pill_tracker[key] if (now - ts) < self.window_s
            ]

            # Add new failure
            self._poison_pill_tracker[key].append((error_hash, now))

            # ROB-003: Check for poison pill (3+ identical failures in window)
            identical_count = sum(1 for eh, _ in self._poison_pill_tracker[key] if eh == error_hash)
            if identical_count >= 3:
                _log.warning(
                    "ROB-003: Poison pill detected for %s/%s: %d identical failures (hash: %s). Stopping retry loop.",
                    target,
                    category,
                    identical_count,
                    error_hash,
                )
                # Mark as poison pill - circuit breaker will stay open longer
                self.recovery_s = self.recovery_s * 3  # Extend recovery time for poison pills

        event = {
            "target": target,
            "category": category,
            "event": "failure",
            "timestamp": datetime.now(UTC).isoformat(),
            "error_hash": error_hash,
        }
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def is_open(self, target: str, category: str = "agent") -> bool:
        """Check if the circuit for a target in a category is open (blocked)."""
        if not self.registry_path.exists():
            return False

        now = datetime.now(UTC)
        failures = 0
        last_failure = None

        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                f_count, ts = _parse_circuit_failure(line, target, category, now, self.window_s)
                if f_count > 0:
                    failures += f_count
                    if ts is not None and (last_failure is None or ts > last_failure):
                        last_failure = ts

        if failures >= self.threshold:
            # Check if we should enter half-open (recovery)
            if last_failure and (now - last_failure).total_seconds() > self.recovery_s:
                return False  # Half-open: allow a trial
            return True  # Open
        return False


class OverrideRegistry:
    """Stores policy overrides with TTL. WP-3003: revalidation on expiry."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.registry_path = session_dir / "override_registry.jsonl"

    def record(self, owner: str, reason: str, ttl_seconds: int) -> None:
        """Record an override; valid until now + ttl_seconds."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now(UTC)
        expires_at = now.timestamp() + ttl_seconds
        event = {
            "owner": owner,
            "reason": reason,
            "timestamp": now.isoformat(),
            "expires_at_utc": datetime.fromtimestamp(expires_at, tz=UTC).isoformat(),
        }
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def has_unexpired(self, owner: str) -> bool:
        """True if owner has an override that has not yet expired."""
        if not self.registry_path.exists():
            return False
        now = datetime.now(UTC)
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in reversed(list(f)):
                if _parse_override_unexpired(line, owner, now):
                    return True
        return False


class EscalationQueue:
    """WP-3008: Governance queue for blocked decisions with SLA tracking."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.queue_path = session_dir / "escalation_queue.jsonl"

    def add(
        self,
        run_id: str,
        reason: str,
        sla_minutes: int = 30,
        owner: str | None = None,
        agent: str | None = None,
        lane: str | None = None,
        priority: int = 0,
    ) -> None:
        """Add a blocked run to the escalation queue."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now(UTC)
        escalate_by = now + timedelta(minutes=sla_minutes)
        event = {
            "run_id": run_id,
            "reason": reason,
            "owner": owner,
            "agent": agent,
            "lane": lane or "standard",
            "priority": priority,
            "blocked_at_utc": now.isoformat(),
            "escalate_by_utc": escalate_by.isoformat(),
            "sla_minutes": sla_minutes,
            "status": "pending",
        }
        with self.queue_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def list_pending(self, past_sla_only: bool = False, limit: int = 50) -> list[dict[str, Any]]:
        """List escalation items. If past_sla_only, return only items past escalate_by."""
        if not self.queue_path.exists():
            return []
        now = datetime.now(UTC)
        items: list[dict[str, Any]] = []
        with self.queue_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if data.get("status") != "pending":
                        continue
                    exp = data.get("escalate_by_utc")
                    if not exp:
                        continue
                    exp_dt = datetime.fromisoformat(exp)
                    if past_sla_only and now <= exp_dt:
                        continue
                    data["past_sla"] = now > exp_dt
                    items.append(data)
                except Exception:
                    continue
        items.sort(key=lambda x: (x.get("priority", 0), x.get("blocked_at_utc", "")))
        return items[-limit:][::-1]

    def resolve(self, run_id: str, resolution: str = "resolved") -> bool:
        """Mark an escalation item as resolved. Returns True if found and updated."""
        if not self.queue_path.exists():
            return False
        lines = self.queue_path.read_text(encoding="utf-8").splitlines()
        updated = False
        new_lines = []
        for line in lines:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if data.get("run_id") == run_id and data.get("status") == "pending":
                    data["status"] = resolution
                    data["resolved_at_utc"] = datetime.now(UTC).isoformat()
                    updated = True
                new_lines.append(json.dumps(data))
            except Exception:
                new_lines.append(line)
        if updated:
            self.queue_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return updated
