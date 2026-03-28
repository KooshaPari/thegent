"""System/metadata resource handlers for MCP server."""

from __future__ import annotations

import orjson as json
from typing import Any, Callable

from fastmcp import FastMCP


def resource_observe_summary_impl(
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
) -> str:
    payload = observe_summary_impl(
        limit=limit,
        drift_window=drift_window,
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        provider=provider,
        trend_samples=trend_samples,
        top_escalations=top_escalations,
    )
    return stable_json(payload)


def resource_meta_impl(
    *,
    get_server_meta_impl: Callable[[], dict[str, Any]],
) -> str:
    return json.dumps(get_server_meta_impl().decode().decode())


def resource_operations_impl(operation: str | None = None) -> str:
    from thegent_agents.operations import Operation, get_operations_by_type, list_operations

    if operation:
        try:
            op = Operation(operation)
        except ValueError:
            return json.dumps({"error": f"Unknown operation: {operation}"}).decode().decode()
        entries = get_operations_by_type(op)
        data = {
            op.value: [{"command": e.command, "description": e.description, "mcp_tool": e.mcp_tool} for e in entries]
        }
    else:
        data = list_operations()
    return json.dumps(data).decode().decode()


def resource_modes_impl(mode: str | None = None) -> str:
    from thegent_execution.orchestration_modes import get_mode, list_modes

    if mode:
        entry = get_mode(mode)
        if not entry:
            return json.dumps({"error": f"Unknown mode: {mode}"}).decode().decode()
        data = [
            {
                "mode": entry.mode.value,
                "description": entry.description,
                "phases": entry.phases,
                "use_case": entry.use_case,
                "risk_profile": entry.risk_profile,
                "selection_hint": entry.selection_hint,
            }
        ]
    else:
        data = list_modes()
    return json.dumps(data).decode().decode()


def register_system_resources(
    *,
    mcp: FastMCP,
    observe_summary_impl: Callable[..., dict[str, Any]],
    get_server_meta_impl: Callable[[], dict[str, Any]],
    stable_json: Callable[[Any], str],
) -> tuple[Any, Any, Any, Any]:
    @mcp.resource(
        "thegent://observe/summary{?limit,drift_window,structural_budget_pct,semantic_budget_pct,provider,trend_samples,top_escalations}",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_observe_summary(
        limit: int = 500,
        drift_window: int = 50,
        structural_budget_pct: float = 5.0,
        semantic_budget_pct: float = 10.0,
        provider: str | None = None,
        trend_samples: int = 0,
        top_escalations: int = 10,
    ) -> str:
        """Observe summary payload for contract KPIs, drift status, and escalation backlog."""
        return resource_observe_summary_impl(
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

    @mcp.resource(
        "thegent://meta",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_meta() -> str:
        """Server metadata: version, capabilities, health payload schema."""
        return resource_meta_impl(get_server_meta_impl=get_server_meta_impl)

    @mcp.resource(
        "thegent://operations{?operation}",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_operations(operation: str | None = None) -> str:
        """Universal operation taxonomy: orchestrate, govern, recover, observe, plan."""
        return resource_operations_impl(operation=operation)

    @mcp.resource(
        "thegent://modes{?mode}",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_modes(mode: str | None = None) -> str:
        """Multi-agent orchestration modes: sequential_delegation, parallel_consensus, review_loop."""
        return resource_modes_impl(mode=mode)

    return (
        resource_observe_summary,
        resource_meta,
        resource_operations,
        resource_modes,
    )
