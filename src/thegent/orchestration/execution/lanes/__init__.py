"""Lane model + canonical lane priority/urgency tables (FR-019).

@trace AUDIT-N+34 dormant-core hardening.
@trace FR-019 -- Adaptive load controls with critical lane protection.

SOTA pass-18 hardening of the dormant-core `LaneModel` +
`LANE_PRIORITIES` + `Lane` enum-style attrs. See
``tests/test_unit_audit_n34_lanes_priority_queue_hardening.py`` for the
NEW-1..NEW-9 contracts; see ``tests/test_unit_orchestration_lanes.py``
+ ``tests/orchestration/test_priority_queue.py`` for the prior dormant
contracts that this surface also satisfies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Urgency constants (FR-019)
# ---------------------------------------------------------------------------

URGENCY_CRITICAL = 1.0
URGENCY_HIGH = 0.8
URGENCY_NORMAL = 0.5
URGENCY_LOW = 0.3

# ---------------------------------------------------------------------------
# Canonical lane priority / urgency tables (NEW-1, NEW-2)
# ---------------------------------------------------------------------------
#
# Lower integer = higher priority (dequeue order). ``critical`` is 0 so it
# always preempts everything else; ``background`` is 100 so it always
# defers. The default fallback for unknown lane names is 50
# (see ``LaneModel.get_priority``).
#
# The urgency values are independent; ``URGENCY_NORMAL`` is the
# standard lane's urgency, ``URGENCY_HIGH`` is the recovery lane's
# urgency, etc. Unknown lanes fall back to ``URGENCY_NORMAL``.

LANE_PRIORITIES: dict[str, int] = {
    "critical": 0,
    "standard": 10,
    "recovery": 20,
    "background": 100,
}

LANE_URGENCY: dict[str, float] = {
    "critical": URGENCY_CRITICAL,
    "standard": URGENCY_NORMAL,
    "recovery": URGENCY_HIGH,
    "background": URGENCY_LOW,
}


# ---------------------------------------------------------------------------
# Lane enum-style facade (NEW-8)
# ---------------------------------------------------------------------------
#
# The original ``Lane`` dataclass is preserved for backwards
# compatibility (constructs ``Lane(name=..., priority=..., capacity=...)``
# continue to work). In addition, the canonical lane names are exposed
# as class attributes so callers can refer to ``Lane.CRITICAL`` instead
# of the string literal ``"critical"``.


@dataclass
class Lane:
    """A lane for task execution.

    Backwards-compatible dataclass form (constructs with
    ``name``/``priority``/``capacity``). In addition, the canonical
    lane names are exposed as class attributes (NEW-8):

    * ``Lane.CRITICAL == "critical"``
    * ``Lane.STANDARD == "standard"``
    * ``Lane.RECOVERY == "recovery"``
    * ``Lane.BACKGROUND == "background"``
    """

    name: str
    priority: int = 2
    capacity: int = 10

    # NEW-8: enum-style attrs string-equal their lane names.
    CRITICAL: str = "critical"
    STANDARD: str = "standard"
    RECOVERY: str = "recovery"
    BACKGROUND: str = "background"


# ---------------------------------------------------------------------------
# LaneModel -- the public facade the executor / cockpit consume
# ---------------------------------------------------------------------------


class LaneModel:
    """Model for a lane (canonical API).

    All public methods are static-ish classmethods (instance construction
    is also supported for backwards compatibility). The hardened API
    surfaces the canonical ``LANE_PRIORITIES`` map, case-insensitive
    lookups, the FR-019 critical-lane protection predicate, and the
    ``sort_tasks`` / ``check_capacity`` helpers the swarm scheduler
    consumes.
    """

    def __init__(self, name: str, priority: int = 2) -> None:
        self.name = name
        self.priority = priority

    # ------------------------------------------------------------------
    # Priority lookup (NEW-3)
    # ------------------------------------------------------------------

    @staticmethod
    def get_priority(name: str) -> int:
        """Return the integer priority for ``name`` (lower = earlier).

        * Case-insensitive (``"CRITICAL"`` == ``"critical"``).
        * Empty / unknown names fall back to the default of ``50``.
        * Returns a real ``int`` (not ``bool``).
        """
        if not name:
            return 50
        canonical = name.strip().lower()
        if canonical in LANE_PRIORITIES:
            value = LANE_PRIORITIES[canonical]
            # Ensure bool never leaks out of the dict lookup.
            return int(value) if isinstance(value, bool) else value
        return 50

    # ------------------------------------------------------------------
    # Urgency lookup (NEW-4)
    # ------------------------------------------------------------------

    @staticmethod
    def get_urgency(name: str) -> float:
        """Return the urgency score for ``name`` (float in ``(0, 1]``).

        * Case-insensitive.
        * Unknown / empty lanes fall back to ``URGENCY_NORMAL`` (0.5).
        """
        if not name:
            return URGENCY_NORMAL
        canonical = name.strip().lower()
        if canonical in LANE_URGENCY:
            value = LANE_URGENCY[canonical]
            return float(value)
        return URGENCY_NORMAL

    # ------------------------------------------------------------------
    # FR-019 critical-lane protection (NEW-5)
    # ------------------------------------------------------------------

    @staticmethod
    def is_protected(name: str) -> bool:
        """Return ``True`` iff ``name`` is the critical lane.

        All other lanes (including unknown / empty) are unprotected.
        """
        if not name:
            return False
        return name.strip().lower() == "critical"

    # ------------------------------------------------------------------
    # sort_tasks -- stable, defensive (NEW-6, NEW-9)
    # ------------------------------------------------------------------

    @staticmethod
    def sort_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Return a fresh list of ``tasks`` sorted by lane priority.

        Sort key is ``(priority asc, started_at_utc asc)`` so that:
        * Critical (0) beats Standard (10) beats Recovery (20) beats
          Background (100).
        * Within the same lane, older ``started_at_utc`` wins.

        Tasks missing ``"lane"`` default to ``"standard"``. The input
        list is **not** mutated (defensive copy); the returned list is a
        fresh ``list`` (NEW-9).
        """
        # Defensive copy of the outer list -- do not mutate caller.
        if not tasks:
            return []
        snapshot = list(tasks)
        snapshot.sort(
            key=lambda t: (
                LaneModel.get_priority(t.get("lane") or "standard"),
                t.get("started_at_utc", ""),
            )
        )
        return snapshot

    # ------------------------------------------------------------------
    # check_capacity -- FR-019 reserved slots (NEW-7)
    # ------------------------------------------------------------------

    @staticmethod
    def check_capacity(
        name: str,
        *,
        active_count: int,
        total_capacity: int,
    ) -> bool:
        """Return ``True`` if ``name`` can take another concurrent run.

        * Critical lane **always** returns ``True`` (bypasses overload).
        * Non-critical lanes have 2 reserved slots held back for
          critical; they return ``True`` iff
          ``active_count < total_capacity - 2``.
        * ``total_capacity < 2`` is floored at
          ``max(active_count, 1)`` -- the critical lane must always
          retain at least one slot even when ``total_capacity`` is
          pathological.
        """
        if LaneModel.is_protected(name):
            return True
        # Non-critical: total_capacity < 2 floors at max(active_count, 1)
        # so critical always keeps a slot.
        if total_capacity < 2:
            return active_count < max(total_capacity, 1)
        return active_count < (total_capacity - 2)


__all__ = [
    "LANE_PRIORITIES",
    "LANE_URGENCY",
    "URGENCY_CRITICAL",
    "URGENCY_HIGH",
    "URGENCY_LOW",
    "URGENCY_NORMAL",
    "Lane",
    "LaneModel",
]
