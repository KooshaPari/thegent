"""Session contract health trend logic.

Extracted from session_health_report_impl.py as part of LOC reduction.
Contains:
- session_contract_health_trend_impl: recent health snapshots and deltas
"""

from __future__ import annotations

import hashlib
import orjson as json
import logging
from datetime import UTC, datetime
from typing import Any, cast

import typer

from thegent.cli.commands.session_health_impl import _extract_blocked_ratio
from thegent.cli.commands.observability_health_impl import HEALTH_PAYLOAD_TYPES  # pyright: ignore[reportMissingImports]

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


def _hash_health_payload(payload: dict[str, Any]) -> str:
    return _health_report_impl()._hash_health_payload(payload)


def _health_snapshot_log_path():
    return _health_report_impl()._health_snapshot_log_path()


def _health_snapshot_max_lines() -> int:
    return _health_report_impl()._health_snapshot_max_lines()


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
        "schema_version": _get_health_payload_schema_version(),
        "payload_type": "session_contract_health_trend",
        "schema_compat_mode": "compat",
        "trend_payload_type": payload_type,
        "scope_key": scope_key,
        "scope_key_json": json.dumps(scope_key, sort_keys=True).decode(),
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
        "latest_issue_types_json": json.dumps(_coerce_issue_types((latest or {}).decode().get("issue_types", []))),
        "latest_issue_types_csv": ", ".join(str(v) for v in _coerce_issue_types((latest or {}).get("issue_types", []))),
        "latest_issue_types_hash": hashlib.sha256(
            json.dumps(_coerce_issue_types((latest or {}).decode().get("issue_types", []))).encode("utf-8")
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
        ).decode(),
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
