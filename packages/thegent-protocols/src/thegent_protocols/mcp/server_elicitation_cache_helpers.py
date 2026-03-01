"""Elicitation cache helpers extracted from MCP server (WL-126)."""

from __future__ import annotations

import hashlib
from typing import Any

from cachetools import TTLCache


def create_elicitation_cache(*, maxsize: int = 100, ttl_seconds: int = 300) -> TTLCache[str, Any]:
    """Create a TTL cache for elicitation responses."""
    return TTLCache(maxsize=maxsize, ttl=ttl_seconds)


def elicitation_cache_key(prompt: str, response_type: type) -> str:
    """Generate cache key for elicitation request."""
    key_data = f"{prompt}:{response_type.__name__}"
    return hashlib.sha256(key_data.encode()).hexdigest()[:16]


def get_cached_elicitation(cache: TTLCache[str, Any], *, prompt: str, response_type: type) -> Any | None:
    """Fetch cached elicitation response if available."""
    return cache.get(elicitation_cache_key(prompt, response_type))


def cache_elicitation_response(
    cache: TTLCache[str, Any],
    *,
    prompt: str,
    response_type: type,
    response: Any,
) -> None:
    """Store elicitation response in cache."""
    cache[elicitation_cache_key(prompt, response_type)] = response


__all__ = [
    "cache_elicitation_response",
    "create_elicitation_cache",
    "elicitation_cache_key",
    "get_cached_elicitation",
]
