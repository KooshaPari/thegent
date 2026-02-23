"""Unified retry utilities for thegent.

Usage:
    from thegent.utils.retry import retry, CircuitBreaker
    
    @retry(max_attempts=3, backoff=2.0)
    def flaky_function():
        ...
"""

import logging
import time

from tenacity import retry as tenacity_retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


def retry(max_attempts=3, backoff=2.0, min_wait=1.0, max_wait=60.0, reraise=True):
    """Decorator for retry with exponential backoff."""
    def decorator(func):
        return tenacity_retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=backoff, min=min_wait, max=max_wait),
            reraise=reraise,
        )(func)
    return decorator


class CircuitBreaker:
    """Simple circuit breaker."""
    
    def __init__(self, threshold=5, timeout=60.0, exception=Exception):
        self.threshold = threshold
        self.timeout = timeout
        self.exception = exception
        self.count = 0
        self.last_fail = None
        self.state = "closed"
    
    def call(self, func):
        if self.state == "open":
            if self.last_fail and time.time() - self.last_fail >= self.timeout:
                self.state = "half-open"
            else:
                raise RuntimeError("breaker open")
        try:
            r = func()
            if self.state == "half-open":
                self.state = "closed"
                self.count = 0
            return r
        except self.exception:
            self.count += 1
            self.last_fail = time.time()
            if self.count >= self.threshold:
                self.state = "open"
            raise


__all__ = ["retry", "CircuitBreaker"]
