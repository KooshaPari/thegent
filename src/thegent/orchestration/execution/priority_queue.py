"""Stub module."""

from __future__ import annotations
import heapq


class PriorityQueue:
    """Priority queue for execution tasks."""

    def __init__(self) -> None:
        self._heap: list = []

    def push(self, priority: int, item: dict) -> None:
        heapq.heappush(self._heap, (priority, item))

    def pop(self) -> dict | None:
        if self._heap:
            _, item = heapq.heappop(self._heap)
            return item
        return None


from dataclasses import dataclass, field
from typing import Any


@dataclass
class QueuedRun:
    """A queued execution run."""

    run_id: str
    priority: int = 0
    status: str = "queued"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""

    def __lt__(self, other: "QueuedRun") -> bool:
        """Compare by priority for heap ordering."""
        return self.priority < other.priority


__all__ = ["PriorityQueue", "QueuedRun", "RunPriorityQueue"]


class RunPriorityQueue:
    """Priority queue specifically for execution runs."""

    def __init__(self) -> None:
        self._heap: list = []
        self._items: dict = {}

    def enqueue(self, run: QueuedRun) -> None:
        """Add a run to the queue."""
        import heapq

        heapq.heappush(self._heap, (run.priority, run.run_id))
        self._items[run.run_id] = run

    def dequeue(self) -> QueuedRun | None:
        """Remove and return the highest priority run."""
        import heapq

        if self._heap:
            _, run_id = heapq.heappop(self._heap)
            return self._items.pop(run_id, None)
        return None

    def peek(self) -> QueuedRun | None:
        """View the highest priority run without removing it."""
        if self._heap:
            _, run_id = self._heap[0]
            return self._items.get(run_id)
        return None

    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self._heap) == 0

    def size(self) -> int:
        """Return the number of items in the queue."""
        return len(self._heap)


def make_priority_queue() -> RunPriorityQueue:
    """Create a new priority queue for execution runs.

    Returns:
        A new RunPriorityQueue instance.
    """
    return RunPriorityQueue()


__all__ = ["PriorityQueue", "QueuedRun", "RunPriorityQueue", "make_priority_queue"]
