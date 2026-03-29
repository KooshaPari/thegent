"""Unit tests for execution modes module (agents/modes.py)."""

import pytest

from thegent.agents.modes import (
    MODE_CATALOG,
    ExecutionMode,
    ModeCapability,
    get_mode_capability,
    list_modes,
)


@pytest.mark.unit
class TestExecutionMode:
    """Tests for ExecutionMode enum."""

    def test_sequential_delegation_mode(self) -> None:
        # @trace FR-MOD-050
        assert ExecutionMode.SEQUENTIAL_DELEGATION.value == "sequential_delegation"

    def test_parallel_consensus_mode(self) -> None:
        # @trace FR-MOD-050
        assert ExecutionMode.PARALLEL_CONSENSUS.value == "parallel_consensus"

    def test_review_loop_mode(self) -> None:
        # @trace FR-MOD-050
        assert ExecutionMode.REVIEW_LOOP.value == "review_loop"

    def test_arbitration_quorum_mode(self) -> None:
        # @trace FR-MOD-050
        assert ExecutionMode.ARBITRATION_QUORUM.value == "arbitration_quorum"

    def test_solo_mode(self) -> None:
        # @trace FR-MOD-050
        assert ExecutionMode.SOLO.value == "solo"

    def test_all_modes_are_strings(self) -> None:
        # @trace FR-MOD-051
        for mode in ExecutionMode:
            assert isinstance(mode.value, str)


@pytest.mark.unit
class TestModeCapability:
    """Tests for ModeCapability dataclass."""

    def test_create_capability(self) -> None:
        # @trace FR-MOD-052
        cap = ModeCapability(
            mode=ExecutionMode.SOLO,
            description="Single agent",
            min_agents=1,
            supports_streaming=True,
            coordination_logic="Direct execution.",
        )
        assert cap.mode == ExecutionMode.SOLO
        assert cap.min_agents == 1
        assert cap.supports_streaming is True

    def test_default_values(self) -> None:
        # @trace FR-MOD-052
        cap = ModeCapability(
            mode=ExecutionMode.SOLO,
            description="desc",
            coordination_logic="logic",
        )
        assert cap.min_agents == 1
        assert cap.supports_streaming is True


@pytest.mark.unit
class TestModeCatalog:
    """Tests for MODE_CATALOG constant."""

    def test_catalog_has_all_modes(self) -> None:
        # @trace FR-MOD-053
        for mode in ExecutionMode:
            assert mode in MODE_CATALOG, f"Missing catalog entry for {mode}"

    def test_arbitration_quorum_requires_three_agents(self) -> None:
        # @trace FR-MOD-053
        cap = MODE_CATALOG[ExecutionMode.ARBITRATION_QUORUM]
        assert cap.min_agents == 3

    def test_solo_requires_one_agent(self) -> None:
        # @trace FR-MOD-053
        cap = MODE_CATALOG[ExecutionMode.SOLO]
        assert cap.min_agents == 1


@pytest.mark.unit
class TestGetModeCapability:
    """Tests for get_mode_capability function."""

    def test_returns_capability_for_valid_mode(self) -> None:
        # @trace FR-MOD-054
        cap = get_mode_capability("solo")
        assert cap is not None
        assert cap.mode == ExecutionMode.SOLO

    def test_returns_none_for_unknown_mode(self) -> None:
        # @trace FR-MOD-054
        result = get_mode_capability("nonexistent_mode")
        assert result is None

    def test_returns_capability_for_each_mode_value(self) -> None:
        # @trace FR-MOD-054
        for mode in ExecutionMode:
            cap = get_mode_capability(mode.value)
            assert cap is not None
            assert cap.mode == mode


@pytest.mark.unit
class TestListModes:
    """Tests for list_modes function."""

    def test_returns_all_modes(self) -> None:
        # @trace FR-MOD-055
        modes = list_modes()
        assert len(modes) == len(ExecutionMode)

    def test_each_entry_is_dict(self) -> None:
        # @trace FR-MOD-055
        modes = list_modes()
        for entry in modes:
            assert isinstance(entry, dict)
            assert "mode" in entry
            assert "description" in entry
            assert "min_agents" in entry
            assert "coordination_logic" in entry
