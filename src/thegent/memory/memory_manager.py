"""MemoryManager: wraps SupermemoryClient for agent lifecycle integration (L3 layer).

Provides a safe, optional facade over SupermemoryClient.  When
THGENT_SUPERMEMORY_API_KEY is absent the manager operates in no-op mode:
every method returns an empty result without raising.

# @trace FR-MEM-002
"""

from __future__ import annotations

import logging
import os

from .supermemory_client import SupermemoryClient, SupermemoryConfigError

logger = logging.getLogger(__name__)

_CONTEXT_SEARCH_LIMIT = 10
_SESSION_SEARCH_LIMIT = 5


class MemoryManager:
    """Facade over SupermemoryClient for agent lifecycle integration.

    Instantiate once per process; it is safe to share across coroutines.
    All public methods are ``async`` and silently no-op when the API key
    is not configured.

    Example::

        mgr = MemoryManager()
        context = await mgr.load_context("claude")
        # ... run agent ...
        await mgr.save_discovery("claude", "Discovered that X causes Y")

    Args:
        api_key: Supermemory API key.  Falls back to
            ``THGENT_SUPERMEMORY_API_KEY`` environment variable.  When
            neither is set the manager operates in no-op mode.
        base_url: Optional base URL override forwarded to
            :class:`~thegent.memory.supermemory_client.SupermemoryClient`.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        from thegent.config import ThegentSettings

        settings = ThegentSettings()
        resolved_key = api_key or settings.supermemory_api_key or ""
        self._enabled = bool(resolved_key)
        self._client: SupermemoryClient | None = None

        if self._enabled:
            try:
                self._client = SupermemoryClient(
                    api_key=resolved_key or None,
                    base_url=base_url,
                )
                logger.debug("MemoryManager: SupermemoryClient initialised (L3 enabled)")
            except SupermemoryConfigError:
                # Key was present but invalid — degrade gracefully.
                self._enabled = False
                logger.warning("MemoryManager: SupermemoryClient config error; running in no-op mode")
        else:
            logger.debug("MemoryManager: THGENT_SUPERMEMORY_API_KEY not set; no-op mode active")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """True when the Supermemory API key is configured."""
        return self._enabled

    async def load_context(self, agent_id: str) -> list[str]:
        """Search for memories relevant to *agent_id* and return their text.

        Uses the agent identifier as the search query so that past
        discoveries tagged for the same agent surface first.

        Args:
            agent_id: The agent name / identifier (e.g. ``"claude"``).

        Returns:
            List of memory content strings ordered by relevance.
            Returns an empty list when memory is disabled or the search
            fails.
        """
        if not self._enabled or self._client is None:
            return []

        try:
            entries = await self._client.search(agent_id, limit=_CONTEXT_SEARCH_LIMIT)
            contents = [e.content for e in entries]
            logger.debug(
                "MemoryManager.load_context: %d entries for agent=%r",
                len(contents),
                agent_id,
            )
            return contents
        except Exception as exc:
            logger.warning("MemoryManager.load_context failed (agent=%r): %s", agent_id, exc)
            return []

    async def save_discovery(self, agent_id: str, content: str) -> None:
        """Store a discovery as a memory entry tagged with *agent_id*.

        Args:
            agent_id: The agent name / identifier used as a tag so the
                memory can be retrieved via :meth:`load_context`.
            content: Textual content to persist (e.g. a result summary).

        Returns:
            None.  Failures are logged and swallowed so callers are not
            impacted by optional memory persistence.
        """
        if not self._enabled or self._client is None:
            return

        if not content or not content.strip():
            logger.debug(
                "MemoryManager.save_discovery: empty content for agent=%r; skipping",
                agent_id,
            )
            return

        try:
            memory_id = await self._client.add(content, tags=[agent_id])
            logger.debug(
                "MemoryManager.save_discovery: stored id=%r for agent=%r",
                memory_id,
                agent_id,
            )
        except Exception as exc:
            logger.warning("MemoryManager.save_discovery failed (agent=%r): %s", agent_id, exc)

    async def get_session_context(self, session_id: str) -> str:
        """Retrieve a summary of memories associated with *session_id*.

        Searches for memories tagged with the session identifier and
        concatenates the results into a single string separated by
        newlines.

        Args:
            session_id: The session identifier to look up.

        Returns:
            Concatenated memory text, or an empty string when memory is
            disabled or no memories exist for the session.
        """
        if not self._enabled or self._client is None:
            return ""

        try:
            entries = await self._client.search(session_id, limit=_SESSION_SEARCH_LIMIT)
            if not entries:
                return ""
            summary = "\n".join(e.content for e in entries)
            logger.debug(
                "MemoryManager.get_session_context: %d entries for session=%r",
                len(entries),
                session_id,
            )
            return summary
        except Exception as exc:
            logger.warning(
                "MemoryManager.get_session_context failed (session=%r): %s",
                session_id,
                exc,
            )
            return ""
