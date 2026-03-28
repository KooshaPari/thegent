"""Registration helpers for queue mutation MCP tools."""

from __future__ import annotations

from typing import Any, Callable

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult


def register_queue_mutation_tools(
    *,
    mcp: FastMCP,
    server_tools_queue: Any,
    settings_factory: Callable[[], Any],
) -> tuple[Any, Any, Any, Any, Any]:
    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_queue_done(item_id: int) -> ToolResult:
        """Mark a queue item as done by id. Use id from thegent_queue_list or thegent_queue_claim."""
        settings = settings_factory()
        return server_tools_queue.queue_done_impl(
            session_dir=settings.session_dir,
            item_id=item_id,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_queue_add(prompt: str, project: str, agent: str | None = None) -> ToolResult:
        """Add a prompt to the queue (deferred execution). Equivalent to $defer in prompt."""
        settings = settings_factory()
        return server_tools_queue.queue_add_impl(
            session_dir=settings.session_dir,
            prompt=prompt,
            project=project,
            agent=agent,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_queue_edit(item_id: int, prompt: str) -> ToolResult:
        """Edit prompt for a pending or claimed queue item. Cannot edit done items."""
        settings = settings_factory()
        return server_tools_queue.queue_edit_impl(
            session_dir=settings.session_dir,
            item_id=item_id,
            prompt=prompt,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_queue_release(item_id: int) -> ToolResult:
        """Release a claimed queue item back to pending. Use when worker cannot complete."""
        settings = settings_factory()
        return server_tools_queue.queue_release_impl(
            session_dir=settings.session_dir,
            item_id=item_id,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_queue_extend_lease(item_id: int, lease_seconds: int = 300) -> ToolResult:
        """Extend lease for a claimed queue item. Use before lease expires."""
        settings = settings_factory()
        return server_tools_queue.queue_extend_lease_impl(
            session_dir=settings.session_dir,
            item_id=item_id,
            lease_seconds=lease_seconds,
        )

    return (
        thegent_queue_done,
        thegent_queue_add,
        thegent_queue_edit,
        thegent_queue_release,
        thegent_queue_extend_lease,
    )
