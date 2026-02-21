"""Thegent implementation layer: functions that return dict/str instead of printing.

_resolve_cwd() defaults to Path.cwd() when no project indicators found, so no
"cd &&" patterns are needed. Use --cd /path for explicit directory override.
MCP tools may still elicit cwd when meta.cwd is absent (see gofastmcp.com/servers/elicitation).
"""

import json
import logging
import os
import platform
import re
import signal
import socket
import subprocess
import sys
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, cast

if TYPE_CHECKING:
    from thegent.config_provider import ConfigProvider

from rich.console import Console

from thegent.infra import run_subprocess_optimized

console = Console()

import typer

import contextlib
import hashlib

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_random_exponential

from thegent.agents import (
    get_fallback_agents,
    get_runner,
    list_agent_names,
    resolve_agent,
)
from thegent.agents.base import AgentRunner, RunResult
from thegent.agents.resilience import is_usage_limit
from thegent.config import ThegentSettings
from thegent.contracts.registry import CONTRACT_SCHEMA_VERSION
from thegent.cli.services import governance as governance_service
from thegent.cli.services import observability as observability_service
from thegent.cli.services import pre_work_gate_helpers
from thegent.cli.services import process_helpers
from thegent.cli.services import prompt_constraint_helpers
from thegent.cli.services import run_audio_helpers
from thegent.cli.services import run_dag_helpers
from thegent.cli.services import run_event_helpers
from thegent.cli.services import run_guard_helpers
from thegent.cli.services import run_health_helpers
from thegent.cli.services import run_input_helpers
from thegent.cli.services import run_model_helpers
from thegent.cli.services import run_observe_helpers
from thegent.cli.services import run_post_surface_helpers
from thegent.cli.services import run_session_helpers
from thegent.cli.services import run_workstream_helpers
from thegent.cli.services import retry_helpers
from thegent.cli.services import spawn_retry_helpers
from thegent.cli.services import work_stream_orchestration
from thegent.execution import AgentSource, InteractivityMode, RunMeta, RunRegistry
from thegent.maif import MAIFRunner

# Approximate seconds per tool call for budget injection (~2.3s * N tool calls ≈ timeout)
SECONDS_PER_TOOL_CALL = 2.3

# Max chars from prior session to inject (fits typical context windows)
_CONTINUATION_TAIL_CHARS = 8000
_CONTINUATION_STDERR_CHARS = 2000
_CONTINUATION_MULTI_HOP_TOTAL_CAP = 12000
_LOG_FOLLOW_POLL_SECONDS = 0.5
_SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
_MODEL_INDEXES_PATH = Path(__file__).resolve().parents[2] / "agents" / "cliproxy_data" / "model_indices.json"
_log = logging.getLogger(__name__)


def _normalize_image_paths(image_paths: list[str] | None) -> list[str]:
    """Backward-compatible wrapper for extracted run input helper service."""
    return run_input_helpers.normalize_image_paths(
        image_paths,
        supported_image_suffixes=_SUPPORTED_IMAGE_SUFFIXES,
    )


def _append_context_usage(payload: dict[str, Any], result: RunResult) -> None:
    """Backward-compatible wrapper for extracted run input helper service."""
    run_input_helpers.append_context_usage(payload, result)


def _resolve_grounding_sources_for_output(
    *,
    stdout: str,
    result_grounding_sources: list[str] | None,
) -> list[str]:
    """Backward-compatible wrapper for extracted run input helper service."""
    return run_input_helpers.resolve_grounding_sources_for_output(
        stdout=stdout,
        result_grounding_sources=result_grounding_sources,
    )


def _resolve_audio_transcript_for_output(
    *,
    injected_audio_transcript: str | None,
    result_audio_transcript: str | None,
) -> str | None:
    """Backward-compatible wrapper for extracted run event helper service."""
    return run_event_helpers.resolve_audio_transcript_for_output(
        injected_audio_transcript=injected_audio_transcript,
        result_audio_transcript=result_audio_transcript,
    )


def _build_audio_summary_metadata(*, audio_transcript: str | None, audio_sources: list[str]) -> dict[str, Any] | None:
    """Backward-compatible wrapper for extracted run audio helper service."""
    return run_audio_helpers.build_audio_summary_metadata(
        audio_transcript=audio_transcript,
        audio_sources=audio_sources,
    )


def _build_run_event_details(
    *,
    grounding_sources: list[str],
    audio_transcript: str | None,
    audio_sources: list[str],
    context_usage_ratio: float | None,
) -> dict[str, Any] | None:
    """Backward-compatible wrapper for extracted run event helper service."""
    return run_event_helpers.build_run_event_details(
        grounding_sources=grounding_sources,
        audio_transcript=audio_transcript,
        audio_sources=audio_sources,
        context_usage_ratio=context_usage_ratio,
    )


def _model_supports_vision(model: str) -> bool:
    """Backward-compatible wrapper for extracted run input helper service."""
    return run_input_helpers.model_supports_vision(
        model,
        model_indexes_path=_MODEL_INDEXES_PATH,
    )


def _validate_image_capability(agent: str, model: str | None) -> None:
    run_input_helpers.validate_image_capability(
        agent=agent,
        model=model,
        model_supports_vision_impl=_model_supports_vision,
    )


def _hash_health_payload(payload: dict[str, Any]) -> dict[str, str]:
    """Backward-compatible wrapper for extracted run health helper service."""
    return run_health_helpers.hash_health_payload(payload)


def _resolve_health_policy(
    policy_profile: str | None,
    strict: bool,
    min_healthy_ratio: float,
) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted run health helper service."""
    return run_health_helpers.resolve_health_policy(
        policy_profile=policy_profile,
        strict=strict,
        min_healthy_ratio=min_healthy_ratio,
        health_policy_profiles=HEALTH_POLICY_PROFILES,
    )


def _health_snapshot_log_path() -> Path:
    """Backward-compatible wrapper for extracted run health helper service."""
    return run_health_helpers.health_snapshot_log_path()


def _health_snapshot_max_lines() -> int:
    """Backward-compatible wrapper for extracted run health helper service."""
    return run_health_helpers.health_snapshot_max_lines()


def _compact_health_snapshot_log() -> None:
    """Backward-compatible wrapper for extracted run health helper service."""
    run_health_helpers.compact_health_snapshot_log(
        log_path_resolver=_health_snapshot_log_path,
        max_lines_resolver=_health_snapshot_max_lines,
    )


def _health_scope_key(payload: dict[str, Any]) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted run health helper service."""
    return run_health_helpers.health_scope_key(payload)


def _coerce_issue_types(value: Any) -> list[str]:
    """Backward-compatible wrapper for extracted run health helper service."""
    return run_health_helpers.coerce_issue_types(value)


def _load_previous_health_snapshot(scope_key: dict[str, Any]) -> dict[str, Any] | None:
    """Backward-compatible wrapper for extracted run health helper service."""
    return run_health_helpers.load_previous_health_snapshot(
        scope_key,
        log_path_resolver=_health_snapshot_log_path,
    )


def _append_health_snapshot(payload: dict[str, Any], scope_key: dict[str, Any]) -> None:
    """Backward-compatible wrapper for extracted run health helper service."""
    run_health_helpers.append_health_snapshot(
        payload,
        scope_key,
        log_path_resolver=_health_snapshot_log_path,
        compact_log_fn=_compact_health_snapshot_log,
        coerce_issue_types_fn=_coerce_issue_types,
    )


def _hash_observe_summary_payload(payload: dict[str, Any]) -> dict[str, str]:
    """Backward-compatible wrapper for extracted observe-summary helper service."""
    return run_observe_helpers.hash_observe_summary_payload(payload)


def _build_observe_summary_trend_scope(
    *,
    provider: str | None,
    drift_window: int,
    structural_budget_pct: float,
    semantic_budget_pct: float,
    limit: int,
    top_escalations: int,
) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted observe-summary helper service."""
    return run_observe_helpers.build_observe_summary_trend_scope(
        provider=provider,
        drift_window=drift_window,
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        limit=limit,
        top_escalations=top_escalations,
    )


def _hash_observe_summary_trend_scope(scope_key: dict[str, Any]) -> str:
    """Backward-compatible wrapper for extracted observe-summary helper service."""
    return run_observe_helpers.hash_observe_summary_trend_scope(scope_key)


def _parse_observe_summary_timestamp(value: str | None) -> datetime | None:
    """Backward-compatible wrapper for extracted observe-summary helper service."""
    return run_observe_helpers.parse_observe_summary_timestamp(value)


def _parse_observe_summary_env_float(name: str, default: float) -> float:
    """Backward-compatible wrapper for extracted observe-summary helper service."""
    return run_observe_helpers.parse_observe_summary_env_float(name, default)


def _parse_observe_summary_env_int(name: str, default: int) -> int:
    """Backward-compatible wrapper for extracted observe-summary helper service."""
    return run_observe_helpers.parse_observe_summary_env_int(name, default)


def _observe_summary_freshness_bucket(
    freshness_seconds: int | None,
    *,
    fresh_seconds: int,
    warm_seconds: int,
    stale_seconds: int,
) -> str:
    """Backward-compatible wrapper for extracted observe-summary helper service."""
    return run_observe_helpers.observe_summary_freshness_bucket(
        freshness_seconds,
        fresh_seconds=fresh_seconds,
        warm_seconds=warm_seconds,
        stale_seconds=stale_seconds,
    )


def _load_observe_summary_snapshots(
    scope_signature: str,
    scope_key_json: str,
    limit: int,
) -> list[dict[str, Any]]:
    """Backward-compatible wrapper for extracted observe-summary helper service."""
    return run_observe_helpers.load_observe_summary_snapshots(scope_signature, scope_key_json, limit)


def _classify_observe_summary_trend_health(
    *,
    enabled: bool,
    baseline_available: bool,
    trend_snapshot_coverage_pct: float | None,
    trend_snapshot_deficit: int,
    trend_snapshot_invalid_timestamps: int,
    trend_snapshot_freshness_bucket: str,
    trend_snapshot_gap_count: int,
    trend_sampling_mode: str,
) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted observe-summary helper service."""
    return run_observe_helpers.classify_observe_summary_trend_health(
        enabled=enabled,
        baseline_available=baseline_available,
        trend_snapshot_coverage_pct=trend_snapshot_coverage_pct,
        trend_snapshot_deficit=trend_snapshot_deficit,
        trend_snapshot_invalid_timestamps=trend_snapshot_invalid_timestamps,
        trend_snapshot_freshness_bucket=trend_snapshot_freshness_bucket,
        trend_snapshot_gap_count=trend_snapshot_gap_count,
        trend_sampling_mode=trend_sampling_mode,
    )


def _append_observe_summary_snapshot(
    payload: dict[str, Any],
    trend_scope_key: dict[str, Any],
    trend_scope_signature: str,
    scope_key_json: str,
    trend_snapshot_ids: list[str],
    trend_summary: dict[str, Any],
) -> None:
    """Backward-compatible wrapper for extracted observe-summary helper service."""
    run_observe_helpers.append_observe_summary_snapshot(
        payload,
        trend_scope_key,
        trend_scope_signature,
        scope_key_json,
        trend_snapshot_ids,
        trend_summary,
    )


# ---------------------------------------------------------------------------
# Subprocess spawn with EAGAIN retry (tenacity-migrate-cli)
# ---------------------------------------------------------------------------
# EAGAIN/EWOULDBLOCK is returned by the kernel when process-table or file-
# descriptor limits are momentarily exhausted.  A short exponential back-off
# lets the OS recover before we give up.
#
# Parameters match the original hand-rolled loop documented in
# TENACITY_RETRY_AUDIT_PLAN.md §3.1:
#   max_attempts = 5, base_backoff = 0.1 s → max ~1.6 s total sleep.
# ---------------------------------------------------------------------------

_EAGAIN_ERRNOS: frozenset[int] = spawn_retry_helpers.EAGAIN_ERRNOS


def _retry_if_eagain(exc: BaseException) -> bool:
    """Backward-compatible wrapper for extracted spawn retry helper service."""
    return spawn_retry_helpers.retry_if_eagain(exc)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_random_exponential(multiplier=0.1, min=0.1, max=5.0),
    retry=retry_if_exception(_retry_if_eagain),
    reraise=True,
)
def _spawn_with_eagain_retry(
    cmd: list[str],
    *,
    cwd: str,
    env: dict[str, str],
    stdin: int | Any,
    stdout: Any,
    stderr: Any,
) -> subprocess.Popen[bytes]:
    """Call subprocess.Popen, retrying on EAGAIN/EWOULDBLOCK with exponential back-off.

    tenacity handles the wait and stop policy; the caller is responsible for
    closing file handles on any exception that propagates out.
    """
    return subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        start_new_session=True,
    )


def _backoff_delay(attempt: int, max_delay: float = 60.0) -> float:
    """Return an exponential-jitter delay for DAG task retry dispatch.

    Uses the same capped-exponential formula as wait_random_exponential so
    that DAG retries follow the same policy as tenacity-managed retries
    without requiring tenacity to manage the DAG control-flow loop.

    Args:
        attempt: 0-based retry count (0 = first retry after first failure).
        max_delay: Maximum delay in seconds (default 60).

    Returns:
        Delay in seconds in [0, min(2**attempt, max_delay)].
    """
    return retry_helpers.backoff_delay(attempt=attempt, max_delay=max_delay)


# ---------------------------------------------------------------------------


def _resolve_droids_dir(cwd: Path | None, settings: ThegentSettings) -> Path:
    """Backward-compatible wrapper for extracted run session helper service."""
    return run_session_helpers.resolve_droids_dir(cwd=cwd, settings=settings)


def _resolve_cwd(cd: Any) -> Path | None:
    """Backward-compatible wrapper for extracted run session helper service."""
    return run_session_helpers.resolve_cwd(cd)


def _resolve_agent_model(
    agent: str,
    model: str | None,
    mode: str,
    settings: ThegentSettings,
) -> str | None:
    """Backward-compatible wrapper for extracted run session helper service."""
    return run_session_helpers.resolve_agent_model(
        agent=agent,
        model=model,
        mode=mode,
        settings=settings,
    )


def _inject_time_constraint(prompt: str, timeout: int, *, summary_mode: bool = True) -> str:
    """Backward-compatible wrapper for extracted prompt constraint helper service."""
    return prompt_constraint_helpers.inject_time_constraint(
        prompt=prompt,
        timeout=timeout,
        seconds_per_tool_call=SECONDS_PER_TOOL_CALL,
        summary_mode=summary_mode,
    )


def _scope_key(owner: str) -> str:
    return run_session_helpers.scope_key(owner)


def _default_owner_tag(cwd: Path | None = None, *, include_process_id: bool = False) -> str:
    return run_session_helpers.default_owner_tag(cwd, include_process_id=include_process_id)


def _compose_owner_tag(user: str, cwd: Path, scope: str = "") -> str:
    """Build deterministic owner tags with optional scope expansion."""
    return run_session_helpers.compose_owner_tag(user=user, cwd=cwd, scope=scope)


def _session_dir(settings: ThegentSettings, owner: str) -> Path:
    return run_session_helpers.session_dir(settings, owner)


def _session_scope_dirs(base: Path, owner: str) -> list[Path]:
    return run_session_helpers.session_scope_dirs(base, owner)


def _session_paths(base: Path, session_id: str) -> dict[str, Path]:
    """Backward-compatible wrapper for extracted run session helper service."""
    return run_session_helpers.session_paths(base=base, session_id=session_id)


def _make_load_classifier(settings: "ThegentSettings") -> Any:
    """WP-5002: Create load classifier instance for load observation."""
    from thegent.execution import LoadClassifier

    return LoadClassifier(
        session_dir=settings.session_dir.expanduser().resolve(),
        spike_threshold=settings.concurrency_min_slots,
        surge_threshold=settings.max_concurrency,
    )


def _new_session_id(agent: str | None, owner: str) -> str:
    """Backward-compatible wrapper for extracted run session helper service."""
    return run_session_helpers.new_session_id(agent=agent, owner=owner)


def _is_pid_running(pid: int) -> bool:
    """Backward-compatible wrapper for extracted process helper service."""
    return process_helpers.is_pid_running(pid)


def _parse_dag_full(path: Path) -> "DagDocument":
    """Backward-compatible wrapper for extracted run DAG helper service."""
    return run_dag_helpers.parse_dag_full(path)


def _serialize_dag(doc: "DagDocument") -> str:
    """Backward-compatible wrapper for extracted run DAG helper service."""
    return run_dag_helpers.serialize_dag(doc)


def _parse_dag_session(path: Path) -> tuple[dict[str, str], list[dict[str, str]]]:
    """Backward-compatible wrapper for extracted run DAG helper service."""
    return run_dag_helpers.parse_dag_session(path)


def _validate_task_id(task_id: str) -> str | None:
    """Backward-compatible wrapper for extracted run DAG helper service."""
    return run_dag_helpers.validate_task_id(task_id)


def _validate_agent(agent: str) -> str | None:
    """Backward-compatible wrapper for extracted run DAG helper service."""
    return run_dag_helpers.validate_agent(agent)


def _validate_dag(doc: "DagDocument") -> list[str]:
    """Backward-compatible wrapper for extracted run DAG helper service."""
    return run_dag_helpers.validate_dag(doc)


def _dag_update_task(
    doc: "DagDocument",
    task_id: str,
    *,
    status: str | None = None,
    session_id: str | None = None,
    prompt: str | None = None,
    agent: str | None = None,
    depends_on: str | None = None,
    retry_count: int | None = None,
    contract_version: str | None = None,
) -> bool:
    """Backward-compatible wrapper for extracted run DAG helper service."""
    return run_dag_helpers.dag_update_task(
        doc=doc,
        task_id=task_id,
        status=status,
        session_id=session_id,
        prompt=prompt,
        agent=agent,
        depends_on=depends_on,
        retry_count=retry_count,
        contract_version=contract_version,
    )


def _parse_depends_on(dep_str: str) -> list[str]:
    """Backward-compatible wrapper for extracted run DAG helper service."""
    return run_dag_helpers.parse_depends_on(dep_str)


def _get_ready_task_ids(tasks: list[dict[str, str]]) -> list[str]:
    """Backward-compatible wrapper for extracted run DAG helper service."""
    return run_dag_helpers.get_ready_task_ids(tasks)


def dag_ready_impl(cd: Path | None = None) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted run DAG helper service."""
    return run_dag_helpers.dag_ready_impl(cd)


# DAG extraction re-export block (WL-120 Wave-3):
# keep legacy import paths in impl.py while delegating implementation to dag_impl.py.
from thegent.cli.commands.dag_impl import (  # noqa: E402 -- re-export block
    TASK_ID_RE,
    DagDocument,
    _atomic_write,
    _check_dag_cycles,
    _dag_path,
    _ensure_contract_version_header,
    _ensure_dag_file,
    _ensure_evidence_header,
    _escape_cell,
    _resolve_prompt,
    _session_status_for,
    dag_list_impl,
    dag_raw_impl,
    dag_recover_impl,
    dag_run_impl,
    dag_status_impl,
    dag_sync_impl,
    rules_sync_impl,
)


from thegent.output_parser import condense_stream_to_display, extract_condensed

# Elicitation messages for MCP tools when cwd/owner are ambiguous
ELICIT_CWD_MSG = "Working directory?"
ELICIT_OWNER_MSG = "Session owner tag?"
# --- Observability/health/escalation/governance/review/compliance ---
# Extracted to observability_impl.py (WL-120 LOC reduction).
# Re-export all public symbols for backward compatibility with existing callers.
from thegent.cli.commands.observability_impl import (  # noqa: E402 -- re-export block
    HEALTH_PAYLOAD_SCHEMA_VERSION,
    HEALTH_PAYLOAD_TYPES,
    HEALTH_POLICY_PROFILES,
    OBSERVE_SUMMARY_PAYLOAD_TYPES,
    OBSERVE_SUMMARY_SCHEMA_VERSION,
    _REVIEW_ALLOWED_TOOLS,
    _REVIEW_SCHEMA_PREAMBLE,
    _extract_agent_from_line,
    _process_run_line,
    escalate_add_impl,
    escalate_approve_impl,
    escalate_list_impl,
    escalate_resolve_impl,
    get_compliance_report_impl,
    get_data_protection_status_impl,
    get_server_meta_impl,
    govern_approve_impl,
    govern_list_pending_impl,
    govern_reject_impl,
    govern_vet_impl,
    observe_summary_impl,
    review_impl,
    sitback_dashboard_impl,
    sweep_impl,
    update_calibration_impl,
)

# --- Session backend ---
# Extracted to session_impl.py (WL-120 Wave-3 W3-B2).
# Re-export all public symbols for backward compatibility with existing callers.
from thegent.cli.commands.session_impl import (  # noqa: E402 -- re-export block
    _build_continuation_prompt,
    _extract_blocked_ratio,
    _find_session_meta,
    _is_non_empty_contract_string,
    _load_prior_session_output,
    _normalize_contract_string,
    _normalize_output_format,
    _parse_contract_timestamp,
    _read_session_meta,
    _resolve_latest_session_id,
    _resolve_session_status,
    _run_background_session_observer,
    _save_session_meta,
    _session_state_path,
    _write_session_state,
    events_impl,
    explain_run_impl,
    history_impl,
    inspect_impl,
    list_session_contracts_impl,
    logs_impl,
    metrics_impl,
    prune_sessions_impl,
    ps_impl,
    purge_impl,
    session_contract_audit_impl,
    session_contract_health_gate_impl,
    session_contract_health_report_impl,
    session_contract_health_trend_impl,
    session_contract_negotiate_impl,
    session_list_impl,
    session_meta_impl,
    session_send_impl,
    status_impl,
    stop_impl,
    wait_impl,
)

# --- Infra/compute/sandbox backend ---
# Extracted to infra_impl.py (WL-120 Wave-3 W3-B3).
# Re-export all public symbols for backward compatibility with existing callers.
from thegent.cli.commands.infra_impl import (  # noqa: E402 -- re-export block
    _scan_ide_agents,
    concurrency_set_impl,
    concurrency_show_impl,
    isolation_check_impl,
    lock_resource_impl,
    monitor_impl,
    orchestrate_plan_impl,
    orchestrate_run_impl,
    unlock_resource_impl,
    verify_context_impl,
)


def _update_teammate_status(task_id: str | None, status: str, summary: str | None = None) -> None:
    """Helper to update teammate delegation status."""
    if not task_id:
        return
    try:
        from thegent.config import ThegentSettings
        from thegent.governance.teammates import TeammateManager

        settings = ThegentSettings()
        mgr = TeammateManager(settings.cache_dir / "teammates.json")
        mgr.update_status(task_id, status, summary=summary)
    except Exception as e:
        _log.debug("Failed to update teammate delegation status: %s", e)


def _apply_pareto_routing(
    agent: str | None,
    model: str | None,
    routing: str | None,
    include_contract: bool,
    route_contract: dict[str, Any] | None,
    route_request: dict[str, Any] | None,
) -> tuple[str | None, str | None, dict[str, Any] | None, dict[str, Any] | None]:
    """Apply ParetoRouter selection when routing="pareto" and no agent/model is pre-set.

    Returns updated (agent, model, route_contract, route_request).
    Falls back to ("antigravity", "gemini-3-flash", ...) when the router returns no result or raises.

    This function is intentionally pure (no side effects beyond logging) so it can be unit-tested
    without standing up the full run_impl machinery.
    """
    if routing != "pareto" or agent is not None or model is not None:
        return agent, model, route_contract, route_request

    try:
        from thegent.models.catalog import _get_catalog
        from thegent.routing.pareto_router import QUALITY_PROXY, ParetoRouter, RouteCandidate

        catalog = _get_catalog()
        candidates: list[RouteCandidate] = []
        for routes in catalog.values():
            for r in routes:
                quality = QUALITY_PROXY.get(r.model_alias, 0.5)
                candidates.append(
                    RouteCandidate(
                        model=r.model_alias,
                        provider=r.provider,
                        cost_per_1k=r.cost_weight,
                        quality_score=quality,
                    )
                )
        if not candidates:
            _log.warning("Pareto router: no candidates from catalog; fallback to antigravity/gemini-3-flash")
            return "antigravity", "gemini-3-flash", route_contract, route_request

        selected = ParetoRouter().select(candidates)
        _log.info(
            "Pareto router: selected %s/%s (quality=%.2f, cost=%.2f)",
            selected.provider,
            selected.model,
            selected.quality_score,
            selected.cost_per_1k,
        )

        updated_contract = route_contract
        updated_request = route_request
        if include_contract:
            updated_contract = dict(route_contract or {})
            updated_contract.update(
                {
                    "provider": selected.provider,
                    "model_alias": selected.model,
                    "backend_type": "direct",
                    "routing_policy": "pareto",
                }
            )
            updated_request = dict(route_request or {})
            updated_request.update(
                {
                    "requested_model": "pareto",
                    "policy": "pareto",
                    "resolved_agent": selected.provider,
                    "resolved_model_alias": selected.model,
                }
            )

        return selected.provider, selected.model, updated_contract, updated_request

    except Exception as _pareto_err:
        _log.warning("Pareto router error: %s; fallback to antigravity/gemini-3-flash", _pareto_err)
        return "antigravity", "gemini-3-flash", route_contract, route_request


def _validate_explicit_ollama_provider(provider: str | None, model: str | None) -> str | None:
    """Backward-compatible wrapper for extracted run model helper service."""
    return run_model_helpers.validate_explicit_ollama_provider(provider=provider, model=model)


def run_impl(
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
    reasoning_effort: Literal["minimal", "low", "medium", "high", "xhigh"] | None = None,
    output_schema: str | None = None,
    image_paths: list[str] | None = None,
    audio_files: list[str] | None = None,
    google_grounding: bool = False,
) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted run execution core helper service."""
    from thegent.cli.services import run_execution_core_helpers

    return run_execution_core_helpers.run_impl_core(
        agent=agent,
        prompt=prompt,
        cd=cd,
        mode=mode,
        timeout=timeout,
        full=full,
        live=live,
        model=model,
        provider=provider,
        run_id=run_id,
        owner=owner,
        include_contract=include_contract,
        route_contract=route_contract,
        route_request=route_request,
        lane=lane,
        confidence=confidence,
        override_reason=override_reason,
        contract_version=contract_version,
        domain=domain,
        idempotency_token=idempotency_token,
        correlation_id=correlation_id,
        speculative=speculative,
        arbitration=arbitration,
        routing=routing,
        enable_search=enable_search,
        debug=debug,
        task_id=task_id,
        shadow=shadow,
        lock=lock,
        remote=remote,
        config_provider=config_provider,
        tenant_id=tenant_id,
        previous_session_id=previous_session_id,
        reasoning_effort=reasoning_effort,
        output_schema=output_schema,
        image_paths=image_paths,
        audio_files=audio_files,
        google_grounding=google_grounding,
        impl_ns=sys.modules[__name__],
    )


def bg_impl(
    *,
    agent: str | None,
    prompt: str,
    cd: Path | None,
    mode: str = "write",
    timeout: int = 90,
    full: bool = False,
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
) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted run execution core helper service."""
    from thegent.cli.services import run_execution_core_helpers

    return run_execution_core_helpers.bg_impl_core(
        agent=agent,
        prompt=prompt,
        cd=cd,
        mode=mode,
        timeout=timeout,
        full=full,
        droid=droid,
        model=model,
        provider=provider,
        owner=owner,
        continue_from=continue_from,
        continuation_include_stderr=continuation_include_stderr,
        include_contract=include_contract,
        route_contract=route_contract,
        route_request=route_request,
        routing=routing,
        failover=failover,
        run_id=run_id,
        lane=lane,
        confidence=confidence,
        contract_version=contract_version,
        domain=domain,
        idempotency_token=idempotency_token,
        speculative=speculative,
        arbitration=arbitration,
        override_reason=override_reason,
        debug=debug,
        task_id=task_id,
        remote=remote,
        image_paths=image_paths,
        config_provider=config_provider,
        tenant_id=tenant_id,
        impl_ns=sys.modules[__name__],
    )
def resume_impl(
    session_id: str | None = None,
    prompt: str | None = None,
    skills: list[str] | None = None,
) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted post-run surface helper service."""
    return run_post_surface_helpers.resume_impl(
        session_id=session_id,
        prompt=prompt,
        skills=skills,
        resolve_latest_session_id=_resolve_latest_session_id,
        session_state_path=_session_state_path,
        normalize_contract_string=_normalize_contract_string,
        session_send_impl=lambda sid, message: session_send_impl(sid, message, msg_type="reprompt"),
        settings_factory=ThegentSettings,
        run_registry_cls=RunRegistry,
    )


def loop_impl(
    agent: str = "cursor",
    prompt: str = "",
    todo_spec: str = "",
    checker: str = "antigravity",
    mode: str = "soft",
    cd: Path | None = None,
    on_worker_output: Any = None,
    on_progress: Any = None,
) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted post-run surface helper service."""
    return run_post_surface_helpers.loop_impl(
        agent=agent,
        prompt=prompt,
        todo_spec=todo_spec,
        checker=checker,
        mode=mode,
        cd=cd,
        on_worker_output=on_worker_output,
        on_progress=on_progress,
        bg_impl=bg_impl,
        settings_factory=ThegentSettings,
    )


def list_agents_impl() -> list[dict[str, str]]:
    """Backward-compatible wrapper for extracted post-run surface helper service."""
    return run_post_surface_helpers.list_agents_impl()


def list_droids_impl(cd: Any = None) -> list[str]:
    """Backward-compatible wrapper for extracted post-run surface helper service."""
    return run_post_surface_helpers.list_droids_impl(
        cd=cd,
        resolve_cwd=_resolve_cwd,
        resolve_droids_dir=_resolve_droids_dir,
        settings_factory=ThegentSettings,
    )


def list_models_impl(
    provider: str | None = None,
    use_scraped: bool = True,
    refresh: bool = False,
    include_contract: bool = False,
    by_model: bool = False,
) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted post-run surface helper service."""
    return run_post_surface_helpers.list_models_impl(
        provider=provider,
        use_scraped=use_scraped,
        refresh=refresh,
        include_contract=include_contract,
        by_model=by_model,
        settings_factory=ThegentSettings,
    )


def _parse_work_stream_md(work_stream_path: Path) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted run workstream helper service."""
    return run_workstream_helpers.parse_work_stream_md(work_stream_path)


def _check_dependencies_satisfied(item: dict[str, Any], completed: set[str], claimed: set[str]) -> bool:
    """Backward-compatible wrapper for extracted run workstream helper service."""
    return run_workstream_helpers.check_dependencies_satisfied(item, completed, claimed)


def _priority_sort_key(priority: str) -> int:
    """Backward-compatible wrapper for extracted run workstream helper service."""
    return run_workstream_helpers.priority_sort_key(priority)


def _collect_work_stream_items(work_stream_path: Path, limit: int) -> tuple[list[dict[str, Any]], list[str]]:
    """Backward-compatible wrapper for extracted run workstream helper service."""
    return run_workstream_helpers.collect_work_stream_items(work_stream_path, limit)


def _collect_queued_items(settings: ThegentSettings, limit: int) -> tuple[list[dict[str, Any]], list[str]]:
    """Backward-compatible wrapper for extracted run workstream helper service."""
    return run_workstream_helpers.collect_queued_items(settings, limit)


def _pre_work_gate_defaults() -> dict[str, Any]:
    """Backward-compatible wrapper for extracted pre-work gate helper service."""
    return pre_work_gate_helpers.pre_work_gate_defaults()


def _pre_work_gate_thresholds(project_dir: Path) -> tuple[dict[str, Any], str]:
    """Backward-compatible wrapper for extracted pre-work gate helper service."""
    return pre_work_gate_helpers.pre_work_gate_thresholds(project_dir)


def _evidence_age_minutes(path: Path) -> int:
    """Backward-compatible wrapper for extracted pre-work gate helper service."""
    return pre_work_gate_helpers.evidence_age_minutes(path)


def _pre_work_governance_block_payload(
    *,
    project_dir: Path,
    thresholds: dict[str, Any],
    violations: list[dict[str, Any]],
    config_source: str,
) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted pre-work gate helper service."""
    return pre_work_gate_helpers.pre_work_governance_block_payload(
        project_dir=project_dir,
        thresholds=thresholds,
        violations=violations,
        config_source=config_source,
    )


def _enforce_pre_work_hard_gate(project_dir: Path) -> dict[str, Any] | None:
    """Backward-compatible wrapper for extracted pre-work gate helper service."""
    return pre_work_gate_helpers.enforce_pre_work_hard_gate(project_dir)


def do_next_impl(cd: Path | None = None, limit: int = 5) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.do_next_impl(cd=cd, limit=limit)


def wait_next_impl(
    cd: Path | None = None,
    poll_interval: float = 2.0,
    timeout: float = 0.0,
    sources: tuple[str, ...] = ("do_next",),
) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.wait_next_impl(
        cd=cd,
        poll_interval=poll_interval,
        timeout=timeout,
        sources=sources,
    )


def spawn_next_impl(
    cd: Path | None = None,
    limit: int = 10,
    agent: str = "free",
    timeout: int | None = None,
    lane: str = "critical",
    override_reason: str = "manual-next-step",
    claim: bool = True,
) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.spawn_next_impl(
        cd=cd,
        limit=limit,
        agent=agent,
        timeout=timeout,
        lane=lane,
        override_reason=override_reason,
        claim=claim,
    )


def work_stream_claim_impl(item_id: str, agent_id: str, cd: Path | None = None) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.work_stream_claim_impl(item_id=item_id, agent_id=agent_id, cd=cd)


def work_stream_complete_impl(item_id: str, agent_id: str, cd: Path | None = None) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.work_stream_complete_impl(item_id=item_id, agent_id=agent_id, cd=cd)


def incorporate_impl(cd: Path | None = None, dry_run: bool = False) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.incorporate_impl(cd=cd, dry_run=dry_run)


def _validate_task_and_record_errors(tf: Path, validation_errors: list[dict[str, Any]]) -> None:
    """Backward-compatible wrapper for extracted post-run surface helper service."""
    run_post_surface_helpers.validate_task_and_record_errors(tf=tf, validation_errors=validation_errors)


def continuity_snapshot_impl(
    owner: str,
    run_ids: list[str],
    state_summary: dict[str, Any] | None = None,
    next_steps: list[str] | None = None,
) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted post-run surface helper service."""
    return run_post_surface_helpers.continuity_snapshot_impl(
        owner=owner,
        run_ids=run_ids,
        state_summary=state_summary,
        next_steps=next_steps,
        settings_factory=ThegentSettings,
    )


def inbox_wait_impl(timeout: int | None = None) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted post-run surface helper service."""
    return run_post_surface_helpers.inbox_wait_impl(timeout=timeout, settings_factory=ThegentSettings)


def inbox_list_impl(
    owner: str | None = None,
    agent: str | None = None,
    event_type: str | None = None,
    status: str | None = None,
    sources: tuple[str, ...] = ("registry", "escalation"),
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Backward-compatible wrapper for extracted post-run surface helper service."""
    return run_post_surface_helpers.inbox_list_impl(
        owner=owner,
        agent=agent,
        event_type=event_type,
        status=status,
        sources=sources,
        limit=limit,
        settings_factory=ThegentSettings,
        run_registry_cls=RunRegistry,
    )


def plan_analyze_impl(
    cd: Path | None = None,
    pert: bool = False,
    resources: bool = False,
    continuity: bool = False,
) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted post-run surface helper service."""
    return run_post_surface_helpers.plan_analyze_impl(
        cd=cd,
        pert=pert,
        resources=resources,
        continuity=continuity,
        resolve_cwd=_resolve_cwd,
        parse_dag_full=_parse_dag_full,
    )


def retry_impl(
    run_id: str,
    agent_override: str | None = None,
    failover: bool = False,
    cd: Path | None = None,
    override_reason: str | None = None,
) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted post-run surface helper service."""
    return run_post_surface_helpers.retry_impl(
        run_id=run_id,
        agent_override=agent_override,
        failover=failover,
        cd=cd,
        override_reason=override_reason,
        resolve_cwd=_resolve_cwd,
        bg_impl=bg_impl,
        settings_factory=ThegentSettings,
        run_registry_cls=RunRegistry,
        get_fallback_agents_fn=get_fallback_agents,
    )


# ---------------------------------------------------------------------------
# Harness TUI Mapper CLI: interact with all agent harnesses
# ---------------------------------------------------------------------------


def harness_interact_impl(
    harness: str,
    action: str,
    host_id: str | None = None,
    prompt: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted post-run surface helper service."""
    return run_post_surface_helpers.harness_interact_impl(
        harness=harness,
        action=action,
        host_id=host_id,
        prompt=prompt,
        session_id=session_id,
    )


def harness_list_actions_impl() -> dict[str, Any]:
    """Backward-compatible wrapper for extracted post-run surface helper service."""
    return run_post_surface_helpers.harness_list_actions_impl()


def harness_register_host_impl(
    host_id: str,
    harness: str,
    command_prefix: str = "",
    custom_actions: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted post-run surface helper service."""
    return run_post_surface_helpers.harness_register_host_impl(
        host_id=host_id,
        harness=harness,
        command_prefix=command_prefix,
        custom_actions=custom_actions,
    )


# ---------------------------------------------------------------------------
# WL-088: orchestrate plan / run implementations
# @trace FR-ORC-088
# @trace WL-088
# ---------------------------------------------------------------------------
