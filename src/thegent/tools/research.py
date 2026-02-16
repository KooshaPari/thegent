import logging
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
