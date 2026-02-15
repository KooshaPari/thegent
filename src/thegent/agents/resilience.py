"""Retry and fallback logic for agent runs.

Distinguishes:
- rate_limit / transient: retry same provider (429, 502/503/504, etc.)
- usage_limit: subscription/quota exhausted; fallback to different provider.
"""

import re
from collections.abc import Callable
from enum import Enum
from typing import TypeVar

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from thegent.agents.base import RunResult

T = TypeVar("T")


class FailureKind(str, Enum):
    """Classification of agent run failure."""

    RATE_LIMIT = "rate_limit"  # 429, too many requests; retry same provider
    TRANSIENT = "transient"  # 502/503/504, reconnecting; retry same provider
    USAGE_LIMIT = "usage_limit"  # Quota/subscription exhausted; fallback to different provider
    UNKNOWN = "unknown"  # Not retryable, not fallback-worthy


# Retry same provider: rate limit or transient gateway/network
_RETRYABLE_PATTERNS = (
    r"429",
    r"rate[\s_-]?limit",
    r"502\s+bad\s+gateway",
    r"503\s+service\s+unavailable",
    r"504\s+gateway\s+timeout",
    r"\b502\b",
    r"\b503\b",
    r"\b504\b",
    r"too\s+many\s+requests",
    r"reconnecting",
    r"retry\s+after",
)

# Usage/subscription limits: fallback to different provider (do not retry same)
_USAGE_LIMIT_PATTERNS = (
    r"quota\s+exceeded",
    r"quota\s+limit",
    r"usage\s+limit",
    r"subscription\s+(exceeded|limit)",
    r"billing\s+(exceeded|limit)",
    r"insufficient\s+(quota|credits)",
    r"out\s+of\s+(quota|credits)",
    r"monthly\s+limit",
    r"daily\s+limit",
)


class TransientAgentError(Exception):
    """Raised when agent failed due to retryable condition (rate limit, 502, etc.)."""

    def __init__(self, result: RunResult) -> None:
        self.result = result
        msg = (result.stderr or "")[:300]
        super().__init__(msg)


class UsageLimitError(Exception):
    """Raised when provider hit usage/quota limit; caller should fallback to different provider."""

    def __init__(self, result: RunResult, agent: str = "") -> None:
        self.result = result
        self.agent = agent
        msg = (result.stderr or "")[:300]
        super().__init__(msg)


def classify_failure(result: RunResult) -> FailureKind:
    """Classify failure as rate_limit (retry), usage_limit (fallback), or unknown."""
    if result.exit_code == 0:
        return FailureKind.UNKNOWN
    text = (result.stderr or "").lower()
    # Check usage limit first (subscription/quota exhausted)
    if any(re.search(p, text, re.IGNORECASE) for p in _USAGE_LIMIT_PATTERNS):
        return FailureKind.USAGE_LIMIT
    # Then rate limit or transient
    if any(re.search(p, text, re.IGNORECASE) for p in _RETRYABLE_PATTERNS):
        return FailureKind.RATE_LIMIT if "429" in text or "rate" in text or "too many" in text else FailureKind.TRANSIENT
    return FailureKind.UNKNOWN


def is_retryable(result: RunResult) -> bool:
    """Return True if failure is rate_limit or transient (retry same provider)."""
    k = classify_failure(result)
    return k in (FailureKind.RATE_LIMIT, FailureKind.TRANSIENT)


def is_usage_limit(result: RunResult) -> bool:
    """Return True if failure indicates usage/quota limit (fallback to different provider)."""
    return classify_failure(result) == FailureKind.USAGE_LIMIT


def with_retry(
    max_attempts: int = 4,
    min_wait: float = 2.0,
    max_wait: float = 60.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that retries on TransientAgentError with exponential backoff."""

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        return retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            retry=retry_if_exception_type(TransientAgentError),
            reraise=True,
        )(fn)

    return decorator
