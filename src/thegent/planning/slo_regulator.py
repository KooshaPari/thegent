"""WP-11001: SLO regulator loop controller.

Provides stable control updates with anti-oscillation guarantees for system SLOs.
"""

from datetime import UTC, datetime
from typing import Any


class SLORegulator:
    """Closed-loop controller for regulating system performance against SLOs."""

    def __init__(self, target_latency_ms: float = 100.0) -> None:
        self.target_latency_ms = target_latency_ms
        self._last_adjustment_time = datetime.now(UTC)
        self._adjustment_interval_s = 600  # 10 minutes anti-oscillation (WP-11001)
        self._current_throttle = 0.0

    def evaluate_and_adjust(self, current_latency_ms: float) -> dict[str, Any]:
        """Evaluate SLO performance and adjust throttle if needed."""
        now = datetime.now(UTC)
        time_since_adj = (now - self._last_adjustment_time).total_seconds()
        can_adjust = time_since_adj >= self._adjustment_interval_s
        adjustment_made = False

        if can_adjust:
            if current_latency_ms > self.target_latency_ms * 1.2:
                self._current_throttle = min(1.0, self._current_throttle + 0.1)
                adjustment_made = True
            elif current_latency_ms < self.target_latency_ms * 0.8:
                self._current_throttle = max(0.0, self._current_throttle - 0.1)
                adjustment_made = True

            if adjustment_made:
                self._last_adjustment_time = now

        return {
            "target_ms": self.target_latency_ms,
            "current_ms": current_latency_ms,
            "throttle": self._current_throttle,
            "can_adjust": can_adjust,
            "adjustment_made": adjustment_made,
            "next_adjustment_allowed_at": (self._last_adjustment_time.timestamp() + self._adjustment_interval_s),
        }
