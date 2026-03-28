"""Ops/provider/audit MCP tool registration helpers."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult


def register_ops_tools(
    *,
    mcp: FastMCP,
    server_tools_catalog: Any,
    server_tools_contract_observe: Any,
    stable_json: Any,
    error_result: Any,
    list_agents_impl: Any,
    list_models_impl: Any,
    observe_summary_impl: Any,
    session_contract_audit_impl: Any,
    session_contract_health_gate_impl: Any,
    session_contract_health_report_impl: Any,
    session_contract_health_trend_impl: Any,
    session_contract_health_gate_helper: Any,
    session_contract_health_report_helper: Any,
    coerce_issue_types: Any,
) -> tuple[object, object, object, object, object, object, object, object, object, object, object]:
    """Register selected operation/provider/audit MCP tools."""

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_list_operations(operation: str | None = None) -> ToolResult:
        """List universal operation taxonomy: orchestrate, govern, recover, observe, plan."""
        return server_tools_catalog.thegent_list_operations_impl(
            operation=operation,
            stable_json_impl=stable_json,
            error_result_impl=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_list_modes(mode: str | None = None) -> ToolResult:
        """List multi-agent orchestration modes (G-KD-04)."""
        return server_tools_catalog.thegent_list_modes_impl(
            mode=mode,
            stable_json_impl=stable_json,
            error_result_impl=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_suggest_mode(
        risk: str = "medium",
        urgency: str = "normal",
        confidence: float = 0.8,
    ) -> ToolResult:
        """WP-Y1: Suggest multi-agent mode based on risk, urgency, confidence (FR-032)."""
        return server_tools_catalog.thegent_suggest_mode_impl(
            risk=risk,
            urgency=urgency,
            confidence=confidence,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_list_agents() -> ToolResult:
        """List available canonical agents for task execution."""
        return server_tools_catalog.thegent_list_agents_impl(
            list_agents_impl=list_agents_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_list_models(
        provider: str | None = None,
        include_contract: bool = False,
        by_model: bool = False,
    ) -> ToolResult:
        """List available AI models and their provider mappings."""
        return server_tools_catalog.thegent_list_models_impl(
            provider=provider,
            include_contract=include_contract,
            by_model=by_model,
            list_models_impl=list_models_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_resolve_model_route(
        model: str,
        provider: str | None = None,
        policy: str = "prefer_direct",
    ) -> ToolResult:
        """Resolve a model to a concrete routing target."""
        return server_tools_catalog.thegent_resolve_model_route_impl(
            model=model,
            provider=provider,
            policy=policy,
            error_result_impl=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_session_contracts(
        owner: str | None = None,
        all: bool = False,
        missing_only: bool = False,
        summary_only: bool = False,
        strict: bool = False,
    ) -> ToolResult:
        """List session routing contract metadata and report completeness."""
        return server_tools_contract_observe.thegent_session_contracts_impl(
            owner=owner,
            all=all,
            missing_only=missing_only,
            summary_only=summary_only,
            strict=strict,
            session_contract_audit_impl=session_contract_audit_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_session_contract_health_gate(
        owner: str | None = None,
        all: bool = False,
        strict: bool = False,
        min_healthy_ratio: float = 1.0,
        policy_profile: str | None = None,
        no_worse_than_baseline: bool = False,
        regression_tolerance: float = 0.0,
    ) -> ToolResult:
        """Evaluate session contract health against a minimum ratio gate."""
        return session_contract_health_gate_helper(
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

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_session_contract_health_report(
        owner: str | None = None,
        all: bool = False,
        strict: bool = False,
        top_blocked: int = 25,
        policy_profile: str | None = None,
        no_worse_than_baseline: bool = False,
        regression_tolerance: float = 0.0,
    ) -> ToolResult:
        """Get contract health report with issue taxonomy and owner-level breakdown."""
        return session_contract_health_report_helper(
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

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_session_contract_health_trend(
        payload_type: str = "session_contract_health_report",
        owner: str | None = None,
        all: bool = False,
        strict: bool = False,
        policy_profile: str | None = None,
        min_healthy_ratio: float = 1.0,
        top_blocked: int = 25,
        limit: int = 20,
    ) -> ToolResult:
        """Get trend snapshots and deltas for session contract health scopes."""
        return server_tools_contract_observe.thegent_session_contract_health_trend_impl(
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
            coerce_issue_types=coerce_issue_types,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_observe_summary(
        limit: int = 500,
        drift_window: int = 50,
        structural_budget_pct: float = 5.0,
        semantic_budget_pct: float = 10.0,
        provider: str | None = None,
        trend_samples: int = 0,
        top_escalations: int = 10,
    ) -> ToolResult:
        """Get unified observability summary for KPIs, drift budget, and escalations."""
        return server_tools_contract_observe.thegent_observe_summary_impl(
            limit=limit,
            drift_window=drift_window,
            structural_budget_pct=structural_budget_pct,
            semantic_budget_pct=semantic_budget_pct,
            provider=provider,
            trend_samples=trend_samples,
            top_escalations=top_escalations,
            observe_summary_impl=observe_summary_impl,
            stable_json=stable_json,
        )

    return (
        thegent_list_operations,
        thegent_list_modes,
        thegent_suggest_mode,
        thegent_list_agents,
        thegent_list_models,
        thegent_resolve_model_route,
        thegent_session_contracts,
        thegent_session_contract_health_gate,
        thegent_session_contract_health_report,
        thegent_session_contract_health_trend,
        thegent_observe_summary,
    )
