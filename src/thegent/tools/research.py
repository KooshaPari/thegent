import asyncio
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def ddg_search(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """
    Perform a web search using DuckDuckGo.
    Requires 'duckduckgo-search' library.
    """
    try:
        from duckduckgo_search import DDGS  # type: ignore[import]
    except ImportError:
        logger.error("duckduckgo-search library not installed. Run: pip install duckduckgo-search")
        return [{"error": "duckduckgo-search library not installed"}]

    results = []
    try:
        with DDGS() as ddgs:
            # use text() method
            results.extend(ddgs.text(query, max_results=max_results))
    except Exception as e:
        logger.error(f"DDG search error: {e}")
        return [{"error": str(e)}]

    return results


def reddit_search(query: str, max_results: int = 5, settings: Any = None) -> list[dict[str, Any]]:
    """
    Perform a search on Reddit.
    Uses PRAW if credentials are provided, otherwise falls back to DDG site:reddit.com.
    """
    if settings and settings.reddit_client_id and settings.reddit_client_secret:
        try:
            import praw  # type: ignore[import]

            reddit = praw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent=settings.reddit_user_agent,
            )
            results = []
            for submission in reddit.subreddit("all").search(query, limit=max_results):
                results.append(
                    {
                        "title": submission.title,
                        "url": f"https://www.reddit.com{submission.permalink}",
                        "body": submission.selftext[:500] + "..."
                        if len(submission.selftext) > 500
                        else submission.selftext,
                        "score": submission.score,
                        "num_comments": submission.num_comments,
                    }
                )
            return results
        except Exception as e:
            logger.warning(f"Reddit API error, falling back to DDG: {e}")

    # Fallback to DDG
    return ddg_search(f"{query} site:reddit.com", max_results=max_results)


async def scrape_url(url: str, use_playwright: bool = True) -> dict[str, Any]:
    """
    Scrape content from a URL.
    Uses Playwright for stealth scraping if available, otherwise falls back to httpx.
    """
    if use_playwright:
        try:
            from playwright.async_api import async_playwright  # type: ignore[import]

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                # Stealth context (simplified)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
                page = await context.new_page()
                await page.goto(url, wait_until="networkidle", timeout=30000)
                content = await page.content()
                title = await page.title()
                text = await page.inner_text("body")
                await browser.close()
                return {
                    "url": url,
                    "title": title,
                    "content": text[:5000],  # Limit content size
                    "method": "playwright",
                }
        except Exception as e:
            logger.warning(f"Playwright scraping failed for {url}: {e}")

    # Fallback to httpx
    try:
        import httpx

        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            resp = await client.get(url, headers={"User-Agent": "thegent/0.1.0"})
            resp.raise_for_status()
            return {"url": url, "content": resp.text[:5000], "method": "httpx"}
    except Exception as e:
        logger.error(f"Scraping failed for {url}: {e}")
        return {"url": url, "error": str(e)}


def deep_research_orchestrator(query: str, depth: int = 1, settings: Any = None) -> dict[str, Any]:
    """
    Orchestrate a deep research protocol.
    1. Broad search.
    2. Reddit search.
    3. Targeted scraping of top results.
    4. Synthesis (simplified here, the agent will do the final synthesis).
    """
    # This is a synchronous wrapper for the protocol
    results = {
        "query": query,
        "broad_results": ddg_search(query, max_results=5),
        "reddit_results": reddit_search(query, max_results=5, settings=settings),
        "links_to_scrape": [],
    }

    # Collect links for Phase 3
    links = []
    for r in results["broad_results"]:
        if "href" in r:
            links.append(r["href"])
    for r in results["reddit_results"]:
        if "url" in r:
            links.append(r["url"])

    results["links_to_scrape"] = links[:3]  # Limit to top 3 links for now

    return results
