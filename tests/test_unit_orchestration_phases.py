"""Unit tests for orchestration phase transition contracts (WP-1004, FR-004)."""

from __future__ import annotations

from thegent.orchestration.phases import (
    PhaseTransitionContract,
    validate_transition,
)


class TestPhaseTransitionContract:
    """Deterministic phase transition validation."""

    def test_pending_to_running_allowed(self) -> None:
        assert validate_transition("pending", "running") is True

    def test_pending_to_failed_allowed(self) -> None:
        assert validate_transition("pending", "failed") is True

    def test_pending_to_completed_disallowed(self) -> None:
        assert validate_transition("pending", "completed") is False

    def test_running_to_success_allowed(self) -> None:
        assert validate_transition("running", "success") is True

    def test_running_to_fallback_allowed(self) -> None:
        assert validate_transition("running", "fallback") is True

    def test_fallback_to_running_allowed(self) -> None:
        assert validate_transition("fallback", "running") is True

    def test_success_to_completed_allowed(self) -> None:
        assert validate_transition("success", "completed") is True

    def test_failed_to_rolled_back_allowed(self) -> None:
        assert validate_transition("failed", "rolled_back") is True

    def test_completed_to_any_disallowed(self) -> None:
        assert validate_transition("completed", "running") is False
        assert validate_transition("completed", "pending") is False

    def test_unknown_from_state_disallowed(self) -> None:
        assert validate_transition("unknown", "running") is False

    def test_phase_transition_contract_class(self) -> None:
        assert PhaseTransitionContract.validate("running", "paused") is True
        assert PhaseTransitionContract.validate("paused", "running") is True

    def test_allowed_targets(self) -> None:
        targets = PhaseTransitionContract.allowed_targets("running")
        assert "success" in targets
        assert "failed" in targets
        assert "fallback" in targets
        assert "paused" in targets
        assert "completed" not in targets

    def test_deterministic_same_input_same_output(self) -> None:
        """Replay: same (from, to) always yields same result."""
        for _ in range(10):
            assert validate_transition("running", "success") is True
            assert validate_transition("completed", "running") is False
