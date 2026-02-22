"""Adaptive per-connector rate limiting with dynamic adjustment.

Implements adaptive rate limiting that increases limits on success and
decreases on throttle events, enabling optimal throughput discovery.

FR traceability: WL-286 (Adaptive Per-Connector Rate Limiter)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class RateLimitState:
    """Represents the current rate limit state for a connector."""

    connector: str
    requests_per_minute: float
    last_updated: datetime


class AdaptiveRateLimiter:
    """Manages adaptive rate limits per connector."""

    def __init__(self, default_rpm: float = 60.0) -> None:
        """Initialize the adaptive rate limiter.

        Args:
            default_rpm: Default requests per minute for all connectors.
        """
        if default_rpm < 1.0:
            raise ValueError("default_rpm must be >= 1.0")

        self._default_rpm = default_rpm
        self._limits: dict[str, float] = {}
        self._last_updated: dict[str, datetime] = {}

        logger.debug(f"Initialized adaptive rate limiter with default {default_rpm} rpm")

    def set_limit(self, connector: str, rpm: float) -> None:
        """Set explicit rate limit for a connector.

        Args:
            connector: Name of the connector.
            rpm: Requests per minute limit.

        Raises:
            ValueError: If rpm < 1.0.
        """
        if rpm < 1.0:
            raise ValueError("rpm must be >= 1.0")

        self._limits[connector] = rpm
        self._last_updated[connector] = datetime.now(timezone.utc)
        logger.debug(f"Set limit for {connector} to {rpm} rpm")

    def get_limit(self, connector: str) -> float:
        """Get the current rate limit for a connector.

        Args:
            connector: Name of the connector.

        Returns:
            Current requests per minute limit for the connector.
        """
        return self._limits.get(connector, self._default_rpm)

    def record_throttle(self, connector: str) -> None:
        """Record a throttle event and reduce the limit.

        Reduces the limit by 20%, with a minimum of 1.0 rpm.

        Args:
            connector: Name of the connector.
        """
        current_limit = self.get_limit(connector)
        new_limit = max(1.0, current_limit * 0.8)
        self._limits[connector] = new_limit
        self._last_updated[connector] = datetime.now(timezone.utc)

        logger.debug(f"Recorded throttle for {connector}: {current_limit} -> {new_limit} rpm")

    def record_success(self, connector: str) -> None:
        """Record a successful request and increase the limit.

        Increases the limit by 5%, with a maximum of 10x the default limit.

        Args:
            connector: Name of the connector.
        """
        current_limit = self.get_limit(connector)
        max_limit = self._default_rpm * 10
        new_limit = min(max_limit, current_limit * 1.05)
        self._limits[connector] = new_limit
        self._last_updated[connector] = datetime.now(timezone.utc)

        logger.debug(f"Recorded success for {connector}: {current_limit} -> {new_limit} rpm")

    def get_state(self, connector: str) -> RateLimitState:
        """Get the current state of a connector's rate limit.

        Args:
            connector: Name of the connector.

        Returns:
            Current rate limit state for the connector.
        """
        rpm = self.get_limit(connector)
        last_updated = self._last_updated.get(connector, datetime.now(timezone.utc))

        return RateLimitState(
            connector=connector,
            requests_per_minute=rpm,
            last_updated=last_updated,
        )
