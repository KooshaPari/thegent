"""Coordination tool handlers for MCP server."""

from __future__ import annotations

import orjson as json
import time
from typing import TYPE_CHECKING, Any, Callable

from fastmcp.tools.tool import ToolResult

if TYPE_CHECKING:
    from logging import Logger
    from thegent_core.config import ThegentSettings


def thegent_wait_impl(
    *,
    session_id: str,
    timeout: int | None,
    logger: Logger,
    wait_impl: Callable[..., dict[str, Any]],
) -> ToolResult:
    logger.info("thegent_wait session_id=%s timeout=%s", session_id, timeout)
    start_time = time.perf_counter()
    result = wait_impl(session_id=session_id, timeout=timeout)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    if result.get("auto_timeout"):
        message = (
            f"⏱️ **Auto-timeout after {int(result.get('elapsed_seconds', 0))}s** to prevent Cursor timeout.\n\n"
            f"Session '{session_id}' is **still running**.\n\n"
            f"**⚠️ CRITICAL: DO NOT TERMINATE THIS CHAT**\n\n"
            f"**Action Required**: Call `thegent_wait(session_id='{session_id}', timeout={timeout})` again "
            f"to continue waiting. The session continues running in the background.\n\n"
            f"This is a safety mechanism to prevent the 4-minute Cursor guard timeout. "
            f"Simply retry the wait command - do not start a new chat or terminate this conversation."
        )
        return ToolResult(
            content=message,
            structured_content={
                "session_id": session_id,
                "auto_timeout": True,
                "elapsed_seconds": result.get("elapsed_seconds", 0),
                "retry_instruction": result.get("retry_instruction", ""),
                "action": "retry",
                "message": message,
                "note": "DO NOT TERMINATE CHAT - Session continues running, just retry the wait command",
            },
            meta={"execution_time_ms": elapsed_ms, "auto_timeout": True, "action": "retry"},
        )

    return ToolResult(
        content=json.dumps(result).decode(), structured_content=result, meta={"execution_time_ms": elapsed_ms}
    )


def thegent_inbox_list_impl(
    *,
    owner: str | None,
    agent: str | None,
    event_type: str | None,
    status: str | None,
    sources: str | None,
    limit: int,
    inbox_list_impl: Callable[..., list[dict[str, Any]]],
) -> ToolResult:
    src_tuple = tuple(s.strip() for s in (sources or "registry,escalation").split(",") if s.strip())
    start_time = time.perf_counter()
    events = inbox_list_impl(
        owner=owner,
        agent=agent,
        event_type=event_type,
        status=status,
        sources=src_tuple,
        limit=limit,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    payload = {"events": events}
    return ToolResult(
        content=json.dumps(payload).decode(),
        structured_content=payload,
        meta={"count": len(events), "execution_time_ms": elapsed_ms},
    )


def thegent_inbox_wait_impl(
    *,
    owner: str | None,
    agent: str | None,
    event_type: str | None,
    status: str | None,
    sources: str | None,
    poll_interval: float,
    timeout: float,
    logger: Logger,
    inbox_list_impl: Callable[..., list[dict[str, Any]]],
) -> ToolResult:
    logger.info(
        "thegent_inbox_wait owner=%s agent=%s event_type=%s poll=%.1f timeout=%.1f",
        owner,
        agent,
        event_type,
        poll_interval,
        timeout,
    )
    src_tuple = tuple(s.strip() for s in (sources or "registry,escalation").split(",") if s.strip())
    start_time = time.perf_counter()
    auto_timeout_secs = 110.0
    effective_timeout = min(timeout, auto_timeout_secs) if timeout > 0 else auto_timeout_secs
    seen_ids: set[str] = set()
    result: dict[str, Any] | list[dict[str, Any]] = []
    initial = inbox_list_impl(owner=owner, agent=agent, event_type=event_type, status=status, sources=src_tuple)
    for ev in initial:
        seen_ids.add(ev.get("run_id", "") + str(ev.get("timestamp", "")))
    while True:
        elapsed = time.perf_counter() - start_time
        if effective_timeout > 0 and elapsed >= effective_timeout:
            auto_timed_out = timeout <= 0 or elapsed < timeout
            result = {"auto_timeout": auto_timed_out, "elapsed_seconds": int(elapsed), "retry_instruction": "retry"}
            break
        current = inbox_list_impl(owner=owner, agent=agent, event_type=event_type, status=status, sources=src_tuple)
        new_events = [ev for ev in current if ev.get("run_id", "") + str(ev.get("timestamp", "")) not in seen_ids]
        if new_events:
            result = new_events
            break
        time.sleep(poll_interval)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    if isinstance(result, dict) and result.get("auto_timeout"):
        message = (
            f"⏱️ **Auto-timeout after {int(result.get('elapsed_seconds', 0))}s** to prevent Cursor timeout.\n\n"
            f"Still waiting for inbox events matching filters.\n\n"
            f"**⚠️ CRITICAL: DO NOT TERMINATE THIS CHAT**\n\n"
            f"**Action Required**: Call `thegent_inbox_wait(owner={owner}, agent={agent}, event_type={event_type}, "
            f"status={status}, sources={sources}, poll_interval={poll_interval}, timeout={timeout})` again "
            f"to continue waiting.\n\n"
            f"This is a safety mechanism to prevent the 4-minute Cursor guard timeout. "
            f"Simply retry the wait command - do not start a new chat or terminate this conversation."
        )
        return ToolResult(
            content=message,
            structured_content={
                "events": [],
                "auto_timeout": True,
                "elapsed_seconds": result.get("elapsed_seconds", 0),
                "retry_instruction": result.get("retry_instruction", ""),
                "action": "retry",
                "message": message,
                "note": "DO NOT TERMINATE CHAT - Continue waiting, just retry the wait command",
            },
            meta={"count": 0, "execution_time_ms": elapsed_ms, "auto_timeout": True, "action": "retry"},
        )

    events = result if isinstance(result, list) else []
    payload = {"events": events}
    return ToolResult(
        content=json.dumps(payload).decode(),
        structured_content=payload,
        meta={"count": len(events), "execution_time_ms": elapsed_ms},
    )


def thegent_stop_impl(
    *,
    session_id: str,
    force: bool,
    logger: Logger,
    stop_impl: Callable[..., dict[str, Any]],
) -> ToolResult:
    logger.info("thegent_stop session_id=%s force=%s", session_id, force)
    start_time = time.perf_counter()
    result = stop_impl(session_id=session_id, force=force)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result).decode(), structured_content=result, meta={"execution_time_ms": elapsed_ms}
    )


def thegent_pause_impl(
    *,
    session_id: str,
    reason: str,
    logger: Logger,
    settings_factory: type[ThegentSettings],
) -> ToolResult:
    logger.info("thegent_pause session_id=%s", session_id)
    from thegent_execution.execution import RunRegistry

    start_time = time.perf_counter()
    settings = settings_factory()
    registry = RunRegistry(settings.session_dir)
    registry.register_pause(run_id=session_id, reason=reason)
    result = {"success": True, "session_id": session_id, "status": "paused", "reason": reason}
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result).decode(),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


def thegent_resume_impl(
    *,
    session_id: str,
    logger: Logger,
    settings_factory: type[ThegentSettings],
) -> ToolResult:
    logger.info("thegent_resume session_id=%s", session_id)
    from thegent_execution.execution import RunRegistry

    start_time = time.perf_counter()
    settings = settings_factory()
    registry = RunRegistry(settings.session_dir)
    registry.register_resume(run_id=session_id)
    result = {"success": True, "session_id": session_id, "status": "running"}
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result).decode(),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


def thegent_continuity_snapshot_impl(
    *,
    owner: str,
    run_ids: list[str],
    state_summary: dict[str, Any] | None,
    next_steps: list[str] | None,
    continuity_snapshot_impl: Callable[..., dict[str, Any]],
) -> ToolResult:
    start_time = time.perf_counter()
    result = continuity_snapshot_impl(
        owner=owner,
        run_ids=run_ids,
        state_summary=state_summary,
        next_steps=next_steps,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result).decode(),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )
