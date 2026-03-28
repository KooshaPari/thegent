"""Execution run metadata and registry for thegent orchestration."""

import hashlib
import orjson as json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from phenotype_thegent_execution.execution.resilience import OverrideRegistry
from phenotype_thegent_execution.execution_coercion_helpers import as_bool as _as_bool_impl
from phenotype_thegent_execution.execution_coercion_helpers import as_float as _as_float_impl
from phenotype_thegent_execution.execution_coercion_helpers import as_int as _as_int_impl
from phenotype_thegent_execution.execution_hash_helpers import calculate_stable_record_hash

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


from .state import RunMeta
from .registry import RunRegistry


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
                fh.write(json.dumps(event, sort_keys=True).decode())
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
            from phenotype_thegent_audit.governance.input_guardrails import guardrails_from_env

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
            from phenotype_thegent_core.contracts.telemetry import ContractTelemetry

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
            from phenotype_thegent_routing.cost.aggregator import CostAggregator

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


class KPIManager:
    """WP-Y7: TRAFFIC KPI framework (10-metric)."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir

    def get_kpis(self) -> dict[str, Any]:
        """Calculate the 10 core KPIs for the dashboard."""
        from phenotype_thegent_core.contracts.telemetry import ContractTelemetry
        from phenotype_thegent_execution.execution import RunRegistry

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
        from phenotype_thegent_core.maif.rust_manager import RustMAIFManager

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
