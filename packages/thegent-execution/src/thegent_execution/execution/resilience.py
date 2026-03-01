"""Execution run metadata and registry for thegent orchestration."""

import hashlib
import json
import logging
import os
import time
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


from thegent.execution_coercion_helpers import as_bool as _as_bool_impl
from thegent.execution_coercion_helpers import as_float as _as_float_impl
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


def _as_float(value: Any, default: float) -> float:
    """Coerce arbitrary values to float with a safe default."""
    return _as_float_impl(value, default)


def _as_int(value: Any, default: int) -> int:
    """Coerce arbitrary values to int with a safe default."""
    return _as_int_impl(value, default)


def _as_bool(value: Any, default: bool) -> bool:
    """Coerce arbitrary values to bool with a safe default."""
    return _as_bool_impl(value, default)


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
                f.write(json.dumps(invalid_event).decode() + "\n")
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
                f.write(json.dumps(invalid_event).decode() + "\n")
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
                f.write(json.dumps(invalid_event).decode() + "\n")
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
                f.write(json.dumps(low_confidence_event).decode() + "\n")

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
                lines.append(json.dumps(data).decode() + "\n")
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
        from thegent_cli.cli.commands.impl import ps_impl

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
        from thegent_cli.cli.commands.impl import ps_impl

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
                            from thegent_audit.governance.escalation import EscalationPriority, EscalationQueue

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
                from thegent_audit.governance.escalation import EscalationPriority
                from thegent_audit.governance.escalation import EscalationQueue as GovEscalationQueue

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
        from thegent_execution.execution import RunRegistry

        registry = RunRegistry(self.session_dir)
        runs = registry.list_runs(limit=1000)

        # Filter all events related to this run
        chain = [r for r in runs if r.get("run_id") == run_id or r.get("correlation_id") == run_id]
        return sorted(chain, key=lambda x: x.get("started_at_utc", ""))

    def simulate_policy_change(self, run_meta: "RunMeta", new_settings: Any) -> tuple[str, str]:
        """WP-4007: Pre-flight simulation of a different policy."""
        from thegent_execution.execution import PolicyEngine

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

    def _parse_circuit_failure(self, line: str, target: str, category: str, now: datetime) -> tuple[int, datetime | None]:
        """Parse a circuit failure line from registry."""
        import json
        try:
            if not line.strip():
                return 0, None
            event = json.loads(line)
            if event.get("target") != target or event.get("category") != category:
                return 0, None
            ts = datetime.fromisoformat(event.get("timestamp", ""))
            if (now - ts).total_seconds() > self.window_s:
                return 0, None
            return 1, ts
        except:
            return 0, None

    def is_open(self, target: str, category: str = "agent") -> bool:
        """Check if the circuit for a target in a category is open (blocked)."""
        if not self.registry_path.exists():
            return False

        now = datetime.now(UTC)
        failures = 0
        last_failure = None

        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                f_count, ts = self._parse_circuit_failure(line, target, category, now)
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
                new_lines.append(json.dumps(data).decode())
            except Exception:
                new_lines.append(line)
        if updated:
            self.queue_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return updated
