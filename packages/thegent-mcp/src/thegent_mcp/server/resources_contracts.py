"""Session contract resource handlers for MCP server."""

from __future__ import annotations

import json
from typing import Any, Callable


def resource_session_contracts_impl(
    *,
    owner: str | None,
    all: bool,
    missing_only: bool,
    summary_only: bool,
    strict: bool,
    session_contract_audit_impl: Callable[..., dict[str, Any]],
) -> str:
    return json.dumps(
        session_contract_audit_impl(
            owner=owner,
            all=all,
            missing_only=missing_only,
            summary_only=summary_only,
            strict=strict,
        )
    )


def resource_session_contract_health_gate_impl(
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
) -> str:
    return stable_json(
        session_contract_health_gate_impl(
            owner=owner,
            all=all,
            strict=strict,
            min_healthy_ratio=min_healthy_ratio,
            policy_profile=policy_profile,
            no_worse_than_baseline=no_worse_than_baseline,
            regression_tolerance=regression_tolerance,
        )
    )


def resource_session_contract_health_report_impl(
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
) -> str:
    return stable_json(
        session_contract_health_report_impl(
            owner=owner,
            all=all,
            strict=strict,
            top_blocked=top_blocked,
            policy_profile=policy_profile,
            no_worse_than_baseline=no_worse_than_baseline,
            regression_tolerance=regression_tolerance,
        )
    )


def resource_session_contract_health_trend_impl(
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
) -> str:
    return stable_json(
        session_contract_health_trend_impl(
            payload_type=payload_type,
            owner=owner,
            all=all,
            strict=strict,
            policy_profile=policy_profile,
            min_healthy_ratio=min_healthy_ratio,
            top_blocked=top_blocked,
            limit=limit,
        )
    )
