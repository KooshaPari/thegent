"""Registration helpers for handoff + queue MCP tools."""

from __future__ import annotations

from typing import Any, Callable

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult


def register_handoff_queue_tools(
    *,
    mcp: FastMCP,
    server_tools_terminal: Any,
    server_tools_queue: Any,
    settings_factory: Callable[[], Any],
    error_result: Callable[..., ToolResult],
) -> tuple[Any, Any, Any, Any, Any]:
    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def phenotype_thegent_handoff_list(limit: int = 10) -> ToolResult:
        """
        List pending handoff snapshots. Equivalent to: thegent orchestrate handoff-list
        """
        return server_tools_terminal.handoff_list_impl(
            limit=limit,
            settings_factory=settings_factory,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def phenotype_thegent_handoff_show(snapshot_id: str) -> ToolResult:
        """
        Show full handoff summary for a snapshot. Equivalent to: thegent orchestrate handoff-show
        """
        return server_tools_terminal.handoff_show_impl(
            snapshot_id=snapshot_id,
            settings_factory=settings_factory,
            error_result=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def phenotype_thegent_handoff_confirm(snapshot_id: str, incoming_owner: str, confidence: float = 1.0) -> ToolResult:
        """
        Incoming owner confirms handoff completeness. Equivalent to: thegent orchestrate handoff-confirm
        """
        return server_tools_terminal.handoff_confirm_impl(
            snapshot_id=snapshot_id,
            incoming_owner=incoming_owner,
            confidence=confidence,
            settings_factory=settings_factory,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def phenotype_thegent_queue_list(
        include_done: bool = False,
        include_expired: bool = True,
        limit: int | None = None,
    ) -> ToolResult:
        """
        List prompt queue items (deferred prompts). Use include_done=True to see completed items.
        Returns items with id for claim/done/release/extend_lease/edit.
        """
        settings = settings_factory()
        return server_tools_queue.queue_list_impl(
            session_dir=settings.session_dir,
            include_done=include_done,
            include_expired=include_expired,
            limit=limit,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def phenotype_thegent_queue_claim(
        claimer_id: str = "mcp-client",
        project: str | None = None,
        lease_seconds: int = 300,
    ) -> ToolResult:
        """
        Atomically claim the first pending queue item. Returns claimed item with id, or null if queue empty.
        Use project to filter by project path.
        """
        settings = settings_factory()
        return server_tools_queue.queue_claim_impl(
            session_dir=settings.session_dir,
            claimer_id=claimer_id,
            project=project,
            lease_seconds=lease_seconds,
        )

    return (
        phenotype_thegent_handoff_list,
        phenotype_thegent_handoff_show,
        phenotype_thegent_handoff_confirm,
        phenotype_thegent_queue_list,
        phenotype_thegent_queue_claim,
    )
