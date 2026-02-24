"""Governance approval/rejection tool handlers for MCP server."""

from __future__ import annotations

import orjson as json
import time
from typing import Any, Callable

from fastmcp.tools.tool import ToolResult


def thegent_govern_approve_impl(
    *,
    run_id: str,
    reason: str | None,
    govern_approve_impl: Callable[..., dict[str, Any]],
) -> ToolResult:
    start_time = time.perf_counter()
    result = govern_approve_impl(run_id=run_id, reason=reason)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


def thegent_govern_reject_impl(
    *,
    run_id: str,
    reason: str | None,
    govern_reject_impl: Callable[..., dict[str, Any]],
) -> ToolResult:
    start_time = time.perf_counter()
    result = govern_reject_impl(run_id=run_id, reason=reason)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


def thegent_govern_vet_impl(
    *,
    run_id: str,
    policy: str,
    session: str | None,
    dry_run: bool,
    org: str | None,
    project: str | None,
    environment: str | None,
    policy_id: str | None,
    govern_vet_impl: Callable[..., dict[str, Any]],
) -> ToolResult:
    start_time = time.perf_counter()
    result = govern_vet_impl(
        run_id=run_id,
        policy=policy,
        session=session,
        dry_run=dry_run,
        org=org,
        project=project,
        environment=environment,
        policy_id=policy_id,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )
