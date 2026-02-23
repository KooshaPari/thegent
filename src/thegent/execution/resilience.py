"""Execution resilience and recovery mechanisms.

Domain: Resilience
Classes:
- DLQManager: Dead letter queue management
- DeferralQueue: Task deferral handling
- CircuitBreakerRegistry: Circuit breaker pattern
- EscalationQueue: Escalation handling
- ContinuityWatchdog: Continuity monitoring
- InterruptionTracker: Interruption tracking
- FreshnessValidator: Freshness validation
- HandoffManager: Agent handoff
- ReplayManager: Replay functionality
"""

from datetime import datetime
from typing import Any


class DLQManager:
    """Dead letter queue manager for failed executions."""

    def __init__(self) -> None:
        self._queue: list[dict[str, Any]] = []

    def add(self, item: dict[str, Any]) -> None:
        """Add item to DLQ."""
        item["timestamp"] = datetime.now().isoformat()
        self._queue.append(item)

    def get_all(self) -> list[dict[str, Any]]:
        """Get all DLQ items."""
        return self._queue.copy()

    def retry(self, item_id: str) -> dict[str, Any] | None:
        """Retry a DLQ item."""
        for item in self._queue:
            if item.get("id") == item_id:
                self._queue.remove(item)
                return item
        return None


class DeferralQueue:
    """Queue for deferred tasks."""

    def __init__(self) -> None:
        self._queue: list[dict[str, Any]] = []

    def defer(self, item: dict[str, Any], delay_seconds: int) -> None:
        """Defer an item for later processing."""
        item["defer_until"] = datetime.now().timestamp() + delay_seconds
        self._queue.append(item)

    def get_ready(self) -> list[dict[str, Any]]:
        """Get items ready for processing."""
        now = datetime.now().timestamp()
        ready = [item for item in self._queue if item.get("defer_until", 0) <= now]
        for item in ready:
            self._queue.remove(item)
        return ready


class CircuitBreakerRegistry:
    """Circuit breaker pattern implementation."""

    def __init__(self, failure_threshold: int = 5) -> None:
        self._breakers: dict[str, dict[str, Any]] = {}
        self._failure_threshold = failure_threshold

    def register(self, name: str) -> None:
        """Register a new circuit breaker."""
        self._breakers[name] = {
            "failures": 0,
            "state": "closed",
            "last_failure": None,
        }

    def record_failure(self, name: str) -> None:
        """Record a failure."""
        if name not in self._breakers:
            self.register(name)
        self._breakers[name]["failures"] += 1
        self._breakers[name]["last_failure"] = datetime.now().isoformat()
        if self._breakers[name]["failures"] >= self._failure_threshold:
            self._breakers[name]["state"] = "open"

    def is_open(self, name: str) -> bool:
        """Check if circuit is open."""
        return self._breakers.get(name, {}).get("state") == "open"


class EscalationQueue:
    """Queue for escalated items."""

    def __init__(self) -> None:
        self._queue: list[dict[str, Any]] = []

    def escalate(self, item: dict[str, Any], priority: int = 0) -> None:
        """Escalate an item."""
        item["priority"] = priority
        item["escalated_at"] = datetime.now().isoformat()
        self._queue.append(item)
        self._queue.sort(key=lambda x: x.get("priority", 0), reverse=True)

    def get_next(self) -> dict[str, Any] | None:
        """Get next escalated item."""
        return self._queue[0] if self._queue else None


class ContinuityWatchdog:
    """Monitors execution continuity."""

    def __init__(self, timeout_seconds: int = 300) -> None:
        self._timeout = timeout_seconds
        self._last_check: datetime | None = None

    def check(self) -> bool:
        """Check if continuity is maintained."""
        self._last_check = datetime.now()
        return True

    def is_healthy(self) -> bool:
        """Check watchdog health."""
        if self._last_check is None:
            return True
        elapsed = (datetime.now() - self._last_check).total_seconds()
        return elapsed < self._timeout


class InterruptionTracker:
    """Tracks execution interruptions."""

    def __init__(self) -> None:
        self._interruptions: list[dict[str, Any]] = []

    def track(self, run_id: str, reason: str) -> None:
        """Track an interruption."""
        self._interruptions.append({
            "run_id": run_id,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        })

    def get_interruptions(self, run_id: str) -> list[dict[str, Any]]:
        """Get interruptions for a run."""
        return [i for i in self._interruptions if i["run_id"] == run_id]


class FreshnessValidator:
    """Validates data freshness."""

    def __init__(self, max_age_seconds: int = 3600) -> None:
        self._max_age = max_age_seconds

    def is_fresh(self, timestamp: str) -> bool:
        """Check if timestamp is fresh."""
        try:
            ts = datetime.fromisoformat(timestamp)
            elapsed = (datetime.now() - ts).total_seconds()
            return elapsed < self._max_age
        except (ValueError, TypeError):
            return False


class HandoffManager:
    """Manages agent handoffs."""

    def __init__(self) -> None:
        self._handoffs: list[dict[str, Any]] = []

    def handoff(self, from_agent: str, to_agent: str, context: dict) -> None:
        """Perform agent handoff."""
        self._handoffs.append({
            "from_agent": from_agent,
            "to_agent": to_agent,
            "context": context,
            "timestamp": datetime.now().isoformat(),
        })

    def get_history(self) -> list[dict[str, Any]]:
        """Get handoff history."""
        return self._handoffs.copy()


class ReplayManager:
    """Manages execution replays."""

    def __init__(self) -> None:
        self._snapshots: dict[str, list[dict[str, Any]]] = {}

    def save_snapshot(self, run_id: str, snapshot: dict[str, Any]) -> None:
        """Save a replay snapshot."""
        if run_id not in self._snapshots:
            self._snapshots[run_id] = []
        self._snapshots[run_id].append(snapshot)

    def get_snapshots(self, run_id: str) -> list[dict[str, Any]]:
        """Get snapshots for a run."""
        return self._snapshots.get(run_id, [])


__all__ = [
    "CircuitBreakerRegistry",
    "ContinuityWatchdog",
    "DLQManager",
    "DeferralQueue",
    "EscalationQueue",
    "FreshnessValidator",
    "HandoffManager",
    "InterruptionTracker",
    "ReplayManager",
]
