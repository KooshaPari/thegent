"""Policy/validator/quality extraction helpers for MCP server wrappers."""

import time
from collections.abc import Callable
from typing import Any

from fastmcp.tools.tool import ToolResult


def resource_session_contract_health_gate_helper(
    *,
    owner: str | None,
    all: bool,
    strict: bool,
    min_healthy_ratio: float,
    policy_profile: str | None,
    no_worse_than_baseline: bool,
    regression_tolerance: float,
    resource_impl: Callable[..., str],
    session_contract_health_gate_impl: Callable[..., Any],
    stable_json: Callable[[Any], str],
) -> str:
    return resource_impl(
        owner=owner,
        all=all,
        strict=strict,
        min_healthy_ratio=min_healthy_ratio,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        session_contract_health_gate_impl=session_contract_health_gate_impl,
        stable_json=stable_json,
    )


def resource_session_contract_health_report_helper(
    *,
    owner: str | None,
    all: bool,
    strict: bool,
    top_blocked: int,
    policy_profile: str | None,
    no_worse_than_baseline: bool,
    regression_tolerance: float,
    resource_impl: Callable[..., str],
    session_contract_health_report_impl: Callable[..., Any],
    stable_json: Callable[[Any], str],
) -> str:
    return resource_impl(
        owner=owner,
        all=all,
        strict=strict,
        top_blocked=top_blocked,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        session_contract_health_report_impl=session_contract_health_report_impl,
        stable_json=stable_json,
    )


def resource_session_contract_health_trend_helper(
    *,
    payload_type: str,
    owner: str | None,
    all: bool,
    strict: bool,
    policy_profile: str | None,
    min_healthy_ratio: float,
    top_blocked: int,
    limit: int,
    resource_impl: Callable[..., str],
    session_contract_health_trend_impl: Callable[..., Any],
    stable_json: Callable[[Any], str],
) -> str:
    return resource_impl(
        payload_type=payload_type,
        owner=owner,
        all=all,
        strict=strict,
        policy_profile=policy_profile,
        min_healthy_ratio=min_healthy_ratio,
        top_blocked=top_blocked,
        limit=limit,
        session_contract_health_trend_impl=session_contract_health_trend_impl,
        stable_json=stable_json,
    )


def phenotype_thegent_session_contract_health_gate_helper(
    *,
    owner: str | None,
    all: bool,
    strict: bool,
    min_healthy_ratio: float,
    policy_profile: str | None,
    no_worse_than_baseline: bool,
    regression_tolerance: float,
    session_contract_health_gate_impl: Callable[..., dict[str, Any]],
    stable_json: Callable[[Any], str],
) -> ToolResult:
    start_time = time.perf_counter()
    payload = session_contract_health_gate_impl(
        owner=owner,
        all=all,
        strict=strict,
        min_healthy_ratio=min_healthy_ratio,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=stable_json(payload),
        structured_content=payload,
        meta={
            "execution_time_ms": elapsed_ms,
            "schema_version": payload.get("schema_version", ""),
            "schema_compat_mode": payload.get("schema_compat_mode", "compat"),
            "payload_type": payload.get("payload_type", ""),
            "payload_signature": payload.get("payload_signature"),
            "status": payload.get("status", ""),
            "policy_profile": payload.get("policy_profile", "custom"),
            "decision_reasons": payload.get("decision_reasons", []),
            "total": payload.get("total", 0),
            "healthy_count": payload.get("healthy_count", 0),
            "unhealthy_count": payload.get("unhealthy_count", 0),
            "blocked_count": payload.get("blocked_count", 0),
            "top_blocked_count": payload.get("top_blocked_count", 0),
            "blocked_sessions_cap": payload.get("blocked_sessions_cap", 0),
        },
    )


def phenotype_thegent_session_contract_health_report_helper(
    *,
    owner: str | None,
    all: bool,
    strict: bool,
    top_blocked: int,
    policy_profile: str | None,
    no_worse_than_baseline: bool,
    regression_tolerance: float,
    session_contract_health_report_impl: Callable[..., dict[str, Any]],
    stable_json: Callable[[Any], str],
) -> ToolResult:
    start_time = time.perf_counter()
    payload = session_contract_health_report_impl(
        owner=owner,
        all=all,
        strict=strict,
        top_blocked=top_blocked,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=stable_json(payload),
        structured_content=payload,
        meta={
            "execution_time_ms": elapsed_ms,
            "schema_version": payload.get("schema_version", ""),
            "schema_compat_mode": payload.get("schema_compat_mode", "compat"),
            "payload_type": payload.get("payload_type", ""),
            "payload_signature": payload.get("payload_signature"),
            "status": payload.get("status", ""),
            "policy_profile": payload.get("policy_profile", "custom"),
            "decision_reasons": payload.get("decision_reasons", []),
            "total": payload.get("total", 0),
            "healthy_count": payload.get("healthy_count", 0),
            "unhealthy_count": payload.get("unhealthy_count", 0),
            "blocked_count": payload.get("blocked_count", 0),
            "top_blocked_count": payload.get("top_blocked_count", 0),
        },
    )
