"""Sitback Agent FastMCP integration: dashboard resource, tool, prompts.

Sitback uses FastMCP as the primary interface (projection over skill + CLI).
Tools and resources are more intuitive: typed, discoverable, URI-addressable.
"""

import orjson as json
from typing import TYPE_CHECKING

from fastmcp.tools.tool import ToolResult

from thegent.cli.commands.impl import sitback_dashboard_impl

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_sitback(mcp: "FastMCP") -> None:
    """Register sitback resource, tool, and prompts with the FastMCP server."""

    # --- Resource: unified dashboard ---
    def resource_sitback_dashboard(profile: str = "medium") -> str:
        """Unified sitback dashboard: sessions, cockpit (circuits, drift, budget), terminals.
        profile: light, medium (default), full (includes plugin widgets, harness)."""
        return json.dumps(sitback_dashboard_impl(profile=profile))

    mcp.resource(
        "thegent://sitback/dashboard{?profile}",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )(resource_sitback_dashboard)

    # --- Tool: dashboard (for tool-only clients) ---
    def thegent_sitback_dashboard(profile: str = "medium") -> ToolResult:
        """
        Unified sitback dashboard: sessions, cockpit (circuits, drift, budget), terminals.
        profile: light (summary only), medium (panels), full (+ plugins, harness).
        Use when THGENT_SITBACK=1 for startup protocol.
        """
        data = sitback_dashboard_impl(profile=profile)
        return ToolResult(
            content=json.dumps(data).decode(),
            structured_content=data,
        )

    mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})(thegent_sitback_dashboard)

    # --- Prompts: startup protocol, spawn sibling ---
    def thegent_sitback_startup() -> str:
        """
        Startup protocol for Sitback Agent (when THGENT_SITBACK=1).
        Call thegent_sitback_dashboard, present the summary, then say "Sitback ready. Awaiting instructions."
        """
        return """You are the Sitback Agent. On startup:
1. Call thegent_sitback_dashboard (or read thegent://sitback/dashboard)
2. Present the summary: sessions, terminals, budget
3. Say: "Sitback ready. Awaiting instructions."
Use MCP tools (thegent_run, thegent_bg, thegent_ps, thegent_terminal_*) as primary; CLI as fallback."""

    mcp.prompt(thegent_sitback_startup)

    def thegent_sitback_spawn_sibling(agent: str = "minimax") -> str:
        """
        Instructions to spawn a sibling Sitback session with the same protocol.
        """
        return f"""Start a sibling Sitback session with provider {agent}.
Run: thegent sitback --agent {agent}
The new session will have the same dashboard protocol and MCP tools."""

    mcp.prompt(thegent_sitback_spawn_sibling)
