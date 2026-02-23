"""Research and discovery tool handlers for MCP server."""

from __future__ import annotations

import json
import time
from typing import Any

from fastmcp.tools.tool import ToolResult


async def thegent_ddg_search_impl(
    *,
    query: str,
    num_results: int,
    ctx: Any,
) -> ToolResult:
    from thegent.skills.research import ddg_search

    await ctx.info(f"thegent_ddg_search query={query!r} num_results={num_results}")
    start_time = time.perf_counter()
    results = ddg_search(query, max_results=num_results)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    results_list = results if isinstance(results, list) else [results]
    result_count = len(results_list)
    await ctx.info(f"thegent_ddg_search returned {result_count} result(s) in {elapsed_ms}ms")
    return ToolResult(
        content=json.dumps(results_list),
        structured_content={"results": results_list, "count": result_count},
        meta={"execution_time_ms": elapsed_ms},
    )


def thegent_reddit_search_impl(
    *,
    query: str,
    num_results: int,
) -> ToolResult:
    from thegent.config import ThegentSettings
    from thegent.skills.research import reddit_search

    settings = ThegentSettings()
    start_time = time.perf_counter()
    results = reddit_search(query, max_results=num_results, settings=settings)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(results),
        structured_content=results,
        meta={"execution_time_ms": elapsed_ms},
    )


async def thegent_scrape_url_impl(
    *,
    url: str,
    use_playwright: bool,
    ctx: Any,
) -> ToolResult:
    from thegent.skills.research import scrape_url

    await ctx.info(f"thegent_scrape_url url={url!r} use_playwright={use_playwright}")
    await ctx.report_progress(progress=0, total=3)
    start_time = time.perf_counter()
    await ctx.report_progress(progress=1, total=3)
    result = await scrape_url(url, use_playwright=use_playwright)
    await ctx.report_progress(progress=2, total=3)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    content_len = len(result.get("content", "")) if isinstance(result, dict) else 0
    await ctx.info(f"thegent_scrape_url done content_len={content_len} elapsed={elapsed_ms}ms")
    await ctx.report_progress(progress=3, total=3)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


def thegent_deep_research_impl(
    *,
    query: str,
    subreddits: str | None,
) -> ToolResult:
    from thegent.skills.deep_research import perform_deep_research

    start_time = time.perf_counter()
    sub_list = [s.strip() for s in subreddits.split(",") if s.strip()] if subreddits else None
    results = perform_deep_research(query, subreddits=sub_list)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(results),
        structured_content=results,
        meta={"execution_time_ms": elapsed_ms},
    )


async def thegent_suggest_prompt_impl(
    *,
    raw_prompt: str,
    ctx: Any,
    logger: Any,
) -> ToolResult:
    start_time = time.perf_counter()
    try:
        result = await ctx.sample(
            "Refine this task prompt to be clearer and more actionable for an AI agent. Keep it concise. "
            "Return only the refined prompt, no explanation.\n\nRaw prompt:\n"
            f"{raw_prompt}",
            temperature=0.3,
            max_tokens=500,
        )
        suggested = (result.text or raw_prompt).strip()
    except Exception as e:
        logger.debug("thegent_suggest_prompt sampling unavailable: %s", e)
        suggested = raw_prompt
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps({"suggested_prompt": suggested, "sampling_used": suggested != raw_prompt}),
        structured_content={"suggested_prompt": suggested, "sampling_used": suggested != raw_prompt},
        meta={"execution_time_ms": elapsed_ms},
    )
