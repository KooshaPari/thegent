"""Deterministic phase transition contracts (WP-1004, FR-004).

Defines allowed state transitions for orchestration. Same (from_state, to_state)
always yields same result — deterministic for replay and idempotency.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import ClassVar

# Canonical orchestration phases (aligned with FallbackStateMachine)
PHASES = (
    "pending",
    "running",
    "success",
    "failed",
    "fallback",
    "paused",
    "completed",
    "rolled_back",
)

# Deterministic transition matrix: from_state -> allowed to_states
# WP-1004: Contract ensures replay produces identical transition validation
_PHASE_TRANSITIONS_RAW: dict[str, tuple[str, ...]] = {
    "pending": ("running", "failed"),
    "running": ("success", "failed", "fallback", "paused"),
    "fallback": ("running", "failed"),
    "paused": ("running", "failed"),
    "success": ("completed",),
    "failed": ("rolled_back",),
}

PHASE_TRANSITIONS: MappingProxyType[str, tuple[str, ...]] = MappingProxyType(_PHASE_TRANSITIONS_RAW)


class PhaseTransitionContract:
    """Deterministic contract for phase transitions.

    Usage:
        contract = PhaseTransitionContract()
        assert contract.validate("pending", "running")
        assert not contract.validate("completed", "running")
    """

    transitions: ClassVar[MappingProxyType[str, tuple[str, ...]]] = PHASE_TRANSITIONS

    @classmethod
    def validate(cls, from_state: str, to_state: str) -> bool:
        """Return True iff transition from_state -> to_state is allowed."""
        allowed = cls.transitions.get(from_state, ())
        return to_state in allowed

    @classmethod
    def allowed_targets(cls, from_state: str) -> tuple[str, ...]:
        """Return allowed target states for from_state."""
        return cls.transitions.get(from_state, ())


def validate_transition(from_state: str, to_state: str) -> bool:
    """Validate phase transition (from_state -> to_state). Deterministic."""
    return PhaseTransitionContract.validate(from_state, to_state)
