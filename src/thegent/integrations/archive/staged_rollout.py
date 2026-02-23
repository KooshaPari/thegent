"""Staged Rollout Profiles for feature rollout management.

WL-239: Staged Rollout Profiles
Provides a standard interface for managing feature rollout stages and percentages,
enabling progressive deployment from canary through full rollout.

# @trace WL-239
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class RolloutStage(Enum):
    """Stages of a feature rollout."""

    CANARY = "canary"
    EARLY_ADOPTER = "early_adopter"
    GENERAL = "general"
    FULL = "full"


@dataclass
class RolloutProfile:
    """Configuration for a feature rollout at a particular stage.

    Attributes:
        feature_id: Unique identifier for the feature being rolled out.
        stage: Current rollout stage (default: CANARY).
        rollout_pct: Percentage of users/systems receiving the feature (default: 0.0).
    """

    feature_id: str
    stage: RolloutStage = RolloutStage.CANARY
    rollout_pct: float = 0.0


class StagedRolloutManager:
    """Manages feature rollout stages and progression."""

    # Stage progression mapping: current stage -> next stage
    _STAGE_PROGRESSION: ClassVar[dict[RolloutStage, RolloutStage]] = {
        RolloutStage.CANARY: RolloutStage.EARLY_ADOPTER,
        RolloutStage.EARLY_ADOPTER: RolloutStage.GENERAL,
        RolloutStage.GENERAL: RolloutStage.FULL,
    }

    # Default rollout percentages for each stage
    _STAGE_PERCENTAGES: ClassVar[dict[RolloutStage, float]] = {
        RolloutStage.CANARY: 5.0,
        RolloutStage.EARLY_ADOPTER: 25.0,
        RolloutStage.GENERAL: 75.0,
        RolloutStage.FULL: 100.0,
    }

    def __init__(self) -> None:
        """Initialize an empty rollout manager."""
        self._profiles: dict[str, RolloutProfile] = {}

    def create(self, feature_id: str) -> RolloutProfile:
        """Create a new rollout profile in CANARY stage with 0% rollout.

        Args:
            feature_id: Unique identifier for the feature.

        Returns:
            The created RolloutProfile.
        """
        profile = RolloutProfile(
            feature_id=feature_id,
            stage=RolloutStage.CANARY,
            rollout_pct=self._STAGE_PERCENTAGES[RolloutStage.CANARY],
        )
        self._profiles[feature_id] = profile
        return profile

    def advance(self, feature_id: str) -> RolloutProfile:
        """Advance a feature to the next rollout stage.

        Progression: CANARY(5%) → EARLY_ADOPTER(25%) → GENERAL(75%) → FULL(100%).

        Args:
            feature_id: Unique identifier for the feature.

        Returns:
            The updated RolloutProfile with new stage and rollout percentage.

        Raises:
            KeyError: If the feature does not exist.
            ValueError: If the feature is already at FULL stage.
        """
        if feature_id not in self._profiles:
            raise KeyError(f"Feature not found: {feature_id}")

        profile = self._profiles[feature_id]

        if profile.stage == RolloutStage.FULL:
            raise ValueError(f"Feature '{feature_id}' is already at FULL rollout stage")

        next_stage = self._STAGE_PROGRESSION[profile.stage]
        profile.stage = next_stage
        profile.rollout_pct = self._STAGE_PERCENTAGES[next_stage]

        return profile

    def get(self, feature_id: str) -> RolloutProfile:
        """Retrieve a rollout profile by feature ID.

        Args:
            feature_id: Unique identifier for the feature.

        Returns:
            The RolloutProfile for the feature.

        Raises:
            KeyError: If the feature does not exist.
        """
        if feature_id not in self._profiles:
            raise KeyError(f"Feature not found: {feature_id}")
        return self._profiles[feature_id]

    def at_stage(self, stage: RolloutStage) -> list[RolloutProfile]:
        """Get all features currently at a specific rollout stage.

        Args:
            stage: The rollout stage to filter by.

        Returns:
            List of RolloutProfile objects at the specified stage.
        """
        return [p for p in self._profiles.values() if p.stage == stage]
