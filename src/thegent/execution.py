"""Execution run metadata and registry for thegent orchestration."""

import hashlib
import json
import logging
import os
import socket
import urllib.error
import urllib.request
import uuid
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field

_log = logging.getLogger(__name__)


class RunState(str, Enum):
    """Run lifecycle state for state-aware orchestration (G-KD-03)."""

    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class RunMeta(BaseModel):
    """Metadata for a single agent/droid execution run."""

    run_id: str = Field(default_factory=lambda: f"run_{uuid.uuid4().hex[:8]}")
    correlation_id: Optional[str] = None
    agent: str
    model: Optional[str] = None
    mode: str = "write"
    prompt: str
    cwd: str
    owner: str
    started_at_utc: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    ended_at_utc: Optional[str] = None
    duration_s: Optional[float] = None
    exit_code: Optional[int] = None
    status: str = "started"  # started, running, completed, failed, timed_out
    error_class: Optional[str] = None  # usage_limit, timeout, logic_error, api_error
    signature: Optional[str] = None
    policy_result: Optional[str] = None  # allow, deny, warn
    policy_reason: Optional[str] = None
    override_reason: Optional[str] = None
    override_by: Optional[str] = None
    rationale: Optional[str] = None  # WP-4002/4007: Full explanation
    feedback_score: Optional[float] = None  # WP-4008
    feedback_note: Optional[str] = None
    host: str = Field(default_factory=socket.gethostname)
    pid: int = Field(default_factory=os.getpid)
    is_background: bool = False
    lane: str = "standard"  # standard, critical, recovery
    idempotency_token: Optional[str] = None
    confidence: Optional[float] = None
    arbitration: Optional[str] = None  # leader, follower, consensus
    
    # Audit trail chaining (WP-3004)
    prev_hash: Optional[str] = None
    hash: Optional[str] = None
    
    # Optional routing contract context
    route_contract: Optional[dict[str, Any]] = None
    route_request: Optional[dict[str, Any]] = None

    # WP-3006: Compliance evidence retention — domain tagging for tiered retention
    domain_tag: Optional[str] = None  # e.g. project-id, compliance-domain, lane

    # XA4: Contract version in task/run metadata for negotiation
    contract_version: Optional[str] = None


class CheckpointMeta(BaseModel):
    """Metadata for a DAG/state checkpoint."""

    checkpoint_id: str = Field(default_factory=lambda: f"ckpt_{uuid.uuid4().hex[:8]}")
    created_at_utc: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    reason: str
    dag_content: str
    session_dir: str
    owner: str


class RunRegistry:
    """Manages persistence and retrieval of execution runs."""

    SCHEMA_VERSION = 1

    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.registry_path = session_dir / "run_registry.jsonl"
        self._ensure_version_marker()

    def _ensure_version_marker(self):
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

    def _get_last_hash(self) -> Optional[str]:
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

    def register_start(self, run: RunMeta):
        """Record the start of a run with hash chaining."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        run.prev_hash = self._get_last_hash()
        data = run.model_dump()
        run.hash = self._calculate_hash(data)
        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(run.model_dump_json() + "\n")

    def register_end(
        self,
        run_id: str,
        exit_code: int,
        status: str,
        ended_at_utc: str,
        duration_s: float,
        error_class: Optional[str] = None,
        cost_usd: Optional[float] = None,
    ):
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

    def register_feedback(self, run_id: str, score: float, note: Optional[str] = None):
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
        continuity_snapshot: Optional[dict[str, Any]] = None,
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

    def get_run_state(self, run_id: str) -> Optional[RunState]:
        """Return current run state from registry events (G-KD-03)."""
        if not self.registry_path.exists():
            return None
        state: Optional[RunState] = None
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get("run_id") != run_id:
                        continue
                    ev = data.get("event")
                    if ev == "start":
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
        sorted_runs = sorted(
            runs.values(), 
            key=lambda x: x.get("started_at_utc", ""), 
            reverse=True
        )
        return sorted_runs[:limit]

    def find_by_token(self, token: str) -> Optional[dict[str, Any]]:
        """Find the most recent run with a given idempotency token."""
        if not self.registry_path.exists():
            return None
        
        best: Optional[dict[str, Any]] = None
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
                        else:
                            # Start event: if we don't have this run or it's newer, use it
                            if not best or data.get("started_at_utc", "") >= best.get("started_at_utc", ""):
                                best = data
                except Exception:
                    continue
        return best

    def get_calibration_factor(self, agent: str) -> float:
        """Calculate calibration factor (avg feedback / avg confidence) for an agent."""
        if not self.registry_path.exists():
            return 1.0
        
        relevant_runs = []
        runs: dict[str, dict[str, Any]] = {}
        
        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    rid = data.get("run_id")
                    if not rid: continue
                    
                    if data.get("event") == "finish":
                        if rid in runs: runs[rid].update(data)
                    elif data.get("event") == "feedback":
                        if rid in runs: runs[rid]["feedback_score"] = data.get("feedback_score")
                    else:
                        if data.get("agent") == agent:
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


class CheckpointRegistry:
    """Manages persistence and retrieval of state checkpoints."""

    def __init__(self, session_dir: Path):
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

    def get_checkpoint(self, checkpoint_id: str) -> Optional[dict[str, Any]]:
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

    def __init__(self, settings: Any):
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
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            result = data.get("result") or {}
            allow = result.get("allow", False)
            reason = result.get("reason", "OPA decision")
            return ("allow", reason) if allow else ("deny", reason)
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError) as e:
            _log.warning("OPA query failed (%s): %s", url, e)
            return None

    def evaluate(self, run: RunMeta, registry: Optional[RunRegistry] = None) -> tuple[str, str]:
        """
        Evaluate a run against active policies.
        Returns (result, reason) where result is 'allow', 'deny', or 'warn'.
        G-GP-01: When THGENT_OPA_URL is set, delegates to OPA first; falls back to Python logic on failure.
        """
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
                old_conf = run.confidence
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
            return "warn", f"{run.lane.capitalize()} actions should ideally carry a confidence score."

        # Policy 4: Trust Score Gate for Production
        if env == "production":
            threshold = self.settings.trust_score_threshold
            conf = run.confidence if run.confidence is not None else 0.5
            if conf < threshold:
                return "deny", f"Production environment requires trust score >= {threshold} (current: {conf}). Provide --override to proceed."

        return "allow", "All policies passed."


class TrustBoundaryValidator:
    """WP-3007: Validates environment transitions (e.g. staging→production)."""

    def __init__(self, session_dir: Path):
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

    def __init__(self, registry_path: Path):
        self.registry_path = registry_path

    def sign_run(self, run: RunMeta) -> str:
        """Generate a cryptographic signature for a run record."""
        # Simple hash-based signature for this phase
        data = f"{run.run_id}|{run.started_at_utc}|{run.owner}|{run.prompt}"
        return hashlib.sha256(data.encode()).hexdigest()

    def verify_registry(self) -> dict[str, Any]:
        """Verify the integrity of all records in the registry, including the hash chain."""
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
                    
                    # 1. Verify Hash Chain
                    prev_hash = data.get("prev_hash")
                    if prev_hash != last_hash:
                        chain_broken = True
                        issues.append(f"Line {i+1}: Chain broken for {rid}. Expected prev_hash {last_hash}, got {prev_hash}")
                    
                    # 2. Verify Record Hash
                    stored_hash = data.get("hash")
                    if stored_hash:
                        # Re-calculate
                        d = {k: v for k, v in data.items() if k != "hash"}
                        body = json.dumps(d, sort_keys=True, separators=(",", ":"))
                        expected_hash = hashlib.sha256(body.encode()).hexdigest()
                        if stored_hash != expected_hash:
                            corrupt += 1
                            issues.append(f"Line {i+1}: Hash mismatch for record {rid}")
                        else:
                            valid += 1
                    else:
                        # Legacy record or missing hash
                        issues.append(f"Line {i+1}: Missing hash for record {rid}")
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
                                issues.append(f"Line {i+1}: Signature mismatch for {rid}")
                    
                    last_hash = stored_hash
                except Exception as e:
                    corrupt += 1
                    issues.append(f"Line {i+1}: JSON decode error: {e}")

        return {
            "status": "passed" if (corrupt == 0 and not chain_broken) else "failed",
            "valid_count": valid,
            "corrupt_count": corrupt,
            "chain_broken": chain_broken,
            "issues": issues,
        }


class CircuitBreakerRegistry:
    """Tracks failures and manages circuit states for models/agents."""

    def __init__(self, session_dir: Path, threshold: int = 5, window_s: int = 300, recovery_s: int = 60):
        self.session_dir = session_dir
        self.registry_path = session_dir / "circuit_breakers.jsonl"
        self.threshold = threshold
        self.window_s = window_s
        self.recovery_s = recovery_s

    def record_failure(self, target: str, category: str = "agent"):
        """Record a failure for a target in a specific category."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        event = {
            "target": target,
            "category": category,
            "event": "failure",
            "timestamp": datetime.now(UTC).isoformat(),
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
                    if data.get("target") == target and data.get("category", "agent") == category and data.get("event") == "failure":
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

    def __init__(self, session_dir: Path):
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

    def __init__(self, session_dir: Path):
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
