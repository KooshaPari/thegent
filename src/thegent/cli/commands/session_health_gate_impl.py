"""Session contract health gate evaluation logic.

Extracted from session_health_impl.py as part of WL-120 LOC Reduction Program.
Contains:
- session_contract_health_gate_impl: evaluate routing contract health against a minimum ratio gate
- Policy resolution, baseline comparison, trend tracking
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from thegent.cli.commands.session_health_contracts_impl import session_contract_audit_impl

_log = logging.getLogger(__name__)

__all__ = [
    "session_contract_health_gate_impl",
]


def _health_impl():  # pyright: ignore[reportMissingImports]
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
    except TypeError, ValueError:
        cur_ratio = 0.0
        cur_count = 0

    if previous is not None:
        try:
            previous_ratio = float(str(previous.get("blocked_ratio", cur_ratio)))
        except TypeError, ValueError:
            previous_ratio = cur_ratio
        try:
            previous_count = int(str(previous.get("blocked_count", cur_count)))
        except TypeError, ValueError:
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
