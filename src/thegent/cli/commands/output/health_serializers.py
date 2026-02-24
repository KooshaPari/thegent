"""Reusable pure serializers for session contract health outputs."""

from __future__ import annotations

import hashlib
import orjson as json
from pathlib import Path
from typing import Any


def _safe_dict(val: object) -> dict[str, Any]:
    return val if isinstance(val, dict) else {}


def _safe_list(val: object) -> list[Any]:
    return val if isinstance(val, list) else []


def _coerce_issue_types(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, dict):
        return [str(v) for v in value]
    if isinstance(value, (list | tuple | set)):
        return [str(v) for v in value]
    return [str(value)]


def serialize_health_report_md(result: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Session Contract Health Report")
    lines.append(f"schema_version: {result['schema_version']}")
    lines.append(f"schema_compat_mode: {result.get('schema_compat_mode', 'compat')}")
    lines.append(f"compat_mode: {_safe_dict(result.get('compat')).get('mode', 'compat')}")
    lines.append(f"compat_aliases: {json.dumps(_safe_dict(result.get('compat')).get('aliases', {}), option=json.OPT_SORT_KEYS)}")
    lines.append(f"payload_type: {result['payload_type']}")
    if result.get("payload_signature"):
        signature = result["payload_signature"]
        lines.append(f"payload_signature: {signature.get('algorithm', 'sha256')}:{signature.get('value', '')}")
    lines.append(f"status: {result['status']}")
    lines.append(f"pass: {result['pass']}")
    lines.append(f"total_sessions: {result['total_sessions']}")
    lines.append(f"healthy_sessions: {result['healthy_sessions']}")
    lines.append(f"unhealthy_sessions: {result['unhealthy_sessions']}")
    lines.append(f"blocked_sessions_count: {result['blocked_sessions_count']}")
    lines.append(f"blocked_ratio: {result['blocked_ratio']}")
    lines.append(f"health: {json.dumps(result['health']).decode()}")
    lines.append(f"strict_checks_enabled: {result['strict_checks_enabled']}")
    if result.get("generated_at_utc"):
        lines.append(f"generated_at_utc: {result['generated_at_utc']}")
    if result.get("generated_query"):
        lines.append(f"generated_query: {json.dumps(result['generated_query']).decode()}")
    lines.append("")

    issue_rows = result["issue_breakdown"]
    if issue_rows:
        lines.append("### Issue Breakdown")
        lines.append("| issue | count |")
        lines.append("|------|------:|")
        for row in issue_rows:
            lines.append(f"| {row['issue']} | {row['count']} |")
        lines.append("")

    owner_rows = result["owner_breakdown"]
    if owner_rows:
        lines.append("### Owner Breakdown")
        lines.append("| owner | total | healthy | warning | error | missing |")
        lines.append("|-------|------:|--------:|--------:|------:|--------:|")
        for owner_key, values in sorted(owner_rows.items(), key=lambda kv: str(kv[0])):
            lines.append(
                f"| {owner_key} | {values['total']} | {values['healthy']} | {values['warning']} | "
                f"{values['error']} | {values['missing']} |"
            )
        lines.append("")

    if result["top_blocked"]:
        lines.append("### Top Blocked Sessions")
        lines.append("| session | owner | state | health | issues | remediation |")
        lines.append("|--------|-------|-------|--------|--------|------------|")
        for row in result["top_blocked"]:
            issues = ", ".join(_coerce_issue_types(row.get("issues")))
            remediation = ", ".join(row.get("remediation", []))
            lines.append(
                f"| {row['session_id']} | {row['owner']} | {row['state']} | "
                f"{row['health']} | {issues or '—'} | {remediation or '—'} |"
            )
    return "\n".join(lines)


def serialize_health_gate_md(result: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Session Contract Health Gate")
    lines.append(f"schema_version: {result['schema_version']}")
    lines.append(f"schema_compat_mode: {result.get('schema_compat_mode', 'compat')}")
    lines.append(f"payload_type: {result['payload_type']}")
    if result.get("payload_signature"):
        signature = result["payload_signature"]
        lines.append(f"payload_signature: {signature.get('algorithm', 'sha256')}:{signature.get('value', '')}")
    lines.append(f"status: {result['status']}")
    lines.append(f"pass: {result['pass']}")
    lines.append(f"ratio: {result['healthy_ratio']} threshold={result['threshold']}")
    lines.append(
        f"total_sessions={result['total_sessions']} healthy_sessions={result['healthy_sessions']} "
        f"unhealthy_sessions={result['unhealthy_sessions']} "
        f"blocked_sessions_count={result['blocked_sessions_count']} "
        f"blocked_ratio={result['blocked_ratio']}"
    )
    lines.append(f"strict_checks_enabled={result['strict_checks_enabled']}")
    lines.append(f"generated_at_utc: {result['generated_at_utc']}")
    lines.append(f"generated_query: {json.dumps(result['generated_query']).decode()}")
    if result["blocked_sessions"]:
        lines.append("")
        lines.append("### Blocked Sessions")
        lines.append("| id | state | health | issues |")
        lines.append("|----|-------|--------|--------|")
        for row in result["blocked_sessions"]:
            issues = ", ".join(_coerce_issue_types(row.get("issues")))
            lines.append(f"| {row['session_id']} | {row['state']} | {row['health']} | {issues or '—'} |")
    return "\n".join(lines)


def serialize_health_trend_md(result: dict[str, Any]) -> str:
    lines: list[str] = []
    compat_aliases_count = result.get(
        "compat_aliases_count",
        len(_safe_dict(result.get("compat")).get("aliases", {}) or {}),
    )
    latest_issue_types = _coerce_issue_types(_safe_dict(result.get("latest")).get("issue_types", []))
    latest_issue_types_json = result.get(
        "latest_issue_types_json",
        json.dumps(latest_issue_types).decode(),
    )
    latest_issue_types_hash = result.get(
        "latest_issue_types_hash",
        hashlib.sha256(latest_issue_types_json.encode("utf-8")).hexdigest(),
    )
    snapshot_ids_csv = result.get(
        "snapshot_ids_csv",
        ", ".join(
            [
                str(_safe_dict(s).get("captured_at_utc", ""))
                for s in _safe_list(result.get("snapshots"))
                if _safe_dict(s).get("captured_at_utc", "")
            ]
        ),
    )
    snapshot_ids_hash = result.get(
        "snapshot_ids_hash",
        hashlib.sha256(snapshot_ids_csv.encode("utf-8")).hexdigest(),
    )
    snapshot_window_seconds = result.get("snapshot_window_seconds")
    snapshot_window_hash = result.get(
        "snapshot_window_hash",
        hashlib.sha256(str(snapshot_window_seconds).encode("utf-8")).hexdigest(),
    )
    snapshot_interval_seconds_avg = result.get("snapshot_interval_seconds_avg")
    snapshot_interval_hash = result.get(
        "snapshot_interval_hash",
        hashlib.sha256(str(snapshot_interval_seconds_avg).encode("utf-8")).hexdigest(),
    )
    snapshot_density_per_hour = result.get("snapshot_density_per_hour")
    snapshot_density_hash = result.get(
        "snapshot_density_hash",
        hashlib.sha256(str(snapshot_density_per_hour).encode("utf-8")).hexdigest(),
    )
    snapshot_freshness_seconds = result.get("snapshot_freshness_seconds")
    snapshot_freshness_hash = result.get(
        "snapshot_freshness_hash",
        hashlib.sha256(str(snapshot_freshness_seconds).encode("utf-8")).hexdigest(),
    )
    snapshot_issue_churn_count = result.get("snapshot_issue_churn_count")
    snapshot_issue_churn_hash = result.get(
        "snapshot_issue_churn_hash",
        hashlib.sha256(str(snapshot_issue_churn_count).encode("utf-8")).hexdigest(),
    )
    snapshot_health_volatility = result.get("snapshot_health_volatility")
    snapshot_health_volatility_hash = result.get(
        "snapshot_health_volatility_hash",
        hashlib.sha256(str(snapshot_health_volatility).encode("utf-8")).hexdigest(),
    )
    lines.append("## Session Contract Health Trend")
    lines.append(f"schema_version: {result['schema_version']}")
    lines.append(f"schema_compat_mode: {result.get('schema_compat_mode', 'compat')}")
    lines.append(f"compat_mode: {_safe_dict(result.get('compat')).get('mode', 'compat')}")
    lines.append(f"compat_aliases: {json.dumps(_safe_dict(result.get('compat')).get('aliases', {}), option=json.OPT_SORT_KEYS)}")
    lines.append(f"compat_aliases_count: {compat_aliases_count}")
    lines.append(f"payload_type: {result['payload_type']}")
    lines.append(f"trend_payload_type: {result['trend_payload_type']}")
    lines.append(f"snapshot_count: {result['snapshot_count']}")
    lines.append(f"snapshot_ids_csv: {snapshot_ids_csv}")
    lines.append(f"snapshot_ids_hash: {snapshot_ids_hash}")
    lines.append(f"snapshot_window_seconds: {snapshot_window_seconds}")
    lines.append(f"snapshot_window_hash: {snapshot_window_hash}")
    lines.append(f"snapshot_interval_seconds_avg: {snapshot_interval_seconds_avg}")
    lines.append(f"snapshot_interval_hash: {snapshot_interval_hash}")
    lines.append(f"snapshot_density_per_hour: {snapshot_density_per_hour}")
    lines.append(f"snapshot_density_hash: {snapshot_density_hash}")
    lines.append(f"snapshot_freshness_seconds: {snapshot_freshness_seconds}")
    lines.append(f"snapshot_freshness_hash: {snapshot_freshness_hash}")
    lines.append(f"snapshot_issue_churn_count: {snapshot_issue_churn_count}")
    lines.append(f"snapshot_issue_churn_hash: {snapshot_issue_churn_hash}")
    lines.append(f"snapshot_health_volatility: {snapshot_health_volatility}")
    lines.append(f"snapshot_health_volatility_hash: {snapshot_health_volatility_hash}")
    lines.append(f"generated_at_utc: {result.get('generated_at_utc', '')}")
    lines.append(f"snapshot_retention_max_lines: {result.get('snapshot_retention_max_lines', '')}")
    lines.append(f"latest_status: {result.get('latest_status', _safe_dict(result.get('latest')).get('status', ''))}")
    lines.append(f"latest_pass: {result.get('latest_pass', _safe_dict(result.get('latest')).get('pass', None))}")
    lines.append(
        f"latest_captured_at_utc: {result.get('latest_captured_at_utc', _safe_dict(result.get('latest')).get('captured_at_utc', ''))}"
    )
    lines.append(
        f"latest_blocked_ratio: {result.get('latest_blocked_ratio', _safe_dict(result.get('latest')).get('blocked_ratio', None))}"
    )
    lines.append(
        f"latest_blocked_count: {result.get('latest_blocked_count', _safe_dict(result.get('latest')).get('blocked_count', None))}"
    )
    lines.append(f"latest_issue_types_count: {result.get('latest_issue_types_count', len(latest_issue_types))}")
    lines.append(f"latest_issue_types_csv: {result.get('latest_issue_types_csv', ', '.join(latest_issue_types))}")
    lines.append(f"latest_issue_types_json: {latest_issue_types_json}")
    lines.append(f"latest_issue_types_hash: {latest_issue_types_hash}")
    lines.append(f"scope_owner: {result.get('scope_owner', _safe_dict(result.get('scope_key')).get('owner', ''))}")
    lines.append(
        f"scope_payload_type: {result.get('scope_payload_type', _safe_dict(result.get('scope_key')).get('payload_type', ''))}"
    )
    lines.append(f"scope_all: {result.get('scope_all', _safe_dict(result.get('scope_key')).get('all', False))}")
    lines.append(
        f"scope_strict: {result.get('scope_strict', _safe_dict(result.get('scope_key')).get('strict', False))}"
    )
    lines.append(
        f"scope_policy_profile: {result.get('scope_policy_profile', _safe_dict(result.get('scope_key')).get('policy_profile', 'custom'))}"
    )
    lines.append(
        f"scope_min_healthy_ratio: {result.get('scope_min_healthy_ratio', _safe_dict(result.get('scope_key')).get('min_healthy_ratio', ''))}"
    )
    lines.append(
        f"scope_top_blocked: {result.get('scope_top_blocked', _safe_dict(result.get('scope_key')).get('top_blocked', ''))}"
    )
    lines.append(
        f"scope_key_json: {result.get('scope_key_json', json.dumps(result.get('scope_key', {}), option=json.OPT_SORT_KEYS))}"
    )
    lines.append(f"scope_key: {json.dumps(result.get('scope_key', {}))}")
    lines.append(
        f"delta_summary_json: {result.get('delta_summary_json', json.dumps(result.get('delta_summary', {}), option=json.OPT_SORT_KEYS))}"
    )
    lines.append(f"delta_summary: {json.dumps(result.get('delta_summary', {}))}")
    if result.get("payload_signature"):
        sig = result["payload_signature"]
        lines.append(f"payload_signature: {sig.get('algorithm', 'sha256')}:{sig.get('value', '')}")
    return "\n".join(lines)


def export_format_from_suffix(suffix: str) -> str | None:
    mapping = {
        ".md": "md",
        ".csv": "csv",
        ".jsonl": "jsonl",
        ".json": "json",
    }
    return mapping.get(suffix.lower())


def infer_export_format(path: Path, fallback: str = "json") -> str:
    inferred = export_format_from_suffix(path.suffix.lower())
    if inferred is not None:
        return inferred
    return fallback


def serialize_health_report_csv(result: dict[str, Any]) -> str:
    from . import health_report_gate_serializers as report_gate

    return report_gate.serialize_health_report_csv(result)


def serialize_health_report_jsonl(result: dict[str, Any]) -> str:
    from . import health_report_gate_serializers as report_gate

    return report_gate.serialize_health_report_jsonl(result)


def serialize_health_gate_csv(result: dict[str, Any]) -> str:
    from . import health_report_gate_serializers as report_gate

    return report_gate.serialize_health_gate_csv(result)


def serialize_health_gate_jsonl(result: dict[str, Any]) -> str:
    from . import health_report_gate_serializers as report_gate

    return report_gate.serialize_health_gate_jsonl(result)


def serialize_health_trend_csv(result: dict[str, Any]) -> str:
    from . import health_trend_csv_serializer as trend_csv

    return trend_csv.serialize_health_trend_csv(result)


def serialize_health_trend_jsonl(result: dict[str, Any]) -> str:
    from . import health_trend_jsonl_serializer as trend_jsonl

    return trend_jsonl.serialize_health_trend_jsonl(result)
