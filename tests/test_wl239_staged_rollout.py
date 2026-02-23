"""Tests for WL-239: Staged Rollout Profiles.

Verifies feature rollout stage management, progression, and profile filtering.

# @trace WL-239
"""

from __future__ import annotations

import pytest

from thegent.integrations.staged_rollout import (
    RolloutProfile,
    RolloutStage,
    StagedRolloutManager,
)


@pytest.mark.requirement("WL-239")
class TestRolloutStage:
    """WL-239: RolloutStage enum defines valid rollout stages."""

    def test_rollout_stage_enum_values(self):
        """# @trace WL-239 — RolloutStage has CANARY, EARLY_ADOPTER, GENERAL, FULL."""
        assert RolloutStage.CANARY.value == "canary"
        assert RolloutStage.EARLY_ADOPTER.value == "early_adopter"
        assert RolloutStage.GENERAL.value == "general"
        assert RolloutStage.FULL.value == "full"


@pytest.mark.requirement("WL-239")
class TestRolloutProfile:
    """WL-239: RolloutProfile dataclass stores rollout configuration."""

    def test_rollout_profile_creation_with_defaults(self):
        """# @trace WL-239 — RolloutProfile defaults to CANARY stage with 0% rollout."""
        profile = RolloutProfile(feature_id="feature-1")

        assert profile.feature_id == "feature-1"
        assert profile.stage == RolloutStage.CANARY
        assert profile.rollout_pct == 0.0

    def test_rollout_profile_creation_with_custom_stage(self):
        """# @trace WL-239 — RolloutProfile accepts custom stage and rollout percentage."""
        profile = RolloutProfile(
            feature_id="feature-2",
            stage=RolloutStage.GENERAL,
            rollout_pct=75.0,
        )

        assert profile.feature_id == "feature-2"
        assert profile.stage == RolloutStage.GENERAL
        assert profile.rollout_pct == 75.0


@pytest.mark.requirement("WL-239")
class TestStagedRolloutManager:
    """WL-239: StagedRolloutManager handles feature rollout progression."""

    def test_create_initializes_new_feature_in_canary(self):
        """# @trace WL-239 — create() initializes feature in CANARY stage with 5% rollout."""
        manager = StagedRolloutManager()
        profile = manager.create("feature-alpha")

        assert profile.feature_id == "feature-alpha"
        assert profile.stage == RolloutStage.CANARY
        assert profile.rollout_pct == 5.0

    def test_get_retrieves_existing_profile(self):
        """# @trace WL-239 — get() returns the RolloutProfile for a created feature."""
        manager = StagedRolloutManager()
        manager.create("feature-beta")
        profile = manager.get("feature-beta")

        assert profile.feature_id == "feature-beta"
        assert profile.stage == RolloutStage.CANARY

    def test_get_raises_keyerror_for_missing_feature(self):
        """# @trace WL-239 — get() raises KeyError if feature does not exist."""
        manager = StagedRolloutManager()

        with pytest.raises(KeyError, match="Feature not found"):
            manager.get("nonexistent-feature")

    def test_advance_from_canary_to_early_adopter(self):
        """# @trace WL-239 — advance() transitions CANARY(5%) → EARLY_ADOPTER(25%)."""
        manager = StagedRolloutManager()
        manager.create("feature-1")
        profile = manager.advance("feature-1")

        assert profile.stage == RolloutStage.EARLY_ADOPTER
        assert profile.rollout_pct == 25.0

    def test_advance_from_early_adopter_to_general(self):
        """# @trace WL-239 — advance() transitions EARLY_ADOPTER(25%) → GENERAL(75%)."""
        manager = StagedRolloutManager()
        manager.create("feature-2")
        manager.advance("feature-2")
        profile = manager.advance("feature-2")

        assert profile.stage == RolloutStage.GENERAL
        assert profile.rollout_pct == 75.0

    def test_advance_from_general_to_full(self):
        """# @trace WL-239 — advance() transitions GENERAL(75%) → FULL(100%)."""
        manager = StagedRolloutManager()
        manager.create("feature-3")
        manager.advance("feature-3")
        manager.advance("feature-3")
        profile = manager.advance("feature-3")

        assert profile.stage == RolloutStage.FULL
        assert profile.rollout_pct == 100.0

    def test_advance_from_full_raises_valueerror(self):
        """# @trace WL-239 — advance() raises ValueError if already at FULL stage."""
        manager = StagedRolloutManager()
        manager.create("feature-4")
        manager.advance("feature-4")
        manager.advance("feature-4")
        manager.advance("feature-4")

        with pytest.raises(ValueError, match="already at FULL rollout stage"):
            manager.advance("feature-4")

    def test_advance_raises_keyerror_for_missing_feature(self):
        """# @trace WL-239 — advance() raises KeyError if feature does not exist."""
        manager = StagedRolloutManager()

        with pytest.raises(KeyError, match="Feature not found"):
            manager.advance("nonexistent-feature")

    def test_at_stage_returns_features_at_canary(self):
        """# @trace WL-239 — at_stage() returns all features at CANARY stage."""
        manager = StagedRolloutManager()
        manager.create("feature-a")
        manager.create("feature-b")
        manager.create("feature-c")
        manager.advance("feature-c")

        canary_features = manager.at_stage(RolloutStage.CANARY)

        assert len(canary_features) == 2
        feature_ids = {p.feature_id for p in canary_features}
        assert feature_ids == {"feature-a", "feature-b"}

    def test_at_stage_returns_features_at_early_adopter(self):
        """# @trace WL-239 — at_stage() returns features at EARLY_ADOPTER stage."""
        manager = StagedRolloutManager()
        manager.create("feature-x")
        manager.create("feature-y")
        manager.create("feature-z")
        manager.advance("feature-y")
        manager.advance("feature-z")
        manager.advance("feature-z")

        early_adopter_features = manager.at_stage(RolloutStage.EARLY_ADOPTER)

        assert len(early_adopter_features) == 1
        assert early_adopter_features[0].feature_id == "feature-y"

    def test_at_stage_returns_features_at_general(self):
        """# @trace WL-239 — at_stage() returns features at GENERAL stage."""
        manager = StagedRolloutManager()
        manager.create("feature-m")
        manager.create("feature-n")
        manager.advance("feature-m")
        manager.advance("feature-m")
        manager.advance("feature-n")
        manager.advance("feature-n")
        manager.advance("feature-n")

        general_features = manager.at_stage(RolloutStage.GENERAL)

        assert len(general_features) == 1
        assert general_features[0].feature_id == "feature-m"

    def test_at_stage_returns_features_at_full(self):
        """# @trace WL-239 — at_stage() returns features at FULL stage."""
        manager = StagedRolloutManager()
        manager.create("feature-p")
        manager.create("feature-q")
        manager.advance("feature-p")
        manager.advance("feature-p")
        manager.advance("feature-p")

        full_features = manager.at_stage(RolloutStage.FULL)

        assert len(full_features) == 1
        assert full_features[0].feature_id == "feature-p"

    def test_at_stage_returns_empty_list_if_no_features_at_stage(self):
        """# @trace WL-239 — at_stage() returns empty list if no features at stage."""
        manager = StagedRolloutManager()
        manager.create("feature-1")

        general_features = manager.at_stage(RolloutStage.GENERAL)

        assert general_features == []

    def test_full_rollout_progression_sequence(self):
        """# @trace WL-239 — feature progresses through all stages: CANARY→EARLY→GENERAL→FULL."""
        manager = StagedRolloutManager()
        profile = manager.create("feature-complete")

        assert profile.stage == RolloutStage.CANARY
        assert profile.rollout_pct == 5.0

        profile = manager.advance("feature-complete")
        assert profile.stage == RolloutStage.EARLY_ADOPTER
        assert profile.rollout_pct == 25.0

        profile = manager.advance("feature-complete")
        assert profile.stage == RolloutStage.GENERAL
        assert profile.rollout_pct == 75.0

        profile = manager.advance("feature-complete")
        assert profile.stage == RolloutStage.FULL
        assert profile.rollout_pct == 100.0

    def test_multiple_features_at_different_stages(self):
        """# @trace WL-239 — manager handles multiple features at different stages."""
        manager = StagedRolloutManager()

        # Create features at different stages
        feature_1 = manager.create("feature-1")  # CANARY
        feature_2 = manager.create("feature-2")  # CANARY
        manager.advance("feature-2")  # EARLY_ADOPTER

        feature_3 = manager.create("feature-3")  # CANARY
        manager.advance("feature-3")  # EARLY_ADOPTER
        manager.advance("feature-3")  # GENERAL

        assert manager.get("feature-1").stage == RolloutStage.CANARY
        assert manager.get("feature-2").stage == RolloutStage.EARLY_ADOPTER
        assert manager.get("feature-3").stage == RolloutStage.GENERAL

        # Verify at_stage filtering works correctly
        canary_count = len(manager.at_stage(RolloutStage.CANARY))
        early_count = len(manager.at_stage(RolloutStage.EARLY_ADOPTER))
        general_count = len(manager.at_stage(RolloutStage.GENERAL))

        assert canary_count == 1
        assert early_count == 1
        assert general_count == 1
