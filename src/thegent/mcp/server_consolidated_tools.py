"""Consolidated MCP tools with intuitive parameter-based actions to reduce tool count."""

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
        from thegent.mcp.server.tools_research import (
            ddg_search_impl,
            scrape_url_impl,
            reddit_search_impl,
            deep_research_impl,
            suggest_prompt_impl,
        )

        if action == "search":
            return await ddg_search_impl(query=query, num_results=num_results, ctx=ctx)
        if action == "scrape":
            return await scrape_url_impl(url=url, use_playwright=True, ctx=ctx)
        if action == "reddit":
            return reddit_search_impl(query=query, num_results=num_results)
        if action == "deep":
            return deep_research_impl(query=query, subreddits=None)
        if action == "suggest":
            return await suggest_prompt_impl(raw_prompt=query, ctx=ctx)
        return ToolResult(content=f"Unknown action: {action}")

    # -------------------------------------------------------------------------
    # thegent_queue: Unified queue operations
    # -------------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    async def thegent_queue(
        action: Literal["add", "list", "next", "done", "claim", "release", "edit", "extend"] = "list",
        prompt: str = "",
        item_id: str = "",
        project: str = "",
        all_items: bool = False,
        lease_seconds: int = 300,
        ctx: Any = CurrentContext(),
    ) -> ToolResult:
        """
        Unified queue management - reduces 8 tools to 1.

        Args:
            action: add=list new item, list=show items, next=get next, done=mark complete,
                   claim=claim item, release=release lease, edit=modify item, extend=extend lease
            prompt: Task prompt (for add action)
            item_id: Item ID (for done, claim, release, edit, extend actions)
            project: Project path filter
            all_items: Include claimed/done items (for list)
            lease_seconds: Lease duration (for extend)
        """
        from thegent.mcp.server.tools_queue import (
            queue_add_impl,
            queue_list_impl,
            queue_next_impl,
            queue_done_impl,
            queue_claim_impl,
            queue_release_impl,
            queue_edit_impl,
            queue_extend_lease_impl,
        )

        if action == "add":
            return queue_add_impl(prompt=prompt, project=project)
        if action == "list":
            return queue_list_impl(project=project, all_items=all_items)
        if action == "next":
            return queue_next_impl(project=project)
        if action == "done":
            return queue_done_impl(item_id=item_id)
        if action == "claim":
            return queue_claim_impl(item_id=item_id, lease_seconds=lease_seconds)
        if action == "release":
            return queue_release_impl(item_id=item_id)
        if action == "edit":
            return queue_edit_impl(item_id=item_id, new_prompt=prompt)
        if action == "extend":
            return queue_extend_lease_impl(item_id=item_id, lease_seconds=lease_seconds)
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
        """
        from thegent.mcp.server.tools_sessions import (
            session_list_impl,
            session_show_impl,
            session_logs_impl,
            session_send_impl,
            session_attach_hint_impl,
        )
        from thegent.cli.commands.impl import ps_impl

        if action == "list":
            sessions = ps_impl(all=all, owner=owner, agent=agent, status=status, limit=limit)
            import json
            return ToolResult(content=json.dumps(sessions, indent=2))
        if action == "show":
            return session_show_impl(session_id=session_id, ps_impl=ps_impl)
        if action == "logs":
            return session_logs_impl(session_id=session_id, stderr=stderr, ps_impl=ps_impl)
        if action == "send":
            return session_send_impl(session_id=session_id, message=message, ps_impl=ps_impl)
        if action == "attach":
            return session_attach_hint_impl(session_id=session_id)
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
        from thegent.cli.commands.impl import (
            do_next_impl,
            work_stream_claim_impl,
            work_stream_complete_impl,
        )
        from pathlib import Path

        cwd = Path(cd) if cd else None

        if action == "do-next":
            result = do_next_impl(cd=cwd, limit=limit)
            import json
            return ToolResult(content=json.dumps(result, indent=2))
        if action == "claim":
            result = work_stream_claim_impl(item_id=item_id, agent_id=agent_id, cd=cwd)
            import json
            return ToolResult(content=json.dumps(result, indent=2))
        if action == "complete":
            result = work_stream_complete_impl(item_id=item_id, agent_id=agent_id, cd=cwd)
            import json
            return ToolResult(content=json.dumps(result, indent=2))
        if action == "progress":
            from thegent.cli.commands.cli import plan_progress_cmd
            # Just return a simple message since progress_cmd prints
            return ToolResult(content="Use 'thegent plan progress' CLI command")
        return ToolResult(content=f"Unknown action: {action}")

    return (
        thegent_web,
        thegent_queue,
        thegent_session,
        thegent_workstream,
    )
