"""Thegent main observability, escalation, governance, review, and compliance impls.

Extracted from observability_impl.py as part of CLI refactoring.
"""

from __future__ import annotations

import orjson as json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from thegent.cli.services import governance as governance_service
from thegent.cli.services import observability as observability_service
from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)

__all__ = [
    "_REVIEW_ALLOWED_TOOLS",
    "_REVIEW_SCHEMA_PREAMBLE",
    "_append_observe_summary_snapshot",
    "_extract_agent_from_line",
    "_extract_review_json_payload",
    "_process_run_line",
    "escalate_add_impl",
    "escalate_approve_impl",
    "escalate_list_impl",
    "escalate_resolve_impl",
    "get_compliance_report_impl",
    "get_data_protection_status_impl",
    "get_server_meta_impl",
    "govern_approve_impl",
    "govern_list_pending_impl",
    "govern_reject_impl",
    "govern_vet_impl",
    "observe_summary_impl",
    "review_impl",
    "sitback_dashboard_impl",
    "sweep_impl",
    "update_calibration_impl",
]

# Constants
_REVIEW_ALLOWED_TOOLS = ["read_file", "glob", "grep", "web_search"]
_REVIEW_SCHEMA_PREAMBLE = (
    "Return JSON only with keys: summary (string), overall_rating (0-100 integer), "
    "issues (array of {file, line, severity, message, suggestion})."
)


def get_server_meta_impl() -> dict[str, Any]:
    """Return server metadata dict for thegent://meta resource."""
    from thegent.cli.commands.observability_health_impl import (  # pyright: ignore[reportMissingImports]
        HEALTH_PAYLOAD_SCHEMA_VERSION,
        HEALTH_PAYLOAD_TYPES,
    )
    from thegent.cli.commands.observability_trends_impl import (  # pyright: ignore[reportMissingImports]
        OBSERVE_SUMMARY_PAYLOAD_TYPES,
        OBSERVE_SUMMARY_SCHEMA_VERSION,
    )

    from thegent.cli.commands.governance_policy_health_cmds import HEALTH_POLICY_PROFILES  # pyright: ignore[reportMissingImports]

    return observability_service.get_server_meta_impl(
        health_payload_schema_version=HEALTH_PAYLOAD_SCHEMA_VERSION,
        health_payload_types=HEALTH_PAYLOAD_TYPES,
        observe_summary_payload_schema_version=OBSERVE_SUMMARY_SCHEMA_VERSION,
        observe_summary_payload_types=OBSERVE_SUMMARY_PAYLOAD_TYPES,
        health_policy_profiles=sorted(HEALTH_POLICY_PROFILES.keys()),
    )


# --- Escalation impls ---


def escalate_add_impl(
    run_id: str,
    reason: str,
    sla_minutes: int = 30,
    owner: str | None = None,
    agent: str | None = None,
    lane: str = "standard",
    priority: int = 0,
) -> None:
    """WP-3008: Add a blocked run to the escalation queue."""
    governance_service.escalate_add_impl(
        run_id=run_id,
        reason=reason,
        sla_minutes=sla_minutes,
        owner=owner,
        agent=agent,
        lane=lane,
        priority=priority,
    )


def escalate_approve_impl(run_id: str) -> bool:
    """WP-3008: Approve an escalation, marking it as approved in the queue (G-GP-05)."""
    return governance_service.escalate_approve_impl(run_id)


def escalate_list_impl(past_sla_only: bool = False, limit: int = 50) -> list[dict[str, Any]]:
    """WP-3008: List escalation queue items (blocked runs with SLA)."""
    return governance_service.escalate_list_impl(past_sla_only=past_sla_only, limit=limit)


def escalate_resolve_impl(run_id: str, resolution: str = "resolved") -> bool:
    """WP-3008: Mark an escalation item as resolved."""
    return governance_service.escalate_resolve_impl(run_id=run_id, resolution=resolution)


def update_calibration_impl() -> dict[str, Any]:
    """G-GP-09: Recalculate and persist calibration factors for all agents."""
    from thegent.execution import CalibrationRegistry, RunRegistry

    settings = ThegentSettings()
    session_dir = Path(settings.session_dir).expanduser().resolve()
    registry = RunRegistry(session_dir)
    cal = CalibrationRegistry(session_dir)

    if not registry.registry_path.exists():
        return {}

    agents: set[str] = set()
    with registry.registry_path.open("r", encoding="utf-8") as f:
        for line in f:
            _extract_agent_from_line(agents, line)

    results: dict[str, Any] = {}
    for agent in agents:
        runs: dict[str, dict[str, Any]] = {}

        with registry.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                _process_run_line(runs, line, agent)

        relevant_runs = [r for r in runs.values() if r.get("feedback_score") is not None]
        if not relevant_runs:
            continue

        avg_feedback = sum(float(r["feedback_score"]) for r in relevant_runs) / len(relevant_runs)
        avg_confidence = sum(float(r.get("confidence") or 0.5) for r in relevant_runs) / len(relevant_runs)

        if avg_confidence > 0:
            factor = min(2.0, max(0.5, avg_feedback / avg_confidence))
            cal.update_agent(agent, factor, sample_size=len(relevant_runs))
            results[agent] = {"factor": factor, "samples": len(relevant_runs)}

    return results


def _extract_agent_from_line(agents: set[str], line: str) -> None:
    """Extract agent name from a single registry line."""
    try:
        data = json.loads(line)
        a = data.get("agent")
        if a:
            agents.add(a)
    except Exception as exc:
        _log.debug("Failed to parse run registry line: %s", exc)


def _process_run_line(runs: dict[str, dict[str, Any]], line: str, agent: str) -> None:
    """Process a single run line for a specific agent."""
    try:
        data = json.loads(line)
        rid = data.get("run_id")
        if not rid:
            return
        if data.get("event") == "finish":
            if rid in runs:
                runs[rid].update(data)
        elif data.get("event") == "feedback":
            if rid in runs:
                runs[rid]["feedback_score"] = data.get("feedback_score")
        elif data.get("agent") == agent:
            runs[rid] = data
    except Exception as exc:
        _log.debug("Failed to process run registry line for %s: %s", agent, exc)


def sweep_impl(
    drift_window: int = 50,
    structural_budget: float = 5.0,
    semantic_budget: float = 10.0,
    include_audit: bool = False,
) -> dict[str, Any]:
    """WP-3005: Policy drift sweep - runs drift detection, budget check, past-SLA escalations."""
    return observability_service.sweep_impl(
        drift_window=drift_window,
        structural_budget=structural_budget,
        semantic_budget=semantic_budget,
        include_audit=include_audit,
        update_calibration_fn=update_calibration_impl,
    )


def observe_summary_impl(
    limit: int = 500,
    drift_window: int = 50,
    structural_budget_pct: float = 5.0,
    semantic_budget_pct: float = 10.0,
    provider: str | None = None,
    top_escalations: int = 10,
    trend_samples: int | Any = 0,
) -> dict[str, Any]:
    """FR-X08: Unified observability summary aggregating KPIs, drift, escalation."""
    from thegent.contracts.telemetry import ContractTelemetry
    from thegent.execution import EscalationQueue

    from thegent.cli.commands.observability_trends_impl import (  # pyright: ignore[reportMissingImports]
        OBSERVE_SUMMARY_SCHEMA_VERSION,
        _build_observe_summary_trend_scope,
        _classify_observe_summary_trend_health,
        _hash_observe_summary_payload,
        _hash_observe_summary_trend_scope,
        _load_observe_summary_snapshots,
        _observe_summary_freshness_bucket,
        _parse_observe_summary_timestamp,
    )

    settings = ThegentSettings()
    session_dir = Path(settings.session_dir).expanduser().resolve()

    ct = ContractTelemetry(session_dir)
    kpis = ct.get_fallback_kpis(
        limit=limit,
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        provider=provider,
    )
    drift_issues = ct.detect_drift(window_size=drift_window)
    budget = ct.get_drift_budget_status(
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        limit=limit,
    )

    queue = EscalationQueue(session_dir)
    pending_window = max(top_escalations * 20, 100)
    pending = queue.list_pending(past_sla_only=False, limit=pending_window)
    past_sla = queue.list_pending(past_sla_only=True, limit=pending_window)

    now = datetime.now(UTC)
    escalation_data = observability_service.build_observe_summary_escalation(
        pending=pending,
        past_sla=past_sla,
        now=now,
        top_escalations=top_escalations,
    )
    top_rows = escalation_data["top_rows"]
    past_sla_count = escalation_data["past_sla_count"]
    backlog_count = len(pending)

    trend_data = observability_service.build_observe_summary_trend(
        trend_samples=trend_samples,
        provider=provider,
        drift_window=drift_window,
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        limit=limit,
        top_escalations=top_escalations,
        now=now,
        kpis=kpis,
        budget=budget,
        backlog_count=backlog_count,
        past_sla_count=past_sla_count,
        build_scope_fn=_build_observe_summary_trend_scope,
        hash_scope_fn=_hash_observe_summary_trend_scope,
        load_snapshots_fn=_load_observe_summary_snapshots,
        parse_timestamp_fn=_parse_observe_summary_timestamp,
        freshness_bucket_fn=_observe_summary_freshness_bucket,
        classify_health_fn=_classify_observe_summary_trend_health,
    )
    trend_summary = trend_data["trend_summary"]
    trend_scope_key = trend_data["trend_scope_key"]
    trend_scope_signature = trend_data["trend_scope_signature"]
    trend_scope_key_json = trend_data["trend_scope_key_json"]
    trend_snapshot_ids = trend_data["trend_snapshot_ids"]
    trend_samples_requested = trend_data["trend_samples_requested"]

    payload = {
        "kpis": {
            "total_events": kpis.get("total", 0),
            "fallback_rate": kpis.get("fallback_rate", 0.0),
            "success_rate": kpis.get("success_rate", 0.0),
            "avg_confidence": kpis.get("avg_confidence", 0.0),
            "structural_drift_pct": kpis.get("structural_drift_pct", 0.0),
            "semantic_drift_pct": kpis.get("semantic_drift_pct", 0.0),
            "by_provider": kpis.get("by_provider", {}),
        },
        "drift": {
            "issues": drift_issues,
            "within_budget": budget.get("within_budget", True),
            "structural_rate_pct": budget.get("structural_rate_pct", 0.0),
            "semantic_rate_pct": budget.get("semantic_rate_pct", 0.0),
            "structural_budget_pct": budget.get("structural_budget_pct", structural_budget_pct),
            "semantic_budget_pct": budget.get("semantic_budget_pct", semantic_budget_pct),
        },
        "escalation": {
            "backlog_count": backlog_count,
            "past_sla_count": past_sla_count,
            "top_escalations": top_rows,
            "provider": provider,
            "top_escalations_count": len(top_rows),
        },
        "payload_type": "observe_summary",
        "payload_schema_version": OBSERVE_SUMMARY_SCHEMA_VERSION,
        "generated_at_utc": now.isoformat(),
        "generated_query": {
            "limit": limit,
            "drift_window": drift_window,
            "structural_budget_pct": structural_budget_pct,
            "semantic_budget_pct": semantic_budget_pct,
            "provider": provider,
            "top_escalations": top_escalations,
            "trend_samples": trend_samples_requested,
            "trend_scope_signature": trend_scope_signature,
        },
        "trend_summary": trend_summary,
        "alerts": [
            alert
            for alert in [
                (f"Escalation backlog critical: {past_sla_count} past-SLA" if past_sla_count else ""),
                (
                    f"Contract drift over budget: structural={budget.get('structural_rate_pct', 0.0)}% "
                    f"(budget {budget.get('structural_budget_pct', structural_budget_pct)}%), "
                    f"semantic={budget.get('semantic_rate_pct', 0.0)}% "
                    f"(budget {budget.get('semantic_budget_pct', semantic_budget_pct)}%)"
                    if not budget.get("within_budget", True)
                    else ""
                ),
            ]
            if alert
        ],
        "status": "critical" if past_sla_count or not budget.get("within_budget", True) else "healthy",
    }
    payload["payload_signature"] = _hash_observe_summary_payload(payload)

    _append_observe_summary_snapshot(
        payload, trend_scope_key, trend_scope_signature, trend_scope_key_json, trend_snapshot_ids, trend_summary
    )
    return payload


def _append_observe_summary_snapshot(
    payload: dict[str, Any],
    trend_scope_key: dict[str, Any],
    trend_scope_signature: str,
    scope_key_json: str,
    trend_snapshot_ids: list[str],
    trend_summary: dict[str, Any],
) -> None:
    from thegent.cli.commands.observability_health_impl import _health_snapshot_log_path  # pyright: ignore[reportMissingImports]
    from thegent.cli.commands.observability_trends_impl import OBSERVE_SUMMARY_SCHEMA_VERSION  # pyright: ignore[reportMissingImports]

    record = {
        "record_type": "observe_summary_snapshot",
        "captured_at_utc": payload.get("generated_at_utc", ""),
        "scope_key": trend_scope_key,
        "scope_key_json": scope_key_json,
        "scope_signature": trend_scope_signature,
        "trend_scope_signature": trend_scope_signature,
        "trend_previous_samples_requested": trend_summary.get("trend_previous_samples_requested", 0),
        "trend_snapshot_expected_count": trend_summary.get("trend_snapshot_expected_count", 0),
        "trend_snapshot_deficit": trend_summary.get("trend_snapshot_deficit", 0),
        "trend_snapshot_interval_seconds_avg": trend_summary.get("trend_snapshot_interval_seconds_avg"),
        "trend_snapshot_interval_seconds_min": trend_summary.get("trend_snapshot_interval_seconds_min"),
        "trend_snapshot_interval_seconds_max": trend_summary.get("trend_snapshot_interval_seconds_max"),
        "trend_snapshot_gap_count": trend_summary.get("trend_snapshot_gap_count", 0),
        "trend_snapshot_invalid_timestamps": trend_summary.get("trend_snapshot_invalid_timestamps", 0),
        "trend_snapshot_coverage_pct": trend_summary.get("trend_snapshot_coverage_pct"),
        "trend_snapshot_freshness_bucket": trend_summary.get("trend_snapshot_freshness_bucket", "unknown"),
        "trend_snapshot_freshness_seconds": trend_summary.get("trend_snapshot_freshness_seconds"),
        "trend_snapshot_health": trend_summary.get("trend_snapshot_health", "disabled"),
        "trend_snapshot_health_score": trend_summary.get("trend_snapshot_health_score"),
        "trend_snapshot_recommendations": trend_summary.get("trend_snapshot_recommendations", []),
        "trend_snapshot_health_breakdown": trend_summary.get("trend_snapshot_health_breakdown", {}),
        "trend_snapshot_ids": trend_snapshot_ids,
        "trend_snapshot_ids_csv": trend_summary.get("trend_snapshot_ids_csv", ""),
        "trend_snapshot_ids_hash": trend_summary.get("trend_snapshot_ids_hash", ""),
        "trend_snapshot_window_seconds": trend_summary.get("trend_snapshot_window_seconds"),
        "trend_sampling_mode": trend_summary.get("trend_sampling_mode", "disabled"),
        "trend_enabled": trend_summary.get("enabled", False),
        "schema_version": payload.get("payload_schema_version", OBSERVE_SUMMARY_SCHEMA_VERSION),
        "payload_type": "observe_summary",
        "status": payload.get("status", ""),
        "total_events": payload.get("kpis", {}).get("total_events", 0),
        "fallback_rate": payload.get("kpis", {}).get("fallback_rate", 0.0),
        "success_rate": payload.get("kpis", {}).get("success_rate", 0.0),
        "avg_confidence": payload.get("kpis", {}).get("avg_confidence", 0.0),
        "structural_drift_pct": payload.get("kpis", {}).get("structural_drift_pct", 0.0),
        "semantic_drift_pct": payload.get("kpis", {}).get("semantic_drift_pct", 0.0),
        "drift_structural_rate_pct": payload.get("drift", {}).get("structural_rate_pct", 0.0),
        "drift_semantic_rate_pct": payload.get("drift", {}).get("semantic_rate_pct", 0.0),
        "backlog_count": payload.get("escalation", {}).get("backlog_count", 0),
        "past_sla_count": payload.get("escalation", {}).get("past_sla_count", 0),
        "provider": payload.get("generated_query", {}).get("provider", None),
        "drift_window": payload.get("generated_query", {}).get("drift_window", 0),
        "structural_budget_pct": payload.get("generated_query", {}).get("structural_budget_pct", 0.0),
        "semantic_budget_pct": payload.get("generated_query", {}).get("semantic_budget_pct", 0.0),
        "top_escalations": payload.get("generated_query", {}).get("top_escalations", 0),
        "limit": payload.get("generated_query", {}).get("limit", 0),
        "trend_samples_requested": payload.get("generated_query", {}).get("trend_samples", 0),
        "trend_effective_samples": trend_summary.get("trend_effective_samples", 0),
        "trend_scope_payload_type": trend_scope_key.get("payload_type", "observe_summary"),
    }

    path = _health_snapshot_log_path()
    try:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True).decode())
            fh.write("\n")
    except OSError:
        return
    from thegent.cli.commands.observability_health_impl import _compact_health_snapshot_log  # pyright: ignore[reportMissingImports]

    _compact_health_snapshot_log()


# --- Governance impls ---


def govern_approve_impl(run_id: str, reason: str | None = None) -> dict[str, Any]:
    """WL-019-B: Approve a HITL-blocked run, updating governance_events.jsonl to 'approved'."""
    return governance_service.govern_approve_impl(run_id=run_id, reason=reason)


def govern_reject_impl(run_id: str, reason: str | None = None) -> dict[str, Any]:
    """WL-019-B: Reject a HITL-blocked run, updating governance_events.jsonl to 'rejected'."""
    return governance_service.govern_reject_impl(run_id=run_id, reason=reason)


def govern_list_pending_impl() -> list[dict[str, Any]]:
    """WL-019-B: List all pending HITL approval events from governance_events.jsonl."""
    return governance_service.govern_list_pending_impl()


def govern_vet_impl(
    run_id: str,
    policy: str = "default",
    session: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """WL-098: Evaluate an existing run against Vetter policy checks."""
    return governance_service.govern_vet_impl(run_id=run_id, policy=policy, session=session, dry_run=dry_run)


# --- Review impl ---


def _extract_review_json_payload(raw_stdout: str) -> dict[str, Any]:
    """Parse review JSON payload, accepting optional fenced JSON blocks."""
    try:
        parsed = json.loads(raw_stdout)
    except json.JSONDecodeError:
        text = raw_stdout.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if len(lines) >= 3 and lines[0].startswith("```") and lines[-1] == "```":
                inner = "\n".join(lines[1:-1]).strip()
                if inner.lower().startswith("json"):
                    inner = inner[4:].lstrip()
                try:
                    parsed = json.loads(inner)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Review output is not valid JSON: {exc}") from exc
            else:
                raise ValueError("Review output is not valid JSON: malformed fenced block.")
        else:
            raise ValueError("Review output is not valid JSON.")
    if not isinstance(parsed, dict):
        raise ValueError("Review output JSON root must be an object.")
    return parsed


def review_impl(
    prompt: str,
    agent: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """WL-107: Read-only agent review turn with structured output."""
    from thegent.agents.review_output import validate_review_output
    from thegent.cli.commands.impl import run_impl

    full_prompt = f"{_REVIEW_SCHEMA_PREAMBLE}\n\n{prompt}"
    response = run_impl(
        agent=agent,
        model=model,
        prompt=full_prompt,
        mode="read-only",
        full=True,
        live=False,
    )

    if response.get("exit_code", 1) != 0:
        return {
            "exit_code": response.get("exit_code", 1),
            "error": response.get("stderr") or response.get("error", "Review run failed."),
            "issues": [],
            "summary": "",
            "overall_rating": 0,
        }

    raw_stdout = response.get("stdout", "")
    if not isinstance(raw_stdout, str):
        raise ValueError("Review output must be a JSON string in stdout.")
    parsed_json = _extract_review_json_payload(raw_stdout)

    validated = validate_review_output(parsed_json)
    issues = validated["issues"]
    result: dict[str, Any] = {
        "exit_code": 1 if issues else 0,
        "issues": issues,
        "summary": validated["summary"],
        "overall_rating": validated["overall_rating"],
        "allowed_tools": _REVIEW_ALLOWED_TOOLS,
        "sandbox_mode": "read_only",
    }
    context_usage = response.get("context_usage")
    if isinstance(context_usage, dict):
        result["context_usage"] = context_usage
    return result


# --- Data protection, sitback, compliance ---


def get_data_protection_status_impl() -> dict[str, Any]:
    """Return status of data protection and privacy controls (WP-3006)."""
    import importlib
    import os

    cli_module = importlib.import_module("thegent.cli.commands.impl")
    settings_cls = getattr(cli_module, "ThegentSettings", ThegentSettings)
    settings = settings_cls()
    session_dir = settings.session_dir.expanduser().resolve()

    perms_ok = False
    if session_dir.exists():
        mode = os.stat(session_dir).st_mode
        perms_ok = oct(mode & 0o777) == "0o700"

    return {
        "session_dir": str(session_dir),
        "session_dir_exists": session_dir.exists(),
        "permissions_restricted": perms_ok,
        "masking_enabled": True,
        "encryption_at_rest": False,
        "pii_scanning_enabled": False,
        "retention_policy_days": settings.retention_days_sessions,
        "retention_registry_days": settings.retention_days_registry,
        "retention_health_days": settings.retention_days_health,
    }


def sitback_dashboard_impl(profile: str = "medium") -> dict[str, Any]:
    """Unified sitback dashboard: sessions, cockpit (circuits, drift, budget), terminals."""
    from thegent.cli.commands.session_ops_list_impl import ps_impl

    settings = ThegentSettings()
    session_dir = settings.session_dir.expanduser().resolve()

    sessions = ps_impl(all=True, include_contract=False)
    running = [s for s in sessions if s.get("status") == "running"]
    failed = [s for s in sessions if "exited" in str(s.get("status", "")) and s.get("status") != "exited:0"]

    from thegent.contracts.telemetry import ContractTelemetry
    from thegent.cost.aggregator import CostAggregator
    from thegent.execution import CircuitBreakerRegistry

    circuit_breaker = CircuitBreakerRegistry(session_dir)
    ct = ContractTelemetry(session_dir)
    agg = CostAggregator(session_dir)
    targets = ["claude", "gemini", "codex", "copilot", "antigravity"]
    open_circuits = [t for t in targets if circuit_breaker.is_open(t)]
    drift = ct.get_drift_budget_status()
    mtd_total = agg.get_mtd_total() if hasattr(agg, "get_mtd_total") else 0.0
    budget_mtd = float(getattr(settings, "cost_budget_mtd", 100.0))

    terminals: list[dict[str, Any]] = []
    try:
        from thegent.skills.terminal import is_claude_code_pane, list_tmux_panes

        for p in list_tmux_panes():
            terminals.append(
                {
                    "pane_id": p.pane_id,
                    "session": p.session_name,
                    "path": p.path,
                    "command": p.command,
                    "title": p.title,
                    "is_claude_code": is_claude_code_pane(p),
                }
            )
    except Exception as e:
        _log.warning("sitback_dashboard terminals: %s", e)

    summary = f"Sessions: {len(running)} running, {len(failed)} failed | Terminals: {len(terminals)} panes ({sum(1 for t in terminals if t.get('is_claude_code'))} Claude Code) | Budget: ${mtd_total:.2f} MTD"
    payload: dict[str, Any] = {
        "sessions": {
            "total": len(sessions),
            "running": len(running),
            "failed": len(failed),
            "items": sessions[:20] if profile != "light" else [],
        },
        "cockpit": {
            "circuits": {"open": open_circuits, "all_closed": len(open_circuits) == 0},
            "drift": drift,
            "budget": {"mtd_total": mtd_total, "mtd_budget": budget_mtd, "within_budget": mtd_total < budget_mtd},
        },
        "terminals": {
            "total": len(terminals),
            "claude_code": sum(1 for t in terminals if t.get("is_claude_code")),
            "items": terminals[:30] if profile != "light" else [],
        },
        "summary": summary,
        "profile": profile,
    }
    if profile == "full":
        from thegent.sitback_plugins import get_registry

        reg = get_registry()
        payload["plugin_widgets"] = reg.get_widgets()
        harness = reg.get_harness_status()
        if harness is not None:
            payload["harness_status"] = harness
    return payload


def get_compliance_report_impl() -> dict[str, Any]:
    """Generate compliance evidence retention report (WP-3006)."""
    from datetime import UTC, datetime

    settings = ThegentSettings()
    session_dir = settings.session_dir

    hot_active = 0
    hot_archived = 0
    if session_dir.exists():
        for d in session_dir.iterdir():
            if d.is_dir():
                meta = d / "meta.json"
                if meta.exists():
                    hot_active += 1
                else:
                    hot_archived += 1

    from thegent.execution import RunRegistry

    registry = RunRegistry(session_dir)
    runs = registry.list_runs(limit=1000)
    domain_counts: dict[str, int] = {}
    for r in runs:
        domain = r.get("domain", "general")
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    retention_matrix = [
        {"domain": domain, "retention_days": 90, "run_count": count} for domain, count in sorted(domain_counts.items())
    ]

    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "tiered_storage": {
            "hot_active_sessions": hot_active,
            "hot_archived": hot_archived,
            "retention_hot_days": 30,
            "cold": 0,
            "retention_cold_days": 365,
        },
        "retention_matrix": retention_matrix,
        "data_protection": {
            "session_dir": str(session_dir),
            "permissions_restricted": session_dir.exists() and oct(session_dir.stat().st_mode)[-3:] in ("700", "750"),
            "masking_enabled": False,
        },
    }
