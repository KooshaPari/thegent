"""Selective retry queue with attempt tracking and max retry limits.

Manages items that need retry with configurable max attempt limits,
separating pending retries from permanently failed items.

FR traceability: WL-273 (Selective Retry Queue)
# @trace WL-273
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RetryItem:
    """An item queued for retry with attempt tracking."""

    item_id: str
    payload: dict[str, Any]
    attempt: int = 0


class SelectiveRetryQueue:
    """Manages retry queue with attempt limits and failure tracking."""

    def __init__(self, max_attempts: int = 3) -> None:
        """Initialize the selective retry queue.

        Args:
            max_attempts: Maximum number of retry attempts before failure.

        Raises:
            ValueError: If max_attempts < 1.
        """
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")

        self._max_attempts = max_attempts
        self._pending: dict[str, RetryItem] = {}
        self._failed: dict[str, RetryItem] = {}

        logger.debug(f"Initialized retry queue with max_attempts={max_attempts}")

    def enqueue(self, item_id: str, payload: dict[str, Any]) -> RetryItem:
        """Enqueue an item for retry.

        Args:
            item_id: Unique identifier for the item.
            payload: Data payload to retry.

        Returns:
            The created RetryItem.
        """
        item = RetryItem(item_id=item_id, payload=payload, attempt=0)
        self._pending[item_id] = item
        logger.debug(f"Enqueued item: {item_id}")
        return item

    def retry(self, item_id: str) -> RetryItem | None:
        """Increment attempt count and return the item, or None if max reached.

        Args:
            item_id: Item identifier.

        Returns:
            Updated RetryItem if under max attempts, None if max reached.
        """
        item = self._pending.get(item_id)
        if item is None:
            logger.warning(f"Retry requested for non-existent item: {item_id}")
            return None

        item.attempt += 1

        if item.attempt >= self._max_attempts:
            del self._pending[item_id]
            self._failed[item_id] = item
            logger.debug(f"Item {item_id} moved to failed after {item.attempt} attempts")
            return None

        logger.debug(f"Retrying item {item_id}: attempt {item.attempt}")
        return item

    def failed(self) -> list[RetryItem]:
        """Get all items that exceeded max attempts.

        Returns:
            List of failed RetryItem objects.
        """
        return list(self._failed.values())

    def pending(self) -> list[RetryItem]:
        """Get all items still pending retry.

        Returns:
            List of pending RetryItem objects.
        """
        return list(self._pending.values())
