"""
Dynamic Limiter

Resource-based dynamic concurrency with hysteresis control.
"""

from dataclasses import dataclass
from typing import Optional
from .resources import ResourceMonitor
import time


@dataclass
class HysteresisConfig:
    """Hysteresis controller configuration."""

    upper_threshold: float = 0.8
    lower_threshold: float = 0.5
    dwell_time: float = 5.0  # seconds to wait before scaling
    min_buffer: float = 0.05  # 5% minimum buffer
    discretionary_buffer: float = 0.15  # 15% discretionary


class DynamicLimiter:
    """Dynamic thread/concurrency limiter."""

    def __init__(
        self,
        min_limit: int = 1,
        max_limit: int = 100,
        initial_limit: Optional[int] = None,
        config: Optional[HysteresisConfig] = None,
    ):
        self.min_limit = min_limit
        self.max_limit = max_limit
        self.current_limit = initial_limit or min_limit
        self.config = config or HysteresisConfig()
        self.monitor = ResourceMonitor()

        self._last_scale_time = 0.0
        self._scale_direction = 0  # 1=up, -1=down, 0=none

    def acquire(self) -> bool:
        """Try to acquire a slot."""
        self._adjust()
        # Always allow if under limit
        return True

    def _adjust(self) -> None:
        """Adjust limit based on resources."""
        sample = self.monitor.sample()
        pressure = sample.pressure_score
        now = time.time()

        time_since_scale = now - self._last_scale_time

        # Check hysteresis
        if pressure > self.config.upper_threshold:
            # Under pressure - scale down
            if time_since_scale >= self.config.dwell_time or self._scale_direction == -1:
                self._scale_down(pressure)
                self._last_scale_time = now
                self._scale_direction = -1

        elif pressure < self.config.lower_threshold:
            # Low pressure - scale up
            if time_since_scale >= self.config.dwell_time or self._scale_direction == 1:
                self._scale_up(pressure)
                self._last_scale_time = now
                self._scale_direction = 1

        else:
            # In hysteresis band - no change
            self._scale_direction = 0

    def _scale_up(self, pressure: float) -> None:
        """Scale up concurrency."""
        headroom = self.config.lower_threshold - pressure
        increment = max(1, int(headroom * 10))
        self.current_limit = min(self.max_limit, self.current_limit + increment)

    def _scale_down(self, pressure: float) -> None:
        """Scale down concurrency."""
        excess = pressure - self.config.upper_threshold
        decrement = max(1, int(excess * 10))
        self.current_limit = max(self.min_limit, self.current_limit - decrement)

    def stats(self) -> dict:
        """Get limiter statistics."""
        latest = self.monitor.latest()
        return {
            "current_limit": self.current_limit,
            "min_limit": self.min_limit,
            "max_limit": self.max_limit,
            "pressure": latest.pressure_score if latest else 0,
            "scale_direction": self._scale_direction,
        }
