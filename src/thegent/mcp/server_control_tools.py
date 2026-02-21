"""Control/status/inspection MCP tool registration helpers."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult


def register_control_tools(
    *,
    mcp: FastMCP,
    server_tools_runtime: Any,
    server_tools_contract_observe: Any,
    server_tools_coordination: Any,
    ps_impl: Any,
    status_impl: Any,
    logs_impl: Any,
    inspect_impl: Any,
    wait_impl: Any,
    inbox_list_impl: Any,
    stop_impl: Any,
    continuity_snapshot_impl: Any,
    settings_factory: Any,
    logger: Any,
) -> tuple[object, ...]:
    """Register control-oriented MCP tools and return stable handler bindings."""

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_ps(owner: str | None = None, all: bool = False, include_contract: bool = False) -> ToolResult:
        """
        List active and historical background sessions for monitoring and discovery.
        Use this to find session_ids for thegent_logs, thegent_status, etc.
        """
        return server_tools_runtime.ps_tool_impl(
            owner=owner,
            all=all,
            include_contract=include_contract,
            ps_impl=ps_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_status(session_id: str, include_contract: bool = False) -> ToolResult:
        """Get session status for quick health check."""
        return server_tools_runtime.status_tool_impl(
            session_id=session_id,
            include_contract=include_contract,
            status_impl=status_impl,
            log=logger,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_logs(session_id: str, tail: int | None = None, stderr: bool = False) -> ToolResult:
        """Read session log output with optional tail limit."""
        return server_tools_runtime.logs_tool_impl(
            session_id=session_id,
            tail=tail,
            stderr=stderr,
            logs_impl=logs_impl,
            log=logger,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_inspect(
        session_ids: list[str] | None = None,
        owner: str | None = None,
        tail: int = 50,
        stderr: bool = False,
        include_contract: bool = False,
    ) -> ToolResult:
        """Multi-session status + logs."""
        return server_tools_contract_observe.thegent_inspect_impl(
            session_ids=session_ids,
            owner=owner,
            tail=tail,
            stderr=stderr,
            include_contract=include_contract,
            inspect_impl=inspect_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_wait(session_id: str, timeout: int | None = None) -> ToolResult:
        """Block until session completes or timeout."""
        return server_tools_coordination.thegent_wait_impl(
            session_id=session_id,
            timeout=timeout,
            logger=logger,
            wait_impl=wait_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_inbox_list(
        owner: str | None = None,
        agent: str | None = None,
        event_type: str | None = None,
        status: str | None = None,
        sources: str | None = None,
        limit: int = 50,
    ) -> ToolResult:
        """List unified inbox events (run registry + escalation) with optional filters."""
        return server_tools_coordination.thegent_inbox_list_impl(
            owner=owner,
            agent=agent,
            event_type=event_type,
            status=status,
            sources=sources,
            limit=limit,
            inbox_list_impl=inbox_list_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": False})
    def thegent_inbox_wait(
        owner: str | None = None,
        agent: str | None = None,
        event_type: str | None = None,
        status: str | None = None,
        sources: str | None = None,
        poll_interval: float = 2.0,
        timeout: float = 60.0,
    ) -> ToolResult:
        """Wait for next inbox event matching filters."""
        return server_tools_coordination.thegent_inbox_wait_impl(
            owner=owner,
            agent=agent,
            event_type=event_type,
            status=status,
            sources=sources,
            poll_interval=poll_interval,
            timeout=timeout,
            logger=logger,
            inbox_list_impl=inbox_list_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False})
    def thegent_stop(session_id: str, force: bool = False) -> ToolResult:
        """Stop a background session."""
        return server_tools_coordination.thegent_stop_impl(
            session_id=session_id,
            force=force,
            logger=logger,
            stop_impl=stop_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_pause(session_id: str, reason: str = "Manual pause") -> ToolResult:
        """Pause a background session (register pause event in registry)."""
        return server_tools_coordination.thegent_pause_impl(
            session_id=session_id,
            reason=reason,
            logger=logger,
            settings_factory=settings_factory,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_resume(session_id: str) -> ToolResult:
        """Resume a paused session (register resume event in registry)."""
        return server_tools_coordination.thegent_resume_impl(
            session_id=session_id,
            logger=logger,
            settings_factory=settings_factory,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_continuity_snapshot(
        owner: str,
        run_ids: list[str],
        state_summary: dict[str, Any] | None = None,
        next_steps: list[str] | None = None,
    ) -> ToolResult:
        """Create a continuity snapshot for shift handoff."""
        return server_tools_coordination.thegent_continuity_snapshot_impl(
            owner=owner,
            run_ids=run_ids,
            state_summary=state_summary,
            next_steps=next_steps,
            continuity_snapshot_impl=continuity_snapshot_impl,
        )

    return (
        thegent_ps,
        thegent_status,
        thegent_logs,
        thegent_inspect,
        thegent_wait,
        thegent_inbox_list,
        thegent_inbox_wait,
        thegent_stop,
        thegent_pause,
        thegent_resume,
        thegent_continuity_snapshot,
    )

