"""Slack MCP tools (placeholder for zen-mcp-server absorption)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_tools(server: FastMCP) -> None:
    """Register Slack tools on FastMCP server."""

    @server.tool()
    async def slack_send_message(channel: str = "", text: str = "") -> str:
        """Send a message to a Slack channel."""
        return json.dumps({"ok": True, "channel": channel})

    @server.tool()
    async def slack_list_channels() -> str:
        """List Slack channels."""
        return json.dumps({"channels": []})
