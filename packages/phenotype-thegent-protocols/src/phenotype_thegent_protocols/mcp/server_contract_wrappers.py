"""Wrapper functions for contract health checks in thegent MCP server."""

from typing import Any, cast

from fastmcp.tools.tool import ToolResult

from phenotype_thegent_protocols.mcp.server_policy_quality_helpers import (
    resource_session_contract_health_trend_helper,
    phenotype_thegent_session_contract_health_gate_helper,
    phenotype_thegent_session_contract_health_report_helper,
)


def resource_session_contract_health_trend(
    payload_type: str = "session_contract_health_report",
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    policy_profile: str | None = None,
    min_healthy_ratio: float = 1.0,
    top_blocked: int = 25,
    limit: int = 20,
    resource_impl: Any = None,
    session_contract_health_trend_impl_fn: Any = None,
    stable_json: Any = None,
) -> str:
    """Wrapper for resource session contract health trend."""
    return resource_session_contract_health_trend_helper(
        payload_type=payload_type,
        owner=owner,
        all=all,
        strict=strict,
        policy_profile=policy_profile,
        min_healthy_ratio=min_healthy_ratio,
        top_blocked=top_blocked,
        limit=limit,
        resource_impl=resource_impl,
        session_contract_health_trend_impl=session_contract_health_trend_impl_fn,
        stable_json=stable_json,
    )


def phenotype_thegent_session_contract_health_gate(
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    min_healthy_ratio: float = 1.0,
    policy_profile: str | None = None,
    no_worse_than_baseline: bool = False,
    regression_tolerance: float = 0.0,
    session_contract_health_gate_impl_fn: Any = None,
    stable_json: Any = None,
) -> ToolResult:
    """Wrapper for thegent session contract health gate."""
    return phenotype_thegent_session_contract_health_gate_helper(
        owner=owner,
        all=all,
        strict=strict,
        min_healthy_ratio=min_healthy_ratio,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        session_contract_health_gate_impl=session_contract_health_gate_impl_fn,
        stable_json=stable_json,
    )


def phenotype_thegent_session_contract_health_report(
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    top_blocked: int = 25,
    policy_profile: str | None = None,
    no_worse_than_baseline: bool = False,
    regression_tolerance: float = 0.0,
    session_contract_health_report_impl_fn: Any = None,
    stable_json: Any = None,
) -> ToolResult:
    """Wrapper for thegent session contract health report."""
    return phenotype_thegent_session_contract_health_report_helper(
        owner=owner,
        all=all,
        strict=strict,
        top_blocked=top_blocked,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        session_contract_health_report_impl=session_contract_health_report_impl_fn,
        stable_json=stable_json,
    )


def phenotype_thegent_session_contract_health_trend(
    payload_type: str = "session_contract_health_report",
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    policy_profile: str | None = None,
    min_healthy_ratio: float = 1.0,
    top_blocked: int = 25,
    limit: int = 20,
    server_tools_contract_observe: Any = None,
    session_contract_health_trend_impl_fn: Any = None,
    stable_json: Any = None,
    coerce_issue_types_fn: Any = None,
) -> ToolResult:
    """Wrapper for thegent session contract health trend."""
    return cast(
        "ToolResult",
        server_tools_contract_observe.phenotype_thegent_session_contract_health_trend_impl(
            payload_type=payload_type,
            owner=owner,
            all=all,
            strict=strict,
            policy_profile=policy_profile,
            min_healthy_ratio=min_healthy_ratio,
            top_blocked=top_blocked,
            limit=limit,
            session_contract_health_trend_impl=session_contract_health_trend_impl_fn,
            stable_json=stable_json,
            coerce_issue_types=coerce_issue_types_fn,
        ),
    )


def phenotype_thegent_observe_summary(
    limit: int = 500,
    drift_window: int = 50,
    structural_budget_pct: float = 5.0,
    semantic_budget_pct: float = 10.0,
    provider: str | None = None,
    trend_samples: int = 0,
    top_escalations: int = 10,
    server_tools_contract_observe: Any = None,
    observe_summary_impl_fn: Any = None,
    stable_json: Any = None,
) -> ToolResult:
    """Wrapper for thegent observe summary."""
    return cast(
        "ToolResult",
        server_tools_contract_observe.phenotype_thegent_observe_summary_impl(
            limit=limit,
            drift_window=drift_window,
            structural_budget_pct=structural_budget_pct,
            semantic_budget_pct=semantic_budget_pct,
            provider=provider,
            trend_samples=trend_samples,
            top_escalations=top_escalations,
            observe_summary_impl=observe_summary_impl_fn,
            stable_json=stable_json,
        ),
    )
