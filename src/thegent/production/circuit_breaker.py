"""
Circuit Breaker

Prevents cascading failures with circuit breaker pattern.
"""

from dataclasses import dataclass
from typing import Optional, Callable
from enum import Enum
import time


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitStats:
    """Circuit breaker statistics."""
    state: CircuitState
    failures: int
    successes: int
    last_failure: Optional[float]
    last_success: Optional[float]


class CircuitBreaker:
    """Circuit breaker for fault tolerance."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_requests: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests

        self._state = CircuitState.CLOSED
        self._failures = 0
        self._successes = 0
        self._last_failure: Optional[float] = None
        self._last_success: Optional[float] = None
        self._half_open_count = 0

    @property
    def state(self) -> CircuitState:
        """Get current state."""
        self._update_state()
        return self._state

    def _update_state(self) -> None:
        """Update state based on conditions."""
        if self._state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self._last_failure and (time.time() - self._last_failure) >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_count = 0

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        self._update_state()

        if self._state == CircuitState.CLOSED:
            return True

        if self._state == CircuitState.HALF_OPEN:
            return self._half_open_count < self.half_open_requests

        return False  # OPEN

    def record_success(self) -> None:
        """Record successful execution."""
        self._successes += 1
        self._last_success = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._half_open_count += 1
            if self._half_open_count >= self.half_open_requests:
                # Reset on successful recovery
                self._state = CircuitState.CLOSED
                self._failures = 0

    def record_failure(self) -> None:
        """Record failed execution."""
        self._failures += 1
        self._last_failure = time.time()

        if self._state == CircuitState.HALF_OPEN:
            # Failure during recovery, go back to open
            self._state = CircuitState.OPEN
        elif self._state == CircuitState.CLOSED:
            if self._failures >= self.failure_threshold:
                self._state = CircuitState.OPEN

    def execute(self, fn: Callable, fallback: Callable | None = None) -> any:
        """Execute function with circuit breaker protection."""
        if not self.can_execute():
            if fallback:
                return fallback()
            raise CircuitOpenError("Circuit breaker is open")

        try:
            result = fn()
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            if fallback:
                return fallback()
            raise

    def reset(self) -> None:
        """Reset circuit breaker."""
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._half_open_count = 0

    def stats(self) -> CircuitStats:
        """Get circuit statistics."""
        return CircuitStats(
            state=self.state,
            failures=self._failures,
            successes=self._successes,
            last_failure=self._last_failure,
            last_success=self._last_success
        )


class CircuitOpenError(Exception):
    """Raised when circuit is open."""
