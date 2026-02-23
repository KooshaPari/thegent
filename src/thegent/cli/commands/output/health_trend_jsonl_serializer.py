"""JSONL serializer for health trend payloads."""

from __future__ import annotations

import hashlib
import orjson as json
from typing import Any

from .health_serializers import _coerce_issue_types, _safe_dict, _safe_list


def serialize_health_trend_jsonl(result: dict[str, Any]) -> str:
    lines: list[str] = []
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
    summary = dict(result)
    summary["record_type"] = "summary"
    summary["compat"] = result.get("compat") or {
        "mode": result.get("schema_compat_mode", "compat"),
        "aliases": _safe_dict(result.get("compat")).get("aliases", {}),
    }
    summary["latest_status"] = result.get("latest_status", _safe_dict(result.get("latest")).get("status", ""))
    summary["latest_pass"] = result.get("latest_pass", _safe_dict(result.get("latest")).get("pass", None))
    summary["latest_captured_at_utc"] = result.get(
        "latest_captured_at_utc", _safe_dict(result.get("latest")).get("captured_at_utc", "")
    )
    summary["latest_blocked_ratio"] = result.get(
        "latest_blocked_ratio", _safe_dict(result.get("latest")).get("blocked_ratio", None)
    )
    summary["latest_blocked_count"] = result.get(
        "latest_blocked_count", _safe_dict(result.get("latest")).get("blocked_count", None)
    )
    summary["latest_issue_types_count"] = result.get(
        "latest_issue_types_count",
        len(latest_issue_types),
    )
    summary["latest_issue_types_csv"] = result.get(
        "latest_issue_types_csv",
        ", ".join(latest_issue_types),
    )
    summary["latest_issue_types_json"] = latest_issue_types_json
    summary["latest_issue_types_hash"] = latest_issue_types_hash
    summary["snapshot_ids_csv"] = snapshot_ids_csv
    summary["snapshot_ids_hash"] = snapshot_ids_hash
    summary["snapshot_window_seconds"] = snapshot_window_seconds
    summary["snapshot_window_hash"] = snapshot_window_hash
    summary["snapshot_interval_seconds_avg"] = snapshot_interval_seconds_avg
    summary["snapshot_interval_hash"] = snapshot_interval_hash
    summary["snapshot_density_per_hour"] = snapshot_density_per_hour
    summary["snapshot_density_hash"] = snapshot_density_hash
    summary["snapshot_freshness_seconds"] = snapshot_freshness_seconds
    summary["snapshot_freshness_hash"] = snapshot_freshness_hash
    summary["snapshot_issue_churn_count"] = snapshot_issue_churn_count
    summary["snapshot_issue_churn_hash"] = snapshot_issue_churn_hash
    summary["snapshot_health_volatility"] = snapshot_health_volatility
    summary["snapshot_health_volatility_hash"] = snapshot_health_volatility_hash
    summary["scope_owner"] = result.get("scope_owner", _safe_dict(result.get("scope_key")).get("owner", ""))
    summary["scope_payload_type"] = result.get(
        "scope_payload_type",
        _safe_dict(result.get("scope_key")).get("payload_type", ""),
    )
    summary["scope_all"] = result.get("scope_all", _safe_dict(result.get("scope_key")).get("all", False))
    summary["scope_strict"] = result.get("scope_strict", _safe_dict(result.get("scope_key")).get("strict", False))
    summary["scope_policy_profile"] = result.get(
        "scope_policy_profile",
        _safe_dict(result.get("scope_key")).get("policy_profile", "custom"),
    )
    summary["scope_min_healthy_ratio"] = result.get(
        "scope_min_healthy_ratio",
        _safe_dict(result.get("scope_key")).get("min_healthy_ratio", ""),
    )
    summary["scope_top_blocked"] = result.get(
        "scope_top_blocked", _safe_dict(result.get("scope_key")).get("top_blocked", "")
    )
    summary["scope_key_json"] = result.get(
        "scope_key_json",
        json.dumps(result.get('scope_key', {})).decode(),
    )
    summary["payload_signature_algorithm"] = _safe_dict(result.get("payload_signature")).get("algorithm", "sha256")
    summary["payload_signature_value"] = _safe_dict(result.get("payload_signature")).get("value", "")
    summary["compat"] = result.get("compat") or {
        "mode": result.get("schema_compat_mode", "compat"),
        "aliases": _safe_dict(result.get("compat")).get("aliases", {}),
    }
    summary["compat_aliases_count"] = compat_aliases_count
    lines.append(json.dumps(summary, option=json.OPT_SORT_KEYS).decode())
    for snap in result.get("snapshots", []):
        row = dict(snap)
        row["record_type"] = "snapshot"
        row["schema_version"] = result["schema_version"]
        row["schema_compat_mode"] = result.get("schema_compat_mode", "compat")
        row["payload_type"] = result["payload_type"]
        row["trend_payload_type"] = result["trend_payload_type"]
        row["snapshot_count"] = result.get("snapshot_count", 0)
        row["limit"] = result.get("limit", 0)
        row["snapshot_retention_max_lines"] = result.get("snapshot_retention_max_lines", "")
        row["generated_at_utc"] = result.get("generated_at_utc", "")
        row["compat_mode"] = _safe_dict(result.get("compat")).get("mode", "compat")
        row["compat_aliases"] = _safe_dict(result.get("compat")).get("aliases", {})
        row["compat_aliases_count"] = compat_aliases_count
        row["scope_key"] = result.get("scope_key", {})
        row["scope_key_json"] = result.get(
            "scope_key_json",
            json.dumps(result.get('scope_key', {}), option=json.OPT_SORT_KEYS),
        )
        row["delta_summary_json"] = result.get(
            "delta_summary_json",
            json.dumps(result.get('delta_summary', {}), option=json.OPT_SORT_KEYS),
        )
        row["delta_summary"] = result.get("delta_summary", {})
        row["blocked_ratio_delta"] = result.get(
            "blocked_ratio_delta",
            result.get("delta_summary", {}).get("blocked_ratio_delta", None),
        )
        row["blocked_count_delta"] = result.get(
            "blocked_count_delta",
            result.get("delta_summary", {}).get("blocked_count_delta", None),
        )
        row["latest_status"] = result.get("latest_status", _safe_dict(result.get("latest")).get("status", ""))
        row["latest_pass"] = result.get("latest_pass", _safe_dict(result.get("latest")).get("pass", None))
        row["latest_captured_at_utc"] = result.get(
            "latest_captured_at_utc", _safe_dict(result.get("latest")).get("captured_at_utc", "")
        )
        row["latest_blocked_ratio"] = result.get(
            "latest_blocked_ratio", _safe_dict(result.get("latest")).get("blocked_ratio", None)
        )
        row["latest_blocked_count"] = result.get(
            "latest_blocked_count", _safe_dict(result.get("latest")).get("blocked_count", None)
        )
        row["latest_issue_types_count"] = result.get(
            "latest_issue_types_count",
            len(latest_issue_types),
        )
        row["latest_issue_types_csv"] = result.get(
            "latest_issue_types_csv",
            ", ".join(latest_issue_types),
        )
        row["latest_issue_types_json"] = latest_issue_types_json
        row["latest_issue_types_hash"] = latest_issue_types_hash
        row["snapshot_ids_csv"] = snapshot_ids_csv
        row["snapshot_ids_hash"] = snapshot_ids_hash
        row["snapshot_window_seconds"] = snapshot_window_seconds
        row["snapshot_window_hash"] = snapshot_window_hash
        row["snapshot_interval_seconds_avg"] = snapshot_interval_seconds_avg
        row["snapshot_interval_hash"] = snapshot_interval_hash
        row["snapshot_density_per_hour"] = snapshot_density_per_hour
        row["snapshot_density_hash"] = snapshot_density_hash
        row["snapshot_freshness_seconds"] = snapshot_freshness_seconds
        row["snapshot_freshness_hash"] = snapshot_freshness_hash
        row["snapshot_issue_churn_count"] = snapshot_issue_churn_count
        row["snapshot_issue_churn_hash"] = snapshot_issue_churn_hash
        row["snapshot_health_volatility"] = snapshot_health_volatility
        row["snapshot_health_volatility_hash"] = snapshot_health_volatility_hash
        row["scope_owner"] = result.get("scope_owner", _safe_dict(result.get("scope_key")).get("owner", ""))
        row["scope_payload_type"] = result.get(
            "scope_payload_type",
            _safe_dict(result.get("scope_key")).get("payload_type", ""),
        )
        row["scope_all"] = result.get("scope_all", _safe_dict(result.get("scope_key")).get("all", False))
        row["scope_strict"] = result.get("scope_strict", _safe_dict(result.get("scope_key")).get("strict", False))
        row["scope_policy_profile"] = result.get(
            "scope_policy_profile",
            _safe_dict(result.get("scope_key")).get("policy_profile", "custom"),
        )
        row["scope_min_healthy_ratio"] = result.get(
            "scope_min_healthy_ratio",
            _safe_dict(result.get("scope_key")).get("min_healthy_ratio", ""),
        )
        row["scope_top_blocked"] = result.get(
            "scope_top_blocked", _safe_dict(result.get("scope_key")).get("top_blocked", "")
        )
        row["payload_signature_algorithm"] = _safe_dict(result.get("payload_signature")).get("algorithm", "sha256")
        row["payload_signature_value"] = _safe_dict(result.get("payload_signature")).get("value", "")
        row["compat"] = result.get("compat") or {
            "mode": result.get("schema_compat_mode", "compat"),
            "aliases": _safe_dict(result.get("compat")).get("aliases", {}),
        }
        lines.append(json.dumps(row, option=json.OPT_SORT_KEYS).decode())
    return "\n".join(lines) + ("\n" if lines else "")
