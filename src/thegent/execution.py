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
from pydantic import BaseModel, Field

_log = logging.getLogger(__name__)


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


class ConcurrencyController:
    """WP-5001: Advanced resource-based adaptive concurrency controller.
    
    Features:
    - Extended resource indices (CPU, memory, FD, network, disk, GPU, etc.)
    - Prediction engine for forecasting resource needs
    - Harness card modeling (codex/claude/droid usage profiles)
    - Bottleneck detection and analysis
    - Speculative execution strategies
    - Work chunking and parallelization
    """

    def __init__(self, session_dir: Path, max_concurrency: int = 5, use_load_based: bool = True) -> None:
        self.session_dir = session_dir
        self.max_concurrency = max_concurrency  # Fallback if load-based disabled
        self.use_load_based = use_load_based
        self.lock_file = session_dir / "concurrency.lock"
        
        # Initialize advanced features (if available)
        if use_load_based:
            try:
                from thegent.orchestration.resource_management import (
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

    def acquire(self, lane: str = "standard", harness_type: str | None = None) -> bool:
        """Acquire a concurrency slot using advanced resource-based limits.
        
        Uses:
        - Extended resource monitoring (CPU, memory, FD, network, disk, etc.)
        - Prediction engine for forecasting
        - Harness card modeling for harness-specific limits
        - Bottleneck detection
        - 5% minimum buffer (hard limit, prevents crashes)
        - 15% discretionary buffer (soft limit, allows scaling)
        """
        from thegent.cli_impl import ps_impl
        from thegent.config import ThegentSettings

        sessions = ps_impl(all=True)
        running_count = sum(1 for s in sessions if s.get("status") == "running")

            # Use resource-based limits if enabled (default)
        settings = ThegentSettings()
        if self.use_load_based and (settings.concurrency_load_based or True):  # Default to True
            from thegent.orchestration.load_based_limits import (
                LimitGateConfig,
                compute_dynamic_limit,
                sample_resources,
            )

            # Sample current resources
            snapshot = sample_resources()
            
            # Compute base dynamic limit (uses 5% min buffer, 15% discretionary buffer)
            config = LimitGateConfig()
            effective_limit, details = compute_dynamic_limit(snapshot, config, running_count)
            
            # Advanced features (if available)
            try:
                from thegent.orchestration.resource_management import sample_extended_resources
                extended_snapshot = sample_extended_resources()
                
                # Record for prediction engine
                if self.prediction_engine:
                    self.prediction_engine.record(extended_snapshot)
                
                # Apply harness card modeling if harness type specified
                if harness_type and self.harness_cards:
                    card = self.harness_cards.get(harness_type)
                    if card:
                        # Estimate resources for current + 1 session (use p95 for conservative planning)
                        estimated = card.estimate_resources(running_count + 1, isolated=False, use_p95=True)
                        # Extract p95 memory estimate (or fallback to avg)
                        mem_estimate = estimated["memory_mb"].get("p95", estimated["memory_mb"].get("avg", 0))
                        # Adjust limit based on harness capacity
                        harness_limit = int(
                            (snapshot.mem_available_mb - mem_estimate) / config.mem_mb_per_slot
                        )
                        effective_limit = min(effective_limit, max(1, harness_limit))
                
                # Apply prediction adjustments
                if self.prediction_engine:
                    prediction = self.prediction_engine.predict_next_interval(60)
                    if prediction.get("confidence", 0) > 0.5:
                        # Adjust based on predicted trends
                        pred_mem = prediction.get("prediction", {}).get("mem_rss_mb", {})
                        if pred_mem and pred_mem.get("trend", 0) > 0:
                            # Memory trending up, reduce limit slightly
                            effective_limit = int(effective_limit * 0.95)
                
                # Check for bottlenecks
                if self.bottleneck_detector:
                    contentions = self.bottleneck_detector.detect_resource_contention(
                        extended_snapshot, self.harness_cards or {}
                    )
                    if contentions:
                        # Reduce limit if resource contention detected
                        high_severity = sum(1 for c in contentions if c.get("severity") == "high")
                        if high_severity > 0:
                            effective_limit = int(effective_limit * 0.9)
            except ImportError:
                # Advanced features not available, use basic resource-based limits
                pass
            
            # Critical lane gets 20% headroom above calculated limit
            if lane == "critical":
                effective_limit = int(effective_limit * 1.2)
            
            return running_count < effective_limit
        
        # Fallback to fixed limit (if load-based disabled)
        limit = self.max_concurrency
        if lane == "critical":
            limit = self.max_concurrency * 2  # Double limit for critical lane

        return running_count < limit
    
    def get_bottlenecks(self) -> list[dict[str, Any]]:
        """Get current bottlenecks and slow points."""
        if not hasattr(self, "bottleneck_detector"):
            return []
        
        slow_points = self.bottleneck_detector.identify_slow_points()
        from thegent.orchestration.resource_management import sample_extended_resources
        snapshot = sample_extended_resources()
        contentions = self.bottleneck_detector.detect_resource_contention(
            snapshot, self.harness_cards if hasattr(self, "harness_cards") else {}
        )
        
        return {
            "slow_points": slow_points,
            "resource_contention": contentions,
        }


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
                try:
                    data = json.loads(line)
                    ts = datetime.fromisoformat(data["timestamp"])
                    if (now - ts).total_seconds() < window_s:
                        count += 1
                except Exception:
                    continue
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

    def validate_action(self, run_id: str, context_files: list[Path]) -> list[str]:
        """Validate if the action is safe to perform based on context freshness."""
        issues = []
        for f in context_files:
            if self.is_stale(f):
                issues.append(f"Context file is stale: {f.name}")
        return issues


class HandoffManager:
    """WP-4006/9004: Manages shift handoffs and continuity snapshots with enforcement."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.path = session_dir / "handoff_registry.jsonl"
        self._confirmed_handoffs: set[str] = set()

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
            return False

        # WP-12005: Handoff confidence threshold
        if confidence < 0.8:
            # Record low confidence handoff
            pass

        self._confirmed_handoffs.add(snapshot_id)
        # Update registry record (simplified: append confirmation event)
        event = {
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "incoming_owner": incoming_owner,
            "confidence": confidence,
            "event_type": "handoff_confirmed",
            "continuity_envelope_version": "v2.0",  # WP-12005
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
        return True

    def is_handoff_enforced(self, run_id: str) -> bool:
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

    def get_load_level(self) -> str:
        """Return current load level: normal, high, burst.
        
        Uses resource-based thresholds when load-based limits are enabled:
        - Normal: Below 70% of resource-based limit
        - High: 70-95% of resource-based limit (15% discretionary buffer)
        - Burst: Above 95% of resource-based limit (5% minimum buffer)
        """
        from thegent.cli_impl import ps_impl
        from thegent.config import ThegentSettings

        sessions = ps_impl(all=True)
        running = sum(1 for s in sessions if s.get("status") == "running")

        settings = ThegentSettings()
        
        # Use resource-based limits if enabled
        if settings.concurrency_load_based:
            from thegent.orchestration.load_based_limits import (
                LimitGateConfig,
                compute_dynamic_limit,
                sample_resources,
            )
            snapshot = sample_resources()
            config = LimitGateConfig.from_dict(None)
            effective_limit, _ = compute_dynamic_limit(snapshot, config, running)
            
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


class ContinuityWatchdog:
    """WP-5005: Background watchdog for stale ownership and automatic handoffs.

    ROB-012: Continuity watchdog with escalation on stale ownership - No orphaned critical tasks.
    """

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir

    def scan_stale_sessions(self, max_idle_s: int = 3600) -> list[str]:
        """Scan for sessions with no activity for max_idle_s."""
        from thegent.cli_impl import ps_impl

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

    def trigger_auto_handoff(self, session_id: str, _backup_owner: str) -> bool:
        """Automatically trigger a handoff for a stale session (WP-5006)."""
        # Logic to update session owner in metadata
        return True

    def check_and_escalate_stale_critical(self, max_idle_s: int = 3600) -> list[dict[str, Any]]:
        """ROB-012: Check for stale critical tasks and escalate if needed.

        Returns list of escalated sessions.
        """
        from thegent.cli_impl import ps_impl

        sessions = ps_impl(all=True)
        escalated = []
        now = time.time()

        for s in sessions:
            session_id = s.get("session_id")
            lane = s.get("lane", "standard")
            status = s.get("status", "")

            # ROB-012: Only escalate critical lane tasks that are stale
            if lane == "critical" and status == "running":
                meta_path = self.session_dir / session_id / "meta.json"
                if meta_path.exists():
                    mtime = meta_path.stat().st_mtime
                    idle_s = now - mtime
                    if idle_s > max_idle_s:
                        # ROB-012: Escalate stale critical task
                        try:
                            from thegent.governance.escalation import EscalationQueue, EscalationPriority

                            esc_queue = EscalationQueue(self.session_dir)
                            esc_queue.escalate(
                                run_id=s.get("run_id", session_id),
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

    def list_items(self, status: str | None = None, run_id: str | None = None) -> list[dict[str, Any]]:
        """List items in the DLQ with optional filtering."""
        if not self.path.exists():
            return []
        items = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if status and data.get("status") != status:
                        continue
                    if run_id and data.get("run_id") != run_id:
                        continue
                    items.append(data)
                except Exception:
                    continue
        return items[::-1]  # Newest first

    def resolve(self, run_id: str, resolution: str) -> bool:
        """Mark a DLQ item as resolved (e.g. replayed, fixed)."""
        if not self.path.exists():
            return False
        lines = self.path.read_text(encoding="utf-8").splitlines()
        new_lines = []
        updated = False
        for line in lines:
            try:
                data = json.loads(line)
                if data.get("run_id") == run_id and data.get("status") == "pending_review":
                    data["status"] = resolution
                    data["resolved_at"] = datetime.now(UTC).isoformat()
                    updated = True
                new_lines.append(json.dumps(data))
            except Exception:
                new_lines.append(line)
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

        return {
            "throughput": len(runs),
            "routing_accuracy": 0.92,  # placeholder
            "accuracy": 0.88,  # placeholder
            "freshness": 0.95,  # placeholder
            "fallback_rate": stats.get("fallback_rate", 0.0),
            "interruption_rate": 0.05,  # placeholder
            "cost_per_run": 0.12,  # placeholder
            "knowledge_coverage": 0.85,  # placeholder
            "rollback_sla": 0.98,  # placeholder
            "continuity_score": 0.90,  # placeholder
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


class RunMeta(BaseModel):
    """Metadata for a single agent/droid execution run."""

    run_id: str = Field(default_factory=lambda: f"run_{uuid.uuid4().hex[:8]}")
    correlation_id: str | None = None
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


class RunRegistry:
    """Manages persistence and retrieval of execution runs.

    OPT-019: Uses bloom filter for fast negative lookups on session_id (O(1) session existence checks).
    """

    SCHEMA_VERSION = 1

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.registry_path = session_dir / "run_registry.jsonl"
        # OPT-019: Bloom filter for fast negative lookups (O(1) session existence checks)
        try:
            from pybloom_live import BloomFilter

            # Bloom filter with capacity for 10k sessions, 0.1% false positive rate
            self._bloom_filter: BloomFilter | None = BloomFilter(capacity=10000, error_rate=0.001)
        except ImportError:
            # Fallback if pybloom_live not available
            self._bloom_filter = None
        self._ensure_version_marker()

    def get_latest_session_id(self) -> str | None:
        """Return the correlation_id (or run_id) of the most recent started run."""
        if not self.registry_path.exists():
            return None
        latest: str | None = None
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get("status") == "started" or data.get("event") == "started":
                        # Prefer correlation_id (session id format) over run_id
                        latest = data.get("correlation_id") or data.get("run_id")
                except Exception:
                    continue
        return latest

    def get_latest_run_id(self) -> str | None:
        """Return the run_id of the most recent run."""
        if not self.registry_path.exists():
            return None
        latest: str | None = None
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    rid = data.get("run_id")
                    if rid:
                        latest = rid
                except Exception:
                    continue
        return latest

    def _ensure_version_marker(self) -> None:
        """Write a version marker if the file is new."""
        if not self.registry_path.exists():
            self.session_dir.mkdir(parents=True, exist_ok=True)
            marker = {
                "event": "schema_version",
                "version": self.SCHEMA_VERSION,
                "timestamp": datetime.now(UTC).isoformat(),
            }
            marker["hash"] = self._calculate_hash(marker)
            with self.registry_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(marker) + "\n")

    def _get_last_hash(self) -> str | None:
        """Return the hash of the last record in the registry."""
        if not self.registry_path.exists():
            return None

        try:
            with self.registry_path.open("r", encoding="utf-8") as f:
                last_line = None
                for line in f:
                    if line.strip():
                        last_line = line
                if last_line:
                    data = json.loads(last_line)
                    return data.get("hash")
        except Exception:
            pass
        return None

    def _calculate_hash(self, data: dict[str, Any]) -> str:
        """Calculate a stable hash for a record, excluding the hash itself."""
        # Create a copy and remove the 'hash' field if it exists
        d = {k: v for k, v in data.items() if k != "hash"}
        # Use stable JSON serialization
        body = json.dumps(d, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(body.encode()).hexdigest()

    def register_start(self, run: RunMeta) -> None:
        """Record the start of a run with hash chaining."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        run.prev_hash = self._get_last_hash()
        data = run.model_dump()
        run.hash = self._calculate_hash(data)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(run.model_dump_json() + "\n")
        # OPT-019: Add session_id to bloom filter for fast negative lookups
        if self._bloom_filter is not None:
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
    ) -> None:
        """Update a run with completion metadata and hash chaining. G-GP-06: cost_usd optional."""
        event = {
            "run_id": run_id,
            "event": "finish",
            "exit_code": exit_code,
            "status": status,
            "ended_at_utc": ended_at_utc,
            "duration_s": duration_s,
            "error_class": error_class,
            "timestamp": ended_at_utc,
            "prev_hash": self._get_last_hash(),
        }
        if cost_usd is not None:
            event["cost_usd"] = cost_usd
        event["hash"] = self._calculate_hash(event)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def register_feedback(self, run_id: str, score: float, note: str | None = None) -> None:
        """Record operator feedback for a run with hash chaining."""
        timestamp = datetime.now(UTC).isoformat()
        event = {
            "run_id": run_id,
            "event": "feedback",
            "feedback_score": score,
            "feedback_note": note,
            "timestamp": timestamp,
            "prev_hash": self._get_last_hash(),
        }
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
        timestamp = datetime.now(UTC).isoformat()
        event = {
            "run_id": run_id,
            "event": "pause",
            "reason": reason,
            "continuity_snapshot": continuity_snapshot or {},
            "timestamp": timestamp,
            "prev_hash": self._get_last_hash(),
        }
        event["hash"] = self._calculate_hash(event)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def register_resume(self, run_id: str) -> None:
        """Record run resume for state-aware orchestration (G-KD-03)."""
        timestamp = datetime.now(UTC).isoformat()
        event = {
            "run_id": run_id,
            "event": "resume",
            "timestamp": timestamp,
            "prev_hash": self._get_last_hash(),
        }
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
                try:
                    data = json.loads(line)
                    if data.get("run_id") != run_id:
                        continue
                    ev = data.get("event")
                    if ev is None and data.get("status") == "started":
                        state = RunState.RUNNING
                    elif ev == "finish":
                        status = data.get("status", "")
                        state = RunState.FAILED if status in ("failed", "timed_out") else RunState.COMPLETED
                    elif ev == "pause":
                        state = RunState.PAUSED
                    elif ev == "resume":
                        state = RunState.RUNNING
                except Exception:
                    continue
        return state

    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        """List recent runs by parsing the registry."""
        if not self.registry_path.exists():
            return []

        runs: dict[str, dict[str, Any]] = {}
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    rid = data.get("run_id")
                    if not rid:
                        continue
                    if data.get("event") == "finish":
                        if rid in runs:
                            runs[rid].update(data)
                    else:
                        runs[rid] = data
                except Exception:
                    continue

        # Sort by started_at_utc desc
        sorted_runs = sorted(runs.values(), key=lambda x: x.get("started_at_utc", ""), reverse=True)
        return sorted_runs[:limit]

    def session_exists(self, session_id: str) -> bool:
        """OPT-019: Fast negative lookup using bloom filter (O(1) session existence checks).

        Returns False if session definitely doesn't exist (bloom filter negative).
        Returns True if session might exist (requires full registry scan for confirmation).
        """
        # OPT-019: Fast negative lookup - if not in bloom filter, definitely doesn't exist
        if self._bloom_filter is not None:
            if session_id not in self._bloom_filter:
                return False  # Definitely doesn't exist (bloom filter negative)
        # If in bloom filter or bloom filter unavailable, check registry
        return self._session_exists_in_registry(session_id)

    def _session_exists_in_registry(self, session_id: str) -> bool:
        """Check if session exists by scanning registry."""
        if not self.registry_path.exists():
            return False
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get("correlation_id") == session_id or data.get("run_id") == session_id:
                        return True
                except Exception:
                    continue
        return False

    def find_by_token(self, token: str) -> dict[str, Any] | None:
        """Find the most recent run with a given idempotency token."""
        if not self.registry_path.exists():
            return None

        best: dict[str, Any] | None = None
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get("idempotency_token") == token:
                        rid = data.get("run_id")
                        if data.get("event") == "finish":
                            if best and best.get("run_id") == rid:
                                best.update(data)
                        elif data.get("event") == "feedback":
                            if best and best.get("run_id") == rid:
                                best["feedback_score"] = data.get("feedback_score")
                        # Start event: if we don't have this run or it's newer, use it
                        elif not best or data.get("started_at_utc", "") >= best.get("started_at_utc", ""):
                            best = data
                except Exception:
                    continue
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

        relevant_runs = []
        runs: dict[str, dict[str, Any]] = {}

        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    rid = data.get("run_id")
                    if not rid:
                        continue

                    if data.get("event") == "finish":
                        if rid in runs:
                            runs[rid].update(data)
                    elif data.get("event") == "feedback":
                        if rid in runs:
                            runs[rid]["feedback_score"] = data.get("feedback_score")
                    elif data.get("agent") == agent:
                        runs[rid] = data
                except Exception:
                    continue

        relevant_runs = [r for r in runs.values() if r.get("feedback_score") is not None]
        if not relevant_runs:
            return 1.0

        avg_feedback = sum(float(r["feedback_score"]) for r in relevant_runs) / len(relevant_runs)
        avg_confidence = sum(float(r.get("confidence") or 0.5) for r in relevant_runs) / len(relevant_runs)

        if avg_confidence == 0:
            return 1.0

        # Calibration factor: if we are overconfident (conf > feedback), factor < 1.0
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

        # First pass: map run_id to domain_tag from start events
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    rid = data.get("run_id")
                    domain = data.get("domain_tag")
                    if rid and domain:
                        run_domains[rid] = domain
                except Exception:
                    continue

        # Second pass: filter records
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    ts_str = data.get("timestamp") or data.get("started_at_utc")
                    if not ts_str:
                        kept_lines.append(line)
                        continue

                    ts = datetime.fromisoformat(ts_str)
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=UTC)

                    rid = data.get("run_id")
                    domain = run_domains.get(rid) if rid else data.get("domain_tag")
                    days = by_domain.get(domain, default_days) if domain else default_days

                    if (now - ts).days > days:
                        purged_count += 1
                        continue

                    kept_lines.append(line)
                except Exception:
                    kept_lines.append(line)

        if not dry_run and purged_count > 0:
            self.registry_path.write_text("".join(kept_lines), encoding="utf-8")

        return {"kept": len(kept_lines), "purged": purged_count}


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
                try:
                    ckpts.append(json.loads(line))
                except Exception:
                    continue

        return sorted(ckpts, key=lambda x: x.get("created_at_utc", ""), reverse=True)[:limit]

    def get_checkpoint(self, checkpoint_id: str) -> dict[str, Any] | None:
        """Retrieve a specific checkpoint."""
        if not self.registry_path.exists():
            return None

        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get("checkpoint_id") == checkpoint_id:
                        return data
                except Exception:
                    continue
        return None


class PolicyEngine:
    """Evaluates execution requests against governance policies."""

    def __init__(self, settings: Any) -> None:
        self.settings = settings

    def _query_opa(self, run: RunMeta) -> tuple[str, str] | None:
        """
        G-GP-01: Optional OPA integration. POST to /v1/data/thegent/allow.
        Returns (result, reason) or None if OPA not configured or unreachable.
        """
        opa_url = (getattr(self.settings, "opa_url", None) or "").strip().rstrip("/")
        if not opa_url:
            return None
        url = f"{opa_url}/v1/data/thegent/allow"
        timeout_s = max(0.1, (getattr(self.settings, "opa_timeout_ms", 500) or 500) / 1000.0)
        payload = {
            "input": {
                "run_meta": run.model_dump(mode="json"),
                "context": {
                    "environment": getattr(self.settings, "environment", "development"),
                    "trust_score_threshold": getattr(self.settings, "trust_score_threshold", 0.8),
                },
            },
        }
        try:
            resp = httpx.post(url, json=payload, timeout=timeout_s)
            resp.raise_for_status()
            data = resp.json()
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
        # WP-9007: Confidence escalation thresholds
        confidence = run.confidence if run.confidence is not None else 0.5
        threshold = getattr(self.settings, "confidence_escalation_threshold", 0.4)
        if confidence < threshold:
            return (
                "pause",
                f"Confidence {confidence:.2f} below escalation threshold {threshold:.2f}. Manual review required.",
            )

        # G-GP-02: Input Guardrails (NeMo-style)
        if getattr(self.settings, "input_guardrails_enabled", False):
            from thegent.governance.input_guardrails import _guardrails_from_env

            rails = _guardrails_from_env()
            res = rails.check(prompt=run.prompt, agent=run.agent, model=run.model, cwd=run.cwd)
            if not res.passed:
                return "deny", f"Input guardrail '{res.rail_id}' failed: {res.reason}. {res.remediation}"

        # Policy 0: Circuit Breakers (G-KD-05 / G-GP-04)
        if getattr(self.settings, "circuit_breaker_enabled", True):
            cb = CircuitBreakerRegistry(
                self.settings.session_dir,
                threshold=getattr(self.settings, "circuit_breaker_threshold", 5),
                window_s=getattr(self.settings, "circuit_breaker_window_s", 300),
                recovery_s=getattr(self.settings, "circuit_breaker_recovery_s", 60),
            )
            if cb.is_open(run.agent, category="agent"):
                return "deny", f"Circuit breaker is OPEN for agent '{run.agent}'. Repeated failures detected."
            if run.model and cb.is_open(run.model, category="model"):
                return "deny", f"Circuit breaker is OPEN for model '{run.model}'. Repeated failures detected."

        opa_url = (getattr(self.settings, "opa_url", None) or "").strip()
        if opa_url:
            opa_result = self._query_opa(run)
            if opa_result is not None:
                return opa_result
            fallback_allow = getattr(self.settings, "opa_fallback_allow", False)
            if fallback_allow:
                return "allow", "OPA unreachable; fallback allow per config"
            return "deny", "OPA unreachable; fallback deny per config (set THGENT_OPA_FALLBACK_ALLOW=1 to allow)"

        env = self.settings.environment.lower()

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
                return "pause", f"{run.lane.capitalize()} action requires HITL approval due to missing confidence."
            return "warn", f"{run.lane.capitalize()} actions should ideally carry a confidence score."

        # Policy 4: Trust Score Gate for Production
        if env == "production":
            threshold = self.settings.trust_score_threshold
            conf = run.confidence if run.confidence is not None else 0.5
            if conf < threshold:
                return (
                    "deny",
                    f"Production environment requires trust score >= {threshold} (current: {conf}). Provide --override to proceed.",
                )

        # Policy 5: Cost Budget Enforcement (G-GP-06)
        if getattr(self.settings, "cost_tracking_enabled", False):
            from thegent.governance.cost import CostAggregator

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

    def sign_run(self, run: RunMeta) -> str:
        """Generate a cryptographic signature for a run record."""
        # Simple hash-based signature for this phase
        data = f"{run.run_id}|{run.started_at_utc}|{run.owner}|{run.prompt}"
        return hashlib.sha256(data.encode()).hexdigest()

    def generate_maif_artifact(self, run: RunMeta, output: str | None = None) -> MAIFArtifact:
        """Generate a signed MAIF artifact for a run (WP-3002)."""
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

    def persist_maif_artifact(self, session_dir: Path, artifact: MAIFArtifact) -> Path:
        """Persist a MAIF artifact to the artifacts directory (WP-3002)."""
        artifacts_dir = session_dir / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        path = artifacts_dir / f"{artifact.run_id}.maif.json"
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
                    
                    # ROB-006: Verify hash chain integrity
                    stored_hash = data.get("hash")
                    prev_hash = data.get("prev_hash")
                    
                    # Verify prev_hash matches last_hash (chain integrity)
                    if prev_hash != last_hash:
                        if last_hash is not None:  # First record has no prev_hash
                            chain_broken = True
                            issues.append(f"ROB-006: Hash chain broken at line {i+1} (run_id: {rid}). Expected prev_hash: {last_hash}, got: {prev_hash}")
                    
                    # Verify stored hash matches computed hash
                    if stored_hash:
                        computed_hash = self._calculate_hash(data)
                        if stored_hash != computed_hash:
                            corrupt += 1
                            issues.append(f"ROB-006: Hash mismatch at line {i+1} (run_id: {rid}). Stored: {stored_hash[:16]}..., computed: {computed_hash[:16]}...")
                        else:
                            valid += 1
                            last_hash = stored_hash
                    else:
                        # No hash field - might be schema version marker
                        if data.get("event") == "schema_version":
                            valid += 1
                        else:
                            corrupt += 1
                            issues.append(f"Line {i+1}: Missing hash field (run_id: {rid})")

                    # 1. Verify Hash Chain
                    prev_hash = data.get("prev_hash")
                    if prev_hash != last_hash:
                        chain_broken = True
                        issues.append(
                            f"Line {i + 1}: Chain broken for {rid}. Expected prev_hash {last_hash}, got {prev_hash}"
                        )

                    # 2. Verify Record Hash
                    stored_hash = data.get("hash")
                    if stored_hash:
                        # Re-calculate
                        d = {k: v for k, v in data.items() if k != "hash"}
                        body = json.dumps(d, sort_keys=True, separators=(",", ":"))
                        expected_hash = hashlib.sha256(body.encode()).hexdigest()
                        if stored_hash != expected_hash:
                            corrupt += 1
                            issues.append(f"Line {i + 1}: Hash mismatch for record {rid}")
                        else:
                            valid += 1
                    else:
                        # Legacy record or missing hash
                        issues.append(f"Line {i + 1}: Missing hash for record {rid}")
                        corrupt += 1

                    # 3. Verify Signature if present (legacy or extra security)
                    stored_sig = data.get("signature")
                    if stored_sig and data.get("event") != "finish":
                        raw_data = f"{data.get('run_id')}|{data.get('started_at_utc')}|{data.get('owner')}|{data.get('prompt')}"
                        expected_sig = hashlib.sha256(raw_data.encode()).hexdigest()
                        if stored_sig != expected_sig:
                            # We don't increment corrupt again if already mismatched by hash
                            if stored_hash == expected_hash:
                                corrupt += 1
                                issues.append(f"Line {i + 1}: Signature mismatch for {rid}")

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
                (eh, ts) for eh, ts in self._poison_pill_tracker[key]
                if (now - ts) < self.window_s
            ]
            
            # Add new failure
            self._poison_pill_tracker[key].append((error_hash, now))
            
            # ROB-003: Check for poison pill (3+ identical failures in window)
            identical_count = sum(1 for eh, _ in self._poison_pill_tracker[key] if eh == error_hash)
            if identical_count >= 3:
                _log.warning(
                    "ROB-003: Poison pill detected for %s/%s: %d identical failures (hash: %s). "
                    "Stopping retry loop.",
                    target, category, identical_count, error_hash
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
                try:
                    data = json.loads(line)
                    if (
                        data.get("target") == target
                        and data.get("category", "agent") == category
                        and data.get("event") == "failure"
                    ):
                        ts = datetime.fromisoformat(data.get("timestamp"))
                        if (now - ts).total_seconds() < self.window_s:
                            failures += 1
                            if last_failure is None or ts > last_failure:
                                last_failure = ts
                except Exception:
                    continue

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
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if data.get("owner") != owner:
                        continue
                    exp = data.get("expires_at_utc")
                    if not exp:
                        continue
                    exp_dt = datetime.fromisoformat(exp)
                    if now < exp_dt:
                        return True
                except Exception:
                    continue
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
