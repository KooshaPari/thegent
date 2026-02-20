import json
import logging
import re
import subprocess
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def run_curl(url: str, user_agent: str = DEFAULT_USER_AGENT) -> str:
    """Run curl with a specific user agent and return the output."""
    import urllib.parse

    # Very simple manual quoting for problematic characters in shell/curl
    safe_url = url.replace(" ", "%20").replace("|", "%7C").replace("^", "%5E")

    try:
        result = subprocess.run(
            ["curl", "-L", "-H", f"User-Agent: {user_agent}", "-s", safe_url],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Curl error for {safe_url}: {e}")
        return ""


def ddg_html_search(query: str) -> list[dict[str, str]]:
    """Perform a DuckDuckGo HTML search and extract results."""
    # This is a simplified version. In a real scenario, we'd use a parser.
    # Since we have 'jaq' or 'jq' but maybe not BeautifulSoup everywhere,
    # we'll try to keep it robust.
    url = f"https://html.duckduckgo.com/html/?q={query}"
    html = run_curl(url)

    # Very basic extraction if we don't have a parser.
    # Ideally we'd use BeautifulSoup, but let's check if it's available.
    results = []
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        for result in soup.find_all("div", class_="result"):
            title_tag = result.find("a", class_="result__a")
            snippet_tag = result.find("a", class_="result__snippet")
            if title_tag:
                results.append(
                    {
                        "title": title_tag.get_text(strip=True),
                        "url": title_tag["href"],
                        "snippet": snippet_tag.get_text(strip=True) if snippet_tag else "",
                    }
                )
    except ImportError:
        logger.warning("BeautifulSoup4 not installed, falling back to regex for DDG HTML search.")
        import re

        # More robust fallback regex extraction
        # DDG HTML results usually look like: <a class="result__a" rel="nofollow" href="...">Title</a>
        matches = re.findall(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html)
        for url, title in matches:
            # Strip tags from title if any
            clean_title = re.sub(r"<[^>]+>", "", title)
            results.append({"title": clean_title, "url": url, "snippet": ""})

    return results


def reddit_json_search(query: str, subreddit: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """Search Reddit using the .json API."""
    if subreddit:
        url = f"https://www.reddit.com/r/{subreddit}/search.json?q={query}&restrict_sr=1&sort=relevance&limit={limit}"
    else:
        url = f"https://www.reddit.com/search.json?q={query}&sort=relevance&limit={limit}"

    content = run_curl(url)
    try:
        data = json.loads(content)
        results = []
        if "data" in data and "children" in data["data"]:
            for child in data["data"]["children"]:
                post = child["data"]
                results.append(
                    {
                        "title": post.get("title"),
                        "url": f"https://www.reddit.com{post.get('permalink')}",
                        "selftext": post.get("selftext"),
                        "score": post.get("score"),
                        "subreddit": post.get("subreddit"),
                    }
                )
        # Add a delay to avoid rate limiting
        import time

        time.sleep(1)
        return results
    except json.JSONDecodeError:
        logger.error("Failed to decode Reddit JSON")
        return []


def arxiv_search(query: str, max_results: int = 50) -> list[dict[str, Any]]:
    """Search Arxiv using their API."""
    url = f"https://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    content = run_curl(url)
    # Arxiv returns XML. Parsing XML without specialized libs is hard.
    # For now, we'll return the raw XML or try basic extraction.
    results = []
    # import re already at top
    entries = re.findall(r"<entry>(.*?)</entry>", content, re.DOTALL)
    for entry in entries:
        title = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
        summary = re.search(r"<summary>(.*?)</summary>", entry, re.DOTALL)
        link = re.search(r"<id>(.*?)</id>", entry, re.DOTALL)
        results.append(
            {
                "title": title.group(1).strip() if title else "No Title",
                "summary": summary.group(1).strip() if summary else "No Summary",
                "url": link.group(1).strip() if link else "No Link",
            }
        )
    return results


def github_search(query: str, max_results: int = 25) -> list[dict[str, Any]]:
    """Search GitHub repositories using their API."""
    # Strip site: operators for GitHub search
    clean_query = re.sub(r"site:[^\s]+", "", query).strip()
    if not clean_query:
        return []

    url = f"https://api.github.com/search/repositories?q={clean_query}&sort=stars&order=desc"
    content = run_curl(url)
    try:
        data = json.loads(content)
        results = []
        for item in data.get("items", [])[:max_results]:
            results.append(
                {
                    "title": item.get("full_name"),
                    "url": item.get("html_url"),
                    "snippet": item.get("description") or "No description",
                    "stars": item.get("stargazers_count"),
                }
            )
        return results
    except Exception:
        return []


def perform_deep_research(query: str, subreddits: list[str] | None = None) -> dict[str, Any]:
    """Execute the full Deep Research Protocol."""
    report = {
        "query": query,
        "ddg_results": ddg_html_search(query),
        "reddit_results": [],
        "arxiv_results": arxiv_search(query),
        "github_results": github_search(query),
        "summary": "",
    }

    # Reddit search
    if subreddits:
        for sub in subreddits:
            report["reddit_results"].extend(reddit_json_search(query, sub))
    else:
        report["reddit_results"].extend(reddit_json_search(query))

    return report
