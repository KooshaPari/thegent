"""Locking/context/retry/incorporate tool handlers for MCP server."""

from __future__ import annotations

import orjson as json
import time
from pathlib import Path
from typing import Any, Callable

from fastmcp.tools.tool import ToolResult


def thegent_lock_resource_impl(
    *,
    resource: str,
    ttl: int,
    cd: str | None,
    error_result_impl: Callable[..., ToolResult],
) -> ToolResult:
    from thegent_cli.cli.commands.impl import _default_owner_tag, lock_resource_impl

    start_time = time.perf_counter()
    agent_id = _default_owner_tag(Path(cd) if cd else None)
    res = lock_resource_impl(resource, agent_id, ttl=ttl, cd=Path(cd) if cd else None)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    if res["success"]:
        return ToolResult(
            content=f"Successfully locked {res['resource']} (token: {res['token']})",
            structured_content=res,
            meta={"execution_time_ms": elapsed_ms},
        )
    return error_result_impl(res["error"], "Retry later or check for stale locks.", extra={"resource": resource})


def thegent_unlock_resource_impl(
    *,
    resource: str,
    token: str,
    cd: str | None,
) -> ToolResult:
    from thegent_cli.cli.commands.impl import _default_owner_tag, unlock_resource_impl

    start_time = time.perf_counter()
    agent_id = _default_owner_tag(Path(cd) if cd else None)
    res = unlock_resource_impl(resource, agent_id, token, cd=Path(cd) if cd else None)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    return ToolResult(
        content=f"Successfully unlocked {resource}",
        structured_content=res,
        meta={"execution_time_ms": elapsed_ms},
    )


def thegent_verify_context_impl(
    *,
    files: list[str],
    cd: str | None,
) -> ToolResult:
    from thegent_cli.cli.commands.impl import verify_context_impl

    start_time = time.perf_counter()
    res = verify_context_impl(files, cd=Path(cd) if cd else None)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    return ToolResult(
        content=json.dumps(res).decode(),
        structured_content=res,
        meta={"execution_time_ms": elapsed_ms},
    )


def thegent_retry_impl(
    *,
    run_id: str,
    agent_override: str | None,
    failover: bool,
    cd: str | None,
    override_reason: str | None,
    retry_impl: Callable[..., dict[str, Any]],
    error_result_impl: Callable[..., ToolResult],
) -> ToolResult:
    cd_path = Path(cd) if cd else None
    start_time = time.perf_counter()
    result = retry_impl(
        run_id=run_id,
        agent_override=agent_override,
        failover=failover,
        cd=cd_path,
        override_reason=override_reason,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    if "error" in result:
        return error_result_impl(result["error"], result.get("remediation", ""), extra=result)
    return ToolResult(
        content=json.dumps(result).decode(),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


def thegent_plan_incorporate_impl(
    *,
    cd: str | None,
    dry_run: bool,
    incorporate_impl: Callable[..., dict[str, Any]],
) -> ToolResult:
    cd_path = Path(cd) if cd else None
    start_time = time.perf_counter()
    result = incorporate_impl(cd=cd_path, dry_run=dry_run)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result).decode(),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )
