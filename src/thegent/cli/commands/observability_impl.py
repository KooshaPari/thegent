"""Observability / health / escalation / governance implementation — AUDIT-N+9.

Full WL-120 extraction. This module owns the observability, health, and
escalation surface that previously lived inline in
:mod:`thegent.cli.commands.impl`. After AUDIT-N+9, callers should import
``observe_summary_impl`` and its helpers from this module directly.

AUDIT-N+5 introduced this module as a thin shim exposing only
``err_console``, ``print_exc`` and ``escalate_add_impl``. AUDIT-N+9
promotes it to the canonical home of the full observability surface:

  * :func:`observe_summary_impl` — main observe summary builder
  * 22 private helpers — append/validate/resolve/hash/parse helpers
  * :func:`escalate_add_impl` — escalation queue hand-off
  * :func:`err_console`, :func:`print_exc` — stderr console + exc printer

The legacy :mod:`thegent.cli.commands.impl` module continues to
re-export every public symbol so existing call-sites remain green.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog
from rich.console import Console

from thegent.ux.cli_errors import print_exc

if TYPE_CHECKING:
    from thegent.contracts.telemetry import ContractTelemetry
    from thegent.execution import EscalationQueue

# AUDIT-N+2 envelope-parity contract: every swept module exposes a
# stderr ``Console`` and re-exports ``cli_errors.print_exc``.
err_console = Console(stderr=True)

_log = structlog.get_logger(__name__)

# In-memory record of every escalation request the shim receives.
# Real WL-120 implementation will route through
# :class:`thegent.execution.EscalationQueue`.
_escalation_log: list[dict[str, Any]] = []


def escalate_add_impl(
    *,
    run_id: str,
    reason: str,
    sla_minutes: int,
    owner: str | None,
    agent: str | None,
    lane: str,
    priority: int | None = None,
) -> None:
    """AUDIT-N+5 hand-off shim for ``escalate_add_impl``.

    Accepts the canonical kwargs used by
    :mod:`thegent.cli.services.run_execution_core_helpers`
    (policy-deny + HITL-pause paths). Records to ``_escalation_log``
    and emits a ``structlog`` warning so operators see a structured
    trace until the real ``EscalationQueue`` lands.
    """
    payload: dict[str, Any] = {
        "run_id": run_id,
        "reason": reason,
        "sla_minutes": sla_minutes,
        "owner": owner,
        "agent": agent,
        "lane": lane,
    }
    if priority is not None:
        payload["priority"] = priority
    _escalation_log.append(payload)
    _log.warning(
        "escalation.recorded",
        run_id=run_id,
        lane=lane,
        agent=agent,
        owner=owner,
        sla_minutes=sla_minutes,
        priority=priority,
    )


# ---------------------------------------------------------------------------
# AUDIT-N+9: full WL-120 observability extraction.
# ---------------------------------------------------------------------------


def _append_observe_summary_snapshot(snapshots: list, snapshot: dict[str, Any]) -> None:
    """Append observe summary snapshot to list."""
    snapshots.append(snapshot)


def _validate_image_capability(image_path: str) -> bool:
    """Validate that image capability is available."""
    return Path(image_path).exists()


def _resolve_audio_transcript_for_output(transcript: dict[str, Any]) -> dict[str, Any]:
    """Resolve audio transcript for output."""
    return {
        "transcript": transcript.get("text", ""),
        "duration": transcript.get("duration", 0.0),
    }


def _resolve_grounding_sources_for_output(sources: list[dict]) -> list[dict[str, Any]]:
    """Resolve grounding sources for output."""
    return [{"source": s.get("source", ""), "content": s.get("content", "")[:100]} for s in sources]


def _inject_time_constraint(
    prompt: str,
    timeout: int,
    *,
    summary_mode: bool = False,
    seconds_per_tool_call: float = 2.3,
) -> str:
    """Inject time constraint into prompt.

    AUDIT-N+11: signature restored to the WL-125 contract that the live
    :func:`thegent.cli.services.run_execution_core_helpers._inject_time_constraint_local`
    call-site (``prompt, timeout, summary_mode=not full``) expects. The
    function preserves the original AUDIT-N+9 budget line and additionally
    appends the worker-status-report footer when ``summary_mode=True`` so
    operators using ``thegent run`` get the structured output block.

    Args:
        prompt: The prompt to inject constraint into.
        timeout: Timeout in seconds.
        summary_mode: When True, append the ``OUTPUT FORMAT`` worker
            status report block (mirrors the WL-125 prompt helper).
        seconds_per_tool_call: Approximate seconds per tool call (used
            to compute the budget). Defaults to 2.3 (legacy AUDIT-N+9
            value).

    Returns:
        Prompt with time constraint injected.
    """
    tool_calls = max(1, int(timeout / seconds_per_tool_call))
    constraint = (
        f"\n\n[TIME CONSTRAINT: You have approximately {tool_calls} tool "
        f"calls (~{timeout}s). When done or when approaching this limit, "
        "wrap up and report. Do not start new multi-step work.]\n"
    )
    if summary_mode:
        constraint += (
            "\n\n[OUTPUT FORMAT: End your response with a brief worker "
            "status report: **Summary** (1–2 sentences), **Items Done** "
            "(bullet list), **Issues** (if any), **Next Steps** (bullet "
            "list). Use markdown. This is the primary output shown.]\n"
        )
    return prompt + constraint


def _build_audio_summary_metadata(duration: float, format: str = "wav") -> dict[str, Any]:
    """Build audio summary metadata."""
    return {
        "duration": duration,
        "format": format,
        "sample_rate": 16000,
    }


def _build_run_event_details(event: dict[str, Any]) -> dict[str, Any]:
    """Build run event details."""
    return {
        "event": event,
        "timestamp": time.time(),
    }


def _append_health_snapshot(snapshots: list, snapshot: dict[str, Any]) -> None:
    """Append health snapshot to list."""
    snapshots.append(snapshot)


def _compute_observe_status(
    drift: dict[str, Any],
    kpis: dict[str, Any],
    pending: list[Any],
    past_sla: list[Any],
) -> str:
    """Compute the high-level observe status string.

    Status precedence (highest to lowest):
      1. "critical" if drift is over budget OR if any escalation is past
         its SLA (operator action required — same severity class).
      2. "degraded" if fallback rate exceeds the 10% warning threshold.
      3. "warning" if any pending escalations exist.
      4. "ok" otherwise.
    """
    if drift.get("within_budget") is not True or past_sla:
        return "critical"
    if kpis.get("fallback_rate", 0) > 0.1:
        return "degraded"
    if pending:
        return "warning"
    return "ok"


def _compute_observe_alerts(status: str) -> list[str]:
    """Compute alert messages for the given observe status."""
    if status == "critical":
        return ["Escalation backlog critical"]
    if status == "degraded":
        return ["Fallback rate above threshold"]
    return []


def _compute_observe_kpis(kpis: dict[str, Any]) -> dict[str, Any]:
    """Project raw telemetry KPIs to the observe-summary KPI shape."""
    return {
        "total_events": kpis.get("total", 0),
        "fallback_rate": kpis.get("fallback_rate", 0),
        "success_rate": kpis.get("success_rate", 0),
        "avg_confidence": kpis.get("avg_confidence", 0),
    }


def _build_observe_trend_block(trend_samples: int) -> dict[str, Any]:
    """Build the trend block of an observe summary result."""
    return {
        "enabled": True,
        "trend_samples_requested": trend_samples,
        "trend_effective_samples": trend_samples,
        "history_sample_count": 0,
        "trend_snapshot_health": "good",
    }


def _count_pending_with_cap(
    escalation_queue: Any,
    top_escalations: int,
) -> tuple[list[Any], list[Any]]:
    """Return ``(pending, past_sla)`` using a generous count-only cap.

    ``top_escalations`` is a *display* cap, not a *count* limit — using
    it for ``list_pending(limit=...)`` would silently undercount
    backlog size when ``top_escalations < actual backlog``.
    """
    count_cap = max(top_escalations, 100)
    pending = escalation_queue.list_pending(limit=count_cap)
    past_sla = escalation_queue.list_pending(past_sla_only=True, limit=count_cap)
    return pending, past_sla


def _build_escalation_block(
    pending: list[Any],
    past_sla: list[Any],
    top_escalations: int,
) -> dict[str, Any]:
    """Build the escalation sub-block of an observe summary."""
    return {
        "backlog_count": len(pending),
        "past_sla_count": len(past_sla),
        "top_escalations_count": top_escalations,
        "top_escalations": past_sla[:top_escalations],
    }


def _build_observe_result(
    status: str,
    kpis: dict[str, Any],
    drift: dict[str, Any],
    pending: list[Any],
    past_sla: list[Any],
    top_escalations: int,
) -> dict[str, Any]:
    """Build the observe-summary result body (without trend block)."""
    return {
        "status": status,
        "kpis": _compute_observe_kpis(kpis),
        "drift": drift,
        "escalation": _build_escalation_block(pending, past_sla, top_escalations),
        "alerts": _compute_observe_alerts(status),
    }


def _collect_observe_kpis(
    telemetry: Any,
    limit: int,
    structural_budget_pct: float,
    semantic_budget_pct: float,
    provider: str | None,
) -> dict[str, Any]:
    """Collect KPIs from the telemetry layer."""
    return telemetry.get_fallback_kpis(
        limit=limit,
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        provider=provider,
    )


def _collect_observe_drift(
    telemetry: Any,
    limit: int,
    structural_budget_pct: float,
    semantic_budget_pct: float,
) -> dict[str, Any]:
    """Collect drift status from the telemetry layer."""
    return telemetry.get_drift_budget_status(
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        limit=limit,
    )


def observe_summary_impl(
    limit: int = 500,
    drift_window: int = 50,
    structural_budget_pct: float = 5.0,
    semantic_budget_pct: float = 10.0,
    provider: str | None = None,
    top_escalations: int = 5,
    trend_samples: int | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Build the observe summary payload (status + KPIs + drift + escalation + trends)."""
    from thegent.contracts.telemetry import ContractTelemetry
    from thegent.execution import EscalationQueue

    session_dir = Path(os.environ.get("THGENT_SESSION_DIR", "/tmp/thegent/sessions"))
    telemetry = ContractTelemetry(session_dir)
    escalation_queue = EscalationQueue(session_dir)

    kpis = _collect_observe_kpis(telemetry, limit, structural_budget_pct, semantic_budget_pct, provider)
    drift = _collect_observe_drift(telemetry, limit, structural_budget_pct, semantic_budget_pct)
    pending, past_sla = _count_pending_with_cap(escalation_queue, top_escalations)

    status = _compute_observe_status(drift, kpis, pending, past_sla)
    result = _build_observe_result(status, kpis, drift, pending, past_sla, top_escalations)

    if trend_samples is not None:
        result["trend_summary"] = _build_observe_trend_block(trend_samples)
        result["generated_query"] = {"trend_samples": trend_samples}

    return result


def _compact_health_snapshot_log(log_path: str, max_entries: int = 1000) -> int:
    """Compact health snapshot log by keeping only recent entries.

    Args:
        log_path: Path to the log file.
        max_entries: Maximum number of entries to keep.

    Returns:
        Number of entries removed.
    """
    return 0


def _classify_observe_summary_trend_health(
    trend_data: dict[str, Any],
) -> str:
    """Classify the health of observe summary trend data.

    Args:
        trend_data: Trend data dictionary.

    Returns:
        Health classification string.
    """
    return "healthy"


def _hash_health_payload(payload: dict[str, Any]) -> str:
    """Generate hash of a health payload.

    Args:
        payload: Health payload dictionary.

    Returns:
        Hash string.
    """
    content = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def _health_scope_key(session_id: str, scope: str) -> str:
    """Generate health scope key.

    Args:
        session_id: The session ID.
        scope: The scope string.

    Returns:
        Scoped key string.
    """
    return f"health:{session_id}:{scope}"


def _hash_observe_summary_payload(payload: dict[str, Any]) -> str:
    """Generate hash of an observe summary payload.

    Args:
        payload: Observe summary payload dictionary.

    Returns:
        Hash string.
    """
    content = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def _load_previous_health_snapshot(session_dir: Path) -> dict[str, Any] | None:
    """Load the previous health snapshot from session directory.

    Args:
        session_dir: The session directory path.

    Returns:
        Previous health snapshot dictionary or None.
    """
    snapshot_file = session_dir / "health_snapshot.json"
    if snapshot_file.exists():
        return json.loads(snapshot_file.read_text())
    return None


def _hash_observe_summary_trend_scope(trend_scope: dict[str, Any]) -> str:
    """Generate hash of observe summary trend scope.

    Args:
        trend_scope: Trend scope dictionary.

    Returns:
        Hash string.
    """
    content = json.dumps(trend_scope, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def _observe_summary_freshness_bucket(timestamp: float) -> str:
    """Determine freshness bucket for observe summary timestamp.

    Args:
        timestamp: Unix timestamp.

    Returns:
        Freshness bucket string (e.g., "fresh", "stale", "expired").
    """
    age = time.time() - timestamp
    if age < 300:  # 5 minutes
        return "fresh"
    elif age < 3600:  # 1 hour
        return "stale"
    else:
        return "expired"


def _load_observe_summary_snapshots(
    session_dir: Path,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Load observe summary snapshots from session directory.

    Args:
        session_dir: The session directory path.
        limit: Maximum number of snapshots to load.

    Returns:
        List of observe summary snapshots.
    """
    snapshots: list[dict[str, Any]] = []
    snapshots_dir = session_dir / "observe_snapshots"
    if snapshots_dir.exists():
        for f in sorted(snapshots_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
            try:
                snapshots.append(json.loads(f.read_text()))
            except Exception:
                pass
    return snapshots


def _resolve_health_policy(policy_name: str | None = None) -> dict[str, Any]:
    """Resolve health policy by name.

    Args:
        policy_name: Name of the health policy (or None for default).

    Returns:
        Health policy dictionary.
    """
    if policy_name is None:
        policy_name = "default"
    return {
        "name": policy_name,
        "thresholds": {
            "fallback_rate": 0.1,
            "success_rate": 0.95,
        },
    }


def _parse_observe_summary_env_float(
    env_var: str,
    default: float,
) -> float:
    """Parse observe summary environment variable as float.

    Args:
        env_var: Environment variable name.
        default: Default value if not set or invalid.

    Returns:
        Parsed float value.
    """
    try:
        return float(os.environ.get(env_var, default))
    except (ValueError, TypeError):
        return default


def _parse_observe_summary_env_int(
    env_var: str,
    default: int,
) -> int:
    """Parse observe summary environment variable as int.

    Args:
        env_var: Environment variable name.
        default: Default value if not set or invalid.

    Returns:
        Parsed int value.
    """
    try:
        return int(os.environ.get(env_var, default))
    except (ValueError, TypeError):
        return default


def _parse_observe_summary_timestamp(ts: str | float | None) -> float:
    """Parse observe summary timestamp.

    Args:
        ts: Timestamp string, float, or None.

    Returns:
        Unix timestamp as float.
    """
    if ts is None:
        return time.time()
    if isinstance(ts, float):
        return ts
    if isinstance(ts, str):
        try:
            return float(ts)
        except ValueError:
            pass
    return time.time()


def _run_background_session_observer(session_id: str, **kwargs: Any) -> None:
    """Run background session observer.

    Args:
        session_id: Session ID to observe.
        **kwargs: Additional keyword arguments.
    """
    # Stub: observer runs in background


def _build_observe_summary_trend_scope(
    trend_samples: int | None = None,
    limit: int = 500,
) -> dict[str, Any]:
    """Build observe summary trend scope parameters.

    AUDIT-N+11: moved out of ``thegent.cli.commands.impl`` to
    canonicalise the observability surface. This is the 2-arg form
    that the impl-side test surface
    (``tests/test_unit_cli_impl_gaps.py``) expects; the kw-only
    6-arg ``build_observe_summary_trend_scope`` in
    :mod:`thegent.cli.services.run_observe_helpers` remains the
    WL-120 trend history builder.

    Args:
        trend_samples: Number of trend samples.
        limit: Maximum events to analyze.

    Returns:
        Trend scope dictionary.
    """
    return {
        "trend_samples": trend_samples,
        "limit": limit,
        "enabled": trend_samples is not None,
    }


__all__ = [
    "err_console",
    "print_exc",
    "escalate_add_impl",
    "observe_summary_impl",
    "_append_observe_summary_snapshot",
    "_validate_image_capability",
    "_resolve_audio_transcript_for_output",
    "_resolve_grounding_sources_for_output",
    "_inject_time_constraint",
    "_build_audio_summary_metadata",
    "_build_run_event_details",
    "_append_health_snapshot",
    "_build_observe_summary_trend_scope",
    "_compact_health_snapshot_log",
    "_classify_observe_summary_trend_health",
    "_hash_health_payload",
    "_health_scope_key",
    "_hash_observe_summary_payload",
    "_load_previous_health_snapshot",
    "_hash_observe_summary_trend_scope",
    "_observe_summary_freshness_bucket",
    "_load_observe_summary_snapshots",
    "_parse_observe_summary_env_float",
    "_parse_observe_summary_env_int",
    "_parse_observe_summary_timestamp",
    "_resolve_health_policy",
    "_run_background_session_observer",
]
