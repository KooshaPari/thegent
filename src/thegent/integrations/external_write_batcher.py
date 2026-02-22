"""External write batching.

Batches write requests together before sending to external systems to reduce
API calls and improve throughput.

# @trace WL-187
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class WriteRequest:
    """Represents a single write request."""

    record_id: str
    payload: dict[str, Any]


class ExternalWriteBatcher:
    """Batches write requests for external systems."""

    def __init__(self, batch_size: int = 50) -> None:
        """Initialize the external write batcher.

        Args:
            batch_size: Maximum number of requests per batch.

        Raises:
            ValueError: If batch_size < 1.
        """
        if batch_size < 1:
            raise ValueError("batch_size must be >= 1")

        self._batch_size = batch_size
        self._pending: list[WriteRequest] = []

        logger.debug(f"Initialized external write batcher with batch_size={batch_size}")

    def add(self, request: WriteRequest) -> None:
        """Add a write request to the pending buffer.

        Args:
            request: The write request to add.
        """
        self._pending.append(request)
        logger.debug(f"Added write request for record {request.record_id}, pending={len(self._pending)}")

    def flush(self) -> list[list[WriteRequest]]:
        """Flush pending requests into batches.

        Splits pending requests into batches of size batch_size, clears the
        pending buffer, and returns the list of batches.

        Returns:
            List of batches, where each batch is a list of WriteRequest objects.
        """
        if not self._pending:
            logger.debug("Flush called with no pending requests")
            return []

        batches: list[list[WriteRequest]] = []
        for i in range(0, len(self._pending), self._batch_size):
            batch = self._pending[i : i + self._batch_size]
            batches.append(batch)
            logger.debug(f"Created batch with {len(batch)} requests")

        self._pending = []
        logger.debug(f"Flushed {len(batches)} batches ({sum(len(b) for b in batches)} total requests)")
        return batches

    def pending_count(self) -> int:
        """Return the number of pending write requests.

        Returns:
            Count of requests awaiting flush.
        """
        return len(self._pending)
