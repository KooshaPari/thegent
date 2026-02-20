"""Database helper utilities."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class DBHelpers:
    """Database helper utilities."""

    @staticmethod
    def build_query(filters: dict[str, Any]) -> str:
        """Build SQL query from filters.

        Args:
            filters: Filter dictionary

        Returns:
            SQL WHERE clause
        """
        conditions = []
        for key, value in filters.items():
            conditions.append(f"{key} = '{value}'")
        return " AND ".join(conditions) if conditions else "1=1"
