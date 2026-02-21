"""Session contract health report and trend logic.

Extracted from session_health_impl.py as part of WL-120 max-lines enforcement.
Contains:
- session_contract_health_report_impl: health report with issue taxonomy and owner breakdown
- session_contract_health_trend_impl: recent health snapshots and deltas
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from typing import Any, cast

import typer

from thegent.cli.commands.observability_impl import (
    HEALTH_PAYLOAD_SCHEMA_VERSION,
    HEALTH_PAYLOAD_TYPES,
    _append_health_snapshot,
    _coerce_issue_types,
    _hash_health_payload,
    _health_scope_key,
    _health_snapshot_log_path,
    _health_snapshot_max_lines,
    _load_previous_health_snapshot,
    _resolve_health_policy,
)
from thegent.cli.commands.session_health_impl import (
    _extract_blocked_ratio,
    session_contract_audit_impl,
)

_log = logging.getLogger(__name__)


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
        "schema_version": HEALTH_PAYLOAD_SCHEMA_VERSION,
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


def session_contract_health_trend_impl(
    payload_type: str = "session_contract_health_report",
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    policy_profile: str | None = None,
    min_healthy_ratio: float = 1.0,
    top_blocked: int = 25,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Return recent health snapshots and deltas for a given policy/query scope.
    """
    if payload_type not in HEALTH_PAYLOAD_TYPES:
        raise typer.BadParameter(
            f"Unsupported payload_type '{payload_type}'. Choose one of: {', '.join(HEALTH_PAYLOAD_TYPES)}."
        )
    policy = _resolve_health_policy(policy_profile, strict, min_healthy_ratio)
    gen_query: dict[str, Any] = {
        "owner": owner,
        "all": all,
        "strict": policy["strict"],
    }
    if payload_type == "session_contract_health_gate":
        gen_query["min_healthy_ratio"] = policy["min_healthy_ratio"]
    else:
        gen_query["top_blocked"] = int(top_blocked)

    scope_payload: dict[str, Any] = {
        "payload_type": payload_type,
        "policy_profile": policy["profile"],
        "generated_query": gen_query,
    }
    scope_key = _health_scope_key(scope_payload)

    max_items = max(1, int(limit))
    path = _health_snapshot_log_path()
    snapshots: list[dict[str, Any]] = []
    if path.exists():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            lines = []
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("record_type") != "health_snapshot":
                continue
            if rec.get("scope_key") != scope_key:
                continue
            snapshots.append(rec)
            if len(snapshots) >= max_items:
                break

    latest = snapshots[0] if snapshots else None
    oldest = snapshots[-1] if snapshots else None
    delta_ratio = None
    delta_count = None
    if latest is not None and oldest is not None and len(snapshots) > 1:
        delta_ratio = float(latest.get("blocked_ratio", 0.0)) - float(oldest.get("blocked_ratio", 0.0))
        delta_count = int(latest.get("blocked_count", 0)) - int(oldest.get("blocked_count", 0))
    snapshot_window_seconds = None
    if latest is not None and oldest is not None and len(snapshots) > 1:
        latest_ts_raw = (latest or {}).get("captured_at_utc", "")
        oldest_ts_raw = (oldest or {}).get("captured_at_utc", "")
        try:
            latest_ts = datetime.fromisoformat(str(latest_ts_raw))
            oldest_ts = datetime.fromisoformat(str(oldest_ts_raw))
            snapshot_window_seconds = int((latest_ts - oldest_ts).total_seconds())
        except (TypeError, ValueError):
            snapshot_window_seconds = None
    snapshot_interval_seconds_avg = None
    parsed_ts: list[datetime] = []
    for snap in snapshots:
        ts_raw = (snap or {}).get("captured_at_utc", "")
        if not ts_raw:
            continue
        try:
            parsed_ts.append(datetime.fromisoformat(str(ts_raw)))
        except (TypeError, ValueError):
            continue
    if len(parsed_ts) > 1:
        parsed_ts.sort()
        diffs: list[int] = []
        for i in range(1, len(parsed_ts)):
            diffs.append(int((parsed_ts[i] - parsed_ts[i - 1]).total_seconds()))
        if diffs:
            snapshot_interval_seconds_avg = int(sum(diffs) / len(diffs))
    snapshot_ids_csv = ", ".join(
        [str((s or {}).get("captured_at_utc", "")) for s in snapshots if (s or {}).get("captured_at_utc", "")]
    )
    generated_at = datetime.now(UTC)
    snapshot_freshness_seconds = None
    if latest is not None:
        latest_ts_raw = (latest or {}).get("captured_at_utc", "")
        try:
            latest_ts = datetime.fromisoformat(str(latest_ts_raw))
            snapshot_freshness_seconds = int((generated_at - latest_ts).total_seconds())
        except (TypeError, ValueError):
            snapshot_freshness_seconds = None
    snapshot_density_per_hour = None
    if snapshot_window_seconds is not None and snapshot_window_seconds > 0 and len(snapshots) > 0:
        snapshot_density_per_hour = round((len(snapshots) * 3600.0) / float(snapshot_window_seconds), 6)
    latest_issue_types = set(_coerce_issue_types((latest or {}).get("issue_types", [])))
    oldest_issue_types = set(_coerce_issue_types((oldest or {}).get("issue_types", [])))
    snapshot_issue_churn_count = len(latest_issue_types.symmetric_difference(oldest_issue_types))
    snapshot_health_volatility = None
    blocked_ratios: list[float] = []
    for snap in snapshots:
        _extract_blocked_ratio(blocked_ratios, snap)
    if len(blocked_ratios) > 1:
        mean_ratio = sum(blocked_ratios) / len(blocked_ratios)
        variance = sum((r - mean_ratio) ** 2 for r in blocked_ratios) / len(blocked_ratios)
        snapshot_health_volatility = round(variance**0.5, 6)

    payload: dict[str, Any] = {
        "schema_version": HEALTH_PAYLOAD_SCHEMA_VERSION,
        "payload_type": "session_contract_health_trend",
        "schema_compat_mode": "compat",
        "trend_payload_type": payload_type,
        "scope_key": scope_key,
        "scope_key_json": json.dumps(scope_key, sort_keys=True),
        "scope_payload_type": scope_key.get("payload_type", ""),
        "scope_owner": scope_key.get("owner", ""),
        "scope_all": scope_key.get("all", False),
        "scope_strict": scope_key.get("strict", False),
        "scope_policy_profile": scope_key.get("policy_profile", "custom"),
        "scope_min_healthy_ratio": scope_key.get("min_healthy_ratio", None),
        "scope_top_blocked": scope_key.get("top_blocked", None),
        "snapshot_count": len(snapshots),
        "snapshot_ids_csv": snapshot_ids_csv,
        "snapshot_ids_hash": hashlib.sha256(snapshot_ids_csv.encode("utf-8")).hexdigest(),
        "snapshot_window_seconds": snapshot_window_seconds,
        "snapshot_window_hash": hashlib.sha256(str(snapshot_window_seconds).encode("utf-8")).hexdigest(),
        "snapshot_interval_seconds_avg": snapshot_interval_seconds_avg,
        "snapshot_interval_hash": hashlib.sha256(str(snapshot_interval_seconds_avg).encode("utf-8")).hexdigest(),
        "snapshot_freshness_seconds": snapshot_freshness_seconds,
        "snapshot_freshness_hash": hashlib.sha256(str(snapshot_freshness_seconds).encode("utf-8")).hexdigest(),
        "snapshot_density_per_hour": snapshot_density_per_hour,
        "snapshot_density_hash": hashlib.sha256(str(snapshot_density_per_hour).encode("utf-8")).hexdigest(),
        "snapshot_issue_churn_count": snapshot_issue_churn_count,
        "snapshot_issue_churn_hash": hashlib.sha256(str(snapshot_issue_churn_count).encode("utf-8")).hexdigest(),
        "snapshot_health_volatility": snapshot_health_volatility,
        "snapshot_health_volatility_hash": hashlib.sha256(str(snapshot_health_volatility).encode("utf-8")).hexdigest(),
        "limit": max_items,
        "latest": latest,
        "latest_status": (latest or {}).get("status", ""),
        "latest_pass": (latest or {}).get("pass", None),
        "latest_captured_at_utc": (latest or {}).get("captured_at_utc", ""),
        "latest_blocked_ratio": (latest or {}).get("blocked_ratio", None),
        "latest_blocked_count": (latest or {}).get("blocked_count", None),
        "latest_issue_types_count": len(_coerce_issue_types((latest or {}).get("issue_types", []))),
        "latest_issue_types_json": json.dumps(_coerce_issue_types((latest or {}).get("issue_types", []))),
        "latest_issue_types_csv": ", ".join(str(v) for v in _coerce_issue_types((latest or {}).get("issue_types", []))),
        "latest_issue_types_hash": hashlib.sha256(
            json.dumps(_coerce_issue_types((latest or {}).get("issue_types", []))).encode("utf-8")
        ).hexdigest(),
        "oldest": oldest,
        "delta_summary": {
            "blocked_ratio_delta": delta_ratio,
            "blocked_count_delta": delta_count,
        },
        "delta_summary_json": json.dumps(
            {
                "blocked_count_delta": delta_count,
                "blocked_ratio_delta": delta_ratio,
            },
            sort_keys=True,
        ),
        "blocked_ratio_delta": delta_ratio,
        "blocked_count_delta": delta_count,
        "snapshot_retention_max_lines": _health_snapshot_max_lines(),
        "snapshots": snapshots,
        "generated_at_utc": generated_at.isoformat(),
        "compat": {
            "mode": "compat",
            "aliases": {
                "scope.owner": "scope_owner",
                "scope.all": "scope_all",
                "scope.strict": "scope_strict",
                "scope.policy_profile": "scope_policy_profile",
                "scope.min_healthy_ratio": "scope_min_healthy_ratio",
                "scope.top_blocked": "scope_top_blocked",
            },
        },
    }
    compat = cast("dict[str, Any]", payload.get("compat", {}))
    compat_aliases = cast("dict[str, str]", compat.get("aliases", {}))
    payload["compat_aliases_count"] = len(compat_aliases)
    payload["payload_signature"] = _hash_health_payload(payload)
    return payload
