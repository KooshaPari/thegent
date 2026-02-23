"""Session contract, observability, and DAG status tool handlers for MCP server."""

from __future__ import annotations

import hashlib
import orjson as json
import time
from pathlib import Path
from typing import Any, Callable

from fastmcp.tools.tool import ToolResult


def thegent_inspect_impl(
    *,
    session_ids: list[str] | None,
    owner: str | None,
    tail: int,
    stderr: bool,
    include_contract: bool,
    inspect_impl: Callable[..., list[dict[str, Any]] | dict[str, Any]],
) -> ToolResult:
    start_time = time.perf_counter()
    result = inspect_impl(
        session_ids=session_ids or [],
        owner=owner,
        tail=tail,
        stderr=stderr,
        include_contract=include_contract,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    # structured_content must be dict or None; inspect_impl returns list
    structured = {"sessions": result} if isinstance(result, list) else result
    return ToolResult(
        content=json.dumps(result).decode().decode(),
        structured_content=structured,
        meta={"execution_time_ms": elapsed_ms},
    )


def thegent_session_contracts_impl(
    *,
    owner: str | None,
    all: bool,
    missing_only: bool,
    summary_only: bool,
    strict: bool,
    session_contract_audit_impl: Callable[..., dict[str, Any]],
) -> ToolResult:
    start_time = time.perf_counter()
    payload = session_contract_audit_impl(
        owner=owner,
        all=all,
        missing_only=missing_only,
        summary_only=summary_only,
        strict=strict,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(content=json.dumps(payload).decode().decode(), structured_content=payload, meta={"execution_time_ms": elapsed_ms})


def thegent_session_contract_health_trend_impl(
    *,
    payload_type: str,
    owner: str | None,
    all: bool,
    strict: bool,
    policy_profile: str | None,
    min_healthy_ratio: float,
    top_blocked: int,
    limit: int,
    session_contract_health_trend_impl: Callable[..., dict[str, Any]],
    stable_json: Callable[[Any], str],
    coerce_issue_types: Callable[[Any], list[str]],
) -> ToolResult:
    start_time = time.perf_counter()
    payload = session_contract_health_trend_impl(
        payload_type=payload_type,
        owner=owner,
        all=all,
        strict=strict,
        policy_profile=policy_profile,
        min_healthy_ratio=min_healthy_ratio,
        top_blocked=top_blocked,
        limit=limit,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    result = ToolResult(
        content=stable_json(payload),
        structured_content=payload,
        meta={
            "execution_time_ms": elapsed_ms,
            "schema_version": payload.get("schema_version", ""),
            "schema_compat_mode": payload.get("schema_compat_mode", "compat"),
            "payload_type": payload.get("payload_type", ""),
            "trend_payload_type": payload.get("trend_payload_type", ""),
            "generated_at_utc": payload.get("generated_at_utc", ""),
            "scope_key": payload.get("scope_key", {}),
            "scope_key_json": payload.get(
                "scope_key_json",
                stable_json(payload.get("scope_key", {})),
            ),
            "scope_payload_type": payload.get(
                "scope_payload_type",
                (payload.get("scope_key") or {}).get("payload_type", ""),
            ),
            "scope_owner": payload.get("scope_owner", (payload.get("scope_key") or {}).get("owner", "")),
            "scope_all": payload.get("scope_all", (payload.get("scope_key") or {}).get("all", False)),
            "scope_strict": payload.get("scope_strict", (payload.get("scope_key") or {}).get("strict", False)),
            "scope_policy_profile": payload.get(
                "scope_policy_profile",
                (payload.get("scope_key") or {}).get("policy_profile", "custom"),
            ),
            "scope_min_healthy_ratio": payload.get(
                "scope_min_healthy_ratio",
                (payload.get("scope_key") or {}).get("min_healthy_ratio", None),
            ),
            "scope_top_blocked": payload.get(
                "scope_top_blocked",
                (payload.get("scope_key") or {}).get("top_blocked", None),
            ),
            "snapshot_count": payload.get("snapshot_count", 0),
            "snapshot_ids_csv": payload.get(
                "snapshot_ids_csv",
                ", ".join(
                    [
                        str((s or {}).get("captured_at_utc", ""))
                        for s in (payload.get("snapshots", []) or [])
                        if (s or {}).get("captured_at_utc", "")
                    ]
                ),
            ),
            "snapshot_ids_hash": payload.get(
                "snapshot_ids_hash",
                hashlib.sha256(
                    payload.get(
                        "snapshot_ids_csv",
                        ", ".join(
                            [
                                str((s or {}).get("captured_at_utc", ""))
                                for s in (payload.get("snapshots", []) or [])
                                if (s or {}).get("captured_at_utc", "")
                            ]
                        ),
                    ).encode("utf-8")
                ).hexdigest(),
            ),
            "snapshot_window_seconds": payload.get("snapshot_window_seconds", None),
            "snapshot_window_hash": payload.get(
                "snapshot_window_hash",
                hashlib.sha256(str(payload.get("snapshot_window_seconds", None)).encode("utf-8")).hexdigest(),
            ),
            "snapshot_interval_seconds_avg": payload.get("snapshot_interval_seconds_avg", None),
            "snapshot_interval_hash": payload.get(
                "snapshot_interval_hash",
                hashlib.sha256(str(payload.get("snapshot_interval_seconds_avg", None)).encode("utf-8")).hexdigest(),
            ),
            "snapshot_density_per_hour": payload.get("snapshot_density_per_hour", None),
            "snapshot_density_hash": payload.get(
                "snapshot_density_hash",
                hashlib.sha256(str(payload.get("snapshot_density_per_hour", None)).encode("utf-8")).hexdigest(),
            ),
            "snapshot_issue_churn_count": payload.get("snapshot_issue_churn_count", None),
            "snapshot_issue_churn_hash": payload.get(
                "snapshot_issue_churn_hash",
                hashlib.sha256(str(payload.get("snapshot_issue_churn_count", None)).encode("utf-8")).hexdigest(),
            ),
            "snapshot_health_volatility": payload.get("snapshot_health_volatility", None),
            "snapshot_health_volatility_hash": payload.get(
                "snapshot_health_volatility_hash",
                hashlib.sha256(str(payload.get("snapshot_health_volatility", None)).encode("utf-8")).hexdigest(),
            ),
            "snapshot_freshness_seconds": payload.get("snapshot_freshness_seconds", None),
            "snapshot_freshness_hash": payload.get(
                "snapshot_freshness_hash",
                hashlib.sha256(str(payload.get("snapshot_freshness_seconds", None)).encode("utf-8")).hexdigest(),
            ),
            "snapshot_retention_max_lines": payload.get("snapshot_retention_max_lines", 0),
            "delta_summary_json": payload.get(
                "delta_summary_json",
                stable_json(payload.get("delta_summary", {})),
            ),
            "blocked_ratio_delta": payload.get(
                "blocked_ratio_delta",
                payload.get("delta_summary", {}).get("blocked_ratio_delta", None),
            ),
            "blocked_count_delta": payload.get(
                "blocked_count_delta",
                payload.get("delta_summary", {}).get("blocked_count_delta", None),
            ),
            "latest_status": payload.get("latest_status", (payload.get("latest") or {}).get("status", "")),
            "latest_pass": payload.get("latest_pass", (payload.get("latest") or {}).get("pass", None)),
            "latest_captured_at_utc": payload.get(
                "latest_captured_at_utc",
                (payload.get("latest") or {}).get("captured_at_utc", ""),
            ),
            "latest_blocked_ratio": payload.get(
                "latest_blocked_ratio",
                (payload.get("latest") or {}).get("blocked_ratio", None),
            ),
            "latest_blocked_count": payload.get(
                "latest_blocked_count",
                (payload.get("latest") or {}).get("blocked_count", None),
            ),
            "latest_issue_types_count": payload.get(
                "latest_issue_types_count",
                len(coerce_issue_types((payload.get("latest") or {}).get("issue_types", []))),
            ),
            "latest_issue_types_csv": payload.get(
                "latest_issue_types_csv",
                ", ".join(coerce_issue_types((payload.get("latest") or {}).get("issue_types", []))),
            ),
            "latest_issue_types_json": payload.get(
                "latest_issue_types_json",
                stable_json(coerce_issue_types((payload.get("latest") or {}).get("issue_types", []))),
            ),
            "latest_issue_types_hash": payload.get(
                "latest_issue_types_hash",
                hashlib.sha256(
                    payload.get(
                        "latest_issue_types_json",
                        stable_json(coerce_issue_types((payload.get("latest") or {}).get("issue_types", []))),
                    ).encode("utf-8")
                ).hexdigest(),
            ),
            "compat_mode": (payload.get("compat") or {}).get("mode", "compat"),
            "compat_aliases": (payload.get("compat") or {}).get("aliases", {}),
            "compat_aliases_count": payload.get(
                "compat_aliases_count",
                len((payload.get("compat") or {}).get("aliases", {}) or {}),
            ),
        },
    )
    return result


def thegent_observe_summary_impl(
    *,
    limit: int,
    drift_window: int,
    structural_budget_pct: float,
    semantic_budget_pct: float,
    provider: str | None,
    trend_samples: int,
    top_escalations: int,
    observe_summary_impl: Callable[..., dict[str, Any]],
    stable_json: Callable[[Any], str],
) -> ToolResult:
    start_time = time.perf_counter()
    payload = observe_summary_impl(
        limit=limit,
        drift_window=drift_window,
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        provider=provider,
        trend_samples=trend_samples,
        top_escalations=top_escalations,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    kpis = payload.get("kpis", {})
    drift = payload.get("drift", {})
    escalation = payload.get("escalation", {})
    return ToolResult(
        content=stable_json(payload),
        structured_content=payload,
        meta={
            "execution_time_ms": elapsed_ms,
            "payload_type": payload.get("payload_type", "observe_summary"),
            "payload_schema_version": payload.get("payload_schema_version", "observe-summary-schema-v1"),
            "status": payload.get("status", ""),
            "alerts_count": len(payload.get("alerts", [])),
            "kpi_total_events": kpis.get("total_events", 0),
            "fallback_rate": kpis.get("fallback_rate", 0.0),
            "structural_drift_pct": kpis.get("structural_drift_pct", 0.0),
            "semantic_drift_pct": kpis.get("semantic_drift_pct", 0.0),
            "drift_within_budget": drift.get("within_budget", True),
            "drift_structural_rate_pct": drift.get("structural_rate_pct", 0.0),
            "drift_semantic_rate_pct": drift.get("semantic_rate_pct", 0.0),
            "drift_structural_budget_pct": drift.get("structural_budget_pct", structural_budget_pct),
            "drift_semantic_budget_pct": drift.get("semantic_budget_pct", semantic_budget_pct),
            "backlog_count": escalation.get("backlog_count", 0),
            "backlog_past_sla_count": escalation.get("past_sla_count", 0),
            "trend_enabled": payload.get("trend_summary", {}).get("enabled", False),
            "trend_samples_requested": payload.get("generated_query", {}).get("trend_samples", 0),
            "top_escalations_count": escalation.get("top_escalations_count", 0),
            "provider": escalation.get("provider", provider),
            "top_escalations_requested": top_escalations,
        },
    )


def thegent_dag_status_impl(
    *,
    cd: str | None,
    dag_status_impl: Callable[..., dict[str, Any]],
) -> ToolResult:
    cd_path = Path(cd) if cd else None
    start_time = time.perf_counter()
    result = dag_status_impl(cd=cd_path)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result).decode().decode(),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )
