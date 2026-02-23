"""Thread-safe resource pool for agent orchestration.

FR-ORCH-001: ResourcePool must serialise concurrent allocate() calls so that
capacity is never over-committed.
"""

from __future__ import annotations

import threading


class ResourceAllocationError(Exception):
    """Raised when a resource allocation request cannot be satisfied."""


class ResourcePool:
    """Thread-safe capacity pool for agent resource allocation.

    A single unit of capacity may be claimed by exactly one caller.
    Concurrent ``allocate`` calls beyond capacity raise
    :class:`ResourceAllocationError`.

    Args:
        capacity: Total allocatable units.
    """

    def __init__(self, capacity: int) -> None:
        if capacity < 0:
            raise ValueError(f"capacity must be >= 0, got {capacity}")
        self._capacity = capacity
        self._allocated: int = 0
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def allocate(self, agent_id: str, amount: int = 1) -> dict[str, object]:
        """Allocate *amount* units for *agent_id*.

        Args:
            agent_id: Identifier of the requesting agent.
            amount:   Units to allocate (default 1).

        Returns:
            A dict with ``agent_id`` and ``amount`` on success.

        Raises:
            ResourceAllocationError: When insufficient capacity remains.
        """
        with self._lock:
            if self._allocated + amount > self._capacity:
                raise ResourceAllocationError(
                    f"Insufficient capacity: requested {amount}, "
                    f"available {self._capacity - self._allocated}"
                )
            self._allocated += amount
            return {"agent_id": agent_id, "amount": amount}

    def release(self, amount: int = 1) -> None:
        """Release *amount* previously allocated units back to the pool.

        Args:
            amount: Units to return (default 1).
        """
        with self._lock:
            self._allocated = max(0, self._allocated - amount)

    @property
    def available(self) -> int:
        """Return the number of currently available units."""
        with self._lock:
            return self._capacity - self._allocated

    @property
    def capacity(self) -> int:
        """Total pool capacity."""
        return self._capacity
