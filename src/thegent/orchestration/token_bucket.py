"""Token bucket rate limiting for swarm API call layer (swarm-token-bucket).

Provides a thread-safe TokenBucket for controlling API call throughput and a
RateLimitedSwarmRunner that wraps any callable with token-bucket-based gating.

Environment variables:
  THGENT_RATE_TOKENS_PER_SEC  -- refill rate (tokens/second); default 10.0
  THGENT_RATE_BUCKET_SIZE     -- bucket capacity; default 20.0
"""

from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

_log = logging.getLogger(__name__)

try:
    import structlog as _structlog

    _slog = _structlog.get_logger(__name__)
except ModuleNotFoundError:
    _slog = _log

# Sentinel object for detecting "no argument passed" in run().
_UNSET: object = object()


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@dataclass
class TokenBucketConfig:
    """Configuration for a token bucket rate limiter.

    Attributes:
        capacity:        Maximum number of tokens the bucket can hold.
        refill_rate:     Tokens added per second (continuous refill).
        initial_tokens:  Starting token count; defaults to ``capacity`` when None.
    """

    capacity: float
    refill_rate: float  # tokens / second
    initial_tokens: float | None = None

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            msg = f"capacity must be > 0, got {self.capacity}"
            raise ValueError(msg)
        if self.refill_rate < 0:
            msg = f"refill_rate must be >= 0, got {self.refill_rate}"
            raise ValueError(msg)
        if self.initial_tokens is not None and self.initial_tokens < 0:
            msg = f"initial_tokens must be >= 0, got {self.initial_tokens}"
            raise ValueError(msg)


# ---------------------------------------------------------------------------
# Core implementation
# ---------------------------------------------------------------------------


class TokenBucket:
    """Thread-safe token bucket for rate limiting.

    Tokens are refilled continuously based on elapsed wall-clock time using
    ``time.monotonic()``.  All public methods acquire an internal ``threading.Lock``
    so the bucket is safe to share across threads.

    Example::

        cfg = TokenBucketConfig(capacity=10.0, refill_rate=2.0)
        bucket = TokenBucket(cfg)
        if bucket.consume():
            make_api_call()
    """

    def __init__(self, config: TokenBucketConfig) -> None:
        self._config = config
        self._tokens: float = (
            config.capacity if config.initial_tokens is None else config.initial_tokens
        )
        self._last_refill: float = time.monotonic()
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)

    # ------------------------------------------------------------------
    # Internal helpers (must be called with lock held)
    # ------------------------------------------------------------------

    def _apply_refill(self) -> None:
        """Compute elapsed time and add tokens (capped at capacity)."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        if elapsed > 0 and self._config.refill_rate > 0:
            added = elapsed * self._config.refill_rate
            self._tokens = min(self._config.capacity, self._tokens + added)
        self._last_refill = now

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def available(self) -> float:
        """Return the current number of available tokens (after refill)."""
        with self._lock:
            self._apply_refill()
            return self._tokens

    def refill(self, tokens: float | None = None) -> None:
        """Manually add tokens to the bucket (or trigger time-based refill).

        Args:
            tokens: If given, add exactly this many tokens (capped at capacity).
                    If None, perform a standard time-based refill.
        """
        with self._not_empty:
            if tokens is None:
                self._apply_refill()
            else:
                if tokens < 0:
                    msg = f"tokens must be >= 0, got {tokens}"
                    raise ValueError(msg)
                self._tokens = min(self._config.capacity, self._tokens + tokens)
                self._last_refill = time.monotonic()
            self._not_empty.notify_all()

    def consume(self, tokens: float = 1.0) -> bool:
        """Attempt to consume *tokens* without blocking.

        Args:
            tokens: Number of tokens to consume (default 1.0).

        Returns:
            True if tokens were consumed; False if insufficient tokens available.
        """
        if tokens <= 0:
            msg = f"tokens must be > 0, got {tokens}"
            raise ValueError(msg)
        with self._not_empty:
            self._apply_refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                _slog.debug(
                    "token_bucket.consumed",
                    tokens=tokens,
                    remaining=self._tokens,
                )
                return True
            _slog.debug(
                "token_bucket.insufficient",
                requested=tokens,
                available=self._tokens,
            )
            return False

    def try_consume(self, tokens: float = 1.0) -> tuple[bool, float]:
        """Attempt to consume without blocking; return result and estimated wait.

        Args:
            tokens: Number of tokens to consume (default 1.0).

        Returns:
            A 2-tuple ``(success, wait_time_s)`` where *wait_time_s* is 0.0 on
            success and the estimated seconds until enough tokens are available
            on failure (0.0 if refill_rate is 0).
        """
        if tokens <= 0:
            msg = f"tokens must be > 0, got {tokens}"
            raise ValueError(msg)
        with self._not_empty:
            self._apply_refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True, 0.0
            deficit = tokens - self._tokens
            wait_s = deficit / self._config.refill_rate if self._config.refill_rate > 0 else 0.0
            return False, wait_s

    def consume_blocking(
        self,
        tokens: float = 1.0,
        timeout_s: float | None = None,
    ) -> bool:
        """Block until enough tokens are available, then consume them.

        Args:
            tokens:    Number of tokens to consume (default 1.0).
            timeout_s: Maximum seconds to wait; None means wait indefinitely.

        Returns:
            True if tokens were consumed within the timeout; False otherwise.
        """
        if tokens <= 0:
            msg = f"tokens must be > 0, got {tokens}"
            raise ValueError(msg)
        if tokens > self._config.capacity:
            # Can never be satisfied — fail immediately.
            return False

        deadline: float | None = None
        if timeout_s is not None:
            if timeout_s < 0:
                msg = f"timeout_s must be >= 0, got {timeout_s}"
                raise ValueError(msg)
            deadline = time.monotonic() + timeout_s

        with self._not_empty:
            while True:
                self._apply_refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    _slog.debug(
                        "token_bucket.blocking_consumed",
                        tokens=tokens,
                        remaining=self._tokens,
                    )
                    return True

                # Compute how long to sleep until refill yields enough tokens.
                if self._config.refill_rate > 0:
                    deficit = tokens - self._tokens
                    wait_for_refill = deficit / self._config.refill_rate
                else:
                    # No automatic refill; can only wake on manual refill.
                    wait_for_refill = None

                if deadline is not None:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        return False
                    cond_wait: float | None = (
                        min(wait_for_refill, remaining)
                        if wait_for_refill is not None
                        else remaining
                    )
                else:
                    cond_wait = wait_for_refill  # None -> wait indefinitely

                self._not_empty.wait(timeout=cond_wait)

                # After waking, re-check deadline before looping.
                if deadline is not None and time.monotonic() >= deadline:
                    self._apply_refill()
                    if self._tokens >= tokens:
                        self._tokens -= tokens
                        return True
                    return False


# ---------------------------------------------------------------------------
# Swarm runner wrapper
# ---------------------------------------------------------------------------


class RateLimitedSwarmRunner:
    """Wraps a callable with token-bucket rate limiting for swarm API calls.

    Each call to ``run()`` acquires a token from the configured bucket before
    invoking the wrapped function.  If insufficient tokens are available, the
    call blocks until a token is obtained (subject to an optional timeout).

    Configuration can be injected directly or loaded from environment variables
    via ``configure_from_env()``.
    """

    def __init__(
        self,
        bucket: TokenBucket | None = None,
        default_timeout_s: float | None = None,
    ) -> None:
        """Initialise with an optional pre-configured bucket.

        Args:
            bucket:            A pre-built :class:`TokenBucket`.  When None, you
                               must call :meth:`configure_from_env` before ``run``.
            default_timeout_s: Default per-call wait timeout passed to
                               ``consume_blocking``.  None means no timeout.
        """
        self._bucket: TokenBucket | None = bucket
        self._default_timeout_s = default_timeout_s

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def configure_from_env(self) -> RateLimitedSwarmRunner:
        """Read bucket config from environment variables and configure bucket.

        Variables:
            THGENT_RATE_TOKENS_PER_SEC -- refill rate (default 10.0)
            THGENT_RATE_BUCKET_SIZE    -- capacity (default 20.0)

        Returns:
            self (for chaining).
        """
        rate = float(os.environ.get("THGENT_RATE_TOKENS_PER_SEC", "10.0"))
        size = float(os.environ.get("THGENT_RATE_BUCKET_SIZE", "20.0"))
        config = TokenBucketConfig(capacity=size, refill_rate=rate)
        self._bucket = TokenBucket(config)
        _slog.info(
            "rate_limited_runner.configured",
            refill_rate=rate,
            capacity=size,
        )
        return self

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        fn: Callable[..., Any],
        /,
        *args: Any,
        timeout_s: Any = _UNSET,
        **kwargs: Any,
    ) -> Any:
        """Acquire a token, then call *fn* with the given arguments.

        Args:
            fn:        Callable to invoke.
            *args:     Positional arguments forwarded to *fn*.
            timeout_s: Override the default per-call timeout (seconds).
                       Pass ``None`` explicitly for no timeout.
            **kwargs:  Keyword arguments forwarded to *fn*.

        Returns:
            The return value of *fn*.

        Raises:
            RuntimeError: If no bucket has been configured.
            TimeoutError: If a token could not be acquired within *timeout_s*.
        """
        if self._bucket is None:
            msg = (
                "RateLimitedSwarmRunner has no bucket configured. "
                "Call configure_from_env() or pass a bucket to __init__."
            )
            raise RuntimeError(msg)

        effective_timeout: float | None = (
            self._default_timeout_s if timeout_s is _UNSET else timeout_s
        )

        acquired = self._bucket.consume_blocking(
            tokens=1.0,
            timeout_s=effective_timeout,
        )
        if not acquired:
            msg = (
                f"Rate limit exceeded: could not acquire token within "
                f"{effective_timeout}s"
            )
            raise TimeoutError(msg)

        return fn(*args, **kwargs)
