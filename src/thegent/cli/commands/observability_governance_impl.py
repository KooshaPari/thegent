"""Observability governance, review, and compliance implementations (WL-120).

Governance approval/rejection, code review, data protection, sitback dashboard.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from thegent.cli.services import governance as governance_service
from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)

__all__ = [
    "_extract_review_json_payload",
    "get_server_meta_impl",
    "govern_approve_impl",
    "govern_reject_impl",
    "govern_list_pending_impl",
    "govern_vet_impl",
    "review_impl",
    "get_data_protection_status_impl",
    "sitback_dashboard_impl",
    "get_compliance_report_impl",
]

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

    from thegent.cli.commands.observability_health_impl import HEALTH_POLICY_PROFILES

    from thegent.cli.services import observability as observability_service

    return observability_service.get_server_meta_impl(
        health_payload_schema_version=HEALTH_PAYLOAD_SCHEMA_VERSION,
        health_payload_types=HEALTH_PAYLOAD_TYPES,
        observe_summary_payload_schema_version=OBSERVE_SUMMARY_SCHEMA_VERSION,
        observe_summary_payload_types=OBSERVE_SUMMARY_PAYLOAD_TYPES,
        health_policy_profiles=sorted(HEALTH_POLICY_PROFILES.keys()),
    )


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


def _extract_review_json_payload(raw_stdout: str) -> dict[str, Any]:
    """Parse review JSON payload, accepting optional fenced JSON blocks."""
    import orjson as json

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
