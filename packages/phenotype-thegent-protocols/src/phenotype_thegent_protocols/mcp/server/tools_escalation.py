"""Escalation and pending-governance tool handlers for MCP server."""

from __future__ import annotations

import orjson as json
import time
from typing import Any, Callable

from fastmcp.tools.tool import ToolResult


def phenotype_thegent_escalate_list_impl(
    *,
    past_sla_only: bool,
    limit: int,
    escalate_list_impl: Callable[..., list[dict[str, Any]]],
) -> ToolResult:
    start_time = time.perf_counter()
    items = escalate_list_impl(past_sla_only=past_sla_only, limit=limit)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(items).decode(),
        structured_content=items,
        meta={"execution_time_ms": elapsed_ms, "count": len(items)},
    )


def phenotype_thegent_escalate_add_impl(
    *,
    run_id: str,
    reason: str,
    sla_minutes: int,
    owner: str | None,
    agent: str | None,
    lane: str,
    priority: int,
    escalate_add_impl: Callable[..., None],
    error_result_impl: Callable[..., ToolResult],
) -> ToolResult:
    start_time = time.perf_counter()
    try:
        escalate_add_impl(
            run_id=run_id,
            reason=reason,
            sla_minutes=sla_minutes,
            owner=owner,
            agent=agent,
            lane=lane,
            priority=priority,
        )
    except Exception as e:
        return error_result_impl(str(e), "Check run_id exists", extra={})
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps({"success": True, "run_id": run_id}).decode(),
        structured_content={"success": True, "run_id": run_id},
        meta={"execution_time_ms": elapsed_ms},
    )


def phenotype_thegent_escalate_approve_impl(
    *,
    run_id: str,
    escalate_approve_impl: Callable[..., bool],
) -> ToolResult:
    start_time = time.perf_counter()
    ok = escalate_approve_impl(run_id=run_id)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps({"success": ok, "run_id": run_id}).decode(),
        structured_content={"success": ok, "run_id": run_id},
        meta={"execution_time_ms": elapsed_ms},
    )


def phenotype_thegent_escalate_resolve_impl(
    *,
    run_id: str,
    resolution: str,
    escalate_resolve_impl: Callable[..., bool],
) -> ToolResult:
    start_time = time.perf_counter()
    ok = escalate_resolve_impl(run_id=run_id, resolution=resolution)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps({"success": ok, "run_id": run_id}).decode(),
        structured_content={"success": ok, "run_id": run_id},
        meta={"execution_time_ms": elapsed_ms},
    )


def phenotype_thegent_govern_list_pending_impl(
    *,
    govern_list_pending_impl: Callable[[], list[dict[str, Any]]],
) -> ToolResult:
    start_time = time.perf_counter()
    items = govern_list_pending_impl()
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(items).decode(),
        structured_content=items,
        meta={"execution_time_ms": elapsed_ms, "count": len(items)},
    )
