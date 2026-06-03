"""Event queue module for orchestration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any


class SubAgentEventQueue:
    """Queue for sub-agent events."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def enqueue(self, event: dict[str, Any]) -> None:
        """Enqueue an event."""
        self._events.append(event)

    def dequeue(self) -> dict[str, Any] | None:
        """Dequeue an event."""
        if self._events:
            return self._events.pop(0)
        return None

    def peek(self) -> dict[str, Any] | None:
        """Peek at the next event without removing it."""
        if self._events:
            return self._events[0]
        return None

    def size(self) -> int:
        """Get the number of events in the queue."""
        return len(self._events)

    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self._events) == 0


__all__ = [
    "SubAgentEventQueue",
    "get_global_event_queue",
    "get_event_queue",
    "reset_global_event_queue",
]


def reset_global_event_queue() -> None:
    """Reset the global event queue."""
    global _global_event_queue
    _global_event_queue = None


# Global event queue instance
_global_event_queue: SubAgentEventQueue | None = None


def get_global_event_queue() -> SubAgentEventQueue:
    """Get the global event queue instance."""
    global _global_event_queue
    if _global_event_queue is None:
        _global_event_queue = SubAgentEventQueue()
    return _global_event_queue


def get_event_queue() -> SubAgentEventQueue:
    """Get an event queue instance (alias for get_global_event_queue)."""
    return get_global_event_queue()
