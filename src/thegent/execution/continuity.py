"""Continuity and handoff - ContinuityPacket, HandoffManager.

Extracted from execution.py for maintainability.
"""

from __future__ import annotations

# Re-export from execution.py for now
from thegent.execution import (
    ContinuityPacket,
    FreshnessValidator,
    HandoffManager,
)

__all__ = [
    "ContinuityPacket",
    "FreshnessValidator",
    "HandoffManager",
]
