"""Resilience patterns - DLQ, Circuit Breaker, Escalation.

Extracted from execution.py for maintainability.
"""

from __future__ import annotations

import logging

_log = logging.getLogger(__name__)


# Re-export from execution.py for now
# TODO: Move implementations here
from thegent.execution import (
    CircuitBreakerRegistry,
    DLQManager,
    DeferralQueue,
    EscalationQueue,
    IdempotencyManager,
    OverrideRegistry,
)

__all__ = [
    "CircuitBreakerRegistry",
    "DLQManager",
    "DeferralQueue",
    "EscalationQueue",
    "IdempotencyManager",
    "OverrideRegistry",
]
