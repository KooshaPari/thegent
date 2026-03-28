"""WP-4004: Interruption taxonomy and fatigue controls."""

import enum
import logging
import time

from phenotype_thegent_core.config import ThegentSettings

_log = logging.getLogger(__name__)


class InterruptionKind(enum.StrEnum):
    """Kinds of system interruptions."""

    POLICY_DENY = "policy_deny"
    CIRCUIT_BREAK = "circuit_break"
    ESCALATION = "escalation"
    WORKER_FAIL = "worker_fail"
    HUMAN_STOP = "human_stop"


class AlertFatigueController:
    """Manages alert volume and prevents operator fatigue."""

    def __init__(self, settings: ThegentSettings) -> None:
        self.settings = settings
        self.alerts_history = []  # (timestamp, kind)
        self.cooldown_window = 300  # 5 minutes
        self.max_alerts_per_window = 10

    def record_alert(self, kind: InterruptionKind) -> bool:
        """Record an alert and return True if it should be suppressed due to fatigue."""
        now = time.time()
        # Clean old alerts
        self.alerts_history = [a for a in self.alerts_history if now - a[0] < self.cooldown_window]

        should_suppress = len(self.alerts_history) >= self.max_alerts_per_window

        if not should_suppress:
            self.alerts_history.append((now, kind))

        return should_suppress

    def get_fatigue_level(self) -> float:
        """Return fatigue level from 0.0 to 1.0."""
        return min(1.0, len(self.alerts_history) / self.max_alerts_per_window)
