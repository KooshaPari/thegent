"""Unit tests for retry policy pull-only mode.

# @trace WL-212
"""

from __future__ import annotations

import pytest

from thegent.sync.retry import RetryPolicy, operation_mode, should_retry


@pytest.mark.requirement("WL-212")
def test_pull_only_mode_enabled_after_write_failure():
    policy = RetryPolicy(max_attempts=3, pull_only_on_failure=True)
    assert operation_mode(write_failures=1, policy=policy) == "pull-only"


@pytest.mark.requirement("WL-212")
def test_pull_only_mode_disabled_without_failure():
    policy = RetryPolicy(max_attempts=3, pull_only_on_failure=True)
    assert operation_mode(write_failures=0, policy=policy) == "bidirectional"


@pytest.mark.requirement("WL-212")
def test_should_retry_respects_max_attempts():
    policy = RetryPolicy(max_attempts=2, pull_only_on_failure=False)
    assert should_retry(attempt=1, policy=policy) is True
    assert should_retry(attempt=2, policy=policy) is False
