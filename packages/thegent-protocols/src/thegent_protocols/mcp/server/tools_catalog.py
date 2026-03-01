"""Catalog/capability/tool-registry handlers for MCP server."""

from __future__ import annotations

import orjson as json
import time
from typing import Any, Callable, cast

from fastmcp.tools.tool import ToolResult


def thegent_list_operations_impl(
    *,
    operation: str | None,
    stable_json_impl: Callable[[Any], str],
    error_result_impl: Callable[..., ToolResult],
) -> ToolResult:
    from thegent.operations import Operation, get_operations_by_type, list_operations

    start_time = time.perf_counter()
    if operation:
        try:
            op = Operation(operation)
        except ValueError:
            return error_result_impl(
                f"Unknown operation: {operation}",
                "Valid: orchestrate, govern, recover, observe, plan",
                extra={"operation": operation},
            )
        entries = get_operations_by_type(op)
        data = {
            op.value: [{"command": e.command, "description": e.description, "mcp_tool": e.mcp_tool} for e in entries]
        }
    else:
        data = list_operations()
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=stable_json_impl(data),
        structured_content=data,
        meta={"execution_time_ms": elapsed_ms},
    )


def thegent_list_modes_impl(
    *,
    mode: str | None,
    stable_json_impl: Callable[[Any], str],
    error_result_impl: Callable[..., ToolResult],
) -> ToolResult:
    from thegent.orchestration_modes import get_mode, list_modes

    start_time = time.perf_counter()
    if mode:
        entry = get_mode(mode)
        if not entry:
            return error_result_impl(
                f"Unknown mode: {mode}",
                "Valid: sequential_delegation, parallel_consensus, review_loop",
                extra={"mode": mode},
            )
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
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=stable_json_impl(data),
        structured_content=data if isinstance(data, dict) else {"modes": data},
        meta={"execution_time_ms": elapsed_ms},
    )


def thegent_list_agents_impl(
    *,
    list_agents_impl: Callable[[], list[dict[str, Any]]],
) -> ToolResult:
    start_time = time.perf_counter()
    result = list_agents_impl()
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result).decode(),
        structured_content={"agents": result},
        meta={"execution_time_ms": elapsed_ms},
    )


def thegent_list_models_impl(
    *,
    provider: str | None,
    include_contract: bool,
    by_model: bool,
    list_models_impl: Callable[..., dict[str, Any]],
) -> ToolResult:
    start_time = time.perf_counter()
    result = list_models_impl(provider=provider, include_contract=include_contract, by_model=by_model)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result).decode(),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


def thegent_resolve_model_route_impl(
    *,
    model: str,
    provider: str | None,
    policy: str,
    error_result_impl: Callable[..., ToolResult],
) -> ToolResult:
    from thegent_core.models import (
        ModelCatalog,
        normalize_model_id,
        normalize_route_policy,
        resolve_route_contract,
    )

    try:
        policy_value = normalize_route_policy(policy)
    except ValueError:
        return error_result_impl(
            f"Invalid policy: {policy}",
            "Valid: prefer_direct, prefer_proxy, failover",
            extra={"policy": policy, "valid_policies": ["prefer_direct", "prefer_proxy", "failover"]},
        )

    start_time = time.perf_counter()
    normalized = normalize_model_id(model)
    route = resolve_route_contract(model, provider_hint=provider, policy=policy_value)
    available_routes = [
        {
            "provider": r.provider,
            "backend_type": r.backend_type,
            "model_alias": r.model_alias,
            "priority": r.priority,
        }
        for r in sorted(ModelCatalog.routes_for(model), key=lambda r: (r.provider, r.priority, r.model_alias))
    ]
    payload = {
        "model": model,
        "normalized_model": normalized,
        "policy": policy_value,
        "provider_hint": provider,
        "route_found": route is not None,
        "available_routes": available_routes,
    }
    if route is not None:
        payload["resolved_route"] = cast(
            "Any",
            {
                "provider": route.provider,
                "model_alias": route.model_alias,
                "backend_type": route.backend_type,
                "priority": route.priority,
                "schema_version": route.schema_version,
            },
        )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(payload).decode(),
        structured_content=payload,
        meta={"execution_time_ms": elapsed_ms},
    )
