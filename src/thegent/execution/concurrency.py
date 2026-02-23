"""Concurrency control - ConcurrencyController, InterruptionTracker.

Extracted from execution.py for maintainability.
"""

from __future__ import annotations

# Re-export from execution.py for now
from thegent.execution import (
    ConcurrencyController,
    ContinuityWatchdog,
    DeferralQueue,
    InterruptionTracker,
)

__all__ = [
    "ConcurrencyController",
    "ContinuityWatchdog",
    "DeferralQueue",
    "InterruptionTracker",
]
