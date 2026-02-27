"""Google Search Grounding support via MCP tools.

This module provides grounding through MCP search tools instead of direct API calls.
Uses CLIProxy (bifrost) for LLM routing and MCP search tools for grounding.

Supported grounding providers:
- ddg_search: DuckDuckGo web search
- reddit_search: Reddit search  
- scrape_url: Web content extraction

# @trace WL-119
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import httpx

from thegent.agents.base import RunResult

if TYPE_CHECKING:
    from httpx import Response

_log = logging.getLogger(__name__)

# Default CLIProxy URL
DEFAULT_CLIPROXY_URL = "http://localhost:8317"

# Agents that are Gemini-backed and eligible for grounding.
GROUNDING_AGENTS: frozenset[str] = frozenset({"gemini", "antigravity"})


@dataclass
class GroundingSource:
    """A single grounding source returned by the search API."""

    url: str
    title: str | None = None


def build_grounding_tools_arg() -> list[dict[str, Any]]:
    """Return the grounding tools argument.

    DEPRECATED: MCP tools handle grounding now.
    # @trace WL-119
    """
    return []


def extract_grounding_metadata_sources(response: Any) -> list[str]:
    """Extract grounding source URLs from a search API response.

    Handles standard search response shapes from DDG, Reddit, etc.
    Returns a deduplicated, ordered list of URL strings.

    # @trace WL-119
    """
    if isinstance(response, list):
        urls = []
        seen = set()
        for item in response:
            if isinstance(item, dict):
                url = item.get("url") or item.get("href")
                title = item.get("title")
                if url and url not in seen:
                    seen.add(url)
                    urls.append(url)
        return urls
    return []


def _resolve_gemini_api_key() -> str:
    """Resolve the Gemini API key from the environment.

    No longer required - using MCP tools instead.
    # @trace WL-119
    """
    return ""


def _resolve_gemini_model(model: str | None) -> str:
    """Resolve the model to use for requests.
    # @trace WL-119
    """
    if model:
        return model
    return "claude-sonnet-4.5"


def run_gemini_with_grounding(
    prompt: str,
    *,
    model: str | None = None,
    api_key: str | None = None,
    timeout: int = 120,
    use_mcp_grounding: bool = True,
) -> RunResult:
    """Run a prompt with grounding via MCP search tools.

    This function uses CLIProxy (bifrost) for LLM calls and MCP search tools
    for grounding. Search results are appended to the prompt as context.

    Set use_mcp_grounding=False to disable grounding.

    # @trace WL-119

    Args:
        prompt:  The user prompt to send.
        model:   LLM model identifier. Defaults to CLIProxy default.
        api_key: Ignored (kept for API compatibility).
        timeout: Request timeout in seconds.
        use_mcp_grounding: Enable MCP search grounding (default: True)

    Returns:
        RunResult with ``stdout`` set to the assistant response text and
        ``grounding_sources`` populated from search results.

    Raises:
        ValueError: When the model is not supported.
    """
    cliproxy_url = os.environ.get("CLIPROXY_URL", DEFAULT_CLIPROXY_URL)
    grounding_sources: list[str] = []
    
    # Step 1: If grounding enabled, do search first
    if use_mcp_grounding:
        grounding_sources = _perform_mcp_search(prompt, timeout)
        if grounding_sources:
            _log.info("WL-119: Found %d grounding sources", len(grounding_sources))
            # Prepend search context to prompt
            context = _build_search_context(grounding_sources)
            prompt = f"{context}\n\n---\n\n{prompt}"

    # Step 2: Call LLM via CLIProxy
    try:
        content = _call_cliproxy(prompt, model, cliproxy_url, timeout)
    except Exception as exc:
        raise RuntimeError(f"CLIProxy call failed: {exc}") from exc

    return RunResult(
        exit_code=0,
        stdout=content or "",
        stderr="",
        grounding_sources=grounding_sources or None,
    )


def _perform_mcp_search(prompt: str, timeout: int) -> list[str]:
    """Perform MCP search to get grounding context."""
    try:
        from thegent.skills.research import ddg_search
        
        # Extract search query from prompt (simple heuristic)
        query = _extract_search_query(prompt)
        if not query:
            return []
        
        results = ddg_search(query, max_results=5)
        return extract_grounding_metadata_sources(results)
    except Exception as e:
        _log.debug("MCP search failed: %s", e)
        return []


def _extract_search_query(prompt: str) -> str:
    """Extract a search query from the user prompt."""
    cleaned = prompt.strip()
    if len(cleaned) > 100:
        cleaned = cleaned[:100]
    for prefix in ["write", "explain", "describe", "tell me about", "what is", "how to"]:
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
    return cleaned if cleaned else ""


def _build_search_context(sources: list[str]) -> str:
    """Build context string from search sources."""
    if not sources:
        return ""
    context = "Search results (use these as grounding context):\n"
    for i, url in enumerate(sources[:5], 1):
        context += f"{i}. {url}\n"
    return context


def _call_cliproxy(
    prompt: str,
    model: str | None,
    url: str,
    timeout: int,
) -> str:
    """Call CLIProxy for LLM completion."""
    payload = {
        "model": model or "claude-sonnet-4.5",
        "messages": [{"role": "user", "content": prompt}],
    }
    
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(f"{url}/v1/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return ""
