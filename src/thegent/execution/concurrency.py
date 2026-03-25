"""Execution run metadata and registry for thegent orchestration."""

import hashlib
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from thegent.config import ThegentSettings
from thegent.execution_coercion_helpers import as_int as _as_int_impl

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


def _as_int(value: Any, default: int) -> int:
    """Coerce arbitrary values to int with a safe default."""
    return _as_int_impl(value, default)


if TYPE_CHECKING:
    from .registry import RunRegistry


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
                ThegentSettings()
                configured_slots = _as_int(os.environ.get("THGENT_CRITICAL_LANE_SLOTS"), 2)
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


class LaneController:
    """WP-1002: Priority and urgency lane model for task management."""

    def __init__(self, session_dir: Path, capacity: int = 10) -> None:
        from .registry import RunRegistry

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
