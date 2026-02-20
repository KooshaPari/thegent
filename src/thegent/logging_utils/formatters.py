"""Logging formatters."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class StructuredFormatter(logging.Formatter):
    """Structured log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record.

        Args:
            record: Log record

        Returns:
            Formatted log string
        """
        return f"{record.levelname}: {record.name}: {record.getMessage()}"
