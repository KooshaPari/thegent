"""Research MCP tool registration helpers."""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.dependencies import CurrentContext
from fastmcp.tools.tool import ToolResult


Context = Any


def register_research_tools(*, mcp: FastMCP, server_tools_research: Any, logger: logging.Logger) -> tuple[object, ...]:
    """Register ddg/reddit/scrape/deep-research/suggest_prompt MCP tools."""

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    async def phenotype_thegent_ddg_search(
        query: str,
        num_results: int = 5,
        ctx: Context = CurrentContext(),
    ) -> ToolResult:
        """
        Search DuckDuckGo for heavy web research.

        Args:
            query: Search query string
            num_results: Max results to return (min: 1, max: 20, default: 5)
        """
        return await server_tools_research.phenotype_thegent_ddg_search_impl(
            query=query,
            num_results=num_results,
            ctx=ctx,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def phenotype_thegent_reddit_search(query: str, num_results: int = 5) -> ToolResult:
        """
        Search Reddit for discussions and community insights.
        Uses Reddit API (if configured) or site-specific search.

        Args:
            query: Search query string
            num_results: Max results to return (min: 1, max: 20, default: 5)
        """
        return server_tools_research.phenotype_thegent_reddit_search_impl(
            query=query,
            num_results=num_results,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    async def phenotype_thegent_scrape_url(
        url: str,
        use_playwright: bool = True,
        ctx: Context = CurrentContext(),
    ) -> ToolResult:
        """
        Scrape content from a URL using stealth tools (Playwright) to bypass blocks.

        Args:
            url: URL to scrape
            use_playwright: Whether to use Playwright for stealth scraping (default: True)
        """
        return await server_tools_research.phenotype_thegent_scrape_url_impl(
            url=url,
            use_playwright=use_playwright,
            ctx=ctx,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def phenotype_thegent_deep_research(query: str, subreddits: str | None = None) -> ToolResult:
        """
        Perform deep research using the Deep Research Protocol (DRP).
        Bypasses blocks by using custom headers and direct API calls.

        Args:
            query: Search query string
            subreddits: Comma-separated list of subreddits to prioritize
        """
        return server_tools_research.phenotype_thegent_deep_research_impl(
            query=query,
            subreddits=subreddits,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    async def phenotype_thegent_suggest_prompt(
        raw_prompt: str,
        ctx: Context = CurrentContext(),
    ) -> ToolResult:
        """
        Refine a raw prompt using LLM sampling. Returns a suggested, clearer prompt.
        When client lacks sampling support, returns raw_prompt with a note.
        """
        return await server_tools_research.phenotype_thegent_suggest_prompt_impl(
            raw_prompt=raw_prompt,
            ctx=ctx,
            logger=logger,
        )

    return (
        phenotype_thegent_ddg_search,
        phenotype_thegent_reddit_search,
        phenotype_thegent_scrape_url,
        phenotype_thegent_deep_research,
        phenotype_thegent_suggest_prompt,
    )
