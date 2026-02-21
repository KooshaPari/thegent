"""SubAgentEventQueue: asyncio.Queue wrapper for SubAgentEvent streaming.

Provides a process-global event queue that SubAgentDispatcher publishes to
and the thegent_orchestration_events MCP tool drains from. Also used by
UnifiedWorkerDaemon to subscribe and consume events in the background.

# @trace WL-085
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator

from thegent.orchestration.protocol import SubAgentEvent  # noqa: TC001 -- used at runtime in asyncio.Queue[SubAgentEvent] generic and return annotations

_log = logging.getLogger(__name__)

# Maximum events held in-flight before put_nowait raises QueueFull.
# Sized to handle bursts; callers MUST drain promptly or they will see errors.
_DEFAULT_MAXSIZE: int = 1024


class SubAgentEventQueue:
    """Thread-safe asyncio.Queue wrapper for SubAgentEvent streaming.

    A single instance is intended to be shared across the process as
    the canonical event sink for SubAgentDispatcher.

    Usage::

        queue = SubAgentEventQueue()
        queue.put(event)          # Called by SubAgentDispatcher (sync-safe)
        async for event in queue.stream(timeout=5.0):
            print(event)

    # @trace WL-085
    """

    def __init__(self, maxsize: int = _DEFAULT_MAXSIZE) -> None:
        self._queue: asyncio.Queue[SubAgentEvent] = asyncio.Queue(maxsize=maxsize)
        self._maxsize = maxsize

    # ------------------------------------------------------------------
    # Producer API (called from SubAgentDispatcher)
    # ------------------------------------------------------------------

    def put(self, event: SubAgentEvent) -> None:
        """Enqueue *event* without blocking.

        Raises:
            asyncio.QueueFull: If the queue has reached its maxsize.

        # @trace WL-085
        """
        self._queue.put_nowait(event)
        _log.debug(
            "event_queue.put event_type=%s request_id=%s qsize=%d",
            event.event_type,
            event.request_id,
            self._queue.qsize(),
        )

    # ------------------------------------------------------------------
    # Consumer API
    # ------------------------------------------------------------------

    async def get(self) -> SubAgentEvent:
        """Await and return the next event from the queue.

        # @trace WL-085
        """
        return await self._queue.get()

    def get_nowait(self) -> SubAgentEvent:
        """Return the next event without blocking.

        Raises:
            asyncio.QueueEmpty: If the queue is empty.

        # @trace WL-085
        """
        return self._queue.get_nowait()

    def drain_nowait(self) -> list[SubAgentEvent]:
        """Return all events currently in the queue without blocking.

        # @trace WL-085
        """
        events: list[SubAgentEvent] = []
        while not self._queue.empty():
            events.append(self._queue.get_nowait())
        return events

    async def stream(self, timeout: float = 30.0) -> AsyncIterator[SubAgentEvent]:
        """Async-iterate over events, yielding each as it arrives.

        Stops after *timeout* seconds of inactivity (no new event).

        Args:
            timeout: Seconds to wait for the next event before stopping.

        Yields:
            SubAgentEvent objects in FIFO order.

        # @trace WL-085
        """
        while True:
            event = await asyncio.wait_for(self._queue.get(), timeout=timeout)
            yield event

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def qsize(self) -> int:
        """Return the current number of events in the queue."""
        return self._queue.qsize()

    @property
    def maxsize(self) -> int:
        """Return the maximum queue capacity."""
        return self._maxsize

    @property
    def empty(self) -> bool:
        """Return True if the queue currently holds no events."""
        return self._queue.empty()


# ---------------------------------------------------------------------------
# Process-global singleton
# ---------------------------------------------------------------------------

_global_queue: SubAgentEventQueue | None = None


def get_global_event_queue() -> SubAgentEventQueue:
    """Return the process-global SubAgentEventQueue, creating it on first call.

    The singleton is intentionally lazy so that tests can construct their own
    instances without side-effects from module import order.

    # @trace WL-085
    """
    global _global_queue  # noqa: PLW0603 -- intentional module-level singleton
    if _global_queue is None:
        _global_queue = SubAgentEventQueue()
    return _global_queue


def reset_global_event_queue() -> None:
    """Replace the process-global queue with a fresh instance.

    Intended for use in tests only. Raises RuntimeError in production-like
    contexts where the guard is enforced by callers.

    # @trace WL-085
    """
    global _global_queue  # noqa: PLW0603 -- intentional module-level singleton
    _global_queue = SubAgentEventQueue()


__all__ = [
    "SubAgentEventQueue",
    "get_global_event_queue",
    "reset_global_event_queue",
]
