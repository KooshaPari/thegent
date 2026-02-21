"""Retry helper utilities — thin wrapper around tenacity."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from tenacity import retry, stop_after_attempt, wait_exponential

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)


class RetryHelpers:
    """Retry helper utilities backed by tenacity."""

    @staticmethod
    def retry_with_backoff(
        func: Callable[[], Any],
        max_attempts: int = 3,
        backoff_factor: float = 2.0,
    ) -> Any:
        """Retry callable with exponential backoff via tenacity.

        Raises the original exception after exhausting all attempts.
        """
        decorated = retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=backoff_factor, min=backoff_factor),
            reraise=True,
        )(func)
        return decorated()
