"""Retry helper utilities."""

import logging
import time
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class RetryHelpers:
    """Retry helper utilities."""

    @staticmethod
    def retry_with_backoff(
        func: Callable,
        max_attempts: int = 3,
        backoff_factor: float = 2.0,
    ) -> Any:
        """Retry function with exponential backoff.

        Args:
            func: Function to retry
            max_attempts: Maximum attempts
            backoff_factor: Backoff factor

        Returns:
            Function result
        """
        for attempt in range(max_attempts):
            try:  # noqa: PERF203 -- intentional retry loop with backoff
                return func()
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise
                wait_time = backoff_factor**attempt
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s")
                time.sleep(wait_time)
