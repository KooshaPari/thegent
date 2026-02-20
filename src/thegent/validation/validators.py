"""Validation utilities."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class Validators:
    """Validation utilities."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address.

        Args:
            email: Email to validate

        Returns:
            True if valid
        """
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL.

        Args:
            url: URL to validate

        Returns:
            True if valid
        """
        import re

        pattern = r"^https?://.+"
        return bool(re.match(pattern, url))
