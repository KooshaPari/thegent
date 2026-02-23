"""No-op fast path for skipping unchanged sync cycles.

Provides a fast path for cycles that have no changes, with explicit telemetry
for unchanged runs and improved performance metrics.

# @trace WL-256
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass
class NoOpResult:
    """Result of a no-op check.

    Attributes:
        skipped: True if the operation was skipped.
        reason: Human-readable reason for the decision.
    """

    skipped: bool
    reason: str = ""


class NoOpFastPath:
    """Fast path check for no-op cycles.

    Detects when a cycle has no changes and skips expensive processing,
    with telemetry for unchanged runs.
    """

    def __init__(self, enabled: bool = True) -> None:
        """Initialize the fast path.

        Args:
            enabled: Whether the fast path is enabled (default True).
        """
        self._enabled = enabled
        logger.debug(f"NoOpFastPath initialized with enabled={enabled}")

    def check(self, item_id: str, condition_fn: Callable[[], bool]) -> NoOpResult:
        """Check if an item should be skipped due to no changes.

        Args:
            item_id: Identifier for the item being checked.
            condition_fn: Callable that returns True if the item is unchanged.

        Returns:
            NoOpResult with skipped status and reason.
        """
        if not self._enabled:
            return NoOpResult(skipped=False, reason="fast path disabled")

        if condition_fn():
            logger.debug(f"No-op detected for item {item_id}")
            return NoOpResult(skipped=True, reason="no changes detected")

        return NoOpResult(skipped=False, reason="changes detected")

    def is_enabled(self) -> bool:
        """Check if the fast path is enabled.

        Returns:
            True if enabled, False otherwise.
        """
        return self._enabled
