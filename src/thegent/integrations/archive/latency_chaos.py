"""Connector latency chaos injection for resilience testing.

This module provides facilities for injecting synthetic latency and failures
into connector operations to validate system resilience and timeout handling.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class ChaosConfig:
    """Configuration for latency chaos injection.

    Attributes:
        enabled: If True, chaos injection is active. Default False.
        min_delay_ms: Minimum delay in milliseconds. Default 100.0.
        max_delay_ms: Maximum delay in milliseconds. Default 2000.0.
        failure_rate: Probability [0.0-1.0] of injecting an error. Default 0.0.
    """

    enabled: bool = False
    min_delay_ms: float = 100.0
    max_delay_ms: float = 2000.0
    failure_rate: float = 0.0


class LatencyChaosInjector:
    """Injects synthetic latency and failures into connector operations.

    This class provides methods to compute random delays and failure probabilities
    based on configured chaos parameters. It supports deterministic seeding for
    reproducible test scenarios.
    """

    def __init__(self, config: ChaosConfig) -> None:
        """Initialize the chaos injector.

        Args:
            config: ChaosConfig instance specifying injection parameters.
        """
        self._config = config
        self._rng = random.Random()

    def compute_delay(self, connector: str) -> float:
        """Compute a random delay in milliseconds.

        Args:
            connector: Connector identifier (for future correlation/logging).

        Returns:
            Delay in milliseconds sampled uniformly from [min_delay_ms, max_delay_ms]
            if enabled, else 0.0.
        """
        if not self._config.enabled:
            return 0.0
        return self._rng.uniform(self._config.min_delay_ms, self._config.max_delay_ms)

    def should_fail(self, connector: str) -> bool:
        """Determine if an error should be injected.

        Args:
            connector: Connector identifier (for future correlation/logging).

        Returns:
            True with probability failure_rate if enabled, else False.
        """
        if not self._config.enabled:
            return False
        return self._rng.random() < self._config.failure_rate

    def inject(self, connector: str) -> tuple[float, bool]:
        """Compute both delay and failure status in one call.

        Args:
            connector: Connector identifier.

        Returns:
            Tuple of (delay_ms, should_fail).
        """
        return (self.compute_delay(connector), self.should_fail(connector))

    def with_seed(self, seed: int) -> LatencyChaosInjector:
        """Create a new injector with same config but seeded RNG.

        Useful for reproducible test scenarios.

        Args:
            seed: Random seed for deterministic behavior.

        Returns:
            New LatencyChaosInjector with same config but seeded RNG.
        """
        new_injector = LatencyChaosInjector(self._config)
        new_injector._rng = random.Random(seed)
        return new_injector
