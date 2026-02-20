"""Priority queue for thegent swarm run scheduling.

Implements a thread-safe priority queue that orders run items by lane priority,
supporting FIFO within the same priority level. Integrates with the existing
lanes.py lane model.

WP-1002, FR-019: Respects lane priorities from LaneModel (critical=0, standard=10,
recovery=20, background=100). Lower priority_score = dispatched first.
"""

from __future__ import annotations

import heapq
import itertools
import threading
import time
from dataclasses import dataclass, field
from queue import Empty, Full
from typing import Any

from thegent.orchestration.execution.lanes import LaneModel

__all__ = [
    "QueuedRun",
    "RunPriorityQueue",
    "make_priority_queue",
]


@dataclass
class QueuedRun:
    """A run item waiting in the priority queue.

    Attributes:
        run_id: Unique identifier for this run.
        lane: Execution lane name (e.g. "critical", "standard", "background").
        priority_score: Scheduling priority; lower value = dispatched first.
        enqueued_at: Monotonic timestamp when the run was enqueued.
        metadata: Arbitrary caller-supplied key/value pairs.
    """

    run_id: str
    lane: str
    priority_score: int
    enqueued_at: float = field(default_factory=time.monotonic)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_lane(
        cls,
        run_id: str,
        lane_name: str,
        metadata: dict[str, Any] | None = None,
    ) -> QueuedRun:
        """Create a QueuedRun with priority_score derived from the lane model.

        Uses ``LaneModel.get_priority`` so the score matches the canonical lane
        ordering defined in ``lanes.py``.

        Args:
            run_id: Unique identifier for this run.
            lane_name: One of "critical", "standard", "recovery", "background",
                or any lane name understood by LaneModel.
            metadata: Optional caller-supplied key/value pairs.

        Returns:
            A ``QueuedRun`` with ``priority_score`` set from the lane model.
        """
        return cls(
            run_id=run_id,
            lane=lane_name,
            priority_score=LaneModel.get_priority(lane_name),
            metadata=metadata or {},
        )


class RunPriorityQueue:
    """Thread-safe priority queue for swarm run scheduling.

    Runs are ordered by ``priority_score`` ascending (lower score = dispatched
    first). Within the same score, FIFO order is preserved via an internal
    sequence counter.

    The interface mirrors ``queue.PriorityQueue`` / ``queue.Queue`` so callers
    can swap without restructuring code.

    Args:
        maxsize: Maximum number of items the queue may hold.  ``0`` means
            unbounded (default).
    """

    def __init__(self, *, maxsize: int = 0) -> None:
        self._maxsize = maxsize
        self._heap: list[tuple[int, int, QueuedRun]] = []
        self._counter = itertools.count()
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        self._not_full = threading.Condition(self._lock)

    # ------------------------------------------------------------------
    # Core enqueue / dequeue
    # ------------------------------------------------------------------

    def put(
        self,
        run: QueuedRun,
        block: bool = True,
        timeout: float | None = None,
    ) -> None:
        """Enqueue *run*, blocking if the queue is full and ``block=True``.

        Args:
            run: The run item to enqueue.
            block: If ``True`` (default), block until space is available.
            timeout: Maximum seconds to wait when ``block=True`` and the queue
                is full.  ``None`` means wait indefinitely.

        Raises:
            Full: If ``block=False`` (or timeout expires) and the queue is full.
        """
        with self._not_full:
            if self._maxsize > 0:
                if not block:
                    if len(self._heap) >= self._maxsize:
                        raise Full
                elif timeout is None:
                    while len(self._heap) >= self._maxsize:
                        self._not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    deadline = time.monotonic() + timeout
                    while len(self._heap) >= self._maxsize:
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            raise Full
                        self._not_full.wait(remaining)
            seq = next(self._counter)
            heapq.heappush(self._heap, (run.priority_score, seq, run))
            self._not_empty.notify()

    def put_nowait(self, run: QueuedRun) -> None:
        """Enqueue *run* without blocking.

        Raises:
            Full: If the queue is full (only when ``maxsize > 0``).
        """
        return self.put(run, block=False)

    def get(
        self,
        block: bool = True,
        timeout: float | None = None,
    ) -> QueuedRun:
        """Dequeue and return the highest-priority run (lowest score).

        Within the same ``priority_score``, items are returned in FIFO order.

        Args:
            block: If ``True`` (default), block until an item is available.
            timeout: Maximum seconds to wait when ``block=True`` and the queue
                is empty.  ``None`` means wait indefinitely.

        Returns:
            The next ``QueuedRun`` in priority order.

        Raises:
            Empty: If ``block=False`` (or timeout expires) and the queue is
                empty.
        """
        with self._not_empty:
            if not block:
                if not self._heap:
                    raise Empty
            elif timeout is None:
                while not self._heap:
                    self._not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                deadline = time.monotonic() + timeout
                while not self._heap:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise Empty
                    self._not_empty.wait(remaining)
            _, _, run = heapq.heappop(self._heap)
            self._not_full.notify()
            return run

    def get_nowait(self) -> QueuedRun:
        """Dequeue and return the highest-priority run without blocking.

        Raises:
            Empty: If the queue is empty.
        """
        return self.get(block=False)

    # ------------------------------------------------------------------
    # Inspection helpers
    # ------------------------------------------------------------------

    def qsize(self) -> int:
        """Return the approximate number of items in the queue."""
        with self._lock:
            return len(self._heap)

    def empty(self) -> bool:
        """Return ``True`` if the queue is empty."""
        with self._lock:
            return not self._heap

    def full(self) -> bool:
        """Return ``True`` if the queue is at ``maxsize``.

        Always returns ``False`` when ``maxsize`` is ``0`` (unbounded).
        """
        with self._lock:
            if self._maxsize <= 0:
                return False
            return len(self._heap) >= self._maxsize

    def peek(self) -> QueuedRun | None:
        """Return the next item without removing it, or ``None`` if empty."""
        with self._lock:
            if not self._heap:
                return None
            _, _, run = self._heap[0]
            return run

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def cancel(self, run_id: str) -> bool:
        """Remove the run with *run_id* from the queue.

        Because the underlying data structure is a heap, this requires a linear
        scan followed by a heap rebuild (O(n)).  Use sparingly on hot paths.

        Args:
            run_id: The ``run_id`` of the ``QueuedRun`` to remove.

        Returns:
            ``True`` if a matching run was found and removed, ``False``
            otherwise.
        """
        with self._lock:
            for i, (_, _, run) in enumerate(self._heap):
                if run.run_id == run_id:
                    # Swap with last element and re-heapify (O(n))
                    self._heap[i] = self._heap[-1]
                    self._heap.pop()
                    heapq.heapify(self._heap)
                    self._not_full.notify()
                    return True
            return False

    def drain(self) -> list[QueuedRun]:
        """Remove and return all items in priority order.

        Returns:
            A list of all ``QueuedRun`` items sorted by priority (lowest score
            first), with FIFO ordering within the same score.
        """
        with self._lock:
            result: list[QueuedRun] = []
            while self._heap:
                _, _, run = heapq.heappop(self._heap)
                result.append(run)
            self._not_full.notify_all()
            return result


def make_priority_queue(maxsize: int = 0) -> RunPriorityQueue:
    """Factory function for ``RunPriorityQueue``.

    Args:
        maxsize: Maximum queue capacity.  ``0`` means unbounded.

    Returns:
        A new ``RunPriorityQueue`` instance.
    """
    return RunPriorityQueue(maxsize=maxsize)
