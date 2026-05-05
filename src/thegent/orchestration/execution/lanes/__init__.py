"""Stub module."""
from dataclasses import dataclass


# Lane priority constants
LANE_PRIORITIES = {
    "critical": 0,
    "high": 1,
    "normal": 2,
    "low": 3,
    "background": 4,
}

LANE_URGENCY = {
    "critical": 1.0,
    "high": 0.8,
    "normal": 0.5,
    "low": 0.3,
    "background": 0.1,
}


@dataclass
class Lane:
    """A lane for task execution."""
    name: str
    priority: int = 2
    capacity: int = 10


__all__ = ["LANE_PRIORITIES", "LANE_URGENCY", "Lane", "URGENCY_CRITICAL", "URGENCY_HIGH", "URGENCY_LOW", "URGENCY_NORMAL", "LaneModel"]


URGENCY_CRITICAL = 1.0
URGENCY_HIGH = 0.8
URGENCY_LOW = 0.3
URGENCY_NORMAL = 0.5


class LaneModel:
    """Model for a lane."""

    def __init__(self, name: str, priority: int = 2) -> None:
        self.name = name
        self.priority = priority
