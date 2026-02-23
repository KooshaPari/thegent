"""Automatic checker for stale sync docs and command reference drift.

Tracks documentation freshness and identifies stale docs that need updating.

# @trace WL-258
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, UTC

logger = logging.getLogger(__name__)


@dataclass
class DocRecord:
    """Record of a document and its freshness status.

    Attributes:
        doc_path: Path to the document.
        last_updated: When the document was last updated.
        stale: Whether the document is marked as stale.
    """

    doc_path: str
    last_updated: datetime
    stale: bool = False


class DocsFreshnessChecker:
    """Tracks and checks documentation freshness.

    Identifies stale docs based on age and provides freshness metrics.
    """

    def __init__(self) -> None:
        """Initialize the freshness checker."""
        self._docs: dict[str, DocRecord] = {}
        logger.debug("DocsFreshnessChecker initialized")

    def register(self, doc_path: str, last_updated: datetime) -> DocRecord:
        """Register a document for freshness tracking.

        Args:
            doc_path: Path to the document.
            last_updated: Timestamp of last update.

        Returns:
            DocRecord for the registered document.
        """
        record = DocRecord(doc_path=doc_path, last_updated=last_updated)
        self._docs[doc_path] = record
        logger.debug(f"Registered document {doc_path}")
        return record

    def check_staleness(self, max_age_days: float = 90.0) -> list[DocRecord]:
        """Check which docs are stale and mark them.

        Args:
            max_age_days: Maximum age in days before a doc is considered stale (default 90).

        Returns:
            List of stale DocRecord objects.
        """
        now = datetime.now(UTC)
        max_age = timedelta(days=max_age_days)
        stale_docs = []

        for record in self._docs.values():
            age = now - record.last_updated
            if age > max_age:
                record.stale = True
                stale_docs.append(record)
                logger.debug(f"Marked {record.doc_path} as stale (age: {age.days} days)")
            else:
                record.stale = False

        return stale_docs

    def stale_count(self) -> int:
        """Get count of stale documents.

        Returns:
            Number of documents marked as stale.
        """
        return sum(1 for record in self._docs.values() if record.stale)

    def fresh_count(self) -> int:
        """Get count of fresh documents.

        Returns:
            Number of documents not marked as stale.
        """
        return sum(1 for record in self._docs.values() if not record.stale)
