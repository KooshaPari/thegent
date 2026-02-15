"""Unit tests for orchestration modes (G-KD-04)."""

import pytest

from thegent.orchestration_modes import (
    MultiAgentMode,
    MODE_CATALOG,
    get_mode,
    list_modes,
    suggest_mode,
)


class TestMultiAgentModeCatalog:
    """Tests for multi-agent mode catalog."""

    def test_catalog_has_three_modes(self) -> None:
        """Catalog contains sequential_delegation, parallel_consensus, review_loop."""
        modes = [e.mode for e in MODE_CATALOG]
        assert MultiAgentMode.SEQUENTIAL_DELEGATION in modes
        assert MultiAgentMode.PARALLEL_CONSENSUS in modes
        assert MultiAgentMode.REVIEW_LOOP in modes
        assert len(MODE_CATALOG) == 3

    def test_list_modes_returns_list_of_dicts(self) -> None:
        """list_modes returns list with mode, description, phases, use_case, risk_profile."""
        data = list_modes()
        assert len(data) == 3
        for item in data:
            assert "mode" in item
            assert "description" in item
            assert "phases" in item
            assert "use_case" in item
            assert "risk_profile" in item
            assert "selection_hint" in item

    def test_get_mode_returns_entry(self) -> None:
        """get_mode returns ModeEntry for valid mode."""
        entry = get_mode("sequential_delegation")
        assert entry is not None
        assert entry.mode == MultiAgentMode.SEQUENTIAL_DELEGATION
        assert "specialization" in entry.description

    def test_get_mode_returns_none_for_invalid(self) -> None:
        """get_mode returns None for invalid mode."""
        assert get_mode("invalid_mode") is None

    def test_suggest_mode_low_confidence_returns_parallel_consensus(self) -> None:
        """Low confidence suggests parallel_consensus."""
        assert suggest_mode(confidence=0.3) == MultiAgentMode.PARALLEL_CONSENSUS

    def test_suggest_mode_high_risk_returns_review_loop(self) -> None:
        """High risk (non-critical) suggests review_loop."""
        assert suggest_mode(risk="high", urgency="normal") == MultiAgentMode.REVIEW_LOOP

    def test_suggest_mode_default_returns_sequential_delegation(self) -> None:
        """Default suggests sequential_delegation."""
        assert suggest_mode(confidence=0.8) == MultiAgentMode.SEQUENTIAL_DELEGATION
