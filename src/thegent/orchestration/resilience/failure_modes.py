"""MAST 14-mode failure taxonomy (WP-2005, FR-007)."""

from __future__ import annotations

from enum import StrEnum


class FailureMode(StrEnum):
    """MAST 14-mode failure taxonomy for classification and recovery."""

    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    AUTH_FAILURE = "auth_failure"
    NETWORK_PARTITION = "network_partition"
    MALFORMED_RESPONSE = "malformed_response"
    STATE_CORRUPTION = "state_corruption"
    BUDGET_EXCEEDED = "budget_exceeded"
    CIRCUIT_OPEN = "circuit_open"
    POLICY_DENY = "policy_deny"
    CONTRACT_DRIFT = "contract_drift"
    RETRY_EXHAUSTED = "retry_exhausted"
    CHECKPOINT_FAILED = "checkpoint_failed"
    ROLLBACK_TRIGGERED = "rollback_triggered"
    UNKNOWN = "unknown"


def classify_failure(error_message: str) -> FailureMode:
    """Classify failure from error message to MAST mode."""
    msg = (error_message or "").lower()
    if "timeout" in msg or "timed out" in msg:
        return FailureMode.TIMEOUT
    if "rate limit" in msg or "429" in msg:
        return FailureMode.RATE_LIMIT
    if "auth" in msg or "401" in msg or "403" in msg or "unauthorized" in msg:
        return FailureMode.AUTH_FAILURE
    if "network" in msg or "connection" in msg or "partition" in msg:
        return FailureMode.NETWORK_PARTITION
    if "malformed" in msg or "parse" in msg or "json" in msg:
        return FailureMode.MALFORMED_RESPONSE
    if "corrupt" in msg or "integrity" in msg:
        return FailureMode.STATE_CORRUPTION
    if "budget" in msg or "quota" in msg:
        return FailureMode.BUDGET_EXCEEDED
    if "circuit" in msg or "breaker" in msg:
        return FailureMode.CIRCUIT_OPEN
    if "policy" in msg or "deny" in msg:
        return FailureMode.POLICY_DENY
    if "drift" in msg or "contract" in msg:
        return FailureMode.CONTRACT_DRIFT
    if "retry" in msg or "exhausted" in msg:
        return FailureMode.RETRY_EXHAUSTED
    if "checkpoint" in msg:
        return FailureMode.CHECKPOINT_FAILED
    if "rollback" in msg:
        return FailureMode.ROLLBACK_TRIGGERED
    return FailureMode.UNKNOWN
