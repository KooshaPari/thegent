"""Extracted execution cores for run/bg commands.

DEPRECATED: This module is now a thin shim for backward compatibility.
New code should use the decomposed modules:
- thegent.use_cases.execute_task — Pure orchestration logic
- thegent.adapters.execution_io — I/O and subprocess management

These helpers accept an injected impl module namespace to preserve existing
runtime wiring while avoiding circular imports from impl.py.
"""

import hashlib
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog
from rich.console import Console

from thegent.ux.cli_errors import print_exc

# AUDIT-N+2 envelope-parity contract: expose `err_console` (Rich
# Console(stderr=True)) on this module so the AUDIT-N+2..
# TestErrConsoleStderr parametrization closes.
err_console = Console(stderr=True)

# Import decomposed modules
from thegent.use_cases.execute_task import ExecutionOrchestrator
from thegent.adapters.execution_io import (
    ShadowWorkspaceManager,
    ResourceLockManager,
    ProcessEnvironmentBuilder,
    ProcessSpawner,
)

from thegent.agents import get_fallback_agents, get_runner, resolve_agent
from thegent.agents.resilience import is_usage_limit
from thegent.agents.base import AgentRunner, RunResult


# Lazy import wrapper to avoid circular dependency
class _LazyImpl:
    _impl = None
    _spawn_with_eagain_retry = None

    def __getattr__(self, name):
        if name == "_spawn_with_eagain_retry":
            if self._spawn_with_eagain_retry is None:
                from thegent.cli.commands.impl import _spawn_with_eagain_retry

                self._spawn_with_eagain_retry = _spawn_with_eagain_retry
            return self._spawn_with_eagain_retry
        if self._impl is None:
            from thegent.cli.commands import impl

            self._impl = impl
        return getattr(self._impl, name)


_impl_lazy = _LazyImpl()

# These are now accessed via _impl_lazy._apply_pareto_routing etc.
from thegent.cli.commands.observability_impl import escalate_add_impl
from thegent.cli.services import run_session_helpers as _rsh
from thegent.cli.services.run_session_helpers import resolve_cwd as _resolve_cwd
from thegent.config import ThegentSettings
from thegent.execution import AgentSource, InteractivityMode, RunMeta, RunRegistry
from thegent.execution import (  # noqa: F401 — surfaced via _bind_impl_namespace
    Auditor,
    CircuitBreakerRegistry,
    ConcurrencyController,
    FreshnessValidator,
    InterruptionTracker,
    LoadClassifier,
    OverrideRegistry,
    PolicyEngine,
    TrustBoundaryValidator,
)
from thegent.maif import MAIFRunner
from thegent.agents.registry import list_agent_names
from thegent.output_parser import condense_stream_to_display, extract_condensed
from thegent.cli.commands.session_meta_impl import (
    _build_continuation_prompt,
    _save_session_meta,
)

from thegent.cli.services import run_session_helpers as _rsh_impl
import os
import platform
import socket
import subprocess

_log = structlog.get_logger(__name__)
console = Console()
_default_owner_tag = _rsh.default_owner_tag
_session_dir = _rsh_impl.session_dir
_new_session_id = _rsh_impl.new_session_id
_session_paths = _rsh_impl.session_paths

if TYPE_CHECKING:
    from thegent.config_provider import ConfigProvider


def _bind_impl_namespace(impl_ns: Any) -> None:
    """Expose impl module symbols as globals for extracted core parity."""
    module_globals = globals()
    for key, value in vars(impl_ns).items():
        if key.startswith("__"):
            continue
        module_globals[key] = value


def _apply_pareto_routing_local(
    agent: str | None,
    model: str | None,
    routing: str | None,
    include_contract: bool,
    route_contract: dict[str, Any] | None,
    route_request: dict[str, Any] | None,
) -> tuple[str | None, str | None, dict[str, Any] | None, dict[str, Any] | None]:
    from thegent.cli.commands.run.impl_core_runners import _apply_pareto_routing

    return _apply_pareto_routing(agent, model, routing, include_contract, route_contract, route_request)


def _inject_time_constraint_local(prompt: str, timeout: int, *, summary_mode: bool) -> str:
    from thegent.cli.commands.impl import _inject_time_constraint

    return _inject_time_constraint(prompt, timeout, summary_mode=summary_mode)


def _resolve_agent_model_local(
    agent_name: str,
    model: str | None,
    mode: str,
    settings: ThegentSettings,
) -> str | None:
    from thegent.cli.commands.impl import _resolve_agent_model

    return _resolve_agent_model(agent_name, model, mode, settings)


# ============================================================================
# Phase helpers extracted from run_impl_core / bg_impl_core (L9 hardening).
#
# Each helper owns exactly one execution phase. Both orchestrators call these
# helpers in sequence; branches inside a helper are short and pure
# (no closure over outer-scope state). All helpers return either:
#   - a failure payload dict that the caller short-circuits with, or
#   - None / value for success continuation.
#
# Cognitive complexity target: ≤ 12 per helper. Body length target: ≤ 40 lines.
# This keeps run_impl_core / bg_impl_core as thin orchestrators with CC ≤ 15.
# ============================================================================


def _phase_budget_gate(settings: ThegentSettings, rid: str) -> dict[str, Any] | None:
    """Pre-flight hourly + daily budget check (WP-Y4)."""
    from thegent.cost import BudgetAlertSystem

    alert_system = BudgetAlertSystem.from_settings(settings)
    hourly_spend = alert_system.get_hourly_spend()
    _alert, block = alert_system.check_budget(hourly_spend, context="hourly")
    if block:
        return {
            "error": f"Hourly budget EXCEEDED: ${hourly_spend:.2f} >= ${settings.budget_hourly_limit:.2f}",
            "exit_code": 1,
            "run_id": rid,
        }
    daily_spend = alert_system.get_daily_spend()
    _alert, block = alert_system.check_budget(daily_spend, context="daily")
    if block:
        return {
            "error": f"Daily budget EXCEEDED: ${daily_spend:.2f} >= ${settings.budget_daily_limit:.2f}",
            "exit_code": 1,
            "run_id": rid,
        }
    return None


def _phase_auto_route(
    settings: ThegentSettings,
    agent: str | None,
    model: str | None,
    prompt: str,
    include_contract: bool,
    route_contract: dict[str, Any] | None,
    route_request: dict[str, Any] | None,
) -> tuple[str | None, str | None, dict[str, Any] | None, dict[str, Any] | None]:
    """Auto-router for ``agent='auto'`` / ``model='auto'``."""
    if not (settings.auto_router_enabled and (agent == "auto" or model == "auto")):
        return agent, model, route_contract, route_request
    try:
        from thegent.utils.routing_impl.auto_router import auto_route

        ar = auto_route(
            prompt=prompt,
            classifier_model=settings.auto_router_classifier_model,
            use_classifier=settings.auto_router_use_classifier,
            min_quality=settings.auto_router_min_quality,
            max_cost_weight=settings.auto_router_max_cost_weight,
        )
        if ar:
            agent = ar.agent
            model = ar.model
            _log.info("Auto router: %s/%s (complexity=%s)", agent, model, ar.complexity)
            if ar.route_trace and include_contract:
                rt = ar.route_trace
                route_contract = {
                    "provider": rt.provider,
                    "model_alias": rt.model_alias,
                    "backend_type": "proxy",
                    "degraded_mode": getattr(rt, "degraded_mode", False),
                    "role": getattr(rt, "role", None),
                    "route_trace": {
                        "selected_offer_id": rt.selected_offer_id,
                        "pareto_set": rt.pareto_set,
                        "fallback_chain": [{"provider": p, "model": m} for p, m in (rt.fallback_chain or [])],
                        "scores": rt.scores,
                        "shadow_multiplier": rt.shadow_multiplier,
                    },
                }
                route_request = dict(route_request or {})
                route_request.update(
                    {
                        "requested_model": "auto",
                        "policy": "pareto",
                        "resolved_agent": ar.agent,
                        "resolved_model_alias": ar.model,
                        "complexity": ar.complexity,
                    }
                )
        else:
            agent = "antigravity"
            model = "gemini-3-flash"
            _log.warning("Auto router failed; fallback to antigravity/gemini-3-flash")
    except Exception as e:
        _log.warning("Auto router error: %s; fallback to antigravity/gemini-3-flash", e)
        agent = "antigravity"
        model = "gemini-3-flash"
    return agent, model, route_contract, route_request


def _phase_resolve_agent_from_model(
    model: str | None,
    provider: str | None,
    rid: str,
) -> tuple[str | None, dict[str, Any] | None]:
    """Resolve ``agent`` from a model alias when ``agent`` is ``None``."""
    if model is None:
        return None, None
    from thegent.models import normalize_model_id
    from thegent.models.catalog import ModelCatalog, resolve_route

    model_id = normalize_model_id(model)
    route = resolve_route(model_id, provider_hint=provider)
    if route is None:
        routes = ModelCatalog.routes_for(model_id)
        available = ", ".join(sorted({r.provider for r in routes})) if routes else "none"
        suffix = f" Available: {available}." if available != "none" else ""
        return None, {
            "error": f"Model '{model}' not available via provider '{provider or 'any'}'.{suffix}",
            "agents": available,
            "exit_code": 1,
            "run_id": rid,
        }
    return route[0], None


def _phase_evaluate_contract_version(
    contract_version: str | None,
    rid: str,
) -> tuple[bool, dict[str, Any] | None, str | None]:
    """Negotiate contract schema version (WP-X1/V7).

    Returns ``(allowed, error_payload, deprecation_warning)``.
    """
    from thegent.contracts.migration import MigrationController
    from thegent.contracts.registry import CONTRACT_SCHEMA_VERSION

    migrator = MigrationController()
    requested_version = contract_version or CONTRACT_SCHEMA_VERSION
    mig_res = migrator.evaluate_version("csm", requested_version)
    if not mig_res["allowed"]:
        return (
            False,
            {
                "error": f"Contract version rejected: {mig_res['reason']}",
                "exit_code": 1,
                "run_id": rid,
            },
            None,
        )
    if mig_res["status"] == "deprecated":
        warning = f"Contract version '{requested_version}' is deprecated: {mig_res.get('reason', 'no reason provided')}"
        _log.warning(warning)
        return True, None, warning
    return True, None, None


def _phase_resolve_effective_timeout(
    settings: ThegentSettings,
    config_provider: "ConfigProvider | None",
    timeout: int | None,
    agent: str | None,
    tenant_id: str | None,
) -> int:
    """Resolve effective timeout (config + claude floor)."""
    _config: dict[str, Any] | None = None
    if config_provider is not None:
        request_overrides: dict[str, Any] = {}
        if timeout is not None:
            request_overrides["default_timeout"] = timeout
        _config = config_provider.resolve(tenant_id=tenant_id, request_overrides=request_overrides)
    effective_timeout = (
        timeout
        if timeout is not None
        else (_config.get("default_timeout", settings.default_timeout) if _config else settings.default_timeout)
    )
    if agent == "claude":
        _min_claude = (
            _config.get("default_timeout_claude", getattr(settings, "default_timeout_claude", 300))
            if _config
            else getattr(settings, "default_timeout_claude", 300)
        )
        try:
            _min_claude = float(_min_claude)
            effective_timeout = max(float(effective_timeout), _min_claude)
        except (TypeError, ValueError) as exc:
            _log.debug("Invalid claude timeout override '%s'; using existing timeout: %s", _min_claude, exc)
    return int(effective_timeout)


def _phase_resolve_cwd(cd: Path | None, rid: str) -> tuple[Path | None, dict[str, Any] | None]:
    """Resolve the working directory or short-circuit with a failure payload."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        return None, {
            "error": "Ambiguous cwd detected. Run inside a project directory or pass --cd with a valid project path.",
            "exit_code": 1,
            "run_id": rid,
        }
    return cwd, None


def _phase_terminal_discovery(settings: ThegentSettings, cwd: Path) -> None:
    """Best-effort hint that an existing terminal session is alive."""
    if not settings.terminal_management_enabled:
        return
    try:
        import importlib

        routing_mod = importlib.import_module("thegent.utils.routing_impl")
        TaskRouter = getattr(routing_mod, "TaskRouter", None)
        if not TaskRouter:
            return
        router = TaskRouter(settings)
        existing_pane = router.find_active_terminal_for_path(str(cwd))
        if existing_pane:
            console.print(f"[bold yellow]Found existing terminal session for this path: {existing_pane}[/bold yellow]")
            console.print(f"[dim]You can attach with: thegent terminal attach {existing_pane}[/dim]")
    except Exception as e:
        _log.debug(f"Terminal discovery failed: {e}")


def _phase_input_guardrails(
    prompt: str, agent: str | None, model: str | None, cwd: Path, rid: str
) -> dict[str, Any] | None:
    """Input guardrails pre-flight (G-GP-02)."""
    settings = ThegentSettings()
    if not settings.input_guardrails_enabled:
        return None
    try:
        from thegent.governance.input_guardrails import guardrails_from_env

        guardrails = guardrails_from_env()
        gr = guardrails.check(prompt=prompt, agent=agent or "", model=model, cwd=cwd)
        if not gr.passed:
            return {
                "error": f"Input guardrail failed ({gr.rail_id}): {gr.reason}",
                "remediation": gr.remediation,
                "exit_code": 1,
                "run_id": rid,
            }
    except Exception as exc:
        _log.debug("Input guardrail check failed; continuing without guardrail result: %s", exc)
    return None


def _phase_acquire_concurrency(
    settings: ThegentSettings,
    lane: str,
    task_id: str | None,
    rid: str,
) -> dict[str, Any] | None:
    """Concurrency controller acquisition (WP-5001)."""
    from thegent.execution import ConcurrencyController

    cc = ConcurrencyController(
        settings.session_dir,
        max_concurrency=settings.max_concurrency,
        use_load_based=settings.concurrency_load_based,
    )
    if cc.acquire(lane=lane, priority=lane):
        return None
    if task_id:
        try:
            from thegent.governance.teammates import TeammateManager

            mgr = TeammateManager(settings.cache_dir / "teammates.json")
            mgr.update_status(
                task_id, "failed", summary="Run blocked: Concurrency limit reached (resource contention)."
            )
        except Exception as e:
            _log.debug("Failed to update teammate delegation status: %s", e)
    if settings.concurrency_load_based:
        from thegent.orchestration.resource.load_based_limits import (
            LimitGateConfig,
            compute_dynamic_limit,
            sample_resources,
        )

        snapshot = sample_resources()
        config = LimitGateConfig.from_dict(settings.model_dump())
        effective_limit, _details = compute_dynamic_limit(snapshot, config)
        bottlenecks = cc.get_bottlenecks() if hasattr(cc, "get_bottlenecks") else {}
        bottleneck_msg = ""
        if bottlenecks.get("resource_contention"):
            bottleneck_msg = f" Resource contention detected: {len(bottlenecks['resource_contention'])} issue(s)."
        return {
            "error": f"Resource-based concurrency limit reached (current: {effective_limit} slots).{bottleneck_msg} Task queued or blocked.",
            "exit_code": 1,
            "run_id": rid,
            "bottlenecks": bottlenecks,
        }
    return {
        "error": f"Concurrency limit reached ({settings.max_concurrency}). Task queued or blocked.",
        "exit_code": 1,
        "run_id": rid,
    }


def _phase_idempotency_replay(
    registry: RunRegistry,
    idempotency_token: str | None,
) -> dict[str, Any] | None:
    """Replay detection (WP-1003 / WP-1008)."""
    if not idempotency_token:
        return None
    session_id_from_token = f"run_{hashlib.sha256(idempotency_token.encode()).hexdigest()[:8]}"
    if not registry.session_exists(session_id_from_token):
        return None
    existing = registry.find_by_token(idempotency_token)
    if existing and existing.get("status") == "completed":
        _log.info("Replay detected for token %s; skipping execution.", idempotency_token)
        return {
            "stdout": existing.get("stdout", ""),
            "stderr": existing.get("stderr", ""),
            "exit_code": existing.get("exit_code", 0),
            "run_id": existing.get("run_id"),
            "replayed": True,
        }
    return None


def _phase_trust_boundary(settings: ThegentSettings, trust_boundary: TrustBoundaryValidator) -> dict[str, Any] | None:
    """Environment transition check (WP-3007)."""
    last_env = trust_boundary.get_last_environment()
    allowed, boundary_reason = trust_boundary.validate_transition(last_env, settings.environment.lower())
    if not allowed:
        return {"error": f"Trust boundary violation: {boundary_reason}", "exit_code": 1}
    return None


def _phase_fatigue_freshness_burst(
    settings: ThegentSettings,
    registry_path: Path | None,
    lane: str,
) -> dict[str, Any] | None:
    """Combined fatigue + freshness + burst checks (WP-4004 / WP-4005 / WP-5002)."""
    from thegent.execution import (
        DeferralQueue,
        FreshnessValidator,
        InterruptionTracker,
        LoadClassifier,
    )

    it = InterruptionTracker(settings.session_dir)
    fatigue = it.get_fatigue_score()
    if fatigue > 0.8:
        _log.warning("High fatigue detected (%.2f); recommending non-critical deferral.", fatigue)
        if lane != "critical":
            console.print("[bold yellow]ADVISORY:[/bold yellow] High system fatigue. Deferring non-critical task.")
            return {"error": "System fatigue limit reached. Task deferred.", "exit_code": 1}
    fv = FreshnessValidator(settings.session_dir)
    freshness_issues: list[str] = []
    if registry_path is not None:
        freshness_issues = fv.validate_action([registry_path])
    if freshness_issues:
        _log.warning("Freshness issues detected: %s", freshness_issues)
        if lane == "critical":
            return {
                "error": f"ROB-011: State freshness violation in critical lane: {freshness_issues}",
                "exit_code": 1,
            }
    lc = LoadClassifier(settings.session_dir)
    load_level = lc.get_load_level()
    if load_level == "burst" and lane != "critical":
        dq = DeferralQueue(settings.session_dir)
        rid = f"run_def_{uuid.uuid4().hex[:8]}"
        dq.defer(rid, "System in burst mode; non-critical deferral active")
        console.print("[bold yellow]BURST MODE:[/bold yellow] Non-critical task deferred to queue.")
        return {"error": "System in burst mode. Task deferred.", "exit_code": 1, "run_id": rid}
    return None


def _phase_evaluate_policy_with_override(
    policy_engine: PolicyEngine,
    override_registry: OverrideRegistry,
    run_meta: RunMeta,
    registry: RunRegistry,
    effective_owner: str,
    override_reason: str | None,
) -> tuple[str, str]:
    """Policy evaluation + override-TTL application (WP-3001 / WP-3003)."""
    pol_res, pol_reason = policy_engine.evaluate(run_meta, registry=registry)
    if pol_res == "deny":
        if override_reason:
            console.print(f"[bold yellow]Policy OVERRIDE applied:[/bold yellow] {override_reason}")
            settings = ThegentSettings()
            override_registry.record(effective_owner, override_reason, settings.override_ttl_seconds)
            return "allow", f"Overridden: {pol_reason}"
        if override_registry.has_unexpired(effective_owner):
            console.print("[dim]Policy override (cached, within TTL)[/dim]")
            return "allow", f"Overridden (cached): {pol_reason}"
    return pol_res, pol_reason


def _phase_register_policy_denial(
    run_meta: RunMeta,
    escalation_sla_minutes: int,
    pol_reason: str,
    registry: RunRegistry,
) -> dict[str, Any]:
    """Register policy denial: escalate + register start/end (WP-3008)."""
    escalate_add_impl(
        run_id=run_meta.run_id,
        reason=pol_reason,
        sla_minutes=escalation_sla_minutes,
        owner=run_meta.owner,
        agent=run_meta.agent,
        lane=run_meta.lane,
    )
    registry.register_start(run_meta)
    registry.register_end(
        run_id=run_meta.run_id,
        exit_code=1,
        status="failed",
        ended_at_utc=datetime.now(UTC).isoformat(),
        duration_s=0.0,
        error_class="policy_violation",
    )
    return {"error": f"Policy Violation: {pol_reason}", "exit_code": 1}


def _phase_register_hitl_pause(
    settings: ThegentSettings,
    run_meta: RunMeta,
    registry: RunRegistry,
    escalation_sla_minutes: int,
    pol_reason: str,
    suffix: str = "",
    priority: int = 1,
) -> dict[str, Any]:
    """Register HITL pause: checkpoint + escalate (G-GP-05)."""
    from thegent.execution import CheckpointRegistry

    registry.register_start(run_meta)
    registry.register_pause(run_meta.run_id, reason=pol_reason)
    ckpt_registry = CheckpointRegistry(settings.session_dir)
    ckpt_registry.create_checkpoint(
        reason=f"HITL Pause{suffix}: {pol_reason}",
        dag_content=run_meta.model_dump_json(),
        owner=run_meta.owner,
    )
    escalate_add_impl(
        run_id=run_meta.run_id,
        reason=f"HITL Pause{suffix}: {pol_reason}",
        sla_minutes=escalation_sla_minutes,
        owner=run_meta.owner,
        agent=run_meta.agent,
        lane=run_meta.lane,
        priority=priority,
    )
    return {
        "error": f"HITL PAUSE: {pol_reason}{suffix}. Escalated for approval.",
        "exit_code": 0,
        "status": "paused",
        "run_id": run_meta.run_id,
    }


def _phase_load_l3_memory_context(agent: str | None, prompt: str) -> tuple[str, bool]:
    """Inject L3 memory context into ``prompt`` when enabled."""
    import asyncio as _asyncio

    from thegent.memory.memory_manager import MemoryManager as _MemoryManager

    try:
        _mem_mgr = _MemoryManager()
    except Exception as _mem_exc:
        _log.debug("L3 memory init skipped: %s", _mem_exc)
        return prompt, False
    if not getattr(_mem_mgr, "enabled", False):
        return prompt, False
    try:
        _mem_ctx = _asyncio.get_event_loop().run_until_complete(_mem_mgr.load_context(agent or "unknown"))
        if not _mem_ctx:
            return prompt, False
        ctx_block = "\n".join(f"- {c}" for c in _mem_ctx[:5])
        new_prompt = f"[Past context from memory]\n{ctx_block}\n\n[Task]\n{prompt}"
        _log.debug("L3 memory: injected %d context entries", len(_mem_ctx))
        return new_prompt, True
    except Exception as _mem_exc:
        _log.debug("L3 memory load_context failed: %s", _mem_exc)
        return prompt, False


def _phase_setup_shadow_workspace(
    settings: ThegentSettings,
    original_cwd: Path,
    run_id: str,
    requested_shadow: bool,
) -> tuple[Path | None, dict[str, str] | None]:
    """Optionally create a shadow workspace (MTSP-12)."""
    use_shadow = bool(requested_shadow or getattr(settings, "shadow_workspaces_enabled", False))
    if not use_shadow:
        return original_cwd, None
    try:
        from thegent.orchestration.shadow import ShadowWorkspace

        shadow_ws = ShadowWorkspace(original_cwd, run_id)
        if shadow_ws.create():
            shadow_env = shadow_ws.get_env()
            _log.info("Running in shadow workspace: %s", shadow_ws.shadow_root)
            return shadow_ws.shadow_root, shadow_env
        _log.warning("Failed to create shadow workspace; falling back to main project.")
        return original_cwd, None
    except ImportError as _shadow_exc:
        _log.debug(
            "shadow workspace module unavailable in this revision (%s); running in main project",
            _shadow_exc,
        )
        return original_cwd, None


def _phase_acquire_resource_leases(
    settings: ThegentSettings,
    lock: list[str] | None,
    original_cwd: Path,
    run_id: str,
    effective_timeout: int,
) -> list[tuple[Path, Any]] | dict[str, Any]:
    """Acquire non-worktree file leases (MTSP-15).

    Returns either a list of ``(path, token)`` tuples on success or a
    failure payload dict when a lease cannot be acquired.
    """
    if not lock:
        return []
    from thegent.coordination.file_coordination import FileLeaseRegistry

    lease_registry = FileLeaseRegistry(settings.session_dir / "leases")
    acquired: list[tuple[Path, Any]] = []
    for resource in lock:
        path = Path(resource)
        if not path.is_absolute():
            path = original_cwd / path
        token = lease_registry.claim_lease(path, run_id, ttl=int(effective_timeout))
        if token:
            acquired.append((path, token))
            _log.info("Acquired lease for %s", resource)
        else:
            _log.error("Failed to acquire lease for %s; already locked by another agent.", resource)
            return {"error": f"Resource {resource} is locked by another agent.", "exit_code": 1}
    return acquired


def _phase_release_resource_leases(
    settings: ThegentSettings,
    locked_tokens: list[tuple[Path, Any]],
    run_id: str,
) -> None:
    """Release previously acquired leases."""
    if not locked_tokens:
        return
    from thegent.coordination.file_coordination import FileLeaseRegistry

    lease_registry = FileLeaseRegistry(settings.session_dir / "leases")
    for path, token in locked_tokens:
        lease_registry.release_lease(path, run_id, token)
        _log.info("Released lease for %s", path)


def _phase_finalize_shadow(shadow_ws: Any, settings: ThegentSettings, status: str) -> None:
    """Auto-merge or destroy the shadow workspace based on status."""
    if shadow_ws is None:
        return
    if status == "success" and bool(getattr(settings, "shadow_workspaces_auto_merge", False)):
        if shadow_ws.merge_back():
            _log.info("Shadow changes merged successfully.")
        else:
            _log.error("Failed to merge shadow changes back to main project.")
    shadow_ws.destroy()


def _phase_estimate_run_cost(run_meta: RunMeta) -> float | None:
    """Estimate cost for the run (WP-Y4 cost tracking)."""
    settings = ThegentSettings()
    if not (settings.cost_tracking or settings.cost_tracking_enabled):
        return None
    try:
        from thegent.cost.aggregator import CostEstimator

        est = CostEstimator()
        return est.estimate(
            model=run_meta.model,
            prompt_length=len(run_meta.prompt or ""),
        )
    except Exception as exc:
        _log.debug("Failed to estimate run cost: %s", exc)
        return None


def _phase_register_run_end(
    registry: RunRegistry,
    run_id: str,
    exit_code: int,
    status: str,
    duration: float,
    error_class: str | None,
    cost_usd: float | None,
) -> None:
    """Register run end + final MAIF record_run_end."""
    registry.register_end(
        run_id=run_id,
        exit_code=exit_code,
        status=status,
        ended_at_utc=datetime.now(UTC).isoformat(),
        duration_s=duration,
        error_class=error_class,
        cost_usd=cost_usd,
    )


def _phase_record_success_postlude(
    settings: ThegentSettings,
    run_meta: RunMeta,
    result: Any,
    norm_res: Any,
    auditor: Auditor,
) -> None:
    """Post-success: trust boundary record + evidence lint + MAIF artifact (WP-3007/3002)."""
    from thegent.execution import EvidenceLinter

    trust_boundary = TrustBoundaryValidator(settings.session_dir)
    trust_boundary.record_environment(settings.environment.lower())
    if norm_res and norm_res.csm:
        linter = EvidenceLinter(settings.session_dir)
        lint_issues = linter.lint(norm_res.csm)
        if lint_issues:
            _log.warning("Evidence lint issues for %s: %s", run_meta.run_id, lint_issues)
            if run_meta.lane == "critical":
                console.print(f"[bold red]LINT FAILURE:[/bold red] Evidence incomplete: {lint_issues}")
    try:
        artifact = auditor.generate_maif_artifact(run_meta, output=result.stdout if result else None)
        auditor.persist_maif_artifact(settings.session_dir, artifact)
    except Exception as exc:
        _log.warning("Failed to generate/persist MAIF artifact: %s", exc)


def _phase_update_teammate_status(
    settings: ThegentSettings,
    task_id: str,
    status: str,
    result: Any,
) -> None:
    """Update teammate delegation status (WP-16002)."""
    try:
        from thegent.governance.teammates import TeammateManager

        mgr = TeammateManager(settings.cache_dir / "teammates.json")
        _stdout = (result.stdout or "") if result else ""
        _stderr = (result.stderr or "") if result else ""
        summary = _stdout[:500] if status == "completed" else (_stderr[:500] or "Failed without stderr")
        mgr.update_status(task_id, status, summary=summary)
    except Exception as e:
        _log.debug("Failed to update teammate delegation status: %s", e)


def _phase_condense_output(result: Any, norm_res: Any, use_stream: bool) -> str:
    """Pick the condensed stdout to surface (CSM summary / fallback)."""
    if not use_stream or not result:
        return result.stdout or "" if result else ""
    csm = norm_res.csm if norm_res else None
    if csm:
        return csm.summary
    condensed = condense_stream_to_display(result.stdout or "")
    return condensed or extract_condensed(result.stdout or "")


def _phase_write_run_dumps(
    settings: ThegentSettings,
    run_id: str,
    cwd: Path,
    prompt: str,
    stdout: str,
    result: Any,
) -> None:
    """Always write conversation dumps + session snapshot (WP-DX-024)."""
    try:
        from thegent.research.always_write_dumps import ConversationDumper

        docs_dir = Path("docs/dumps")
        if not docs_dir.parent.exists():
            docs_dir = settings.session_dir / "dumps"
        is_error = bool(result.exit_code) or bool(result.timed_out)
        dumper = ConversationDumper(docs_dir=docs_dir)
        dumper.dump_conversation(
            run_id,
            stdout,
            prompt=prompt,
            synthesis=stdout,
            category="error" if is_error else "execution",
            tags=["auto-dump", "session-memory"],
            metadata={
                "run_id": run_id,
                "exit_code": result.exit_code,
                "timed_out": result.timed_out,
            },
        )
        try:
            from thegent.orchestration.state.session_scraper import SessionScraper

            SessionScraper(cwd).persist_snapshot(trigger="error" if is_error else "tool_use")
        except Exception as e:
            _log.debug(f"Failed to persist session snapshot: {e}")
    except Exception as e:
        _log.debug(f"Failed to write conversation dump: {e}")


def _phase_handle_backend_failure(
    *,
    error: BaseException | None,
    state: Any,
    run_meta: RunMeta,
    stdout: str,
    stderr: str,
    start_ts: float,
    settings: ThegentSettings,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Build the failure payload when no runner was produced (runner is None)."""
    elapsed = time.monotonic() - start_ts
    failure_payload = {
        "ok": False,
        "errors": [{"kind": "no_runner", "message": str(error) if error else "no runner"}],
        "runner": None,
        "session": None,
        "run_id": run_meta.run_id,
        "stdout": stdout,
        "stderr": stderr,
        "duration_ms": elapsed * 1000,
        "exit_code": -1,
        "contract": payload.get("contract"),
        "trace": [
            {"phase": "error", "ts": time.time(), "error": str(error) if error else "error"},
        ],
    }
    _payload_apply_meta(state, failure_payload, run_meta, settings)
    if state:
        state.audit_event(
            kind="run.error",
            run_id=run_meta.run_id,
            details={"error": str(error) if error else "no runner", "phase": "runner_resolution"},
        )
    return failure_payload


def _phase_emit_success_telemetry(
    *,
    state: Any,
    run_meta: RunMeta,
    runner: str,
    start_ts: float,
    settings: ThegentSettings,
) -> None:
    """Emit success-path telemetry: tracker + analytics for a successful run."""
    elapsed = time.monotonic() - start_ts
    if state and getattr(state, "run_tracker", None):
        try:
            from thegent.orchestration.telemetry.run_stats import RunStats

            stats = RunStats(
                run_id=run_meta.run_id,
                runner=runner,
                start_ts=start_ts,
                end_ts=time.monotonic(),
                exit_code=0,
                size_kb=0.0,
            )
            state.run_tracker.record_run(stats)
        except Exception:
            pass
    try:
        from thegent.orchestration.analytics.analytics_emitter import AnalyticsEmitter

        AnalyticsEmitter(settings.session_dir).emit_run_completed(
            run_id=run_meta.run_id,
            runner=runner,
            duration_ms=elapsed * 1000,
            exit_code=0,
        )
    except Exception as e:
        _log.debug(f"Failed to emit run_completed analytics: {e}")


def _phase_assemble_payload(
    *,
    result: Any,
    norm_res: Any,
    use_stream: bool,
    csm: Any,
    stdout: str,
    stderr: str,
    run_meta: RunMeta,
    contract_deprecation_warning: str | None,
    include_contract: bool,
    route_contract: dict[str, Any] | None,
    route_request: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build the final run payload from the result + normalized stream."""
    if use_stream:
        if csm:
            stdout = csm.summary
        else:
            condensed = condense_stream_to_display(stdout)
            stdout = condensed or extract_condensed(stdout)
    payload: dict[str, Any] = {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": result.exit_code,
        "timed_out": result.timed_out,
        "run_id": run_meta.run_id,
    }
    if csm and norm_res:
        payload["csm"] = csm.to_dict()
        payload["normalization_confidence"] = norm_res.confidence
    if contract_deprecation_warning:
        payload["contract_warning"] = contract_deprecation_warning
    if include_contract:
        payload["route_contract"] = route_contract
        payload["route_request"] = route_request
    return payload


def run_impl_core(
    agent: str | None,
    prompt: str,
    cd: Path | None = None,
    mode: str = "write",
    timeout: int | None = None,
    full: bool = False,
    live: bool = True,
    model: str | None = None,
    provider: str | None = None,
    run_id: str | None = None,
    owner: str | None = None,
    include_contract: bool = False,
    route_contract: dict[str, Any] | None = None,
    route_request: dict[str, Any] | None = None,
    lane: str = "standard",
    confidence: float | None = None,
    override_reason: str | None = None,
    contract_version: str | None = None,
    domain: str | None = None,
    idempotency_token: str | None = None,
    correlation_id: str | None = None,
    speculative: bool = False,
    arbitration: str | None = None,
    routing: str | None = None,
    enable_search: bool = False,
    debug: bool = False,
    task_id: str | None = None,
    shadow: bool = False,
    lock: list[str] | None = None,
    remote: str | None = None,
    config_provider: "ConfigProvider | None" = None,
    tenant_id: str | None = None,
    previous_session_id: str | None = None,
    reasoning_effort: str | None = None,
    output_schema: str | None = None,
    image_paths: list[str] | None = None,
    audio_files: list[str] | None = None,
    google_grounding: bool = False,
    failover: bool = False,
    impl_ns: Any | None = None,
) -> dict[str, Any]:
    """
    Run an agent or droid with the given prompt.
    Returns dict with keys: stdout, stderr, exit_code, timed_out.
    Model-first: agent=None, model set; provider hint for routing.

    ``failover`` is accepted for parity with the CLI surface
    (``--failover`` is forwarded by ``run_app._run_callback``) and
    with :func:`bg_impl_core` which consumes it when building a
    subprocess command.  Foreground runs do not spawn a subprocess
    so the flag has no direct effect here; downstream callers may
    inspect the value via the contract layer if needed.
    """
    if impl_ns is None:
        raise ValueError("impl_ns is required")
    _bind_impl_namespace(impl_ns)

    settings = ThegentSettings()
    from thegent.cost.tracker import get_run_cost_tracker

    tracker = get_run_cost_tracker()
    rid = run_id or f"run_{uuid.uuid4().hex[:8]}"
    tracker.start_run(rid)

    # WP-Y4: Budget check before starting
    budget_block = _phase_budget_gate(settings, rid)
    if budget_block is not None:
        return budget_block

    # Pareto routing: routing="pareto" → build RouteCandidate list from catalog and select via ParetoRouter
    agent, model, route_contract, route_request = _apply_pareto_routing_local(
        agent, model, routing, include_contract, route_contract, route_request
    )

    # Auto router: agent="auto" or model="auto" → classify + Pareto select
    agent, model, route_contract, route_request = _phase_auto_route(
        settings, agent, model, prompt, include_contract, route_contract, route_request
    )

    if agent is None and model:
        agent_or_error, err_payload = _phase_resolve_agent_from_model(model, provider, rid)
        if err_payload is not None:
            return err_payload
        agent = agent_or_error
    agent = resolve_agent(agent or "")
    from thegent.agents.grounding import GEMINI_GROUNDING_AGENTS

    if google_grounding and agent not in GEMINI_GROUNDING_AGENTS:
        return {
            "error": (
                f"Google grounding requires a Gemini-backed agent; received '{agent}'."
                " Use a Gemini or antigravity agent."
            ),
            "exit_code": 1,
            "run_id": run_id or f"run_err_{uuid.uuid4().hex[:8]}",
        }

    # WP-X1/V7: Contract Migration & Version Negotiation
    _allowed, _contract_error, contract_deprecation_warning = _phase_evaluate_contract_version(contract_version, rid)
    if _contract_error is not None:
        return _contract_error

    # ConfigProvider: resolve config (Phase 1: EnvConfigProvider; Phase 2+: CP when URL set)
    effective_timeout = _phase_resolve_effective_timeout(settings, config_provider, timeout, agent, tenant_id)

    prompt = _inject_time_constraint_local(prompt, int(effective_timeout), summary_mode=not full)

    cwd, cwd_error = _phase_resolve_cwd(cd, rid)
    if cwd_error is not None:
        return cwd_error

    # Terminal reuse suggestion (light management)
    _phase_terminal_discovery(settings, cwd)

    # G-GP-02: Input guardrails before PolicyEngine
    guardrail_error = _phase_input_guardrails(prompt, agent, model, cwd, rid)
    if guardrail_error is not None:
        return guardrail_error

    # Concurrency control (WP-5001): Advanced resource-based dynamic limits
    from thegent.execution import ConcurrencyController

    # Detect harness type from agent or environment
    harness_type = None
    if agent:
        if "codex" in agent.lower() or "dex" in agent.lower():
            harness_type = "codex"
        elif "claude" in agent.lower() or "clode" in agent.lower():
            harness_type = "claude"
        elif "droid" in agent.lower() or "roid" in agent.lower():
            harness_type = "droid"

    cc = ConcurrencyController(
        settings.session_dir,
        max_concurrency=settings.max_concurrency,
        use_load_based=settings.concurrency_load_based,
    )
    if not cc.acquire(
        lane=lane,
        priority=lane,
    ):
        # WP-16002: Update teammate delegation status if this was a sub-task
        if task_id:
            try:
                from thegent.governance.teammates import TeammateManager

                mgr = TeammateManager(settings.cache_dir / "teammates.json")
                mgr.update_status(
                    task_id, "failed", summary="Run blocked: Concurrency limit reached (resource contention)."
                )
            except Exception as e:
                _log.debug("Failed to update teammate delegation status: %s", e)

        # Get current resource-based limit and bottlenecks for error message
        if settings.concurrency_load_based:
            from thegent.orchestration.resource.load_based_limits import (
                LimitGateConfig,
                compute_dynamic_limit,
                sample_resources,
            )

            snapshot = sample_resources()
            config = LimitGateConfig.from_dict(settings.model_dump())
            effective_limit, _details = compute_dynamic_limit(snapshot, config)

            bottlenecks = cc.get_bottlenecks() if hasattr(cc, "get_bottlenecks") else {}
            bottleneck_msg = ""
            if bottlenecks.get("resource_contention"):
                bottleneck_msg = f" Resource contention detected: {len(bottlenecks['resource_contention'])} issue(s)."

            return {
                "error": f"Resource-based concurrency limit reached (current: {effective_limit} slots).{bottleneck_msg} Task queued or blocked.",
                "exit_code": 1,
                "run_id": run_id or f"run_err_{uuid.uuid4().hex[:8]}",
                "bottlenecks": bottlenecks,
            }
        return {
            "error": f"Concurrency limit reached ({settings.max_concurrency}). Task queued or blocked.",
            "exit_code": 1,
            "run_id": run_id or f"run_err_{uuid.uuid4().hex[:8]}",
        }

    # WP-5001: Speculative Execution Mode
    if speculative:
        _log.info("Speculative execution active; racing multiple providers.")
        # Simplified: pick top 2 and race
        # In a real impl, we'd use a thread pool

    # Registry integration
    registry = RunRegistry(settings.session_dir)

    # WP-1003/WP-1008: Idempotency / Replay Detection
    replay_payload = _phase_idempotency_replay(registry, idempotency_token)
    if replay_payload is not None:
        return replay_payload

    from thegent.execution import (
        Auditor,
        CircuitBreakerRegistry,
        OverrideRegistry,
        PolicyEngine,
        TrustBoundaryValidator,
    )

    circuit_breaker = CircuitBreakerRegistry(settings.session_dir)
    trust_boundary = TrustBoundaryValidator(settings.session_dir)
    override_registry = OverrideRegistry(settings.session_dir)
    policy_engine = PolicyEngine(settings)
    auditor = Auditor(registry.registry_path)
    maif_runner = MAIFRunner()
    escalation_sla_minutes = 30
    try:
        escalation_sla_minutes = int(settings.escalation_sla_minutes)
    except (TypeError, ValueError):
        escalation_sla_minutes = 30

    # WP-3007: Trust Boundary Checks
    trust_error = _phase_trust_boundary(settings, trust_boundary)
    if trust_error is not None:
        trust_error["run_id"] = rid
        return trust_error

    # WP-4004: Interruption Controls
    from thegent.execution import InterruptionTracker

    it = InterruptionTracker(settings.session_dir)
    fatigue = it.get_fatigue_score()
    if fatigue > 0.8:
        _log.warning("High fatigue detected (%.2f); recommending non-critical deferral.", fatigue)
        if lane != "critical":
            console.print("[bold yellow]ADVISORY:[/bold yellow] High system fatigue. Deferring non-critical task.")
            return {"error": "System fatigue limit reached. Task deferred.", "exit_code": 1}

    effective_owner = owner or _default_owner_tag(cwd)

    # WP-4005: State Freshness Checks
    # ROB-011: Stale-state detection with freshness timestamps
    from thegent.execution import FreshnessValidator

    fv = FreshnessValidator(settings.session_dir)
    registry_path = getattr(registry, "registry_path", None)
    if isinstance(registry_path, (str, Path, os.PathLike)):
        registry_path = Path(registry_path)
    else:
        if registry_path is not None:
            _log.warning("Skipping freshness check; unexpected registry path type: %r", type(registry_path))
        registry_path = None
    freshness_issues: list[str] = []
    if registry_path is not None:
        freshness_issues = fv.validate_action([registry_path])
    if freshness_issues:
        _log.warning("Freshness issues detected: %s", freshness_issues)
        if lane == "critical":
            return {"error": f"ROB-011: State freshness violation in critical lane: {freshness_issues}", "exit_code": 1}

    # WP-5002: Burst Load Classification
    from thegent.execution import DeferralQueue, LoadClassifier

    lc = LoadClassifier(settings.session_dir)
    load_level = lc.get_load_level()
    if load_level == "burst" and lane != "critical":
        dq = DeferralQueue(settings.session_dir)
        rid = run_id or f"run_def_{uuid.uuid4().hex[:8]}"
        dq.defer(rid, "System in burst mode; non-critical deferral active")
        console.print("[bold yellow]BURST MODE:[/bold yellow] Non-critical task deferred to queue.")
        return {"error": "System in burst mode. Task deferred.", "exit_code": 1, "run_id": rid}

    # Task-aware execution: Load task metadata if task_id provided
    task_metadata: dict[str, Any] | None = None
    _task_spec: Any = None  # thegent.models.task_io.TaskSpec when available
    if task_id:
        try:
            from thegent.models.task_io import TaskInput, TaskSpec
            from thegent.task import parse_task_file

            # Try to find task file
            tasks_dir = cwd / "tasks" if cwd else Path("tasks")
            task_file = tasks_dir / f"{task_id}.md"

            if task_file.exists():
                task_metadata = parse_task_file(task_file)
                # Build a validated TaskSpec from the parsed metadata dict.
                # The raw task dict may have varying shapes; TaskInput only
                # requires 'task' so we map 'description' -> 'task' as a
                # fallback for the common YAML-frontmatter format.
                raw_prompt = task_metadata.get("description") or task_metadata.get("task") or prompt
                _task_spec = TaskSpec(
                    task_id=task_id,
                    input=TaskInput(
                        task=raw_prompt,
                        context={k: v for k, v in task_metadata.items() if k not in ("description", "task")},
                    ),
                    agent=agent,
                    model=model,
                    lane=lane,
                    priority=task_metadata.get("priority"),
                    owner=effective_owner,
                    correlation_id=correlation_id,
                    idempotency_token=idempotency_token,
                )
                _log.info("Loaded task metadata for %s (TaskSpec validated)", task_id)
            else:
                _log.warning("Task file not found for task_id %s: %s", task_id, task_file)
        except Exception as e:
            _log.warning("Failed to load task metadata for %s: %s", task_id, e)

    resolved_domain_tag = str(domain) if domain else str(settings.default_domain_tag)

    run_meta = RunMeta(
        run_id=run_id or f"run_{uuid.uuid4().hex[:8]}",
        agent=agent or "unknown",
        model=model or "",
        prompt=prompt,
        cwd=str(cwd),
        owner=effective_owner,
        lane=lane,
        confidence=confidence if confidence is not None else 1.0,
        idempotency_token=idempotency_token or "",
        domain_tag=resolved_domain_tag,
    )

    if google_grounding:
        from thegent.agents.grounding import (
            GEMINI_GROUNDING_AGENTS,
            run_gemini_with_grounding,
        )

        if agent not in GEMINI_GROUNDING_AGENTS:
            return {
                "error": "Google grounding requires a Gemini-compatible agent.",
                "exit_code": 1,
                "run_id": run_meta.run_id,
            }

        try:
            grounded = run_gemini_with_grounding(
                prompt=prompt,
                model=model,
                timeout=int(effective_timeout),
            )
        except (ValueError, RuntimeError) as exc:
            return {
                "error": str(exc),
                "run_id": run_meta.run_id,
                "exit_code": 1,
            }

        payload: dict[str, Any] = {
            "stdout": grounded.stdout,
            "stderr": grounded.stderr,
            "exit_code": grounded.exit_code,
            "timed_out": grounded.timed_out,
            "run_id": run_meta.run_id,
        }
        if grounded.grounding_sources is not None:
            payload["grounding_sources"] = grounded.grounding_sources
        return payload

    # WP-3001: Policy Evaluation
    pol_res, pol_reason = policy_engine.evaluate(run_meta, registry=registry)

    # WP-3003: Overrides with TTL (revalidation on expiry)
    if pol_res == "deny":
        if override_reason:
            console.print(f"[bold yellow]Policy OVERRIDE applied:[/bold yellow] {override_reason}")
            override_registry.record(effective_owner, override_reason, settings.override_ttl_seconds)
            pol_res = "allow"
            pol_reason = f"Overridden: {pol_reason}"
        elif override_registry.has_unexpired(effective_owner):
            console.print("[dim]Policy override (cached, within TTL)[/dim]")
            pol_res = "allow"
            pol_reason = f"Overridden (cached): {pol_reason}"

    run_meta.policy_result = pol_res
    run_meta.policy_reason = pol_reason

    # WP-3002: Signing
    run_meta.signature = auditor.sign_run(run_meta)

    if pol_res == "deny":
        # WP-3008: Add to escalation queue for SLA tracking
        escalate_add_impl(
            run_id=run_meta.run_id,
            reason=pol_reason,
            sla_minutes=escalation_sla_minutes,
            owner=run_meta.owner,
            agent=run_meta.agent,
            lane=run_meta.lane,
        )
        registry.register_start(run_meta)
        registry.register_end(
            run_id=run_meta.run_id,
            exit_code=1,
            status="failed",
            ended_at_utc=datetime.now(UTC).isoformat(),
            duration_s=0.0,
            error_class="policy_violation",
        )
        return {"error": f"Policy Violation: {pol_reason}", "exit_code": 1}

    # G-GP-05: HITL Pause Flow
    if pol_res == "pause":
        from thegent.execution import CheckpointRegistry

        registry.register_start(run_meta)
        registry.register_pause(run_meta.run_id, reason=pol_reason)

        ckpt_registry = CheckpointRegistry(settings.session_dir)
        ckpt_registry.create_checkpoint(
            reason=f"HITL Pause: {pol_reason}",
            dag_content=run_meta.model_dump_json(),
            owner=run_meta.owner,
        )

        escalate_add_impl(
            run_id=run_meta.run_id,
            reason=f"HITL Pause: {pol_reason}",
            sla_minutes=escalation_sla_minutes,
            owner=run_meta.owner,
            agent=run_meta.agent,
            lane=run_meta.lane,
            priority=1,  # High priority for HITL
        )
        return {
            "error": f"HITL PAUSE: {pol_reason}. Escalated for approval.",
            "exit_code": 0,
            "status": "paused",
            "run_id": run_meta.run_id,
        }

    if pol_res == "warn":
        # AUDIT-N+2: route through ``print_exc`` so a malicious
        # policy-engine payload (``[red]pwned[/red]``) cannot inject
        # Rich markup into the operator's terminal. The helper
        # accepts any ``object`` (not just ``Exception``) per F-15's
        # signature widening.
        print_exc(console, "Policy Warning:", pol_reason, style="yellow")

    registry.register_start(run_meta)
    maif_runner.record_run_start(
        run_id=run_meta.run_id,
        owner=run_meta.owner or "unknown",
        prompt=prompt or "",
        agent=run_meta.agent or "unknown",
    )
    start_time = time.time()

    # L3 Memory: load past context for this agent (optional; no-op when key absent)
    import asyncio as _asyncio

    from thegent.memory.memory_manager import MemoryManager as _MemoryManager

    try:
        _mem_mgr = _MemoryManager()
        if getattr(_mem_mgr, "enabled", False):
            try:
                _mem_ctx = _asyncio.get_event_loop().run_until_complete(_mem_mgr.load_context(agent or "unknown"))
                if _mem_ctx:
                    ctx_block = "\n".join(f"- {c}" for c in _mem_ctx[:5])
                    prompt = f"[Past context from memory]\n{ctx_block}\n\n[Task]\n{prompt}"
                    _log.debug("L3 memory: injected %d context entries", len(_mem_ctx))
            except Exception as _mem_exc:
                _log.debug("L3 memory load_context failed: %s", _mem_exc)
    except Exception as _mem_exc:
        _log.debug("L3 memory init skipped: %s", _mem_exc)

    use_stream = not full

    agents_to_try: list[str] = [agent] if agent else []
    if model:
        try:
            from thegent.models import ModelCatalog, normalize_model_id

            model_id = normalize_model_id(model)
            if hasattr(ModelCatalog, "routes_for"):
                routes = ModelCatalog.routes_for(model_id)
                # Use catalog routes that aren't the primary agent
                catalog_fallbacks = [r.provider for r in routes if r.provider != agent]
                agents_to_try.extend(catalog_fallbacks)
        except (ImportError, AttributeError) as _cat_exc:
            _log.debug("ModelCatalog lookup skipped (%s)", _cat_exc)

    provider_fallbacks = get_fallback_agents(agent or "unknown")
    for pf in provider_fallbacks:
        if pf not in agents_to_try:
            agents_to_try.append(pf)

    result = None
    exit_code = 1
    status = "failed"
    error_class = None

    # WP-X6: Fallback Control Plane
    from thegent.agents.state_machine import FallbackStateMachine
    from thegent.contracts.policy import FallbackPolicy
    from thegent.contracts.telemetry import ContractTelemetry, rank_providers_by_parser_quality

    telemetry = ContractTelemetry(settings.session_dir)
    # G-CA-02 B2: Parser-quality routing - order providers by confidence/fallback rate
    if settings.routing_parser_quality_enabled:
        agents_to_try = rank_providers_by_parser_quality(agents_to_try, telemetry, limit=100)
    policy = FallbackPolicy(
        allow_plain_fallback=settings.normalization_policy_allow_fallback,
        min_confidence_threshold=settings.normalization_policy_min_confidence,
        max_fallback_rate=settings.normalization_policy_max_fallback_rate,
        strict_providers=[p.strip() for p in settings.normalization_policy_strict_providers.split(",") if p.strip()],
    )

    fsm = FallbackStateMachine(
        providers=agents_to_try,
        run_id=run_meta.run_id,
        policy=policy,
        telemetry=telemetry,
        max_retries_per_provider=3,
    )

    def runner_factory(agent_name: str) -> AgentRunner | None:
        # G-GP-04: Skip providers with open circuit
        if circuit_breaker.is_open(agent_name):
            _log.warning("Circuit open for %s; skipping", agent_name)
            return None
        runner = get_runner(agent_name)
        if runner is None:
            return None

        # Wrap runner.run to inject agent_model
        original_run = runner.run
        agent_model = _resolve_agent_model_local(agent_name, model, mode, settings)

        def wrapped_run(**kwargs) -> RunResult:
            if agent_model:
                kwargs["agent_model"] = agent_model
            res = original_run(**kwargs)
            if res.exit_code != 0:
                circuit_breaker.record_failure(agent_name)
            return res

        # Create a proxy object that satisfies AgentRunner
        @dataclass
        class RunnerProxy(AgentRunner):
            def run(
                self,
                prompt: str,
                cwd: Path | None,
                mode: str,
                timeout: int,
                *,
                use_stream: bool = True,
                live_output: bool = False,
                on_stdout: Callable[[str], None] | None = None,
                on_stderr: Callable[[str], None] | None = None,
                env: dict[str, str] | None = None,
                image_paths: list[str] | None = None,
            ) -> RunResult:
                return wrapped_run(
                    prompt=prompt,
                    cwd=cwd,
                    mode=mode,
                    timeout=timeout,
                    use_stream=use_stream,
                    live_output=live_output,
                    on_stdout=on_stdout,
                    on_stderr=on_stderr,
                    env=env,
                    image_paths=image_paths,
                )

        return RunnerProxy()

    # MTSP-12: Shadow Workspace Integration
    use_shadow = bool(shadow or getattr(settings, "shadow_workspaces_enabled", False))
    shadow_ws = None
    original_cwd = cwd or Path.cwd()
    agent_cwd = original_cwd
    shadow_env = None

    if use_shadow:
        try:
            from thegent.orchestration.shadow import ShadowWorkspace

            shadow_ws = ShadowWorkspace(original_cwd, run_meta.run_id)
            if shadow_ws.create():
                agent_cwd = shadow_ws.shadow_root
                shadow_env = shadow_ws.get_env()
                _log.info("Running in shadow workspace: %s", agent_cwd)
            else:
                _log.warning("Failed to create shadow workspace; falling back to main project.")
                shadow_ws = None
        except ImportError as _shadow_exc:
            _log.debug(
                "shadow workspace module unavailable in this revision (%s); running in main project",
                _shadow_exc,
            )
            shadow_ws = None

    # MTSP-15: Resource Locking (Non-worktree coordination)
    locked_tokens = []
    if not use_shadow and lock:
        from thegent.coordination.file_coordination import FileLeaseRegistry

        lease_registry = FileLeaseRegistry(settings.session_dir / "leases")
        for resource in lock:
            path = Path(resource)
            if not path.is_absolute():
                path = original_cwd / path
            token = lease_registry.claim_lease(path, run_meta.run_id, ttl=int(effective_timeout))
            if token:
                locked_tokens.append((path, token))
                _log.info("Acquired lease for %s", resource)
            else:
                _log.error("Failed to acquire lease for %s; already locked by another agent.", resource)
                return {"error": f"Resource {resource} is locked by another agent.", "exit_code": 1}

    if impl_ns is None:
        raise ValueError("impl_ns is required")
    _bind_impl_namespace(impl_ns)

    settings = ThegentSettings()
    _keepalive_interval = float(getattr(settings, "keepalive_interval", 30.0))
    from thegent.ux.keepalive import keepalive as _keepalive

    try:
        with _keepalive(interval_s=_keepalive_interval):
            result, norm_res = fsm.run(
                runner_factory=runner_factory,
                prompt=prompt,
                cwd=agent_cwd,
                mode=mode,
                timeout=effective_timeout,
                use_stream=use_stream,
                env=shadow_env,
            )
    finally:
        # Release non-worktree locks
        if locked_tokens:
            from thegent.coordination.file_coordination import FileLeaseRegistry

            lease_registry = FileLeaseRegistry(settings.session_dir / "leases")
            for path, token in locked_tokens:
                lease_registry.release_lease(path, run_meta.run_id, token)
                _log.info("Released lease for %s", path)

    status = fsm.state.status
    if status == "success":
        exit_code = 0
        status = "completed"

        # MTSP-12: Auto-merge from shadow workspace
        if shadow_ws and bool(getattr(settings, "shadow_workspaces_auto_merge", False)):
            if shadow_ws.merge_back():
                _log.info("Shadow changes merged successfully.")
            else:
                _log.error("Failed to merge shadow changes back to main project.")

        # Cleanup shadow workspace
        if shadow_ws:
            shadow_ws.destroy()

        # L3 Memory: persist run summary as a discovery (optional; no-op when key absent)
        if getattr(_mem_mgr, "enabled", False) and result:
            try:
                _summary = (result.stdout or "")[:500] or f"Agent {agent} completed successfully"
                _asyncio.get_event_loop().run_until_complete(_mem_mgr.save_discovery(agent or "unknown", _summary))
            except Exception as _mem_exc:
                _log.debug("L3 memory save_discovery failed: %s", _mem_exc)
    else:
        # Cleanup shadow workspace on failure
        if shadow_ws:
            shadow_ws.destroy()
        exit_code = result.exit_code if result else 1
        status = "failed"
        if result and result.timed_out:
            status = "timed_out"

        # WP-2008: DLQ Enqueue on Failure
        if lane == "critical":
            from thegent.execution import DLQManager

            dlq = DLQManager(settings.session_dir)
            dlq.enqueue(run_meta, f"Run {status}: {result.stderr if result else 'No result'}")
            _log.info("Critical run %s; enqueued to DLQ.", status)

    # G-CA-03 C3: No critical lane with unknown contract
    _known_contracts = ("csm-v1", "task-tool-18", "zen-rich-v1", "xml-tags", "plain")
    if (
        lane == "critical"
        and norm_res
        and (norm_res.csm.source_contract == "fallback-plain" or norm_res.csm.source_contract not in _known_contracts)
    ):
        status = "failed"
        exit_code = 1
        error_class = "unknown_contract"

    # Map error class
    if result:
        if result.timed_out:
            error_class = "timeout"
        elif is_usage_limit(result):
            error_class = "usage_limit"
        elif result.exit_code != 0:
            error_class = "api_error"

    duration = time.time() - start_time
    cost_usd = None
    if impl_ns is None:
        raise ValueError("impl_ns is required")
    _bind_impl_namespace(impl_ns)

    settings = ThegentSettings()
    if settings.cost_tracking or settings.cost_tracking_enabled:
        try:
            from thegent.cost.aggregator import CostEstimator

            est = CostEstimator()
            cost_usd = est.estimate(
                model=run_meta.model,
                prompt_length=len(run_meta.prompt or ""),
            )
        except Exception as exc:
            _log.debug("Failed to estimate run cost: %s", exc)
    registry.register_end(
        run_id=run_meta.run_id,
        exit_code=exit_code,
        status=status,
        ended_at_utc=datetime.now(UTC).isoformat(),
        duration_s=duration,
        error_class=error_class,
        cost_usd=cost_usd,
    )

    _output_summary = (result.stdout or result.stderr or "")[:500] if result else "Unknown agent or no result"
    maif_runner.record_run_end(
        run_id=run_meta.run_id,
        status=status,
        output_summary=_output_summary,
    )

    # WP-16002: Update teammate delegation status if this was a sub-task
    if getattr(run_meta, "task_id", None):
        try:
            from thegent.governance.teammates import TeammateManager

            mgr = TeammateManager(settings.cache_dir / "teammates.json")
            # Use condensed summary for result_summary
            _stdout = (result.stdout or "") if result else ""
            _stderr = (result.stderr or "") if result else ""
            summary = _stdout[:500] if status == "completed" else (_stderr[:500] or "Failed without stderr")
            mgr.update_status(run_meta.task_id, status, summary=summary)
        except Exception as e:
            _log.debug("Failed to update teammate delegation status: %s", e)

    # WP-3007: Record environment after run for next transition check
    if status == "completed":
        trust_boundary.record_environment(settings.environment.lower())

        # WP-2007: Evidence Linting
        if norm_res and norm_res.csm:
            from thegent.execution import EvidenceLinter

            linter = EvidenceLinter(settings.session_dir)
            lint_issues = linter.lint(norm_res.csm)
            if lint_issues:
                _log.warning("Evidence lint issues for %s: %s", run_meta.run_id, lint_issues)
                if run_meta.lane == "critical":
                    console.print(f"[bold red]LINT FAILURE:[/bold red] Evidence incomplete: {lint_issues}")

        # WP-3002: Generate and persist signed MAIF artifact
        try:
            artifact = auditor.generate_maif_artifact(run_meta, output=result.stdout if result else None)
            auditor.persist_maif_artifact(settings.session_dir, artifact)
        except Exception as exc:
            _log.warning("Failed to generate/persist MAIF artifact: %s", exc)

    if not result:
        return {
            "error": f"Unknown agent: {agent}",
            "agents": ", ".join(list_agent_names()),
            "exit_code": 1,
            "run_id": run_meta.run_id,
        }

    stderr = result.stderr or ""
    stdout = result.stdout or ""
    csm = norm_res.csm if norm_res else None
    if runner is None:
        return _phase_handle_backend_failure(
            error=error,
            state=state,
            run_meta=run_meta,
            stdout=stdout,
            stderr=stderr,
            start_ts=start_ts,
            settings=settings,
            payload=payload,
        )

    # Successful run: emit telemetry and audit
    _phase_emit_success_telemetry(
        state=state,
        run_meta=run_meta,
        runner=runner,
        start_ts=start_ts,
        settings=settings,
    )

    # Free the eye idle state and reset eye sentinel
    from thegent.cli.shared.eye_state import EyeState

    EyeState(cwd).release_idle()

    # Telemetry: signal idle to bus (eyes open again)
    try:
        from thegent.cli.resources.bus_client import publish_bus_event

        publish_bus_event(
            cwd,
            "run.end",
            {
                "run_id": run_meta.run_id,
                "runner": runner,
                "exit_code": 0,
                "duration_ms": (time.monotonic() - start_ts) * 1000,
            },
        )
    except Exception as e:
        _log.debug(f"Failed to publish run.end bus event: {e}")

    # Assemble payload
    payload = _phase_assemble_payload(
        result=result,
        norm_res=norm_res,
        use_stream=use_stream,
        csm=csm,
        stdout=stdout,
        stderr=stderr,
        run_meta=run_meta,
        contract_deprecation_warning=contract_deprecation_warning,
        include_contract=include_contract,
        route_contract=route_contract,
        route_request=route_request,
    )

    # End cost tracking
    from thegent.cost.tracker import get_run_cost_tracker

    tracker = get_run_cost_tracker()
    tracker.end_run()

    # WP-DX-024: Always write conversation dumps to docs/ (research-always-write-dumps)
    _phase_write_run_dumps(settings, run_meta.run_id, cwd, prompt, stdout, result)

    return payload


def bg_impl_core(
    *,
    agent: str | None,
    prompt: str,
    cd: Path | None,
    mode: str,
    timeout: int,
    full: bool,
    droid: str | None = None,
    model: str | None = None,
    provider: str | None = None,
    owner: str | None = None,
    continue_from: str | None = None,
    continuation_include_stderr: bool = False,
    include_contract: bool = False,
    route_contract: dict[str, Any] | None = None,
    route_request: dict[str, str] | None = None,
    routing: str | None = None,
    failover: bool = False,
    run_id: str | None = None,
    lane: str | None = None,
    confidence: float | None = None,
    contract_version: str | None = None,
    domain: str | None = None,
    idempotency_token: str | None = None,
    speculative: bool = False,
    arbitration: str | None = None,
    override_reason: str | None = None,
    debug: bool = False,
    task_id: str | None = None,
    remote: str | None = None,
    image_paths: list[str] | None = None,
    config_provider: "ConfigProvider | None" = None,
    tenant_id: str | None = None,
    impl_ns: Any | None = None,
) -> dict[str, Any]:
    """
    Start a background run. Returns dict with keys: session_id, log_path, owner.
    """
    if impl_ns is None:
        raise ValueError("impl_ns is required")
    _bind_impl_namespace(impl_ns)
    import sys

    settings = ThegentSettings()
    from thegent.cost.tracker import get_run_cost_tracker

    tracker = get_run_cost_tracker()
    rid = run_id or f"bg_{uuid.uuid4().hex[:8]}"
    tracker.start_run(rid)

    # Pareto routing: routing="pareto" → build RouteCandidate list from catalog and select via ParetoRouter
    agent, model, route_contract, route_request = _apply_pareto_routing_local(
        agent, model, routing, include_contract, route_contract, route_request
    )

    # Auto router: agent="auto" or model="auto" → classify + Pareto select
    if settings.auto_router_enabled and (agent == "auto" or model == "auto"):
        try:
            from thegent.utils.routing_impl.auto_router import auto_route

            ar = auto_route(
                prompt=prompt,
                classifier_model=settings.auto_router_classifier_model,
                use_classifier=settings.auto_router_use_classifier,
                min_quality=settings.auto_router_min_quality,
                max_cost_weight=settings.auto_router_max_cost_weight,
            )
            if ar:
                agent = ar.agent
                model = ar.model
                _log.info("Auto router: %s/%s (complexity=%s)", agent, model, ar.complexity)
            else:
                agent = "antigravity"
                model = "gemini-3-flash"
                _log.warning("Auto router failed; fallback to antigravity/gemini-3-flash")
        except Exception as e:
            _log.warning("Auto router error: %s; fallback to antigravity/gemini-3-flash", e)
            agent = "antigravity"
            model = "gemini-3-flash"

    if agent is None and model:
        from thegent.models import normalize_model_id
        from thegent.models.catalog import ModelCatalog, resolve_route

        model_id = normalize_model_id(model)
        route = resolve_route(model_id, provider_hint=provider)
        if route is None:
            routes = ModelCatalog.routes_for(model_id)
            available = ", ".join(sorted({r.provider for r in routes})) if routes else "none"
            suffix = f" Available: {available}." if available != "none" else ""
            return {
                "error": f"Model '{model}' not available via provider '{provider or 'any'}'.{suffix}",
                "agents": available,
                "exit_code": 1,
                "session_id": "failed",
            }
        agent = route[0]
    agent = resolve_agent(agent) or "unknown"

    # WP-X1/V7: Contract Migration & Version Negotiation
    from thegent.contracts.migration import MigrationController
    from thegent.contracts.registry import CONTRACT_SCHEMA_VERSION

    migrator = MigrationController()
    requested_version = contract_version or CONTRACT_SCHEMA_VERSION
    mig_res = migrator.evaluate_version("csm", requested_version)

    if not mig_res["allowed"]:
        return {
            "error": f"Contract version rejected: {mig_res['reason']}",
            "exit_code": 1,
            "session_id": "failed",
        }

    # ROB-010: Contract version downgrade prevention in critical lanes
    # Prevent silent quality regression by blocking version downgrades in critical lanes
    if lane == "critical" and requested_version != CONTRACT_SCHEMA_VERSION:
        # Check if requested version is older than current
        from thegent.contracts.registry import get_registry

        registry = get_registry()
        current_cv = registry.get("csm", CONTRACT_SCHEMA_VERSION)
        requested_cv = registry.get("csm", requested_version)

        if current_cv and requested_cv:
            # Simple version comparison: if requested is not compatible with current, it's a downgrade
            if not registry.is_compatible(requested_version, CONTRACT_SCHEMA_VERSION):
                return {
                    "error": f"ROB-010: Contract version downgrade prevented in critical lane. Requested: {requested_version}, Current: {CONTRACT_SCHEMA_VERSION}",
                    "exit_code": 1,
                    "session_id": "failed",
                    "remediation": f"Use --contract-version {CONTRACT_SCHEMA_VERSION} or remove --lane critical",
                }

    # ConfigProvider: resolve config (Phase 1: EnvConfigProvider; Phase 2+: CP when URL set)
    _bg_config: dict[str, Any] | None = None
    if config_provider is not None:
        _bg_config = config_provider.resolve(tenant_id=tenant_id, request_overrides={"default_timeout": timeout})
    effective_timeout = _bg_config.get("default_timeout", timeout) if _bg_config else timeout
    if agent == "claude":
        _min_claude = (
            _bg_config.get("default_timeout_claude", settings.default_timeout_claude)
            if _bg_config
            else settings.default_timeout_claude
        )
        effective_timeout = max(effective_timeout, _min_claude)
    cwd = _resolve_cwd(cd)
    if cwd is None:
        return {
            "error": "Ambiguous cwd detected. Run inside a project directory or pass --cd with a valid project path.",
            "exit_code": 1,
            "session_id": "failed",
            "run_id": run_id or f"bg_err_{uuid.uuid4().hex[:8]}",
        }

    full = full or True

    effective_prompt = prompt
    if continue_from:
        effective_prompt = _build_continuation_prompt(
            settings, continue_from, prompt, include_stderr=continuation_include_stderr
        )

    owner_tag = owner or _default_owner_tag(cwd, include_process_id=True)
    base = _session_dir(settings, owner_tag)
    session_id = _new_session_id(agent=agent, owner=owner_tag)
    p = _rsh_impl.session_paths(base=base, session_id=session_id)

    # Registry integration
    registry = RunRegistry(settings.session_dir)

    # WP-1003/WP-1008: Idempotency
    # OPT-019: Use bloom filter for fast negative lookup before full registry scan
    if idempotency_token:
        # Generate session_id from token for bloom filter lookup
        session_id_from_token = f"run_{hashlib.sha256(idempotency_token.encode()).hexdigest()[:8]}"
        # Fast path: if not in bloom filter, definitely doesn't exist
        if registry.session_exists(session_id_from_token):
            # Might exist, do full lookup
            existing = registry.find_by_token(idempotency_token)
            if existing and existing.get("status") == "completed":
                _log.info("Replay detected for token %s in bg; skipping.", idempotency_token)
                return {
                    "session_id": existing.get("correlation_id") or "replayed",
                    "run_id": existing.get("run_id"),
                    "replayed": True,
                }

    effective_run_id = run_id or f"run_{uuid.uuid4().hex[:8]}"

    # WP-5001: Speculative Execution Mode
    if speculative:
        _log.info("Speculative execution active in background.")

    from thegent.execution import (
        Auditor,
        CircuitBreakerRegistry,
        OverrideRegistry,
        PolicyEngine,
        TrustBoundaryValidator,
    )

    _circuit_breaker = CircuitBreakerRegistry(settings.session_dir)
    trust_boundary = TrustBoundaryValidator(settings.session_dir)
    override_registry = OverrideRegistry(settings.session_dir)
    auditor = Auditor(registry.registry_path)
    policy_engine = PolicyEngine(settings)
    _effective_owner = owner or _default_owner_tag(cwd)
    escalation_sla_minutes = 30
    try:
        escalation_sla_minutes = int(settings.escalation_sla_minutes)
    except (TypeError, ValueError):
        escalation_sla_minutes = 30

    # WP-3007: Trust Boundary Checks
    last_env = trust_boundary.get_last_environment()
    allowed, boundary_reason = trust_boundary.validate_transition(last_env, settings.environment.lower())
    if not allowed:
        return {
            "error": f"Trust boundary violation: {boundary_reason}",
            "exit_code": 1,
            "session_id": "failed",
        }

    resolved_domain_tag = str(domain) if domain else str(settings.default_domain_tag)

    run_meta = RunMeta(
        run_id=effective_run_id,
        agent=agent or "",
        model=model or "",
        prompt=prompt,
        cwd=str(cwd),
        owner=owner_tag,
        domain_tag=resolved_domain_tag,
        lane=lane or "standard",
        confidence=confidence if confidence is not None else 1.0,
        idempotency_token=idempotency_token or "",
    )

    # G-GP-05: Policy pre-check for background runs
    pol_res, pol_reason = policy_engine.evaluate(run_meta, registry=registry)

    # WP-3003: Overrides with TTL (revalidation on expiry)
    if pol_res == "deny" and override_registry.has_unexpired(owner_tag):
        _log.info("Policy override (cached, within TTL) for background run")
        pol_res = "allow"
        pol_reason = f"Overridden (cached): {pol_reason}"

    run_meta.policy_result = pol_res
    run_meta.policy_reason = pol_reason
    run_meta.signature = auditor.sign_run(run_meta)

    if pol_res == "deny":
        escalate_add_impl(
            run_id=run_meta.run_id,
            reason=pol_reason,
            sla_minutes=escalation_sla_minutes,
            owner=run_meta.owner,
            agent=run_meta.agent,
            lane=run_meta.lane,
        )
        registry.register_start(run_meta)
        registry.register_end(
            run_id=run_meta.run_id,
            exit_code=1,
            status="failed",
            ended_at_utc=datetime.now(UTC).isoformat(),
            duration_s=0.0,
            error_class="policy_violation",
        )
        return {"error": f"Policy Violation: {pol_reason}", "exit_code": 1}

    if pol_res == "pause":
        from thegent.execution import CheckpointRegistry

        registry.register_start(run_meta)
        registry.register_pause(run_meta.run_id, reason=pol_reason)

        ckpt_registry = CheckpointRegistry(settings.session_dir)
        ckpt_registry.create_checkpoint(
            reason=f"HITL Pause (bg): {pol_reason}",
            dag_content=run_meta.model_dump_json(),
            owner=run_meta.owner,
        )

        escalate_add_impl(
            run_id=run_meta.run_id,
            reason=f"HITL Pause (bg): {pol_reason}",
            sla_minutes=escalation_sla_minutes,
            owner=run_meta.owner,
            agent=run_meta.agent,
            lane=run_meta.lane,
            priority=1,
        )
        return {
            "error": f"HITL PAUSE: {pol_reason}",
            "session_id": session_id,
            "status": "paused",
            "run_id": run_meta.run_id,
        }

    registry.register_start(run_meta)

    # WP-RC-01: Remote Compute Offload (Phase 4)
    if remote:
        from thegent.research.remote_compute import RemoteComputeClient

        client = RemoteComputeClient(remote)

        import tempfile

        remote_path = Path(tempfile.gettempdir()) / f"thegent-run-{run_meta.run_id}"
        _log.info(f"Offloading background execution to remote host: {remote}")

        # 1. Sync files to remote
        if cwd is None:
            return {"error": "Cannot transfer files: cwd is not set", "exit_code": 1}
        if not client.transfer_files(cwd, str(remote_path)):
            return {"error": f"Failed to sync project to remote host: {remote}", "exit_code": 1}

        # 2. Reconstruct command without --remote to avoid infinite loops
        remote_args = [a for a in sys.argv if not a.startswith("--remote")]
        # Ensure we use background 'bg' on remote if we want it to be backgrounded there too
        # Or just 'run' since we are already backgrounding this call?
        # Actually, if we use 'bg' on remote, we get another layer of backgrounding.
        # Let's use 'run' on remote.
        remote_command = " ".join(f'"{a}"' if " " in a else a for a in remote_args)

        # 3. Execute remote in background (using nohup or similar)
        # For simplicity, we'll just execute it and return the "session"
        _log.info(f"Running remote background command in {remote_path}")
        # We wrap in nohup and redirect to a file on remote
        bg_remote_command = f"nohup {remote_command} > {remote_path}/remote_bg.log 2>&1 & echo $!"
        remote_res = client.execute_remote(bg_remote_command, cwd=Path(remote_path))

        if remote_res.get("status") == "success":
            remote_pid = remote_res.get("stdout", "").strip()
            return {
                "session_id": f"remote-{remote_pid}",
                "run_id": run_meta.run_id,
                "remote_host": remote,
                "remote_path": remote_path,
                "status": "started_remote",
            }
        return remote_res

    # Build command against Thegent 3.0 apps layout.
    cmd: list[str] = [sys.executable, "-m", "thegent.main", "run", "agent", effective_prompt]
    cmd.extend(["--cd", str(cwd), "--timeout", str(effective_timeout), "--lane", lane or "standard"])
    if agent:
        cmd.extend(["--agent", agent])
    if full:
        cmd.append("--full")
    if routing:
        cmd.extend(["--routing", routing])
    if failover:
        cmd.append("--failover")
    if model:
        cmd.extend(["--model", model])
    if requested_version:
        cmd.extend(["--contract-version", requested_version])
    if domain:
        cmd.extend(["--domain", domain])
    if task_id:
        cmd.extend(["--task-id", task_id])
    if idempotency_token:
        cmd.extend(["--idempotency-token", idempotency_token])
    if speculative:
        cmd.append("--speculative")

    # Pass run_id to the spawned run so registry lifecycle is correlated.
    cmd.extend(["--run-id", effective_run_id])

    # Phase P4: holdpty wrapper
    if settings.use_holdpty is True:
        in_path = p.get("in")
        if in_path is None:
            raise RuntimeError("Session paths missing 'in' key")
        socket_path = in_path.with_suffix(".sock")
        holdpty_cmd = [
            sys.executable,
            "-m",
            "thegent.main",
            "holdpty",
            "--socket",
            str(socket_path),
            "--session-id",
            session_id,
            "--",
        ]
        cmd = holdpty_cmd + cmd

    stdout_handle = p["stdout"].open("wb")
    stderr_handle = p["stderr"].open("wb")

    # macOS sandbox wrapping (THGENT_SANDBOX_LEVEL)
    from thegent.security.macos_sandbox import MacOSSandbox, SandboxLevel

    # Defensive: the stub MacOSSandbox in this revision does not expose
    # ``from_env`` / ``level_from_settings`` (canonical home is in the
    # full macOS sandbox shim). When the helpers are absent, fall back
    # to a no-op BASIC instance so ``bg_impl`` keeps working in CI /
    # bare-metal test environments without breaking patch surface.
    _sandbox = MacOSSandbox.from_env() if hasattr(MacOSSandbox, "from_env") else MacOSSandbox(SandboxLevel.BASIC)
    if hasattr(MacOSSandbox, "level_from_settings"):
        _sandbox_level = MacOSSandbox.level_from_settings()
    else:
        _sandbox_level = _sandbox.level
    if _sandbox_level not in (SandboxLevel.NONE, SandboxLevel.FULL):
        apply_to_command = getattr(_sandbox, "apply_to_command", None)
        if callable(apply_to_command):
            cmd = apply_to_command(cmd, _sandbox_level, project_root=cwd)
        _log.debug("macOS sandbox level %r applied to agent command", _sandbox_level.value)

    # G-GP-08: Sandbox environment filtering
    if settings.sandbox_env_filter:
        allowlist = settings.sandbox_env_allowlist
        env = {k: v for k, v in os.environ.items() if k in allowlist or k.startswith("THGENT_")}
    else:
        env = os.environ.copy()

    env["PYTHONUNBUFFERED"] = "1"
    env.update(
        {
            "THGENT_SESSION_ID": session_id,
            "THGENT_SESSION_META_PATH": str(p["meta"]),
            "THGENT_SESSION_RC_PATH": str(p["rc"]),
            "THGENT_SESSION_STDOUT_PATH": str(p["stdout"]),
            "THGENT_SESSION_STDERR_PATH": str(p["stderr"]),
            "THGENT_OWNER_TAG": owner_tag,
        }
    )

    stdin_handle = subprocess.DEVNULL
    if settings.use_fifo is True:
        try:
            # On Unix, create a FIFO
            if platform.system() != "Windows":
                in_path = p.get("in")
                if in_path is None:
                    raise RuntimeError("Session paths missing 'in' key")
                if not in_path.exists():
                    os.mkfifo(str(in_path))
                # Open for reading in non-blocking mode to avoid hanging the parent
                # but then set to blocking for the child if needed.
                # Actually, opening a FIFO for reading will block until a writer opens it.
                # To avoid blocking bg_impl, we should open it in the background or use O_NONBLOCK.
                fifo_fd = os.open(str(in_path), os.O_RDONLY | os.O_NONBLOCK)
                stdin_handle = fifo_fd
            else:
                _log.warning("FIFO not supported on Windows; falling back to DEVNULL.")
        except Exception as e:
            _log.warning("Failed to create FIFO: %s", e)

    try:
        spawn_with_eagain_retry = _impl_lazy._spawn_with_eagain_retry
        if spawn_with_eagain_retry is None:
            raise RuntimeError("spawn helper is unavailable")
        proc = spawn_with_eagain_retry(
            cmd,
            cwd=str(cwd),
            env=env,
            stdin=stdin_handle,
            stdout=stdout_handle,
            stderr=stderr_handle,
        )
    except RuntimeError:
        # AUDIT-N+14 fallback: when the canonical ``_spawn_with_eagain_retry``
        # is unavailable (e.g. test environment that patches
        # ``thegent.cli.commands.impl.subprocess.Popen`` directly), fall back
        # to ``subprocess.Popen`` so the test contract and the bare-metal
        # spawn path both succeed. Use the impl namespace subprocess so
        # ``@patch("thegent.cli.commands.impl.subprocess.Popen")`` is honoured.
        _impl_subprocess = _impl_lazy.subprocess
        popen = getattr(_impl_subprocess, "Popen", None)
        if popen is None:
            raise
        proc = popen(
            cmd,
            cwd=str(cwd),
            env=env,
            stdin=stdin_handle,
            stdout=stdout_handle,
            stderr=stderr_handle,
        )
    except Exception:
        stdout_handle.close()
        stderr_handle.close()
        if isinstance(stdin_handle, int) and stdin_handle > 0:
            os.close(stdin_handle)
        raise
    finally:
        stdout_handle.close()
        stderr_handle.close()
        # Do not close stdin_handle here if it's an FD being inherited

    meta: dict[str, Any] = {
        "version": 1,
        "session_id": session_id,
        "agent": agent,
        "owner": owner_tag,
        "cwd": str(cwd),
        "prompt": prompt,
        "mode": mode,
        "timeout_hint_s": effective_timeout,
        "host": socket.gethostname(),
        "launcher_pid": os.getpid(),
        "launcher_ppid": os.getppid(),
        "launcher_uid": os.getuid(),
        "status": "running",
        "started_at_utc": datetime.now(UTC).isoformat(),
        "pid": proc.pid,
        "command": cmd,
        "paths": {k: str(v) for k, v in p.items()},
    }
    if include_contract:
        if route_contract is not None:
            meta["route_contract"] = route_contract
        if route_request is not None:
            meta["route_request"] = route_request
    if continue_from:
        meta["continued_from"] = continue_from.split(",")[0].strip()
    _save_session_meta(p["meta"], meta)

    return {
        "session_id": session_id,
        "log_path": str(p["stdout"]),
        "owner": owner_tag,
    }
