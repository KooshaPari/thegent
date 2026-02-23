"""Lane control - LaneController, CalibrationRegistry.

Extracted from execution.py for maintainability.
"""

from __future__ import annotations

# Re-export from execution.py for now
from thegent.execution import (
    CalibrationRegistry,
    LaneController,
)

__all__ = [
    "CalibrationRegistry",
    "LaneController",
]
