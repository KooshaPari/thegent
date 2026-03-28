"""CSV/JSONL serializers for health report and health gate payloads."""

from __future__ import annotations

import csv
import io
import orjson as json
from typing import Any

from .health_serializers import _coerce_issue_types, _safe_dict


def serialize_health_report_csv(result: dict[str, Any]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "schema_version",
            "schema_compat_mode",
            "payload_type",
            "payload_signature_algorithm",
            "payload_signature_value",
            "generated_at_utc",
            "generated_query_owner",
            "generated_query_all",
            "generated_query_strict",
            "generated_query_top_blocked",
            "record_type",
            "status",
            "pass",
            "total_sessions",
            "healthy_sessions",
            "unhealthy_sessions",
            "blocked_sessions_count",
            "blocked_ratio",
            "top_blocked_count",
            "healthy",
            "warning",
            "error",
            "missing",
            "strict_checks_enabled",
            "session_id",
            "owner",
            "state",
            "health",
            "issues",
            "remediation",
            "started_at_utc",
            "agent",
        ]
    )
    writer.writerow(
        [
            result["schema_version"],
            result.get("schema_compat_mode", "compat"),
            result["payload_type"],
            _safe_dict(result.get("payload_signature")).get("algorithm", "sha256"),
            _safe_dict(result.get("payload_signature")).get("value", ""),
            result.get("generated_at_utc", ""),
            _safe_dict(result.get("generated_query")).get("owner", ""),
            str(_safe_dict(result.get("generated_query")).get("all", "")),
            str(_safe_dict(result.get("generated_query")).get("strict", "")),
            str(_safe_dict(result.get("generated_query")).get("top_blocked", "")),
            "summary",
            result["status"],
            str(result["pass"]),
            result["total_sessions"],
            result["healthy_sessions"],
            result["unhealthy_sessions"],
            result["blocked_sessions_count"],
            result["blocked_ratio"],
            result["top_blocked_count"],
            result["health"].get("healthy", ""),
            result["health"].get("warning", ""),
            result["health"].get("error", ""),
            result["health"].get("missing", ""),
            str(result["strict_checks_enabled"]),
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
    )
    for row in result["top_blocked"]:
        writer.writerow(
            [
                result["schema_version"],
                result.get("schema_compat_mode", "compat"),
                result["payload_type"],
                _safe_dict(result.get("payload_signature")).get("algorithm", "sha256"),
                _safe_dict(result.get("payload_signature")).get("value", ""),
                result.get("generated_at_utc", ""),
                _safe_dict(result.get("generated_query")).get("owner", ""),
                str(_safe_dict(result.get("generated_query")).get("all", "")),
                str(_safe_dict(result.get("generated_query")).get("strict", "")),
                str(_safe_dict(result.get("generated_query")).get("top_blocked", "")),
                "blocked_session",
                result["status"],
                str(result["pass"]),
                result["total_sessions"],
                result["healthy_sessions"],
                result["unhealthy_sessions"],
                result["blocked_sessions_count"],
                result["blocked_ratio"],
                result["top_blocked_count"],
                result["health"].get("healthy", ""),
                result["health"].get("warning", ""),
                result["health"].get("error", ""),
                result["health"].get("missing", ""),
                str(result["strict_checks_enabled"]),
                row.get("session_id", ""),
                row.get("owner", ""),
                row.get("state", ""),
                row.get("health", ""),
                ", ".join(_coerce_issue_types(row.get("issues"))),
                ", ".join(row.get("remediation", [])),
                row.get("started_at_utc", ""),
                row.get("agent", ""),
            ]
        )
    return buffer.getvalue()


def serialize_health_report_jsonl(result: dict[str, Any]) -> str:
    lines: list[str] = []
    summary_row = dict(result)
    summary_row["record_type"] = "summary"
    summary_row["payload_signature_algorithm"] = _safe_dict(result.get("payload_signature")).get("algorithm", "sha256")
    summary_row["payload_signature_value"] = _safe_dict(result.get("payload_signature")).get("value", "")
    lines.append(json.dumps(summary_row, sort_keys=True).decode().decode())
    for row in result["top_blocked"]:
        row_copy = dict(row)
        row_copy["record_type"] = "blocked_session"
        row_copy["payload_type"] = result["payload_type"]
        row_copy["schema_version"] = result["schema_version"]
        row_copy["schema_compat_mode"] = result.get("schema_compat_mode", "compat")
        row_copy["status"] = result.get("status", "")
        row_copy["pass"] = result.get("pass", False)
        row_copy["summary_status"] = result.get("status", "")
        row_copy["strict_checks_enabled"] = result.get("strict_checks_enabled", False)
        row_copy["total_sessions"] = result.get("total_sessions", 0)
        row_copy["healthy_sessions"] = result.get("healthy_sessions", 0)
        row_copy["unhealthy_sessions"] = result.get("unhealthy_sessions", 0)
        row_copy["blocked_sessions_count"] = result.get("blocked_sessions_count", 0)
        row_copy["top_blocked_count"] = result.get("top_blocked_count", 0)
        row_copy["healthy"] = result.get("health", {}).get("healthy", 0)
        row_copy["warning"] = result.get("health", {}).get("warning", 0)
        row_copy["error"] = result.get("health", {}).get("error", 0)
        row_copy["missing"] = result.get("health", {}).get("missing", 0)
        row_copy["blocked_ratio"] = result.get("blocked_ratio", 0.0)
        row_copy["payload_signature_algorithm"] = _safe_dict(result.get("payload_signature")).get("algorithm", "sha256")
        row_copy["payload_signature_value"] = _safe_dict(result.get("payload_signature")).get("value", "")
        row_copy["generated_at_utc"] = result.get("generated_at_utc", "")
        row_copy["generated_query"] = _safe_dict(result.get("generated_query"))
        lines.append(json.dumps(row_copy, sort_keys=True).decode().decode())
    return "\n".join(lines) + ("\n" if lines else "")


def serialize_health_gate_csv(result: dict[str, Any]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "schema_version",
            "schema_compat_mode",
            "payload_type",
            "payload_signature_algorithm",
            "record_type",
            "payload_signature_value",
            "status",
            "pass",
            "healthy_ratio",
            "threshold",
            "total_sessions",
            "healthy_sessions",
            "unhealthy_sessions",
            "blocked_sessions_count",
            "blocked_ratio",
            "top_blocked_count",
            "blocked_sessions_cap",
            "healthy",
            "warning",
            "error",
            "missing",
            "strict_checks_enabled",
            "generated_at_utc",
            "owner",
            "all",
            "strict",
            "min_healthy_ratio",
            "session_id",
            "state",
            "health",
            "issues",
        ]
    )
    writer.writerow(
        [
            result["schema_version"],
            result.get("schema_compat_mode", "compat"),
            result["payload_type"],
            _safe_dict(result.get("payload_signature")).get("algorithm", "sha256"),
            "summary",
            _safe_dict(result.get("payload_signature")).get("value", ""),
            result["status"],
            str(result["pass"]),
            result["healthy_ratio"],
            result["threshold"],
            result["total_sessions"],
            result["healthy_sessions"],
            result["unhealthy_sessions"],
            result["blocked_sessions_count"],
            result["blocked_ratio"],
            result["top_blocked_count"],
            result["blocked_sessions_cap"],
            result["summary"]["health"]["healthy"],
            result["summary"]["health"]["warning"],
            result["summary"]["health"]["error"],
            result["summary"]["health"]["missing"],
            str(result["strict_checks_enabled"]),
            result["generated_at_utc"],
            result["generated_query"].get("owner", ""),
            result["generated_query"].get("all", False),
            result["generated_query"].get("strict", False),
            result["generated_query"].get("min_healthy_ratio", 1.0),
            "",
            "",
            "",
            "",
        ]
    )
    for row in result.get("blocked_sessions", []):
        issues = ", ".join(_coerce_issue_types(row.get("issues")))
        writer.writerow(
            [
                result["schema_version"],
                result.get("schema_compat_mode", "compat"),
                result["payload_type"],
                _safe_dict(result.get("payload_signature")).get("algorithm", "sha256"),
                "blocked_session",
                _safe_dict(result.get("payload_signature")).get("value", ""),
                result["status"],
                str(result["pass"]),
                result["healthy_ratio"],
                result["threshold"],
                result["total_sessions"],
                result["healthy_sessions"],
                result["unhealthy_sessions"],
                result["blocked_sessions_count"],
                result["blocked_ratio"],
                result["top_blocked_count"],
                result["blocked_sessions_cap"],
                result["summary"]["health"]["healthy"],
                result["summary"]["health"]["warning"],
                result["summary"]["health"]["error"],
                result["summary"]["health"]["missing"],
                str(result["strict_checks_enabled"]),
                result["generated_at_utc"],
                result["generated_query"].get("owner", ""),
                result["generated_query"].get("all", False),
                result["generated_query"].get("strict", False),
                result["generated_query"].get("min_healthy_ratio", 1.0),
                row.get("session_id", ""),
                row.get("state", ""),
                row.get("health", ""),
                issues,
            ]
        )
    return buffer.getvalue()


def serialize_health_gate_jsonl(result: dict[str, Any]) -> str:
    lines: list[str] = []
    summary_row = dict(result)
    summary_row["record_type"] = "summary"
    lines.append(json.dumps(summary_row, sort_keys=True).decode().decode())
    for row in result.get("blocked_sessions", []):
        blocked_row = dict(row)
        blocked_row["record_type"] = "blocked_session"
        blocked_row["payload_type"] = result["payload_type"]
        blocked_row["schema_version"] = result["schema_version"]
        blocked_row["schema_compat_mode"] = result.get("schema_compat_mode", "compat")
        blocked_row["status"] = result.get("status", "")
        blocked_row["pass"] = result.get("pass", False)
        blocked_row["summary_status"] = result["status"]
        blocked_row["healthy_ratio"] = result["healthy_ratio"]
        blocked_row["threshold"] = result["threshold"]
        blocked_row["total_sessions"] = result["total_sessions"]
        blocked_row["healthy_sessions"] = result["healthy_sessions"]
        blocked_row["unhealthy_sessions"] = result["unhealthy_sessions"]
        blocked_row["blocked_sessions_count"] = result["blocked_sessions_count"]
        blocked_row["blocked_ratio"] = result["blocked_ratio"]
        blocked_row["top_blocked_count"] = result["top_blocked_count"]
        blocked_row["blocked_sessions_cap"] = result["blocked_sessions_cap"]
        blocked_row["generated_at_utc"] = result["generated_at_utc"]
        blocked_row["strict_checks_enabled"] = result["strict_checks_enabled"]
        blocked_row["payload_signature_algorithm"] = _safe_dict(result.get("payload_signature")).get(
            "algorithm", "sha256"
        )
        blocked_row["payload_signature_value"] = _safe_dict(result.get("payload_signature")).get("value", "")
        blocked_row["generated_query"] = _safe_dict(result.get("generated_query"))
        lines.append(json.dumps(blocked_row, sort_keys=True).decode().decode())
    return "\n".join(lines) + ("\n" if lines else "")
