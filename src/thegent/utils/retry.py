"""Unified retry utilities for thegent.

Usage:
    from thegent.utils.retry import retry, CircuitBreaker
    
    @retry(max_attempts=3, backoff=2.0)
    def flaky_function():
        ...
"""

from __future__ import annotations

import errno
import logging
import time
from typing import Any, Callable

from tenacity import (
    retry as tenacity_retry,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    backoff: float = 2.0,
    min_wait: float = 1.0,
    max_wait: float = 60.0,
    reraise: bool = True,
):
    """Decorator for retry with exponential backoff."""
    def decorator(func):
        return tenacity_retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=backoff, min=min_wait, max=max_wait),
            reraise=reraise,
        )(func)
    return decorator


EAGAIN_ERRNOS = frozenset({errno.EAGAIN, errno.EWOULDBLOCK})


class CircuitBreaker:
    """Simple circuit breaker implementation."""
    
    def __init__(self, failure_threshold=5, recovery_timeout=60.0, expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"
    
    def call(self, func):
        if self.state == "open":
            if self.last_failure_time and time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "half-open"
            else:
                raise RuntimeError("Circuit breaker OPEN")
        try:
            result = func()
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            return self.call(lambda: func(*args, **kwargs)
        return wrapper


__all__ = ["retry", "CircuitBreaker"]
