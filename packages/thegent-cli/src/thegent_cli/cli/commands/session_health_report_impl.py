"""Session contract health report logic.

Extracted from session_health_impl.py as part of WL-120 max-lines enforcement.
Trend logic extracted to session_health_trend_impl.py.
Contains:
- session_contract_health_report_impl: health report with issue taxonomy and owner breakdown
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, cast

from thegent.cli.commands.session_health_impl import session_contract_audit_impl

_log = logging.getLogger(__name__)


def _health_report_impl():
    from thegent.cli.commands import impl as cli_impl

    return cli_impl


def _get_health_payload_schema_version() -> str:
    return _health_report_impl().HEALTH_PAYLOAD_SCHEMA_VERSION


def _get_health_payload_types() -> list[str]:
    return _health_report_impl().HEALTH_PAYLOAD_TYPES


def _resolve_health_policy(policy_profile: str | None, strict: bool, min_healthy_ratio: float) -> dict[str, Any]:
    return _health_report_impl()._resolve_health_policy(
        policy_profile=policy_profile, strict=strict, min_healthy_ratio=min_healthy_ratio
    )


def _coerce_issue_types(value: Any) -> list[str]:
    return _health_report_impl()._coerce_issue_types(value)


def _health_scope_key(payload: dict[str, Any]) -> dict[str, Any]:
    return _health_report_impl()._health_scope_key(payload)


def _load_previous_health_snapshot(scope_key: dict[str, Any]) -> dict[str, Any] | None:
    return _health_report_impl()._load_previous_health_snapshot(scope_key)


def _append_health_snapshot(payload: dict[str, Any], scope_key: dict[str, Any]) -> None:
    return _health_report_impl()._append_health_snapshot(payload, scope_key)


def _hash_health_payload(payload: dict[str, Any]) -> str:
    return _health_report_impl()._hash_health_payload(payload)


def _health_snapshot_log_path():
    return _health_report_impl()._health_snapshot_log_path()


def _health_snapshot_max_lines() -> int:
    return _health_report_impl()._health_snapshot_max_lines()


def session_contract_health_report_impl(
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    top_blocked: int = 25,
    policy_profile: str | None = None,
    no_worse_than_baseline: bool = False,
    regression_tolerance: float = 0.0,
) -> dict[str, Any]:
    """
    Return health report with issue taxonomy and owner-level breakdown.
    """
    remediation_map = {
        "misalign:provider_hint": "Normalize requested_provider_hint to match contract provider or clear hint before routing.",
        "misalign:resolved_alias": "Align resolved alias/model with chosen contract model_alias.",
        "misalign:resolved_agent": "Set resolved_agent to selected contract provider.",
        "missing_contract:provider": "Ensure route_contract includes provider metadata at session creation.",
        "missing_contract:model_alias": "Ensure route_contract includes model_alias metadata at session creation.",
        "missing_contract:backend_type": "Ensure route_contract includes backend_type metadata at session creation.",
        "missing_contract:priority": "Ensure route_contract includes routing priority metadata at session creation.",
        "missing_contract:schema_version": "Ensure route_contract captures schema version at session creation.",
        "missing_request:requested_model": "Populate requested_model in route_request before persisting session metadata.",
        "missing_request:policy": "Persist route request policy (prefer_direct, prefer_proxy, failover).",
    }

    def _remediation_lines(row_issues: list[str]) -> list[str]:
        lines: list[str] = []
        for issue in row_issues:
            hint = remediation_map.get(str(issue))
            if hint is not None:
                lines.append(hint)
        if not lines and row_issues:
            lines.append("Review session route metadata capture path and re-run routing with include_contract.")
        if not row_issues:
            lines.append("No issues detected; this row is not blocked.")
        return lines

    max_blocked = top_blocked
    if max_blocked is None:
        max_blocked = 25
    max_blocked = max(max_blocked, 0)

    policy = _resolve_health_policy(policy_profile, strict, 1.0)
    effective_strict = bool(policy["strict"])
    tolerance = max(0.0, float(regression_tolerance))

    audit = session_contract_audit_impl(
        owner=owner,
        all=all,
        missing_only=False,
        summary_only=False,
        strict=effective_strict,
    )
    rows = audit["rows"]
    summary = audit["summary"]
    health = summary.get("health", {})
    total = int(summary.get("total", 0))

    issue_counts: dict[str, int] = {}
    owner_breakdown: dict[str, dict[str, int]] = {}
    blocked_rows: list[dict[str, Any]] = []

    for row in rows:
        owner_name = str(row.get("owner", ""))
        bucket = owner_breakdown.setdefault(
            owner_name,
            {"total": 0, "healthy": 0, "warning": 0, "error": 0, "missing": 0},
        )
        bucket["total"] += 1
        health_state = str(row.get("contract_health", "warning"))
        bucket[health_state] = bucket.get(health_state, 0) + 1

        issues = row.get("contract_issues") or []
        for issue in _coerce_issue_types(issues):
            issue_key = str(issue)
            issue_counts[issue_key] = issue_counts.get(issue_key, 0) + 1

        if row.get("contract_health") != "healthy":
            issues = sorted(
                [str(issue) for issue in _coerce_issue_types(row.get("contract_issues") or [])],
                key=str,
            )
            blocked_rows.append(
                {
                    "session_id": str(row.get("session_id", "")),
                    "owner": owner_name,
                    "state": row.get("contract_state"),
                    "health": row.get("contract_health"),
                    "issues": issues,
                    "remediation": _remediation_lines(cast("list[str]", issues)),
                    "started_at_utc": row.get("started_at_utc", ""),
                    "agent": row.get("agent", ""),
                }
            )

    issue_counts = {key: issue_counts[key] for key in sorted(issue_counts)}
    issue_breakdown = [
        {"issue": key, "count": count}
        for key, count in sorted(
            issue_counts.items(),
            key=lambda kv: (kv[1], str(kv[0])),
        )
        if count
    ]
    issue_breakdown = sorted(
        issue_breakdown,
        key=lambda row: (-int(row["count"]), str(row["issue"])),
    )

    for row in owner_breakdown.values():
        row.setdefault("missing", row.get("missing", 0))
        row.setdefault("warning", row.get("warning", 0))
        row.setdefault("error", row.get("error", 0))
        row.setdefault("healthy", row.get("healthy", 0))

    owner_breakdown = {owner_key: owner_breakdown[owner_key] for owner_key in sorted(owner_breakdown, key=str.lower)}

    blocked_rows_sorted = sorted(
        blocked_rows,
        key=lambda row: (
            str(row.get("health") or ""),
            str(row.get("owner") or ""),
            str(row.get("state") or ""),
            str(row.get("session_id") or ""),
        ),
    )
    blocked_count = len(blocked_rows)
    healthy_count = int(health.get("healthy", 0))
    unhealthy_count = max(total - int(health.get("healthy", 0)), 0)
    payload = {
        "schema_version": _get_health_payload_schema_version(),
        "payload_type": "session_contract_health_report",
        "schema_compat_mode": "compat",
        "pass": blocked_count == 0,
        "status": "passed" if blocked_count == 0 else "blocked",
        "total": total,
        "total_sessions": total,
        "healthy_count": healthy_count,
        "healthy_sessions": healthy_count,
        "unhealthy_count": unhealthy_count,
        "unhealthy_sessions": unhealthy_count,
        "summary": summary,
        "health": health,
        "issue_counts": issue_counts,
        "issue_breakdown": issue_breakdown,
        "owner_breakdown": owner_breakdown,
        "top_blocked": blocked_rows_sorted[:max_blocked],
        "blocked_count": blocked_count,
        "blocked_sessions": blocked_count,
        "blocked_sessions_count": blocked_count,
        "top_blocked_count": min(max_blocked, len(blocked_rows)),
        "strict_checks_enabled": effective_strict,
        "policy_profile": policy["profile"],
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "generated_query": {
            "owner": owner,
            "all": all,
            "strict": effective_strict,
            "top_blocked": max_blocked,
        },
    }

    scope_key = _health_scope_key(payload)
    previous = _load_previous_health_snapshot(scope_key)

    cur_count = blocked_count
    cur_ratio = (1.0 - (healthy_count / total)) if total > 0 else 0.0
    if previous is not None:
        try:
            previous_ratio = float(str(previous.get("blocked_ratio", cur_ratio)))
        except (TypeError, ValueError):
            previous_ratio = cur_ratio
        try:
            previous_count = int(str(previous.get("blocked_count", cur_count)))
        except (TypeError, ValueError):
            previous_count = cur_count
    else:
        previous_ratio = cur_ratio
        previous_count = cur_count
    previous_issue_types = set(_coerce_issue_types((previous or {}).get("issue_types", [])))
    current_issue_types: set[str] = set()
    for row in blocked_rows:
        current_issue_types.update(_coerce_issue_types(row.get("issues", [])))

    baseline_pass = True
    if no_worse_than_baseline and previous is not None:
        baseline_pass = cur_ratio <= (previous_ratio + tolerance)

    final_pass = (blocked_count == 0) and baseline_pass
    payload["pass"] = final_pass
    payload["status"] = "passed" if final_pass else "blocked"
    payload["blocked_ratio"] = cur_ratio
    payload["trend_summary"] = {
        "baseline_available": previous is not None,
        "blocked_ratio_delta": (cur_ratio - previous_ratio if previous is not None else None),
        "blocked_count_delta": cur_count - previous_count if previous is not None else None,
        "new_issue_types": sorted(current_issue_types - previous_issue_types),
        "resolved_issue_types": sorted(previous_issue_types - current_issue_types),
    }
    payload["compat"] = {
        "mode": "compat",
        "aliases": {
            "total_sessions": "total",
            "healthy_sessions": "healthy_count",
            "unhealthy_sessions": "unhealthy_count",
            "blocked_sessions_count": "blocked_count",
        },
    }
    payload["payload_signature"] = _hash_health_payload(payload)
    _append_health_snapshot(payload, scope_key)
    return payload


