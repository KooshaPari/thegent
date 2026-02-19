"""Priority and urgency lane model (WP-1002, FR-019).

Defines execution lanes with priority ordering and critical lane protection.
Critical lane bypasses overload rejection and gets reserved capacity under burst.
"""

from __future__ import annotations

from enum import Enum, StrEnum
from types import MappingProxyType
from typing import Any, ClassVar

# Lane priority: lower numeric value = higher priority (dispatched first)
# FR-019: critical lane protected under burst; reserved slots prevent starvation
_LANE_PRIORITIES_RAW: dict[str, int] = {
    "critical": 0,
    "standard": 10,
    "recovery": 20,
    "background": 100,
}
LANE_PRIORITIES: MappingProxyType[str, int] = MappingProxyType(_LANE_PRIORITIES_RAW)

# Urgency tier for policy and SLO decisions
URGENCY_CRITICAL = "critical"
URGENCY_HIGH = "high"
URGENCY_NORMAL = "normal"
URGENCY_LOW = "low"

_LANE_URGENCY_RAW: dict[str, str] = {
    "critical": URGENCY_CRITICAL,
    "standard": URGENCY_NORMAL,
    "recovery": URGENCY_HIGH,
    "background": URGENCY_LOW,
}
LANE_URGENCY: MappingProxyType[str, str] = MappingProxyType(_LANE_URGENCY_RAW)


class Lane(StrEnum):
    """Canonical execution lanes (WP-1002)."""

    CRITICAL = "critical"
    STANDARD = "standard"
    RECOVERY = "recovery"
    BACKGROUND = "background"


class LaneModel:
    """Priority and urgency lane model for task management (WP-1002, FR-019).

    Usage:
        model = LaneModel()
        model.get_priority("critical")  # 0 (highest)
        model.is_protected("critical")   # True - bypasses overload rejection
        model.reserved_slots_for_critical  # 2
    """

    priorities: ClassVar[MappingProxyType[str, int]] = LANE_PRIORITIES
    urgency: ClassVar[MappingProxyType[str, str]] = LANE_URGENCY
    reserved_slots_for_critical: ClassVar[int] = 2

    @classmethod
    def get_priority(cls, lane: str) -> int:
        """Return numeric priority for a lane (lower = higher priority)."""
        return cls.priorities.get(lane.lower() if lane else "", 50)

    @classmethod
    def get_urgency(cls, lane: str) -> str:
        """Return urgency tier for a lane."""
        return cls.urgency.get(lane.lower() if lane else "", URGENCY_NORMAL)

    @classmethod
    def is_protected(cls, lane: str) -> bool:
        """True if lane bypasses overload rejection (FR-019 critical lane protection)."""
        return (lane or "").lower() == Lane.CRITICAL

    @classmethod
    def sort_tasks(cls, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Sort tasks by lane priority (asc) then by creation time (asc)."""
        return sorted(
            tasks,
            key=lambda x: (
                cls.get_priority(x.get("lane", "standard")),
                x.get("started_at_utc", x.get("blocked_at_utc", "")),
            ),
        )

    @classmethod
    def check_capacity(
        cls,
        lane: str,
        active_count: int,
        total_capacity: int,
    ) -> bool:
        """Check if lane has capacity (starvation prevention, FR-019).

        Critical lane always has capacity. Non-critical lanes leave reserved
        slots for critical to prevent starvation under burst.
        """
        if cls.is_protected(lane):
            return True
        available = total_capacity - cls.reserved_slots_for_critical
        return active_count < max(1, available)
