"""CSV serializer for health trend payloads."""

from __future__ import annotations

import csv
import hashlib
import io
import orjson as json
from typing import Any

from .health_serializers import _coerce_issue_types, _safe_dict, _safe_list


def serialize_health_trend_csv(result: dict[str, Any]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    latest_issue_types = _coerce_issue_types(_safe_dict(result.get("latest")).get("issue_types", []))
    compat_aliases_count = result.get(
        "compat_aliases_count",
        len(_safe_dict(result.get("compat")).get("aliases", {}) or {}),
    )
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
    writer.writerow(
        [
            "schema_version",
            "schema_compat_mode",
            "payload_type",
            "trend_payload_type",
            "payload_signature_algorithm",
            "payload_signature_value",
            "record_type",
            "generated_at_utc",
            "snapshot_count",
            "snapshot_ids_csv",
            "snapshot_ids_hash",
            "snapshot_window_seconds",
            "snapshot_window_hash",
            "snapshot_interval_seconds_avg",
            "snapshot_interval_hash",
            "snapshot_density_per_hour",
            "snapshot_density_hash",
            "snapshot_freshness_seconds",
            "snapshot_freshness_hash",
            "snapshot_issue_churn_count",
            "snapshot_issue_churn_hash",
            "snapshot_health_volatility",
            "snapshot_health_volatility_hash",
            "limit",
            "snapshot_retention_max_lines",
            "latest_status",
            "latest_pass",
            "latest_captured_at_utc",
            "latest_blocked_ratio",
            "latest_blocked_count",
            "latest_issue_types_count",
            "latest_issue_types_csv",
            "latest_issue_types_json",
            "latest_issue_types_hash",
            "scope_payload_type",
            "scope_owner",
            "scope_all",
            "scope_strict",
            "scope_policy_profile",
            "scope_min_healthy_ratio",
            "scope_top_blocked",
            "scope_key_json",
            "delta_summary_json",
            "scope_key",
            "blocked_ratio_delta",
            "blocked_count_delta",
            "captured_at_utc",
            "status",
            "pass",
            "total",
            "healthy_count",
            "unhealthy_count",
            "blocked_count",
            "blocked_ratio",
            "issue_types",
            "compat_mode",
            "compat_aliases_json",
            "compat_aliases_count",
        ]
    )
    writer.writerow(
        [
            result["schema_version"],
            result.get("schema_compat_mode", "compat"),
            result["payload_type"],
            result["trend_payload_type"],
            _safe_dict(result.get("payload_signature")).get("algorithm", "sha256"),
            _safe_dict(result.get("payload_signature")).get("value", ""),
            "summary",
            result.get("generated_at_utc", ""),
            result.get("snapshot_count", 0),
            snapshot_ids_csv,
            snapshot_ids_hash,
            str(snapshot_window_seconds),
            snapshot_window_hash,
            str(snapshot_interval_seconds_avg),
            snapshot_interval_hash,
            str(snapshot_density_per_hour),
            snapshot_density_hash,
            str(snapshot_freshness_seconds),
            snapshot_freshness_hash,
            str(snapshot_issue_churn_count),
            snapshot_issue_churn_hash,
            str(snapshot_health_volatility) if snapshot_health_volatility is not None else "None",
            snapshot_health_volatility_hash,
            result.get("limit", 0),
            result.get("snapshot_retention_max_lines", ""),
            result.get("latest_status", _safe_dict(result.get("latest")).get("status", "")),
            result.get("latest_pass", _safe_dict(result.get("latest")).get("pass", "")),
            result.get("latest_captured_at_utc", _safe_dict(result.get("latest")).get("captured_at_utc", "")),
            result.get("latest_blocked_ratio", _safe_dict(result.get("latest")).get("blocked_ratio", None)),
            result.get("latest_blocked_count", _safe_dict(result.get("latest")).get("blocked_count", None)),
            result.get("latest_issue_types_count", len(latest_issue_types)),
            result.get(
                "latest_issue_types_csv",
                ", ".join(latest_issue_types),
            ),
            latest_issue_types_json,
            latest_issue_types_hash,
            result.get("scope_payload_type", _safe_dict(result.get("scope_key")).get("payload_type", "")),
            result.get("scope_owner", _safe_dict(result.get("scope_key")).get("owner", "")),
            result.get("scope_all", _safe_dict(result.get("scope_key")).get("all", False)),
            result.get("scope_strict", _safe_dict(result.get("scope_key")).get("strict", False)),
            result.get(
                "scope_policy_profile",
                _safe_dict(result.get("scope_key")).get("policy_profile", "custom"),
            ),
            result.get(
                "scope_min_healthy_ratio",
                _safe_dict(result.get("scope_key")).get("min_healthy_ratio", ""),
            ),
            result.get(
                "scope_top_blocked",
                _safe_dict(result.get("scope_key")).get("top_blocked", ""),
            ),
            result.get("scope_key_json", json.dumps(result.get('scope_key', {}), option=json.OPT_SORT_KEYS)),
            result.get("delta_summary_json", json.dumps(result.get('delta_summary', {}), option=json.OPT_SORT_KEYS)),
            json.dumps(result.get('scope_key', {}), option=json.OPT_SORT_KEYS),
            result.get(
                "blocked_ratio_delta",
                result.get("delta_summary", {}).get("blocked_ratio_delta", None),
            ),
            result.get(
                "blocked_count_delta",
                result.get("delta_summary", {}).get("blocked_count_delta", None),
            ),
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            _safe_dict(result.get("compat")).get("mode", "compat"),
            json.dumps(_safe_dict(result.get("compat")).get("aliases", {}), option=json.OPT_SORT_KEYS),
            compat_aliases_count,
        ]
    )
    for snap in result.get("snapshots", []):
        writer.writerow(
            [
                result["schema_version"],
                result.get("schema_compat_mode", "compat"),
                result["payload_type"],
                result["trend_payload_type"],
                _safe_dict(result.get("payload_signature")).get("algorithm", "sha256"),
                _safe_dict(result.get("payload_signature")).get("value", ""),
                "snapshot",
                result.get("generated_at_utc", ""),
                result.get("snapshot_count", 0),
                snapshot_ids_csv,
                snapshot_ids_hash,
                snapshot_window_seconds,
                snapshot_window_hash,
                snapshot_interval_seconds_avg,
                snapshot_interval_hash,
                snapshot_density_per_hour,
                snapshot_density_hash,
                snapshot_freshness_seconds,
                snapshot_freshness_hash,
                snapshot_issue_churn_count,
                snapshot_issue_churn_hash,
                str(snapshot_health_volatility) if snapshot_health_volatility is not None else "None",
                snapshot_health_volatility_hash,
                result.get("limit", 0),
                result.get("snapshot_retention_max_lines", ""),
                result.get("latest_status", _safe_dict(result.get("latest")).get("status", "")),
                result.get("latest_pass", _safe_dict(result.get("latest")).get("pass", "")),
                result.get("latest_captured_at_utc", _safe_dict(result.get("latest")).get("captured_at_utc", "")),
                result.get("latest_blocked_ratio", _safe_dict(result.get("latest")).get("blocked_ratio", None)),
                result.get("latest_blocked_count", _safe_dict(result.get("latest")).get("blocked_count", None)),
                result.get("latest_issue_types_count", len(latest_issue_types)),
                result.get(
                    "latest_issue_types_csv",
                    ", ".join(latest_issue_types),
                ),
                latest_issue_types_json,
                latest_issue_types_hash,
                result.get("scope_payload_type", _safe_dict(result.get("scope_key")).get("payload_type", "")),
                result.get("scope_owner", _safe_dict(result.get("scope_key")).get("owner", "")),
                result.get("scope_all", _safe_dict(result.get("scope_key")).get("all", False)),
                result.get("scope_strict", _safe_dict(result.get("scope_key")).get("strict", False)),
                result.get(
                    "scope_policy_profile",
                    _safe_dict(result.get("scope_key")).get("policy_profile", "custom"),
                ),
                result.get(
                    "scope_min_healthy_ratio",
                    _safe_dict(result.get("scope_key")).get("min_healthy_ratio", ""),
                ),
                result.get(
                    "scope_top_blocked",
                    _safe_dict(result.get("scope_key")).get("top_blocked", ""),
                ),
                result.get("scope_key_json", json.dumps(result.get('scope_key', {}), option=json.OPT_SORT_KEYS)),
                result.get("delta_summary_json", json.dumps(result.get('delta_summary', {}), option=json.OPT_SORT_KEYS)),
                json.dumps(result.get('scope_key', {}), option=json.OPT_SORT_KEYS),
                result.get(
                    "blocked_ratio_delta",
                    result.get("delta_summary", {}).get("blocked_ratio_delta", None),
                ),
                result.get(
                    "blocked_count_delta",
                    result.get("delta_summary", {}).get("blocked_count_delta", None),
                ),
                snap.get("captured_at_utc", ""),
                snap.get("status", ""),
                snap.get("pass", False),
                snap.get("total", 0),
                snap.get("healthy_count", 0),
                snap.get("unhealthy_count", 0),
                snap.get("blocked_count", 0),
                snap.get("blocked_ratio", 0.0),
                ", ".join(_coerce_issue_types(snap.get("issue_types", []))),
                _safe_dict(result.get("compat")).get("mode", "compat"),
                json.dumps(_safe_dict(result.get("compat")).get("aliases", {}), option=json.OPT_SORT_KEYS),
                compat_aliases_count,
            ]
        )
    return buffer.getvalue()
