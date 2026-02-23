"""Retry Class Policy (WL-251): Classify errors and determine retry strategies.

Provides error classification based on error patterns and associated retry behavior.
Supports transient, permanent, and rate-limited error types with configurable
maximum attempt counts per error class.

# @trace WL-251
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Error Classification
# ---------------------------------------------------------------------------


class RetryClass(Enum):
    """Error classification for retry behavior."""

    TRANSIENT = "transient"
    """Temporary failure; retry is safe and recommended."""

    PERMANENT = "permanent"
    """Permanent failure; retrying will not help."""

    RATE_LIMITED = "rate_limited"
    """API rate limit or quota exceeded; retry with backoff."""


# ---------------------------------------------------------------------------
# Policy Configuration
# ---------------------------------------------------------------------------


@dataclass
class RetryClassPolicy:
    """Policy for a single error pattern classification.

    Attributes:
        error_pattern: Substring to match in error messages (case-insensitive).
        retry_class: The retry class assigned to matching errors.
        max_attempts: Maximum total attempts for this error (default: 3).
    """

    error_pattern: str
    """Substring to match in error messages (case-insensitive)."""

    retry_class: RetryClass
    """The retry class for matching errors."""

    max_attempts: int = 3
    """Maximum total attempts (including initial attempt)."""

    def __post_init__(self) -> None:
        """Validate policy configuration."""
        if not self.error_pattern:
            raise ValueError("error_pattern cannot be empty")
        if self.max_attempts < 1:
            raise ValueError(f"max_attempts must be >= 1, got {self.max_attempts}")


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------


class RetryClassifier:
    """Classifies errors and determines retry behavior.

    Uses substring matching on error messages against registered policies.
    Returns the first matching policy's retry class, or TRANSIENT as default.
    """

    # Default max attempts by retry class
    DEFAULT_MAX_ATTEMPTS: ClassVar[dict[RetryClass, int]] = {
        RetryClass.TRANSIENT: 3,
        RetryClass.PERMANENT: 1,
        RetryClass.RATE_LIMITED: 5,
    }

    def __init__(self) -> None:
        """Initialize the retry classifier."""
        self._policies: list[RetryClassPolicy] = []

    def add_policy(
        self,
        error_pattern: str,
        retry_class: RetryClass,
        max_attempts: int = 3,
    ) -> RetryClassPolicy:
        """Register an error classification policy.

        Args:
            error_pattern: Substring to match in error messages (case-insensitive).
            retry_class: The retry class for matching errors.
            max_attempts: Maximum total attempts for this error (default: 3).

        Returns:
            The registered RetryClassPolicy.

        Raises:
            ValueError: If policy is invalid.

        Example:
            >>> classifier = RetryClassifier()
            >>> classifier.add_policy("Connection timeout", RetryClass.TRANSIENT, max_attempts=3)
            >>> classifier.add_policy("Permission denied", RetryClass.PERMANENT, max_attempts=1)
            >>> classifier.add_policy("Rate limit exceeded", RetryClass.RATE_LIMITED, max_attempts=5)
        """
        policy = RetryClassPolicy(
            error_pattern=error_pattern,
            retry_class=retry_class,
            max_attempts=max_attempts,
        )
        self._policies.append(policy)
        logger.debug(
            "Registered retry policy: pattern=%r, class=%s, max_attempts=%d",
            error_pattern,
            retry_class.value,
            max_attempts,
        )
        return policy

    def classify(self, error_message: str) -> RetryClass:
        """Classify an error and return its retry class.

        Matches error_message against registered policies using substring matching
        (case-insensitive). Returns the first matching policy's retry class.

        Args:
            error_message: The error message to classify.

        Returns:
            The RetryClass for the error. Defaults to TRANSIENT if no match.

        Example:
            >>> classifier = RetryClassifier()
            >>> classifier.add_policy("timeout", RetryClass.TRANSIENT)
            >>> classifier.add_policy("denied", RetryClass.PERMANENT)
            >>> classifier.classify("Connection timeout occurred")
            <RetryClass.TRANSIENT: 'transient'>
            >>> classifier.classify("Permission denied")
            <RetryClass.PERMANENT: 'permanent'>
            >>> classifier.classify("Unknown error")
            <RetryClass.TRANSIENT: 'transient'>
        """
        error_lower = error_message.lower()
        for policy in self._policies:
            if policy.error_pattern.lower() in error_lower:
                logger.debug(
                    "Error classified as %s (matched pattern: %r)",
                    policy.retry_class.value,
                    policy.error_pattern,
                )
                return policy.retry_class

        logger.debug("Error not matched by any policy; defaulting to TRANSIENT")
        return RetryClass.TRANSIENT

    def should_retry(self, error_message: str, attempt: int) -> bool:
        """Determine whether to retry based on error and attempt count.

        Args:
            error_message: The error message to evaluate.
            attempt: The current attempt number (1-indexed, so first attempt is 1).

        Returns:
            True if the error should be retried, False otherwise.

        Raises:
            ValueError: If attempt < 1.

        Example:
            >>> classifier = RetryClassifier()
            >>> classifier.add_policy("timeout", RetryClass.TRANSIENT, max_attempts=3)
            >>> classifier.add_policy("denied", RetryClass.PERMANENT, max_attempts=1)
            >>> classifier.should_retry("Connection timeout", attempt=1)
            True
            >>> classifier.should_retry("Connection timeout", attempt=3)
            False
            >>> classifier.should_retry("Permission denied", attempt=1)
            False
        """
        if attempt < 1:
            raise ValueError(f"attempt must be >= 1, got {attempt}")

        # Find matching policy for max_attempts
        retry_class = self.classify(error_message)
        max_attempts = self.DEFAULT_MAX_ATTEMPTS.get(
            retry_class,
            self.DEFAULT_MAX_ATTEMPTS[RetryClass.TRANSIENT],
        )

        # Override max_attempts if a matching policy exists
        for policy in self._policies:
            if policy.error_pattern.lower() in error_message.lower():
                max_attempts = policy.max_attempts
                break

        should_retry = attempt < max_attempts
        logger.debug(
            "Retry decision: class=%s, attempt=%d, max_attempts=%d, should_retry=%s",
            retry_class.value,
            attempt,
            max_attempts,
            should_retry,
        )
        return should_retry
