# @trace WL-202 B90-W2-B1
"""Anti-flap hysteresis to prevent rapid status oscillation.

Prevents work items from rapidly changing status back and forth within
a single sync cycle or across consecutive cycles.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional


@dataclass
class HysteresisConfig:
    """Configuration for hysteresis gate.

    Attributes:
        min_stable_cycles: Minimum number of stable cycles before allowing transition.
        cooldown_seconds: Cooldown period after a transition before allowing another.
    """

    min_stable_cycles: int = 2
    cooldown_seconds: int = 300


@dataclass
class _TransitionRecord:
    """Internal record of a transition event.

    Attributes:
        from_status: Status before transition
        to_status: Status after transition
        timestamp: When the transition occurred
    """

    from_status: str
    to_status: str
    timestamp: datetime


class HysteresisGate:
    """Gate to prevent rapid status oscillation (flapping).

    Tracks recent transitions per work item and prevents rapid back-and-forth
    changes based on configurable stable cycle counts and cooldown periods.
    """

    def __init__(self, config: Optional[HysteresisConfig] = None):
        """Initialize the hysteresis gate.

        Args:
            config: HysteresisConfig. Defaults to HysteresisConfig() if not provided.
        """
        self.config = config or HysteresisConfig()
        # Track recent transitions per WL item: wl_id -> list of _TransitionRecord
        self._transition_history: dict[str, list[_TransitionRecord]] = {}

    def should_apply_transition(self, wl_id: str, new_status: str) -> bool:
        """Determine whether a transition should be applied.

        A transition is blocked if:
        1. The item recently transitioned to new_status (cooldown active), or
        2. The item recently oscillated between two statuses (flapping).

        Args:
            wl_id: Work item identifier
            new_status: Proposed new status

        Returns:
            True if transition should be applied, False if blocked by hysteresis.
        """
        now = datetime.now(timezone.utc)

        # Get or initialize transition history for this WL item
        if wl_id not in self._transition_history:
            self._transition_history[wl_id] = []

        history = self._transition_history[wl_id]

        # Clean up old transitions (older than cooldown period)
        cutoff = now - timedelta(seconds=self.config.cooldown_seconds)
        self._transition_history[wl_id] = [
            t for t in history if t.timestamp > cutoff
        ]
        history = self._transition_history[wl_id]

        # If no recent transitions, allow
        if not history:
            return True

        last_transition = history[-1]

        # Check cooldown: if we just transitioned to this status, block
        if last_transition.to_status == new_status:
            time_since = (now - last_transition.timestamp).total_seconds()
            if time_since < self.config.cooldown_seconds:
                return False

        # Check for flapping: if we're oscillating back to a previous status
        # within min_stable_cycles transitions, block
        if len(history) >= self.config.min_stable_cycles:
            recent = history[-self.config.min_stable_cycles :]
            # Check if the pattern shows oscillation back to new_status
            for old_trans in recent:
                if old_trans.to_status == new_status:
                    # We've been in new_status recently; check for flapping
                    # by seeing if we've transitioned away and are trying to return
                    if last_transition.to_status != new_status:
                        return False

        return True

    def record_transition(
        self, wl_id: str, from_status: str, to_status: str
    ) -> None:
        """Record a transition that was applied.

        Args:
            wl_id: Work item identifier
            from_status: Source status
            to_status: Target status
        """
        if wl_id not in self._transition_history:
            self._transition_history[wl_id] = []

        self._transition_history[wl_id].append(
            _TransitionRecord(
                from_status=from_status,
                to_status=to_status,
                timestamp=datetime.now(timezone.utc),
            )
        )
