"""Retry policy helpers with pull-only-on-failure mode.

# @trace WL-212
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    pull_only_on_failure: bool = False


def should_retry(*, attempt: int, policy: RetryPolicy) -> bool:
    if policy.max_attempts <= 0:
        raise ValueError("max_attempts must be positive")
    return attempt < policy.max_attempts


def operation_mode(*, write_failures: int, policy: RetryPolicy) -> str:
    if write_failures < 0:
        raise ValueError("write_failures cannot be negative")
    if policy.pull_only_on_failure and write_failures > 0:
        return "pull-only"
    return "bidirectional"
