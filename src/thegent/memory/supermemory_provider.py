"""SupermemoryProvider: cloud persistence for ContinuityPackets (L3/L4).

Wraps SupermemoryClient to store and retrieve ContinuityPackets by
session_id using the Supermemory.ai API.

No fallbacks — if the API is unavailable, raises SupermemoryUnavailableError.

Config:
    THGENT_SUPERMEMORY_API_KEY  - Required. API key.
    THGENT_SUPERMEMORY_BASE_URL - Optional. Defaults to https://api.supermemory.ai/v3.

# @trace FR-HAX-004
"""

from __future__ import annotations

import orjson as json
import logging

from thegent.execution import ContinuityPacket
from thegent.memory.supermemory_client import SupermemoryClient, SupermemoryConfigError

logger = logging.getLogger(__name__)

_TAG_PREFIX = "continuity_packet"


class SupermemoryUnavailableError(Exception):
    """Raised when the Supermemory API is not reachable or not configured."""


class SupermemoryProvider:
    """Cloud persistence provider for ContinuityPackets.

    Uses SupermemoryClient to POST (store) and GET (retrieve) continuity
    packets associated with a session_id.

    Raises SupermemoryUnavailableError if the API key is not configured
    or the API is unreachable — no silent fallbacks.

    Example::

        provider = SupermemoryProvider()
        memory_id = await provider.store(packet)
        recovered = await provider.retrieve(session_id)
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialise the provider.

        Args:
            api_key: Supermemory API key. Falls back to THGENT_SUPERMEMORY_API_KEY.
            base_url: Optional base URL override.

        Raises:
            SupermemoryUnavailableError: If no API key is available.
        """
        try:
            self._client = SupermemoryClient(api_key=api_key, base_url=base_url)
        except SupermemoryConfigError as exc:
            raise SupermemoryUnavailableError(
                f"Supermemory API key is required for SupermemoryProvider: {exc}"
            ) from exc

        logger.debug("SupermemoryProvider initialised")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _packet_tag(session_id: str) -> str:
        """Build the tag used to identify a packet for a given session."""
        return f"{_TAG_PREFIX}:{session_id}"

    @staticmethod
    def _serialise(packet: ContinuityPacket) -> str:
        """Serialise a ContinuityPacket to a JSON string for storage."""
        return packet.model_dump_json()

    @staticmethod
    def _deserialise(content: str) -> ContinuityPacket:
        """Deserialise a JSON string back to a ContinuityPacket.

        Raises:
            ValueError: If the content cannot be parsed as a ContinuityPacket.
        """
        data = json.loads(content)
        return ContinuityPacket(**data)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def store(self, packet: ContinuityPacket) -> str:
        """Persist a ContinuityPacket to the Supermemory API.

        Args:
            packet: The continuity packet to store.

        Returns:
            The memory ID assigned by the Supermemory API.

        Raises:
            SupermemoryUnavailableError: On API connectivity failures.
            SupermemoryAPIError: On non-retryable API errors.
        """
        content = self._serialise(packet)
        tags = [_TAG_PREFIX]
        if packet.session_id:
            tags.append(self._packet_tag(packet.session_id))

        try:
            memory_id = await self._client.add(content, tags=tags)
        except Exception as exc:
            raise SupermemoryUnavailableError(
                f"Failed to store ContinuityPacket (session={packet.session_id!r}): {exc}"
            ) from exc

        logger.info(
            "SupermemoryProvider.store: packet stored (session=%r, memory_id=%r)",
            packet.session_id,
            memory_id,
        )
        return memory_id

    async def retrieve(self, session_id: str) -> ContinuityPacket | None:
        """Retrieve the most recent ContinuityPacket for a session.

        Searches for memories tagged with the session-specific tag and
        returns the most recently created packet, or None if none exist.

        Args:
            session_id: The session ID to look up.

        Returns:
            The most recent ContinuityPacket for the session, or None.

        Raises:
            SupermemoryUnavailableError: On API connectivity failures.
            SupermemoryAPIError: On non-retryable API errors.
        """
        tag = self._packet_tag(session_id)

        try:
            entries = await self._client.search(tag, limit=5)
        except Exception as exc:
            raise SupermemoryUnavailableError(
                f"Failed to retrieve ContinuityPacket (session={session_id!r}): {exc}"
            ) from exc

        # Filter to entries that match the session tag exactly and parse them
        for entry in entries:
            if tag not in (entry.tags or []):
                continue
            try:
                packet = self._deserialise(entry.content)
                logger.info(
                    "SupermemoryProvider.retrieve: found packet (session=%r, memory_id=%r)",
                    session_id,
                    entry.id,
                )
                return packet
            except (ValueError, KeyError, TypeError) as parse_err:
                logger.warning(
                    "SupermemoryProvider.retrieve: could not parse entry id=%r: %s",
                    entry.id,
                    parse_err,
                )
                continue

        logger.debug("SupermemoryProvider.retrieve: no packet found for session=%r", session_id)
        return None
