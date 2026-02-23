"""Metadata freshness tracking with TTL-based expiration.

Provides time-to-live (TTL) based caching for metadata records,
allowing automatic eviction of stale entries based on age.

FR traceability: WL-270 (Metadata Freshness TTL)
# @trace WL-270
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class MetadataRecord:
    """A metadata record with creation timestamp."""

    key: str
    value: str
    fetched_at: datetime


class MetadataFreshnessTTL:
    """Manages metadata with TTL-based freshness tracking."""

    def __init__(self, ttl_seconds: float = 300.0) -> None:
        """Initialize the metadata freshness manager.

        Args:
            ttl_seconds: Time-to-live for metadata records in seconds.

        Raises:
            ValueError: If ttl_seconds <= 0.0.
        """
        if ttl_seconds <= 0.0:
            raise ValueError("ttl_seconds must be > 0.0")

        self._ttl_seconds = ttl_seconds
        self._records: dict[str, MetadataRecord] = {}

        logger.debug(f"Initialized metadata freshness with TTL {ttl_seconds}s")

    def put(self, key: str, value: str) -> MetadataRecord:
        """Store a metadata record with current timestamp.

        Args:
            key: Metadata key.
            value: Metadata value.

        Returns:
            The created MetadataRecord.
        """
        record = MetadataRecord(
            key=key,
            value=value,
            fetched_at=datetime.now(timezone.utc),
        )
        self._records[key] = record
        logger.debug(f"Stored metadata: {key}")
        return record

    def get(self, key: str) -> str | None:
        """Retrieve metadata if fresh, None if expired or missing.

        Args:
            key: Metadata key.

        Returns:
            The metadata value if fresh, None otherwise.
        """
        record = self._records.get(key)
        if record is None:
            return None

        if self.is_fresh(key):
            return record.value

        del self._records[key]
        logger.debug(f"Evicted stale metadata: {key}")
        return None

    def is_fresh(self, key: str) -> bool:
        """Check if a metadata record is still fresh.

        Args:
            key: Metadata key.

        Returns:
            True if the record exists and is not expired, False otherwise.
        """
        record = self._records.get(key)
        if record is None:
            return False

        age_seconds = (datetime.now(timezone.utc) - record.fetched_at).total_seconds()
        return age_seconds < self._ttl_seconds

    def evict_stale(self) -> int:
        """Remove all expired metadata records.

        Returns:
            Number of records evicted.
        """
        now = datetime.now(timezone.utc)
        stale_keys = [
            key
            for key, record in self._records.items()
            if (now - record.fetched_at).total_seconds() >= self._ttl_seconds
        ]

        for key in stale_keys:
            del self._records[key]

        if stale_keys:
            logger.debug(f"Evicted {len(stale_keys)} stale metadata records")

        return len(stale_keys)
