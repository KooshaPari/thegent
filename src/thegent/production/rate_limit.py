"""
Rate Limiter

Token bucket rate limiting.
"""

from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""

    requests_per_second: float = 10.0
    burst_size: int = 20
    wait_timeout: float = 5.0


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self._tokens = float(self.config.burst_size)
        self._last_update = time.time()
        self._total_requests = 0
        self._rejected = 0

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self._last_update
        new_tokens = elapsed * self.config.requests_per_second
        self._tokens = min(self.config.burst_size, self._tokens + new_tokens)
        self._last_update = now

    def acquire(self, tokens: int = 1, wait: bool = False) -> bool:
        """Try to acquire tokens."""
        self._refill()
        self._total_requests += 1

        if self._tokens >= tokens:
            self._tokens -= tokens
            return True

        if wait:
            # Wait for tokens to be available
            needed = tokens - self._tokens
            wait_time = needed / self.config.requests_per_second

            if wait_time <= self.config.wait_timeout:
                time.sleep(wait_time)
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True

        self._rejected += 1
        return False

    def try_acquire(self, tokens: int = 1) -> bool:
        """Non-blocking acquire."""
        return self.acquire(tokens, wait=False)

    def wait_acquire(self, tokens: int = 1) -> bool:
        """Blocking acquire with wait."""
        return self.acquire(tokens, wait=True)

    @property
    def available(self) -> float:
        """Get available tokens."""
        self._refill()
        return self._tokens

    def stats(self) -> dict:
        """Get rate limiter statistics."""
        return {
            "available_tokens": self.available,
            "burst_size": self.config.burst_size,
            "requests_per_second": self.config.requests_per_second,
            "total_requests": self._total_requests,
            "rejected": self._rejected,
            "rejection_rate": self._rejected / self._total_requests if self._total_requests > 0 else 0,
        }


class MultiRateLimiter:
    """Rate limiter with multiple buckets."""

    def __init__(self):
        self._limiters: dict[str, RateLimiter] = {}

    def get(self, key: str, config: Optional[RateLimitConfig] = None) -> RateLimiter:
        """Get or create rate limiter for key."""
        if key not in self._limiters:
            self._limiters[key] = RateLimiter(config)
        return self._limiters[key]

    def acquire(self, key: str, tokens: int = 1, wait: bool = False) -> bool:
        """Acquire tokens for a key."""
        return self.get(key).acquire(tokens, wait)

    def stats(self) -> dict:
        """Get statistics for all limiters."""
        return {key: limiter.stats() for key, limiter in self._limiters.items()}
