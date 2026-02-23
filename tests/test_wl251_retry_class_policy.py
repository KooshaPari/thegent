"""Tests for WL-251: Retry Class Policy.

Verifies error classification and retry decision-making.

# @trace WL-251
"""

from __future__ import annotations

import pytest

from thegent.integrations.retry_class_policy import (
    RetryClass,
    RetryClassifier,
    RetryClassPolicy,
)


@pytest.mark.requirement("WL-251")
class TestRetryClassPolicy:
    """WL-251: Retry class policy."""

    def test_policy_creation(self):
        """RetryClassPolicy instantiation succeeds with valid inputs."""
        policy = RetryClassPolicy(
            error_pattern="timeout",
            retry_class=RetryClass.TRANSIENT,
            max_attempts=3,
        )
        assert policy.error_pattern == "timeout"
        assert policy.retry_class == RetryClass.TRANSIENT
        assert policy.max_attempts == 3

    def test_policy_validation_empty_pattern(self):
        """RetryClassPolicy rejects empty error_pattern."""
        with pytest.raises(ValueError, match="error_pattern cannot be empty"):
            RetryClassPolicy(
                error_pattern="",
                retry_class=RetryClass.TRANSIENT,
            )

    def test_policy_validation_invalid_max_attempts(self):
        """RetryClassPolicy rejects max_attempts < 1."""
        with pytest.raises(ValueError, match="max_attempts must be >= 1"):
            RetryClassPolicy(
                error_pattern="error",
                retry_class=RetryClass.TRANSIENT,
                max_attempts=0,
            )

    def test_classifier_add_policy(self):
        """add_policy() registers a policy and returns it."""
        classifier = RetryClassifier()
        policy = classifier.add_policy(
            "timeout",
            RetryClass.TRANSIENT,
            max_attempts=3,
        )
        assert policy.error_pattern == "timeout"
        assert policy.retry_class == RetryClass.TRANSIENT

    def test_classifier_classify_no_match(self):
        """classify() returns TRANSIENT for unmatched error."""
        classifier = RetryClassifier()
        classifier.add_policy("timeout", RetryClass.TRANSIENT)
        result = classifier.classify("Unknown error")
        assert result == RetryClass.TRANSIENT

    def test_classifier_classify_first_match(self):
        """classify() returns first matching policy's class."""
        classifier = RetryClassifier()
        classifier.add_policy("timeout", RetryClass.TRANSIENT)
        classifier.add_policy("denied", RetryClass.PERMANENT)
        result = classifier.classify("Connection timeout occurred")
        assert result == RetryClass.TRANSIENT

    def test_classifier_classify_case_insensitive(self):
        """classify() performs case-insensitive matching."""
        classifier = RetryClassifier()
        classifier.add_policy("TIMEOUT", RetryClass.TRANSIENT)
        result = classifier.classify("connection timeout")
        assert result == RetryClass.TRANSIENT

    def test_classifier_classify_multiple_policies(self):
        """classify() returns correct class for different errors."""
        classifier = RetryClassifier()
        classifier.add_policy("timeout", RetryClass.TRANSIENT)
        classifier.add_policy("permission denied", RetryClass.PERMANENT)
        classifier.add_policy("rate limit", RetryClass.RATE_LIMITED)

        assert classifier.classify("Connection timeout") == RetryClass.TRANSIENT
        assert (
            classifier.classify("Permission denied") == RetryClass.PERMANENT
        )
        assert (
            classifier.classify("Rate limit exceeded") == RetryClass.RATE_LIMITED
        )

    def test_classifier_should_retry_invalid_attempt(self):
        """should_retry() raises ValueError for attempt < 1."""
        classifier = RetryClassifier()
        with pytest.raises(ValueError, match="attempt must be >= 1"):
            classifier.should_retry("error", attempt=0)

    def test_classifier_should_retry_transient(self):
        """should_retry() returns True for transient errors within limit."""
        classifier = RetryClassifier()
        classifier.add_policy("timeout", RetryClass.TRANSIENT, max_attempts=3)

        assert classifier.should_retry("Connection timeout", attempt=1)
        assert classifier.should_retry("Connection timeout", attempt=2)
        assert not classifier.should_retry("Connection timeout", attempt=3)

    def test_classifier_should_retry_permanent(self):
        """should_retry() returns False for permanent errors."""
        classifier = RetryClassifier()
        classifier.add_policy("denied", RetryClass.PERMANENT, max_attempts=1)

        assert not classifier.should_retry("Permission denied", attempt=1)

    def test_classifier_should_retry_rate_limited(self):
        """should_retry() respects rate-limited max_attempts."""
        classifier = RetryClassifier()
        classifier.add_policy(
            "rate limit",
            RetryClass.RATE_LIMITED,
            max_attempts=5,
        )

        assert classifier.should_retry("Rate limit exceeded", attempt=1)
        assert classifier.should_retry("Rate limit exceeded", attempt=4)
        assert not classifier.should_retry("Rate limit exceeded", attempt=5)

    def test_classifier_should_retry_unmatched_uses_defaults(self):
        """should_retry() uses default max_attempts for unmatched errors."""
        classifier = RetryClassifier()
        # No policies; should use default TRANSIENT max_attempts = 3
        assert classifier.should_retry("Unknown error", attempt=1)
        assert classifier.should_retry("Unknown error", attempt=2)
        assert not classifier.should_retry("Unknown error", attempt=3)

    def test_classifier_multiple_registrations(self):
        """add_policy() can register multiple policies."""
        classifier = RetryClassifier()
        p1 = classifier.add_policy("timeout", RetryClass.TRANSIENT)
        p2 = classifier.add_policy("denied", RetryClass.PERMANENT)
        p3 = classifier.add_policy("rate limit", RetryClass.RATE_LIMITED)

        assert p1.error_pattern == "timeout"
        assert p2.error_pattern == "denied"
        assert p3.error_pattern == "rate limit"

    def test_classifier_policy_override(self):
        """Later policies do not override earlier ones (first match wins)."""
        classifier = RetryClassifier()
        classifier.add_policy("error", RetryClass.TRANSIENT)
        classifier.add_policy("error", RetryClass.PERMANENT)

        # First match (TRANSIENT) should be returned
        result = classifier.classify("This is an error")
        assert result == RetryClass.TRANSIENT

    def test_classifier_substring_matching(self):
        """classify() uses substring matching, not exact match."""
        classifier = RetryClassifier()
        classifier.add_policy("timeout", RetryClass.TRANSIENT)
        result = classifier.classify("Connection timeout after 5 seconds")
        assert result == RetryClass.TRANSIENT

    def test_retry_class_values(self):
        """RetryClass enum has expected values."""
        assert RetryClass.TRANSIENT.value == "transient"
        assert RetryClass.PERMANENT.value == "permanent"
        assert RetryClass.RATE_LIMITED.value == "rate_limited"
