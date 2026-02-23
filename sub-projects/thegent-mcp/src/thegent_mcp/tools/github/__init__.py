"""GitHub MCP tools (placeholder for zen-mcp-server absorption)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_tools(server: FastMCP) -> None:
    """Register GitHub tools on FastMCP server."""

    @server.tool()
    async def github_list_repos(owner: str = "") -> str:
        """List repositories for a GitHub user or org."""
        # Placeholder: will be wired to actual GitHub API after zen-mcp-server absorption
        return json.dumps({"repos": [], "owner": owner})

    @server.tool()
    async def github_create_issue(
        owner: str = "",
        repo: str = "",
        title: str = "",
        body: str = "",
    ) -> str:
        """Create a GitHub issue."""
        return json.dumps({
            "issue_url": f"https://github.com/{owner}/{repo}/issues/new",
            "title": title,
        })
