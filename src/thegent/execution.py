"""Execution run metadata and registry for thegent orchestration."""

import contextlib
import hashlib
import orjson as json
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
            f.write(json.dumps(event).decode().decode() + "\n")        return snapshot_id

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
                f.write(json.dumps(invalid_event).decode().decode() + "\n")            return False

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
                f.write(json.dumps(invalid_event).decode().decode() + "\n")            return False

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
                f.write(json.dumps(invalid_event).decode().decode() + "\n")            return False

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
                f.write(json.dumps(low_confidence_event).decode().decode() + "\n")
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
            f.write(json.dumps(event).decode().decode() + "\n")        return True

    def get_snapshot(self, snapshot_id: str) -> dict[str, Any] | None:
        """Retrieve a specific handoff snapshot by ID."""
        if not self.path.exists():
            return None
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json_loads(line)
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
                data = json_loads(line)
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
            f.write(json.dumps(event).decode().decode() + "\n")
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
                data = json_loads(line)
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
                data = json_loads(stripped)
                if data.get("run_id") == run_id and data.get("status") == "deferred":
                    data["status"] = "resumed"
                    found = True
                lines.append(json.dumps(data).decode().decode() + "\n")        if found:
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
            f.write(json.dumps(event).decode().decode() + "\n")
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
            return json_loads(self.path.read_text(encoding="utf-8"))
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
        self.path.write_text(json.dumps(scores, indent=2).decode().decode(), encoding="utf-8")        return {"status": "updated", "new_score": scores[characteristic][provider]}


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
            data = json_loads(self.path.read_text(encoding="utf-8"))
            return data.get(agent, {}).get("factor", 1.0)
        except Exception:
            return 1.0

    def update_agent(self, agent: str, factor: float, sample_size: int) -> None:
        """Persist a new calibration factor for an agent."""
        data = {}
        if self.path.exists():
            with contextlib.suppress(Exception):
                data = json_loads(self.path.read_text(encoding="utf-8"))
        data[agent] = {
            "factor": factor,
            "sample_size": sample_size,
            "updated_at_utc": datetime.now(UTC).isoformat(),
        }
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2).decode().decode(), encoding="utf-8")

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
                f.write(json.dumps(marker).decode().decode() + "\n")
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

                data = json_loads(last_line)
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
            f.write(json.dumps(event).decode().decode() + "\n")
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
            f.write(json.dumps(event).decode().decode() + "\n")
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
            f.write(json.dumps(event).decode().decode() + "\n")
    def register_resume(self, run_id: str) -> None:
        """Record run resume for state-aware orchestration (G-KD-03)."""
        event = build_resume_event(run_id=run_id, prev_hash=self._get_last_hash())
        event["hash"] = self._calculate_hash(event)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event).decode().decode() + "\n")
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
            f.write(json.dumps(update).decode().decode() + "\n")

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
                fh.write(json.dumps(event, sort_keys=True).decode().decode())                fh.write("\n")
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
            data = json_loads(self.state_path.read_text(encoding="utf-8"))
            return data.get("last_environment")
        except Exception:
            return None

    def record_environment(self, env: str) -> None:
        """Record current environment after successful run."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        data = {"last_environment": env, "updated_at": datetime.now(UTC).isoformat()}
        self.state_path.write_text(json.dumps(data, indent=2).decode().decode(), encoding="utf-8")
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
            path.write_text(json.dumps(artifact, indent=2).decode().decode(), encoding="utf-8")        else:
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
                    data = json_loads(line)
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
            f.write(json.dumps(event).decode().decode() + "\n")
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
            f.write(json.dumps(event).decode().decode() + "\n")
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
            f.write(json.dumps(event).decode().decode() + "\n")
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
                    data = json_loads(line)
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
                data = json_loads(line)
                if data.get("run_id") == run_id and data.get("status") == "pending":
                    data["status"] = resolution
                    data["resolved_at_utc"] = datetime.now(UTC).isoformat()
                    updated = True
                new_lines.append(json.dumps(data).decode().decode())            except Exception:
                new_lines.append(line)
        if updated:
            self.queue_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return updated
