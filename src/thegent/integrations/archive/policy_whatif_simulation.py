"""Policy what-if simulation for autosync governance.

# @trace WL-294
"""

from __future__ import annotations

from dataclasses import dataclass


OPEN_STATUSES: set[str] = {"BACKLOG", "IN PROGRESS", "REVIEW", "TODO", "OPEN"}


@dataclass(frozen=True)
class PolicySimulationInput:
    """Inputs for policy what-if simulation."""

    total_items: int
    open_items: int
    blocked_items: int
    current_cycle_interval_seconds: int
    proposed_cycle_interval_seconds: int
    max_changes_per_cycle: int


@dataclass(frozen=True)
class PolicySimulationResult:
    """Computed outcome for a hypothetical policy change."""

    current_open_rate_per_hour: float
    proposed_open_rate_per_hour: float
    current_time_to_clear_hours: float
    proposed_time_to_clear_hours: float
    improvement_hours: float


def simulate_policy_change(payload: PolicySimulationInput) -> PolicySimulationResult:
    """Simulate impact of proposed sync cadence and change budget.

    Raises ValueError when inputs are invalid or non-positive where required.
    """
    if payload.total_items < 0 or payload.open_items < 0 or payload.blocked_items < 0:
        raise ValueError("item counts must be non-negative")
    if payload.open_items > payload.total_items:
        raise ValueError("open_items cannot exceed total_items")
    if payload.blocked_items > payload.open_items:
        raise ValueError("blocked_items cannot exceed open_items")
    if payload.current_cycle_interval_seconds <= 0 or payload.proposed_cycle_interval_seconds <= 0:
        raise ValueError("cycle intervals must be positive")
    if payload.max_changes_per_cycle <= 0:
        raise ValueError("max_changes_per_cycle must be positive")

    actionable_open = payload.open_items - payload.blocked_items
    if actionable_open <= 0:
        return PolicySimulationResult(
            current_open_rate_per_hour=0.0,
            proposed_open_rate_per_hour=0.0,
            current_time_to_clear_hours=0.0,
            proposed_time_to_clear_hours=0.0,
            improvement_hours=0.0,
        )

    current_cycles_per_hour = 3600.0 / float(payload.current_cycle_interval_seconds)
    proposed_cycles_per_hour = 3600.0 / float(payload.proposed_cycle_interval_seconds)

    current_open_rate = current_cycles_per_hour * payload.max_changes_per_cycle
    proposed_open_rate = proposed_cycles_per_hour * payload.max_changes_per_cycle

    current_time = actionable_open / current_open_rate if current_open_rate > 0 else float("inf")
    proposed_time = actionable_open / proposed_open_rate if proposed_open_rate > 0 else float("inf")

    return PolicySimulationResult(
        current_open_rate_per_hour=current_open_rate,
        proposed_open_rate_per_hour=proposed_open_rate,
        current_time_to_clear_hours=current_time,
        proposed_time_to_clear_hours=proposed_time,
        improvement_hours=current_time - proposed_time,
    )
