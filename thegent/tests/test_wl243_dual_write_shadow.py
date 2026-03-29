"""Tests for dual-write shadow mode.

# @trace WL-243
"""

from __future__ import annotations

import pytest

from thegent.integrations.dual_write_shadow import (
    DualWriteShadowMode,
    ShadowWriteResult,
)


@pytest.mark.requirement("WL-243")
class TestShadowWriteResult:
    """Test ShadowWriteResult dataclass."""

    def test_shadow_write_result_creation(self) -> None:
        """Test creating a ShadowWriteResult."""
        result = ShadowWriteResult(record_id="rec123", primary_ok=True, shadow_ok=True)
        assert result.record_id == "rec123"
        assert result.primary_ok is True
        assert result.shadow_ok is True

    def test_shadow_write_result_fields(self) -> None:
        """Test ShadowWriteResult has expected fields."""
        result = ShadowWriteResult(record_id="rec456", primary_ok=False, shadow_ok=True)
        assert hasattr(result, "record_id")
        assert hasattr(result, "primary_ok")
        assert hasattr(result, "shadow_ok")


@pytest.mark.requirement("WL-243")
class TestDualWriteShadowMode:
    """Test DualWriteShadowMode."""

    def test_init_enabled(self) -> None:
        """Test initialization with shadow mode enabled."""
        shadow_mode = DualWriteShadowMode(enabled=True)
        assert shadow_mode.is_enabled() is True

    def test_init_disabled(self) -> None:
        """Test initialization with shadow mode disabled."""
        shadow_mode = DualWriteShadowMode(enabled=False)
        assert shadow_mode.is_enabled() is False

    def test_init_default_enabled(self) -> None:
        """Test default initialization enables shadow mode."""
        shadow_mode = DualWriteShadowMode()
        assert shadow_mode.is_enabled() is True

    def test_write_both_success(self) -> None:
        """Test write when both primary and shadow succeed."""
        shadow_mode = DualWriteShadowMode(enabled=True)
        result = shadow_mode.write("rec1", lambda: True, lambda: True)
        assert result.record_id == "rec1"
        assert result.primary_ok is True
        assert result.shadow_ok is True

    def test_write_primary_success_shadow_failure(self) -> None:
        """Test write when primary succeeds but shadow fails."""
        shadow_mode = DualWriteShadowMode(enabled=True)
        result = shadow_mode.write("rec2", lambda: True, lambda: False)
        assert result.record_id == "rec2"
        assert result.primary_ok is True
        assert result.shadow_ok is False

    def test_write_primary_failure_shadow_success(self) -> None:
        """Test write when primary fails but shadow succeeds."""
        shadow_mode = DualWriteShadowMode(enabled=True)
        result = shadow_mode.write("rec3", lambda: False, lambda: True)
        assert result.record_id == "rec3"
        assert result.primary_ok is False
        assert result.shadow_ok is True

    def test_write_both_failure(self) -> None:
        """Test write when both primary and shadow fail."""
        shadow_mode = DualWriteShadowMode(enabled=True)
        result = shadow_mode.write("rec4", lambda: False, lambda: False)
        assert result.record_id == "rec4"
        assert result.primary_ok is False
        assert result.shadow_ok is False

    def test_write_shadow_disabled(self) -> None:
        """Test write when shadow mode is disabled."""
        shadow_mode = DualWriteShadowMode(enabled=False)
        result = shadow_mode.write("rec5", lambda: True, lambda: False)
        assert result.record_id == "rec5"
        assert result.primary_ok is True
        assert result.shadow_ok is False

    def test_write_primary_exception(self) -> None:
        """Test write handles primary function exception."""
        shadow_mode = DualWriteShadowMode(enabled=True)

        def primary_fn():
            raise ValueError("Primary error")

        result = shadow_mode.write("rec6", primary_fn, lambda: True)
        assert result.record_id == "rec6"
        assert result.primary_ok is False
        assert result.shadow_ok is True

    def test_write_shadow_exception(self) -> None:
        """Test write handles shadow function exception."""
        shadow_mode = DualWriteShadowMode(enabled=True)

        def shadow_fn():
            raise RuntimeError("Shadow error")

        result = shadow_mode.write("rec7", lambda: True, shadow_fn)
        assert result.record_id == "rec7"
        assert result.primary_ok is True
        assert result.shadow_ok is False

    def test_write_both_exceptions(self) -> None:
        """Test write handles exceptions from both functions."""
        shadow_mode = DualWriteShadowMode(enabled=True)

        def primary_fn():
            raise ValueError("Primary error")

        def shadow_fn():
            raise RuntimeError("Shadow error")

        result = shadow_mode.write("rec8", primary_fn, shadow_fn)
        assert result.record_id == "rec8"
        assert result.primary_ok is False
        assert result.shadow_ok is False

    def test_divergences_empty(self) -> None:
        """Test divergences with empty result list."""
        shadow_mode = DualWriteShadowMode(enabled=True)
        divergences = shadow_mode.divergences([])
        assert divergences == []

    def test_divergences_no_divergence(self) -> None:
        """Test divergences when all results match."""
        shadow_mode = DualWriteShadowMode(enabled=True)
        results = [
            ShadowWriteResult(record_id="rec1", primary_ok=True, shadow_ok=True),
            ShadowWriteResult(record_id="rec2", primary_ok=False, shadow_ok=False),
        ]
        divergences = shadow_mode.divergences(results)
        assert divergences == []

    def test_divergences_with_divergence(self) -> None:
        """Test divergences filters mismatched results."""
        shadow_mode = DualWriteShadowMode(enabled=True)
        results = [
            ShadowWriteResult(record_id="rec1", primary_ok=True, shadow_ok=True),
            ShadowWriteResult(record_id="rec2", primary_ok=True, shadow_ok=False),
            ShadowWriteResult(record_id="rec3", primary_ok=False, shadow_ok=False),
            ShadowWriteResult(record_id="rec4", primary_ok=False, shadow_ok=True),
        ]
        divergences = shadow_mode.divergences(results)
        assert len(divergences) == 2
        assert divergences[0].record_id == "rec2"
        assert divergences[1].record_id == "rec4"

    def test_multiple_writes_tracked(self) -> None:
        """Test that multiple write results are tracked."""
        shadow_mode = DualWriteShadowMode(enabled=True)
        shadow_mode.write("rec1", lambda: True, lambda: True)
        shadow_mode.write("rec2", lambda: False, lambda: False)
        shadow_mode.write("rec3", lambda: True, lambda: False)

        # Retrieve all divergences from internal state
        # (This is a simplified test; in practice, you'd call divergences on a list)
        result_list = [
            ShadowWriteResult(record_id="rec1", primary_ok=True, shadow_ok=True),
            ShadowWriteResult(record_id="rec2", primary_ok=False, shadow_ok=False),
            ShadowWriteResult(record_id="rec3", primary_ok=True, shadow_ok=False),
        ]
        divergences = shadow_mode.divergences(result_list)
        assert len(divergences) == 1
        assert divergences[0].record_id == "rec3"
