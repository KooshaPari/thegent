"""Default Enablement Migration Plan tracking.

WL-260: Default Enablement Migration Plan
Manages feature enablement through migration phases: PLAN -> PILOT -> ROLLOUT -> COMPLETE.

# @trace WL-260
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MigrationPhase(str, Enum):
    """Phases of feature enablement migration."""

    PLAN = "plan"
    PILOT = "pilot"
    ROLLOUT = "rollout"
    COMPLETE = "complete"


@dataclass
class EnablementMigrationPlan:
    """A feature enablement migration plan with current phase."""

    feature_id: str
    phase: MigrationPhase = MigrationPhase.PLAN


class DefaultEnablementMigrator:
    """Manages feature enablement migration plans."""

    def __init__(self) -> None:
        """Initialize the migrator with no registered features."""
        self._plans: dict[str, EnablementMigrationPlan] = {}

    def register(self, feature_id: str) -> EnablementMigrationPlan:
        """Register a new feature in PLAN phase.

        Args:
            feature_id: Unique identifier for the feature.

        Returns:
            The newly registered EnablementMigrationPlan.

        Raises:
            ValueError: If feature_id is already registered.
        """
        if feature_id in self._plans:
            raise ValueError(f"Feature '{feature_id}' already registered")
        plan = EnablementMigrationPlan(feature_id=feature_id)
        self._plans[feature_id] = plan
        return plan

    def advance(self, feature_id: str) -> EnablementMigrationPlan:
        """Advance a feature to the next migration phase.

        Args:
            feature_id: ID of feature to advance.

        Returns:
            The updated EnablementMigrationPlan.

        Raises:
            KeyError: If feature_id not found.
            ValueError: If feature is already in COMPLETE phase.
        """
        if feature_id not in self._plans:
            raise KeyError(f"Feature '{feature_id}' not found")

        plan = self._plans[feature_id]
        phase_order = [MigrationPhase.PLAN, MigrationPhase.PILOT, MigrationPhase.ROLLOUT, MigrationPhase.COMPLETE]
        current_index = phase_order.index(plan.phase)

        if current_index >= len(phase_order) - 1:
            raise ValueError(f"Feature '{feature_id}' is already in {plan.phase.value} phase")

        plan.phase = phase_order[current_index + 1]
        return plan

    def get(self, feature_id: str) -> EnablementMigrationPlan:
        """Retrieve a feature's migration plan.

        Args:
            feature_id: ID of feature to retrieve.

        Returns:
            The EnablementMigrationPlan for the feature.

        Raises:
            KeyError: If feature_id not found.
        """
        if feature_id not in self._plans:
            raise KeyError(f"Feature '{feature_id}' not found")
        return self._plans[feature_id]

    def by_phase(self, phase: MigrationPhase) -> list[EnablementMigrationPlan]:
        """Get all features in a specific phase.

        Args:
            phase: The migration phase to filter by.

        Returns:
            List of EnablementMigrationPlan objects in the given phase, sorted by feature_id.
        """
        results = [plan for plan in self._plans.values() if plan.phase == phase]
        return sorted(results, key=lambda p: p.feature_id)
