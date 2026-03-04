"""Consolidated MCP tools with intuitive parameter-based actions to reduce tool count."""

import orjson as json
import logging
from typing import Any, Literal

from fastmcp import FastMCP
from fastmcp.server.dependencies import CurrentContext
from fastmcp.tools.tool import ToolResult


def register_consolidated_tools(*, mcp: FastMCP, logger: logging.Logger) -> tuple[object, ...]:
    """Register consolidated MCP tools with parameter-based actions."""

    # -------------------------------------------------------------------------
    # thegent_web: Unified web research (ddg, reddit, scrape, deep)
    # -------------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    async def thegent_web(
        action: Literal["search", "scrape", "reddit", "deep", "suggest"] = "search",
        query: str = "",
        url: str = "",
        num_results: int = 5,
        ctx: Any = CurrentContext(),
    ) -> ToolResult:
        """
        Unified web research tool - reduces 5 tools to 1.

        Args:
            action: Action to perform (search=DDG, scrape=URL, reddit=Reddit, deep=Deep research, suggest=Prompt)
            query: Search query (for search, reddit, deep, suggest actions)
            url: URL to scrape (for scrape action)
            num_results: Max results (default: 5)
        """
        from thegent_mcp.mcp.server.tools_research import (
            thegent_ddg_search_impl,
            thegent_scrape_url_impl,
            thegent_reddit_search_impl,
            thegent_deep_research_impl,
            thegent_suggest_prompt_impl,
        )

        if action == "search":
            return await thegent_ddg_search_impl(query=query, num_results=num_results, ctx=ctx)
        if action == "scrape":
            return await thegent_scrape_url_impl(url=url, use_playwright=True, ctx=ctx)
        if action == "reddit":
            return thegent_reddit_search_impl(query=query, num_results=num_results)
        if action == "deep":
            return thegent_deep_research_impl(query=query, subreddits=None)
        if action == "suggest":
            return await thegent_suggest_prompt_impl(raw_prompt=query, ctx=ctx, logger=logger)
        return ToolResult(content=f"Unknown action: {action}")

    # -------------------------------------------------------------------------
    # thegent_queue: Unified queue operations
    # -------------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    async def thegent_queue(
        action: Literal["add", "list", "claim", "done", "release", "edit", "extend"] = "list",
        prompt: str = "",
        item_id: str = "",
        project: str = "",
        all_items: bool = False,
        lease_seconds: int = 300,
        ctx: Any = CurrentContext(),
    ) -> ToolResult:
        """
        Unified queue management - reduces 7 tools to 1.

        Args:
            action: add=list new item, list=show items, done=mark complete,
                   claim=claim item, release=release lease, edit=modify item, extend=extend lease
            prompt: Task prompt (for add action)
            item_id: Item ID as integer string (for done, release, edit, extend actions)
            project: Project path filter (for add, claim)
            all_items: Include done items in list (for list)
            lease_seconds: Lease duration (for claim, extend)
        """
        from thegent_mcp.mcp.server.tools_queue import (
            queue_add_impl,
            queue_list_impl,
            queue_done_impl,
            queue_claim_impl,
            queue_release_impl,
            queue_edit_impl,
            queue_extend_lease_impl,
        )
        from thegent_core.config import ThegentSettings

        settings = ThegentSettings()
        session_dir = settings.session_dir
        item_id_int = int(item_id) if item_id else 0

        if action == "add":
            return queue_add_impl(session_dir=session_dir, prompt=prompt, project=project, agent=None)
        if action == "list":
            return queue_list_impl(
                session_dir=session_dir,
                include_done=all_items,
                include_expired=all_items,
                limit=None,
            )
        if action == "done":
            return queue_done_impl(session_dir=session_dir, item_id=item_id_int)
        if action == "claim":
            return queue_claim_impl(
                session_dir=session_dir,
                claimer_id="mcp-client",
                project=project or None,
                lease_seconds=lease_seconds,
            )
        if action == "release":
            return queue_release_impl(session_dir=session_dir, item_id=item_id_int)
        if action == "edit":
            return queue_edit_impl(session_dir=session_dir, item_id=item_id_int, prompt=prompt)
        if action == "extend":
            return queue_extend_lease_impl(session_dir=session_dir, item_id=item_id_int, lease_seconds=lease_seconds)
        return ToolResult(content=f"Unknown action: {action}")

    # -------------------------------------------------------------------------
    # thegent_session: Unified session management
    # -------------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    async def thegent_session(
        action: Literal["list", "show", "logs", "send", "attach"] = "list",
        session_id: str = "",
        all: bool = False,
        owner: str = "",
        agent: str = "",
        status: str = "",
        limit: int = 50,
        stderr: bool = False,
        message: str = "",
        tail: int = 100,
        msg_type: str = "reprompt",
        ctx: Any = CurrentContext(),
    ) -> ToolResult:
        """
        Unified session management - reduces 5 tools to 1.

        Args:
            action: list=show sessions, show=session details, logs=view logs, send=send message, attach=attach hint
            session_id: Session ID (for show, logs, send, attach)
            all: Show all sessions (for list)
            owner: Filter by owner
            agent: Filter by agent
            status: Filter by status
            limit: Max results (default: 50)
            stderr: Show stderr (for logs)
            message: Message to send (for send action)
            tail: Number of log lines (for logs)
            msg_type: Message type for send (default: reprompt)
        """
        from thegent_mcp.mcp.server.tools_sessions import (
            session_list_impl,
            session_show_impl,
            session_logs_impl,
            session_send_impl,
            session_attach_hint_impl,
        )
        from thegent_cli.cli.commands.session_ops_impl import ps_impl, logs_impl
        from thegent_cli.cli.commands.session_control_impl import session_send_impl as raw_send_impl

        if action == "list":
            result = session_list_impl(
                all=all,
                owner=owner or None,
                agent=agent or None,
                status=status or None,
                limit=limit,
                ps_impl=ps_impl,
            )
            return ToolResult(content=result)
        if action == "show":
            return ToolResult(content=session_show_impl(session_id=session_id, ps_impl=ps_impl))
        if action == "logs":
            return ToolResult(
                content=session_logs_impl(
                    session_id=session_id,
                    stderr=stderr,
                    tail=tail,
                    logs_impl=logs_impl,
                )
            )
        if action == "send":
            return ToolResult(
                content=session_send_impl(
                    session_id=session_id,
                    message=message,
                    msg_type=msg_type,
                    send_impl=raw_send_impl,
                )
            )
        if action == "attach":
            return ToolResult(content=session_attach_hint_impl(session_id=session_id, ps_impl=ps_impl))
        return ToolResult(content=f"Unknown action: {action}")

    # -------------------------------------------------------------------------
    # thegent_workstream: Unified workstream operations
    # -------------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    async def thegent_workstream(
        action: Literal["do-next", "claim", "complete", "progress"] = "do-next",
        item_id: str = "",
        agent_id: str = "",
        limit: int = 5,
        cd: str = "",
        ctx: Any = CurrentContext(),
    ) -> ToolResult:
        """
        Unified workstream operations - reduces 4+ tools to 1.

        Args:
            action: do-next=get next item, claim=claim item, complete=mark complete, progress=show progress
            item_id: Work item ID (for claim/complete)
            agent_id: Agent ID (for claim/complete)
            limit: Max items (for do-next)
            cd: Working directory
        """
        from thegent_cli.cli.commands.impl import (
            do_next_impl,
            work_stream_claim_impl,
            work_stream_complete_impl,
        )
        from pathlib import Path

        cwd = Path(cd) if cd else None

        if action == "do-next":
            result = do_next_impl(cd=cwd, limit=limit)
            return ToolResult(content=json.dumps(result, indent=2).decode().decode())
        if action == "claim":
            result = work_stream_claim_impl(item_id=item_id, agent_id=agent_id, cd=cwd)
            return ToolResult(content=json.dumps(result, indent=2).decode().decode())
        if action == "complete":
            result = work_stream_complete_impl(item_id=item_id, agent_id=agent_id, cd=cwd)
            return ToolResult(content=json.dumps(result, indent=2).decode().decode())
        if action == "progress":
            return ToolResult(content="Use 'thegent plan progress' CLI command")
        return ToolResult(content=f"Unknown action: {action}")

    return (
        thegent_web,
        thegent_queue,
        thegent_session,
        thegent_workstream,
    )
