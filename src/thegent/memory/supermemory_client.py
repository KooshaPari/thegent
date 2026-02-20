"""Supermemory.ai client for persistent agent memory (L3 layer).

Provides async CRUD operations and semantic search over the Supermemory REST API.
Uses httpx for HTTP, tenacity for retry on transient errors (429/503).

Config:
    THGENT_SUPERMEMORY_API_KEY  - Required. API key (x-sm-api-key header).
    THGENT_SUPERMEMORY_BASE_URL - Optional. Defaults to https://api.supermemory.ai/v3.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "https://api.supermemory.ai/v3"
_MAX_RETRY_ATTEMPTS = 4
_RETRY_MIN_WAIT = 1
_RETRY_MAX_WAIT = 30


class SupermemoryConfigError(Exception):
    """Raised when SupermemoryClient is misconfigured (e.g. missing API key)."""


class SupermemoryAPIError(Exception):
    """Raised on unrecoverable API errors (4xx excluding 429, 5xx excluding 503)."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(f"Supermemory API error {status_code}: {message}")
        self.status_code = status_code


@dataclass
class MemoryEntry:
    """A single memory entry returned by the Supermemory API.

    Attributes:
        id: Unique identifier assigned by the API.
        content: Text content of the memory.
        tags: List of tags associated with this entry.
        created_at: ISO-8601 timestamp when the entry was created.
        score: Relevance score (only present on search results).
    """

    id: str
    content: str
    tags: list[str] = field(default_factory=list)
    created_at: str = ""
    score: float | None = None

    @classmethod
    def from_api_dict(cls, data: dict[str, Any]) -> MemoryEntry:
        """Construct a MemoryEntry from a raw API response dict."""
        return cls(
            id=data.get("id", ""),
            content=data.get("content", ""),
            tags=data.get("tags") or [],
            created_at=data.get("created_at", ""),
            score=data.get("score"),
        )


def _is_retryable(exc: BaseException) -> bool:
    """Return True for transient errors that should be retried (429, 503)."""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 503)
    if isinstance(exc, (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError)):
        return True
    return False


class SupermemoryClient:
    """Async client for the Supermemory.ai REST API.

    Raises SupermemoryConfigError immediately on construction if the API key
    is not provided (either via parameter or THGENT_SUPERMEMORY_API_KEY env var).

    Uses httpx.AsyncClient and tenacity for retry on 429/503.

    Example::

        client = SupermemoryClient(api_key="sm_...")
        memory_id = await client.add("Agent found X while processing Y", tags=["discovery"])
        results = await client.search("X processing", limit=5)
        await client.delete(memory_id)
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialise the client.

        Args:
            api_key: Supermemory API key. Falls back to THGENT_SUPERMEMORY_API_KEY.
            base_url: Override the API base URL. Falls back to THGENT_SUPERMEMORY_BASE_URL
                      or https://api.supermemory.ai/v3.

        Raises:
            SupermemoryConfigError: If no API key is available.
        """
        from thegent.config import ThegentSettings

        settings = ThegentSettings()
        resolved_key = api_key or settings.supermemory_api_key or ""
        if not resolved_key:
            raise SupermemoryConfigError(
                "Supermemory API key is required. Set THGENT_SUPERMEMORY_API_KEY or pass api_key= to SupermemoryClient."
            )

        resolved_url = (base_url or settings.supermemory_base_url or _DEFAULT_BASE_URL).rstrip("/")

        self._base_url = resolved_url
        self._headers = {
            "x-sm-api-key": resolved_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        logger.debug("SupermemoryClient initialised (base_url=%s)", self._base_url)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _make_client(self) -> httpx.AsyncClient:
        """Create a configured AsyncClient instance."""
        return httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._headers,
            timeout=httpx.Timeout(30.0),
        )

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        """Raise appropriate exceptions for error responses.

        Retryable errors (429, 503) raise httpx.HTTPStatusError so tenacity
        can catch them. All other non-2xx responses raise SupermemoryAPIError.
        """
        if response.is_success:
            return
        if response.status_code in (429, 503):
            # Let tenacity see this as retryable
            response.raise_for_status()
        try:
            detail = response.json().get("message", response.text)
        except Exception:
            detail = response.text
        raise SupermemoryAPIError(response.status_code, detail)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def add(self, content: str, tags: list[str] | None = None) -> str:
        """Store a new memory entry.

        Args:
            content: Text content to store.
            tags: Optional list of tags for categorisation.

        Returns:
            The memory ID assigned by the API.

        Raises:
            SupermemoryAPIError: On non-retryable API errors.
            httpx.HTTPStatusError: On 429/503 after all retries exhausted.
        """
        payload: dict[str, Any] = {"content": content}
        if tags:
            payload["tags"] = tags

        @retry(
            retry=retry_if_exception(_is_retryable),
            wait=wait_random_exponential(min=_RETRY_MIN_WAIT, max=_RETRY_MAX_WAIT),
            stop=stop_after_attempt(_MAX_RETRY_ATTEMPTS),
            reraise=True,
        )
        async def _do_add() -> str:
            async with self._make_client() as client:
                response = await client.post("/memories", json=payload)
                self._raise_for_status(response)
                data = response.json()
                memory_id: str = data.get("id", "")
                logger.debug("Memory added (id=%s)", memory_id)
                return memory_id

        return await _do_add()

    async def search(self, query: str, limit: int = 10) -> list[MemoryEntry]:
        """Semantic search over stored memories.

        Args:
            query: Search query string.
            limit: Maximum number of results to return (default 10).

        Returns:
            List of MemoryEntry objects ordered by relevance.

        Raises:
            SupermemoryAPIError: On non-retryable API errors.
            httpx.HTTPStatusError: On 429/503 after all retries exhausted.
        """

        @retry(
            retry=retry_if_exception(_is_retryable),
            wait=wait_random_exponential(min=_RETRY_MIN_WAIT, max=_RETRY_MAX_WAIT),
            stop=stop_after_attempt(_MAX_RETRY_ATTEMPTS),
            reraise=True,
        )
        async def _do_search() -> list[MemoryEntry]:
            async with self._make_client() as client:
                response = await client.get(
                    "/memories/search",
                    params={"q": query, "limit": limit},
                )
                self._raise_for_status(response)
                data = response.json()
                results = data if isinstance(data, list) else data.get("results", [])
                entries = [MemoryEntry.from_api_dict(item) for item in results]
                logger.debug("Search returned %d results (query=%r)", len(entries), query)
                return entries

        return await _do_search()

    async def delete(self, memory_id: str) -> None:
        """Delete a memory entry by ID.

        Args:
            memory_id: The ID of the memory entry to delete.

        Raises:
            SupermemoryAPIError: On non-retryable API errors.
            httpx.HTTPStatusError: On 429/503 after all retries exhausted.
        """

        @retry(
            retry=retry_if_exception(_is_retryable),
            wait=wait_random_exponential(min=_RETRY_MIN_WAIT, max=_RETRY_MAX_WAIT),
            stop=stop_after_attempt(_MAX_RETRY_ATTEMPTS),
            reraise=True,
        )
        async def _do_delete() -> None:
            async with self._make_client() as client:
                response = await client.delete(f"/memories/{memory_id}")
                self._raise_for_status(response)
                logger.debug("Memory deleted (id=%s)", memory_id)

        await _do_delete()

    async def list(self, tags: list[str] | None = None) -> list[MemoryEntry]:
        """List stored memory entries, optionally filtered by tags.

        Args:
            tags: If provided, only return entries matching ALL given tags.

        Returns:
            List of MemoryEntry objects.

        Raises:
            SupermemoryAPIError: On non-retryable API errors.
            httpx.HTTPStatusError: On 429/503 after all retries exhausted.
        """
        params: dict[str, Any] = {}
        if tags:
            # API accepts repeated tag params or comma-separated; use comma-separated
            params["tags"] = ",".join(tags)

        @retry(
            retry=retry_if_exception(_is_retryable),
            wait=wait_random_exponential(min=_RETRY_MIN_WAIT, max=_RETRY_MAX_WAIT),
            stop=stop_after_attempt(_MAX_RETRY_ATTEMPTS),
            reraise=True,
        )
        async def _do_list() -> list[MemoryEntry]:
            async with self._make_client() as client:
                response = await client.get("/memories", params=params)
                self._raise_for_status(response)
                data = response.json()
                items = data if isinstance(data, list) else data.get("memories", [])
                entries = [MemoryEntry.from_api_dict(item) for item in items]
                logger.debug("List returned %d entries", len(entries))
                return entries

        return await _do_list()
