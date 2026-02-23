"""Execution concurrency control.

Domain: Concurrency
Classes:
- IdempotencyManager: Idempotency checking
- ConcurrencyController: Concurrency control
- LaneController: Lane-based execution
- LoadClassifier: Load classification
"""

import hashlib
import time
from typing import Any


class IdempotencyManager:
    """Manages idempotency for execution operations."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self._cache: dict[str, float] = {}
        self._ttl = ttl_seconds

    def _make_key(self, operation: str, params: dict[str, Any]) -> str:
        """Generate idempotency key."""
        content = f"{operation}:{sorted(params.items())}"
        return hashlib.sha256(content.encode()).hexdigest()

    def is_idempotent(self, operation: str, params: dict[str, Any]) -> bool:
        """Check if operation is idempotent."""
        key = self._make_key(operation, params)
        if key in self._cache:
            age = time.time() - self._cache[key]
            return age < self._ttl
        return True

    def mark_executed(self, operation: str, params: dict[str, Any]) -> None:
        """Mark operation as executed."""
        key = self._make_key(operation, params)
        self._cache[key] = time.time()

    def cleanup(self) -> None:
        """Clean up expired entries."""
        now = time.time()
        self._cache = {k: v for k, v in self._cache.items() if now - v < self._ttl}


class ConcurrencyController:
    """Controls concurrent execution."""

    def __init__(self, max_concurrent: int = 10) -> None:
        self._max = max_concurrent
        self._current = 0
        self._waiting: list[dict[str, Any]] = []

    def acquire(self, operation_id: str) -> bool:
        """Acquire a concurrency slot."""
        if self._current < self._max:
            self._current += 1
            return True
        self._waiting.append({"id": operation_id, "time": time.time()})
        return False

    def release(self, operation_id: str) -> None:
        """Release a concurrency slot."""
        if self._current > 0:
            self._current -= 1
        if self._waiting:
            self._waiting.pop(0)

    def get_stats(self) -> dict[str, Any]:
        """Get concurrency stats."""
        return {
            "current": self._current,
            "max": self._max,
            "waiting": len(self._waiting),
        }


class LaneController:
    """Controls lane-based execution."""

    def __init__(self) -> None:
        self._lanes: dict[str, dict[str, Any]] = {}

    def create_lane(self, name: str, priority: int = 0) -> None:
        """Create a new lane."""
        self._lanes[name] = {
            "priority": priority,
            "queue": [],
            "active": False,
        }

    def add_to_lane(self, lane_name: str, item: dict[str, Any]) -> None:
        """Add item to lane."""
        if lane_name not in self._lanes:
            self.create_lane(lane_name)
        self._lanes[lane_name]["queue"].append(item)

    def get_next(self) -> dict[str, Any] | None:
        """Get next item from highest priority lane."""
        sorted_lanes = sorted(
            self._lanes.items(),
            key=lambda x: x[1].get("priority", 0),
            reverse=True,
        )
        for name, lane in sorted_lanes:
            if lane["queue"]:
                return lane["queue"].pop(0)
        return None


class LoadClassifier:
    """Classifies execution load."""

    def __init__(self) -> None:
        self._thresholds = {
            "low": 10,
            "medium": 50,
            "high": 100,
        }

    def classify(self, active_count: int) -> str:
        """Classify current load."""
        if active_count >= self._thresholds["high"]:
            return "high"
        elif active_count >= self._thresholds["medium"]:
            return "medium"
        return "low"

    def set_thresholds(self, low: int, medium: int, high: int) -> None:
        """Set classification thresholds."""
        self._thresholds = {
            "low": low,
            "medium": medium,
            "high": high,
        }


__all__ = [
    "ConcurrencyController",
    "IdempotencyManager",
    "LaneController",
    "LoadClassifier",
]
