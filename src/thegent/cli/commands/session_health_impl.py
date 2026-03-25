"""Session contract listing, audit, and health gate logic.

Extracted from session_impl.py as part of WL-120 LOC Reduction Program (Wave-3, W3-B2-split).
health_report_impl and health_trend_impl split to session_health_report_impl.py.
Contains:
- _extract_blocked_ratio: helper for blocked ratio extraction
- list_session_contracts_impl: list sessions with contract metadata and quality signal
- session_contract_audit_impl: session contract audit rows with filtering and summary
- session_contract_health_gate_impl: evaluate routing contract health against a minimum ratio gate
"""

from __future__ import annotations

import contextlib
import logging
from datetime import UTC, datetime
from typing import Any


def _health_impl():
    from thegent.cli.commands import impl as cli_impl

    return cli_impl


def _health_impl_payload_schema_version() -> str:
    return _health_impl().HEALTH_PAYLOAD_SCHEMA_VERSION


def _resolve_health_policy(policy_profile: str | None, strict: bool, min_healthy_ratio: float) -> dict[str, Any]:
    return _health_impl()._resolve_health_policy(policy_profile, strict, min_healthy_ratio)


def _coerce_issue_types(value: Any) -> list[str]:
    return _health_impl()._coerce_issue_types(value)


def _hash_health_payload(payload: dict[str, Any]) -> dict[str, str]:
    return _health_impl()._hash_health_payload(payload)


def _health_scope_key(payload: dict[str, Any]) -> dict[str, Any]:
    return _health_impl()._health_scope_key(payload)


def _load_previous_health_snapshot(scope_key: dict[str, Any]) -> dict[str, Any] | None:
    return _health_impl()._load_previous_health_snapshot(scope_key)


def _append_health_snapshot(payload: dict[str, Any], scope_key: dict[str, Any]) -> None:
    return _health_impl()._append_health_snapshot(payload, scope_key)


_log = logging.getLogger(__name__)

__all__ = [
    "_extract_blocked_ratio",
    "list_session_contracts_impl",
    "session_contract_audit_impl",
    "session_contract_health_gate_impl",
]


def _extract_blocked_ratio(ratios: list[float], snap: dict[str, Any] | None) -> None:
    """Extract blocked ratio from a single snapshot safely."""
    with contextlib.suppress(TypeError, ValueError):
        ratios.append(float((snap or {}).get("blocked_ratio", 0.0)))


def list_session_contracts_impl(
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
) -> list[dict[str, Any]]:
    """
    Return sessions with route-request/route-contract metadata and contract quality signal.
    """
    from thegent.cli.commands import impl as cli_impl

    def _alignment_issues(
        route_request: dict[str, Any] | None,
        route_contract: dict[str, Any] | None,
    ) -> list[str]:
        if not strict or not route_request or not route_contract:
            return []

        issues: list[str] = []
        requested_provider = route_request.get("requested_provider_hint")
        contract_provider = route_contract.get("provider")
        if requested_provider is not None and contract_provider is not None and requested_provider != contract_provider:
            issues.append("misalign:provider_hint")

        requested_alias = route_request.get("resolved_model_alias") or route_request.get("resolved_alias")
        contract_alias = route_contract.get("model_alias")
        if requested_alias is not None and contract_alias is not None and requested_alias != contract_alias:
            issues.append("misalign:resolved_alias")

        resolved_agent = route_request.get("resolved_agent")
        if resolved_agent is not None and contract_provider is not None and resolved_agent != contract_provider:
            issues.append("misalign:resolved_agent")

        return issues

    rows = cli_impl.ps_impl(owner=owner, all=all, include_contract=True)
    contracts: list[dict[str, Any]] = []

    for row in rows:
        route_request = row.get("route_request")
        route_contract = row.get("route_contract")
        request_obj = route_request if isinstance(route_request, dict) else None
        contract_obj = route_contract if isinstance(route_contract, dict) else None
        request_present = request_obj is not None
        contract_present = contract_obj is not None

        contract_issues: list[str] = []
        if contract_obj is not None:
            required_contract_fields = ("provider", "model_alias", "backend_type", "priority")
            for key in required_contract_fields:
                if contract_obj.get(key) is None:
                    contract_issues.append(f"missing_contract:{key}")
            if contract_obj.get("schema_version") is None:
                contract_issues.append("missing_contract:schema_version")
        if request_obj is not None:
            if not request_obj.get("requested_model"):
                contract_issues.append("missing_request:requested_model")
            if request_obj.get("policy") not in {"prefer_direct", "prefer_proxy", "failover"}:
                contract_issues.append("missing_request:policy")

        if not request_present and not contract_present:
            state = "untracked"
        elif request_present and not contract_present:
            state = "request_only"
        elif contract_present and not request_present:
            state = "contract_only"
        elif contract_issues:
            state = "partial"
        else:
            state = "complete"

        alignment_issues = _alignment_issues(request_obj, contract_obj)
        contract_issues.extend(alignment_issues)

        if not request_present or not contract_present:
            contract_health = "missing"
        elif any(issue.startswith("misalign:") for issue in alignment_issues):
            contract_health = "error"
        elif contract_issues:
            contract_health = "warning"
        else:
            contract_health = "healthy"

        contracts.append(
            {
                "session_id": row.get("id", ""),
                "agent": row.get("agent", ""),
                "owner": row.get("owner", ""),
                "pid": row.get("pid", 0),
                "status": row.get("status", "unknown"),
                "started_at_utc": row.get("started_at_utc", ""),
                "route_request": request_obj,
                "route_contract": contract_obj,
                "contract_state": state,
                "route_request_present": request_present,
                "route_contract_present": contract_present,
                "contract_health": contract_health,
                "strict_checks_enabled": strict,
                "contract_issues": contract_issues,
                "requested_model": request_obj.get("requested_model") if request_obj is not None else None,
                "requested_provider_hint": request_obj.get("requested_provider_hint")
                if request_obj is not None
                else None,
                "resolved_model_alias": (request_obj.get("resolved_model_alias") or request_obj.get("resolved_alias"))
                if request_obj is not None
                else None,
                "policy": request_obj.get("policy") if request_obj is not None else None,
            }
        )

    return contracts


def session_contract_audit_impl(
    owner: str | None = None,
    all: bool = False,
    missing_only: bool = False,
    summary_only: bool = False,
    strict: bool = False,
) -> dict[str, Any]:
    """
    Return session contract audit rows with optional filtering and summary.
    """
    from thegent.cli.commands import impl as cli_impl

    rows = cli_impl.list_session_contracts_impl(owner=owner, all=all, strict=strict)
    if missing_only:
        rows = [row for row in rows if row.get("contract_state") != "complete"]

    states: dict[str, int] = {}
    for row in rows:
        state = str(row.get("contract_state", "unknown"))
        states[state] = states.get(state, 0) + 1

    health: dict[str, int] = {"healthy": 0, "warning": 0, "error": 0, "missing": 0}
    for row in rows:
        key = str(row.get("contract_health", "warning"))
        health[key] = health.get(key, 0) + 1

    summary = {
        "total": len(rows),
        "complete": states.get("complete", 0),
        "partial": states.get("partial", 0),
        "request_only": states.get("request_only", 0),
        "contract_only": states.get("contract_only", 0),
        "untracked": states.get("untracked", 0),
        "strict_checks_enabled": strict,
        "health": health,
    }
    if summary_only:
        return {"rows": [], "summary": summary}
    return {"rows": rows, "summary": summary}


def session_contract_health_gate_impl(
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    min_healthy_ratio: float = 1.0,
    policy_profile: str | None = None,
    no_worse_than_baseline: bool = False,
    regression_tolerance: float = 0.0,
) -> dict[str, Any]:
    """
    Evaluate routing contract health against a minimum healthy-ratio gate.
    """
    policy = _resolve_health_policy(policy_profile, strict, min_healthy_ratio)
    effective_strict = bool(policy["strict"])
    threshold = float(policy["min_healthy_ratio"])
    tolerance = max(0.0, float(regression_tolerance))

    audit = session_contract_audit_impl(
        owner=owner,
        all=all,
        missing_only=False,
        summary_only=False,
        strict=effective_strict,
    )
    summary = audit["summary"]
    rows = audit["rows"]
    total = int(summary.get("total", 0))

    health = summary.get("health", {})
    healthy_count = int(health.get("healthy", 0))
    unhealthy_count = max(total - healthy_count, 0)
    ratio = (healthy_count / total) if total > 0 else 1.0
    ratio_pass = total == 0 or ratio >= threshold

    blockers = [
        {
            "session_id": str(row.get("session_id")),
            "state": row.get("contract_state"),
            "health": row.get("contract_health"),
            "issues": _coerce_issue_types(row.get("contract_issues")),
        }
        for row in rows
        if row.get("contract_health") != "healthy"
    ]
    blockers = sorted(
        blockers,
        key=lambda row: (
            str(row.get("health") or ""),
            str(row.get("state") or ""),
            str(row.get("session_id") or ""),
        ),
    )
    blockers = [
        {
            **row,
            "issues": sorted(_coerce_issue_types(row.get("issues", [])), key=str),
        }
        for row in blockers
    ]

    payload = {
        "schema_version": _health_impl_payload_schema_version(),
        "payload_type": "session_contract_health_gate",
        "schema_compat_mode": "compat",
        "pass": ratio_pass,
        "status": "passed" if ratio_pass else "blocked",
        "threshold": threshold,
        "total": total,
        "total_sessions": total,
        "healthy_count": healthy_count,
        "healthy_sessions": healthy_count,
        "unhealthy_count": unhealthy_count,
        "unhealthy_sessions": unhealthy_count,
        "healthy_ratio": ratio,
        "summary": summary,
        "blocked_count": len(blockers),
        "blocked_sessions_count": len(blockers),
        "blocked_ratio": (1.0 - ratio) if total > 0 else 0.0,
        "top_blocked_count": min(200, len(blockers)),
        "blocked_sessions_cap": 200,
        "blocked_sessions": blockers[:200],
        "strict_checks_enabled": effective_strict,
        "policy_profile": policy["profile"],
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "generated_query": {
            "owner": owner,
            "all": all,
            "strict": effective_strict,
            "min_healthy_ratio": threshold,
        },
    }
    scope_key = _health_scope_key(payload)
    previous = _load_previous_health_snapshot(scope_key)

    blocked_ratio_val = payload.get("blocked_ratio", 0.0)
    blocked_count_val = payload.get("blocked_count", 0)
    cur_ratio = 0.0
    cur_count = 0
    try:
        if blocked_ratio_val is not None:
            cur_ratio = float(str(blocked_ratio_val))
        if blocked_count_val is not None:
            cur_count = int(str(blocked_count_val))
    except (TypeError, ValueError):
        cur_ratio = 0.0
        cur_count = 0

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
    for row in blockers:
        current_issue_types.update(_coerce_issue_types(row.get("issues", [])))

    baseline_pass = True
    if no_worse_than_baseline and previous is not None:
        baseline_pass = cur_ratio <= (previous_ratio + tolerance)

    final_pass = ratio_pass and baseline_pass
    reason_codes: list[str] = []
    if not ratio_pass:
        reason_codes.append("ratio_below_threshold")
    if no_worse_than_baseline and previous is not None and not baseline_pass:
        reason_codes.append("baseline_regression")
    payload["pass"] = final_pass
    payload["status"] = "passed" if final_pass else "blocked"
    payload["decision_reasons"] = reason_codes or ["ok"]
    payload["policy_evaluation"] = {
        "profile": policy["profile"],
        "profile_exists": policy["profile_exists"],
        "enforce_no_worse_than_baseline": bool(no_worse_than_baseline),
        "regression_tolerance": tolerance,
        "rules": [
            {
                "id": "min_healthy_ratio",
                "pass": ratio_pass,
                "actual_healthy_ratio": ratio,
                "threshold": threshold,
            },
            {
                "id": "no_worse_than_baseline",
                "enabled": bool(no_worse_than_baseline),
                "baseline_available": previous is not None,
                "pass": baseline_pass if no_worse_than_baseline and previous is not None else True,
                "baseline_blocked_ratio": previous_ratio if previous is not None else None,
                "current_blocked_ratio": cur_ratio,
                "blocked_ratio_delta": (cur_ratio - previous_ratio if previous is not None else None),
            },
        ],
        "final_pass": final_pass,
    }
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


# Note: session_contract_health_report_impl and session_contract_health_trend_impl
# are NOT re-exported here due to circular import dependencies. Import them directly
# from their respective modules:
# from thegent.cli.commands.session_health_report_impl import session_contract_health_report_impl
# from thegent.cli.commands.session_health_trend_impl import session_contract_health_trend_impl
