"""Adaptive sync interval controller for dynamic scheduler tuning.

Dynamically adjusts synchronization loop intervals based on drift rate, error rate,
and system load. Enables smooth performance scaling from low-traffic to high-traffic
scenarios without manual intervention.

# @trace WL-267
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace

logger = logging.getLogger(__name__)


@dataclass
class SyncIntervalConfig:
    """Configuration for adaptive sync interval tuning.

    Attributes:
        min_seconds: Minimum interval in seconds (default: 60).
        max_seconds: Maximum interval in seconds (default: 3600).
        current_seconds: Current interval in seconds (default: 300).
    """

    min_seconds: float = 60.0
    max_seconds: float = 3600.0
    current_seconds: float = 300.0


class AdaptiveSyncIntervalController:
    """Manages dynamic adjustment of sync intervals.

    Provides methods to increase/decrease sync intervals based on system conditions,
    keeping intervals within configured min/max bounds.
    """

    @staticmethod
    def increase(config: SyncIntervalConfig, factor: float = 2.0) -> SyncIntervalConfig:
        """Increase the sync interval by the specified factor (up to max).

        Useful when the system is stable and we want to reduce sync frequency to
        lower resource consumption.

        Args:
            config: Current sync interval configuration.
            factor: Multiplication factor for the interval (default: 2.0).

        Returns:
            New SyncIntervalConfig with the increased interval.
        """
        new_interval = config.current_seconds * factor
        # Cap at max_seconds
        capped_interval = min(new_interval, config.max_seconds)

        logger.debug(
            f"Increasing sync interval: {config.current_seconds}s -> {capped_interval}s (factor: {factor})"
        )

        return replace(config, current_seconds=capped_interval)

    @staticmethod
    def decrease(config: SyncIntervalConfig, factor: float = 2.0) -> SyncIntervalConfig:
        """Decrease the sync interval by the specified factor (down to min).

        Useful when the system is under stress or has high drift, requiring more
        frequent synchronization.

        Args:
            config: Current sync interval configuration.
            factor: Division factor for the interval (default: 2.0).

        Returns:
            New SyncIntervalConfig with the decreased interval.
        """
        new_interval = config.current_seconds / factor
        # Cap at min_seconds
        capped_interval = max(new_interval, config.min_seconds)

        logger.debug(
            f"Decreasing sync interval: {config.current_seconds}s -> {capped_interval}s (factor: {factor})"
        )

        return replace(config, current_seconds=capped_interval)

    @staticmethod
    def reset(config: SyncIntervalConfig) -> SyncIntervalConfig:
        """Reset the sync interval to the midpoint between min and max.

        Useful as a baseline recovery point when conditions stabilize after a
        period of turbulence.

        Args:
            config: Current sync interval configuration.

        Returns:
            New SyncIntervalConfig with interval reset to (min + max) / 2.
        """
        midpoint = (config.min_seconds + config.max_seconds) / 2.0

        logger.debug(f"Resetting sync interval to midpoint: {midpoint}s")

        return replace(config, current_seconds=midpoint)
