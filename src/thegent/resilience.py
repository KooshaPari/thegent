"""Unified retry decorators using tenacity. Replaces all manual retry loops.

GOVERNANCE: Per CLAUDE.md Library-First Policy, tenacity is the ONLY retry mechanism.
Manual retry loops (while True, for i in range(n)) are FORBIDDEN.

This module provides standardized retry decorators for common scenarios:
- Transient errors (network timeouts, 502/503, rate limits)
- Compare-And-Swap operations (atomic writes with collision detection)
- User input validation (interactive re-prompting)
- HTTP calls with status-code-based retry logic
"""

import logging
from typing import Any, Callable, TypeVar

from tenacity import (
    RetryError,
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
    wait_random_exponential,
)

_log = logging.getLogger(__name__)

T = TypeVar("T")

__all__ = [
    "RetryError",
    "cas_retry",
    "http_retry",
    "transient_retry",
    "user_input_retry",
]


def transient_retry(
    max_attempts: int = 3,
    min_wait: float = 0.5,
    max_wait: float = 60.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry decorator for transient errors: network timeouts, 502/503, rate limits.

    Uses exponential backoff with jitter to avoid thundering herd.
    Logs warnings on each retry attempt.

    Args:
        max_attempts: Maximum number of attempts (default: 3).
        min_wait: Minimum wait time in seconds (default: 0.5).
        max_wait: Maximum wait time in seconds (default: 60.0).

    Returns:
        Decorated function that retries on exception with exponential backoff.

    Example:
        @transient_retry(max_attempts=5, max_wait=30.0)
        async def call_api():
            return await client.get("https://api.example.com/data")

    Raises:
        RetryError: If max_attempts exceeded and last exception is re-raised.
    """

    def _before_sleep_log(retry_state: Any) -> None:
        exc = retry_state.outcome.exception() if retry_state.outcome else None
        _log.warning(
            "Transient error (attempt %d/%d): %s. Retrying in %.1fs...",
            retry_state.attempt_number,
            max_attempts,
            type(exc).__name__ if exc else "unknown",
            retry_state.next_action.sleep if retry_state.next_action else 0,
        )

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_random_exponential(min=min_wait, max=max_wait),
        reraise=True,
        before_sleep=_before_sleep_log,
    )


def cas_retry(
    max_attempts: int = 5,
    base_delay: float = 0.1,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry decorator for Compare-And-Swap operations (atomic git ref updates, CAS writes).

    CAS operations fail when the observed value changes between check and update.
    Uses exponential backoff with jitter. Logs collision detection and retries.

    Args:
        max_attempts: Maximum number of attempts (default: 5).
        base_delay: Base delay for exponential backoff in seconds (default: 0.1).

    Returns:
        Decorated function that retries on CAS collision.

    Example:
        @cas_retry(max_attempts=3)
        def update_ref_atomic(ref, new_hash, old_hash):
            # Raises ValueError on CAS collision; tenacity retries
            result = git_update_ref(ref, new_hash, old_hash, compare=True)
            return result

    Raises:
        RetryError: If max_attempts exceeded and last exception is re-raised.
    """

    def _before_sleep_log(retry_state: Any) -> None:
        exc = retry_state.outcome.exception() if retry_state.outcome else None
        _log.debug(
            "CAS collision (attempt %d/%d): %s. Retrying with backoff...",
            retry_state.attempt_number,
            max_attempts,
            type(exc).__name__ if exc else "unknown",
        )

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_random_exponential(min=base_delay, max=30.0),
        reraise=True,
        before_sleep=_before_sleep_log,
    )


def user_input_retry(
    max_attempts: int = 3,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry decorator for user input elicitation that must produce valid input.

    For interactive user prompting. Short waits (100ms) since user is interactive.
    Used when user input validation fails and must re-prompt.

    Args:
        max_attempts: Maximum number of prompts (default: 3).

    Returns:
        Decorated function that retries on ValueError (validation failure).

    Example:
        @user_input_retry(max_attempts=3)
        async def elicit_choice(ctx, prompt, options):
            choice = await ctx.elicit_str(prompt)
            if choice not in options:
                raise ValueError(f"Invalid choice: {choice}")
            return choice

    Raises:
        RetryError: If max_attempts exceeded and last ValueError is re-raised.
    """

    def _before_sleep_log(retry_state: Any) -> None:
        exc = retry_state.outcome.exception() if retry_state.outcome else None
        _log.debug(
            "User input invalid (attempt %d/%d): %s. Re-prompting...",
            retry_state.attempt_number,
            max_attempts,
            str(exc)[:50] if exc else "unknown",
        )

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_fixed(0.1),
        retry=retry_if_exception_type(ValueError),
        reraise=True,
        before_sleep=_before_sleep_log,
    )


def http_retry(
    max_attempts: int = 3,
    status_codes: tuple[int, ...] = (429, 500, 502, 503, 504),
    min_wait: float = 0.5,
    max_wait: float = 60.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry decorator for HTTP calls with status-code-based retry logic.

    Retries on specific HTTP status codes (rate limit, server errors) and network errors
    (timeouts, connection errors). Uses exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (default: 3).
        status_codes: HTTP status codes to retry on (default: 429, 500, 502, 503, 504).

    Returns:
        Decorated function that retries on HTTP errors or specified status codes.

    Example:
        @http_retry(max_attempts=5, status_codes=(429, 503))
        async def call_llm_api():
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()

    Raises:
        httpx.HTTPStatusError: If non-retryable status code is returned.
        RetryError: If max_attempts exceeded on retryable errors.

    Note:
        Requires httpx to be installed. Will be checked at decorator application time.
    """

    def _should_retry(exc: BaseException) -> bool:
        try:
            import httpx

            if isinstance(exc, httpx.HTTPStatusError):
                return exc.response.status_code in status_codes
            if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError)):
                return True
        except ImportError:
            _log.warning("httpx not installed; http_retry may not work as intended")
        return False

    def _before_sleep_log(retry_state: Any) -> None:
        exc = retry_state.outcome.exception() if retry_state.outcome else None
        exc_name = type(exc).__name__ if exc else "unknown"
        exc_response = getattr(exc, "response", None) if exc is not None else None
        status_or_type = (
            f"HTTP {exc_response.status_code}"
            if exc_response is not None
            else exc_name
        )
        _log.warning(
            "HTTP error (attempt %d/%d): %s. Retrying with exponential backoff...",
            retry_state.attempt_number,
            max_attempts,
            status_or_type,
        )

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_random_exponential(min=min_wait, max=max_wait),
        retry=retry_if_exception(_should_retry),
        reraise=True,
        before_sleep=_before_sleep_log,
    )
