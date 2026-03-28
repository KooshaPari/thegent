"""Planning and history tool handlers for MCP server."""

from __future__ import annotations

import asyncio
import orjson as json
import time
from pathlib import Path
from typing import Any, Callable

from fastmcp.tools.tool import ToolResult


def thegent_plan_get_next_impl(
    *,
    cd: str | None,
    do_next_impl: Callable[..., dict[str, Any]],
    error_result_impl: Callable[..., ToolResult],
) -> ToolResult:
    cd_path = Path(cd) if cd else None
    result = do_next_impl(cd=cd_path, limit=1)
    if result.get("governance_blocked"):
        remediation = result.get("remediation", "Refresh verification evidence and retry get-next.")
        return error_result_impl(result["error"], remediation, extra=result)
    if "error" in result:
        return error_result_impl(result["error"], result.get("remediation", ""), extra=result)
    items = result.get("next_items", [])
    if not items:
        return error_result_impl("No pending items.", "Run thegent plan do-next", extra={"next_items": []})
    item = items[0]
    return ToolResult(
        content=json.dumps(item).decode().decode(),
        structured_content=item,
        meta={"execution_time_ms": 0},
    )


async def thegent_dag_list_impl(
    *,
    cd: str | None,
    default_cwd: Any,
    ctx: Any,
    resolve_cwd: Callable[[Path | None], Path | None],
    elicit_cwd_msg: str,
    elicit_timeout_s: int,
    accepted_elicitation_type: type,
    declined_elicitation_type: type,
    cancelled_elicitation_type: type,
    dag_list_impl: Callable[..., dict[str, Any]],
    error_result_impl: Callable[..., ToolResult],
) -> ToolResult:
    cd_path = Path(cd) if cd else default_cwd
    cwd = resolve_cwd(cd_path)
    if cwd is None:
        try:
            elicitation = await asyncio.wait_for(
                ctx.elicit(elicit_cwd_msg, response_type=str),
                timeout=elicit_timeout_s,
            )
        except TimeoutError:
            return error_result_impl(
                "Elicitation timed out (no response from client).",
                "Provide cd=/path in tool call",
                extra={"frontmatter": {}, "tasks": []},
            )
        if isinstance(elicitation, accepted_elicitation_type):
            cwd = Path(str(elicitation.data)).expanduser().resolve()
        elif isinstance(elicitation, declined_elicitation_type):
            return error_result_impl(
                "User declined to provide working directory.",
                "Provide cd=/path in tool call",
                extra={"frontmatter": {}, "tasks": []},
            )
        elif isinstance(elicitation, cancelled_elicitation_type):
            return error_result_impl(
                "Elicitation cancelled.",
                "Retry with explicit params",
                extra={"frontmatter": {}, "tasks": []},
            )
        else:
            return error_result_impl(
                "Ambiguous cwd.",
                "Provide cd=/path or run from project root",
                extra={"frontmatter": {}, "tasks": []},
            )
    start_time = time.perf_counter()
    result = dag_list_impl(cd=cwd)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result).decode().decode(),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


def thegent_do_next_impl(
    *,
    cd: str | None,
    limit: int,
    do_next_impl: Callable[..., dict[str, Any]],
) -> ToolResult:
    cd_path = Path(cd) if cd else None
    start_time = time.perf_counter()
    result = do_next_impl(cd=cd_path, limit=limit)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result).decode().decode(),
        structured_content=result,
        meta={
            "count": result.get("count", 0),
            "sources_checked": result.get("sources_checked", []),
            "execution_time_ms": elapsed_ms,
        },
    )


def thegent_plan_wait_next_impl(
    *,
    cd: str | None,
    poll: float,
    timeout: float,
    sources: str,
    wait_next_impl: Callable[..., dict[str, Any]],
    error_result_impl: Callable[..., ToolResult],
) -> ToolResult:
    cd_path = Path(cd) if cd else None
    src_tuple = tuple(s.strip() for s in sources.split(",") if s.strip())
    result = wait_next_impl(cd=cd_path, poll_interval=poll, timeout=timeout, sources=src_tuple)
    if "error" in result:
        return error_result_impl(result["error"], result.get("remediation", ""), extra=result)
    return ToolResult(
        content=json.dumps(result).decode().decode(),
        structured_content=result,
        meta={"execution_time_ms": 0},
    )


def thegent_history_impl(
    *,
    limit: int,
    history_impl: Callable[..., list[dict[str, Any]]],
) -> ToolResult:
    start_time = time.perf_counter()
    runs = history_impl(limit=limit)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(runs).decode().decode(),
        structured_content=runs,
        meta={"execution_time_ms": elapsed_ms, "count": len(runs)},
    )


def thegent_plan_progress_impl(
    *,
    limit: int,
    history_impl: Callable[..., list[dict[str, Any]]],
) -> ToolResult:
    start_time = time.perf_counter()
    runs = history_impl(limit=limit)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(runs).decode().decode(),
        structured_content=runs,
        meta={"execution_time_ms": elapsed_ms, "count": len(runs)},
    )


def thegent_plan_analyze_impl(
    *,
    cd: str | None,
    pert: bool,
    resources: bool,
    continuity: bool,
    plan_analyze_impl: Callable[..., dict[str, Any]],
    error_result_impl: Callable[..., ToolResult],
) -> ToolResult:
    cd_path = Path(cd) if cd else None
    start_time = time.perf_counter()
    result = plan_analyze_impl(cd=cd_path, pert=pert, resources=resources, continuity=continuity)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    if "error" in result:
        return error_result_impl(result["error"], result.get("remediation", ""), extra=result)
    return ToolResult(
        content=json.dumps(result).decode().decode(),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )
