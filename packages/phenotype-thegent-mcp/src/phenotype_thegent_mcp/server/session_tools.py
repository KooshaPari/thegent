"""Session tool registrations for MCP server."""

from __future__ import annotations

from typing import Any, Callable

from fastmcp import FastMCP


def register_session_tools(
    *,
    mcp: FastMCP,
    server_tools_sessions: Any,
    ps_impl: Callable[..., list[dict[str, Any]]],
    logs_impl: Callable[..., str | None],
    session_send_impl: Callable[..., tuple[bool, str]],
) -> tuple[Any, Any, Any, Any, Any]:
    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    async def phenotype_thegent_session_list(
        all: bool = False,
        owner: str | None = None,
        agent: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> str:
        """
        List agent sessions from the registry (WP-9006).

        Args:
            all: Show sessions for all owners (admin)
            owner: Filter by owner tag
            agent: Filter by agent name
            status: Filter by status (running, completed, failed)
            limit: Max sessions to return
        """
        return server_tools_sessions.session_list_impl(
            all=all,
            owner=owner,
            agent=agent,
            status=status,
            limit=limit,
            ps_impl=ps_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    async def phenotype_thegent_session_show(
        session_id: str,
    ) -> str:
        """
        Get detailed metadata for a session (WP-9006).

        Args:
            session_id: The ID of the session
        """
        return server_tools_sessions.session_show_impl(
            session_id=session_id,
            ps_impl=ps_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    async def phenotype_thegent_session_logs(
        session_id: str,
        stderr: bool = False,
        tail: int = 100,
    ) -> str:
        """
        Read session logs (stdout/stderr) (WP-9006).

        Args:
            session_id: The ID of the session
            stderr: Read stderr instead of stdout
            tail: Number of lines to return from the end
        """
        return server_tools_sessions.session_logs_impl(
            session_id=session_id,
            stderr=stderr,
            tail=tail,
            logs_impl=logs_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    async def phenotype_thegent_session_send(
        session_id: str,
        message: str,
        msg_type: str = "reprompt",
    ) -> str:
        """
        Send a message/reprompt to a running session (WP-9004).

        Args:
            session_id: The ID of the session
            message: The message text to send
            msg_type: reprompt, command, system
        """
        return server_tools_sessions.session_send_impl(
            session_id=session_id,
            message=message,
            msg_type=msg_type,
            send_impl=session_send_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    async def phenotype_thegent_session_attach_hint(
        session_id: str,
    ) -> str:
        """
        Return the command to attach to a session (WP-9007).

        Args:
            session_id: The ID of the session
        """
        return server_tools_sessions.session_attach_hint_impl(
            session_id=session_id,
            ps_impl=ps_impl,
        )

    return (
        phenotype_thegent_session_list,
        phenotype_thegent_session_show,
        phenotype_thegent_session_logs,
        phenotype_thegent_session_send,
        phenotype_thegent_session_attach_hint,
    )
