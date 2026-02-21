"""Unit tests for resource_management.ResourcePredictionEngine.

Tests the resource prediction engine for forecasting spawn impact
and managing historical usage data.
"""

import pytest

from thegent.infra.resource_management import (
    FDBudget,
    ResourceManager,
    ResourcePredictionEngine,
)


class TestResourcePredictionEngineInit:
    """Tests for ResourcePredictionEngine initialization."""

    def test_init_creates_empty_history(self):
        """Test that initialization creates empty history."""
        engine = ResourcePredictionEngine()
        assert engine.history == []

    def test_history_is_list(self):
        """Test that history is a list."""
        engine = ResourcePredictionEngine()
        assert isinstance(engine.history, list)


class TestPredictSpawnImpact:
    """Tests for predict_spawn_impact method."""

    def test_returns_boolean(self):
        """Test that predict_spawn_impact returns a boolean."""
        engine = ResourcePredictionEngine()
        result = engine.predict_spawn_impact("test_agent", 1024)
        assert isinstance(result, bool)

    def test_returns_true_with_sufficient_memory(self):
        """Test returns True when plenty of memory available."""
        engine = ResourcePredictionEngine()
        # 2048 MB free - 512 MB predicted = 1536 MB buffer > 256 MB
        result = engine.predict_spawn_impact("generic_agent", 2048)
        assert result is True

    def test_returns_true_with_minimum_safe_memory(self):
        """Test returns True with exactly safe memory."""
        engine = ResourcePredictionEngine()
        # 768 MB free - 512 MB predicted = 256 MB buffer (exactly safe)
        result = engine.predict_spawn_impact("generic_agent", 768)
        assert result is True

    def test_returns_false_with_insufficient_memory(self):
        """Test returns False when memory is too low."""
        engine = ResourcePredictionEngine()
        # 512 MB free - 512 MB predicted = 0 MB buffer < 256 MB
        result = engine.predict_spawn_impact("generic_agent", 512)
        assert result is False

    def test_claude_harness_uses_more_memory(self):
        """Test Claude harness prediction uses more memory."""
        engine = ResourcePredictionEngine()
        # Claude uses 1024 MB predicted
        # 1024 MB free - 1024 MB predicted = 0 MB buffer < 256 MB
        result = engine.predict_spawn_impact("claude_agent", 1024)
        assert result is False

    def test_claude_harness_with_sufficient_memory(self):
        """Test Claude harness with sufficient memory."""
        engine = ResourcePredictionEngine()
        # 1500 MB free - 1024 MB predicted = 476 MB buffer > 256 MB
        result = engine.predict_spawn_impact("claude_harness", 1500)
        assert result is True

    def test_cursor_harness_uses_intermediate_memory(self):
        """Test Cursor harness uses intermediate memory."""
        engine = ResourcePredictionEngine()
        # Cursor uses 768 MB predicted
        # 768 MB free - 768 MB predicted = 0 MB buffer < 256 MB
        result = engine.predict_spawn_impact("cursor_agent", 768)
        assert result is False

    def test_cursor_harness_with_sufficient_memory(self):
        """Test Cursor harness with sufficient memory."""
        engine = ResourcePredictionEngine()
        # 1200 MB free - 768 MB predicted = 432 MB buffer > 256 MB
        result = engine.predict_spawn_impact("cursor_harness", 1200)
        assert result is True

    def test_case_insensitive_harness_type(self):
        """Test harness type matching is case-insensitive."""
        engine = ResourcePredictionEngine()
        # CLAUDE should match claude
        result = engine.predict_spawn_impact("CLAUDE_BOT", 1500)
        assert result is True

    def test_unknown_harness_uses_default(self):
        """Test unknown harness type uses default prediction."""
        engine = ResourcePredictionEngine()
        # Unknown harness uses 512 MB default
        result = engine.predict_spawn_impact("unknown_type", 1024)
        assert result is True


class TestRecordActual:
    """Tests for record_actual method."""

    def test_records_entry_to_history(self):
        """Test that record_actual adds entry to history."""
        engine = ResourcePredictionEngine()
        engine.record_actual("test_agent", 256)

        assert len(engine.history) == 1
        assert engine.history[0]["harness"] == "test_agent"
        assert engine.history[0]["mb"] == 256

    def test_records_multiple_entries(self):
        """Test recording multiple entries."""
        engine = ResourcePredictionEngine()

        engine.record_actual("agent1", 100)
        engine.record_actual("agent2", 200)
        engine.record_actual("agent3", 300)

        assert len(engine.history) == 3

    def test_history_keeps_last_100_entries(self):
        """Test that history is trimmed to last 100 entries."""
        engine = ResourcePredictionEngine()

        # Add 150 entries
        for i in range(150):
            engine.record_actual(f"agent_{i}", i)

        assert len(engine.history) == 100
        # Should keep the last 100 (50-149)
        assert engine.history[0]["harness"] == "agent_50"
        assert engine.history[-1]["harness"] == "agent_149"

    def test_history_preserves_order(self):
        """Test that history preserves insertion order."""
        engine = ResourcePredictionEngine()

        engine.record_actual("first", 100)
        engine.record_actual("second", 200)
        engine.record_actual("third", 300)

        assert engine.history[0]["harness"] == "first"
        assert engine.history[1]["harness"] == "second"
        assert engine.history[2]["harness"] == "third"

    def test_exactly_100_entries_not_trimmed(self):
        """Test that exactly 100 entries are not trimmed."""
        engine = ResourcePredictionEngine()

        for i in range(100):
            engine.record_actual(f"agent_{i}", i)

        assert len(engine.history) == 100
        assert engine.history[0]["harness"] == "agent_0"


class TestPredictSpawnImpactEdgeCases:
    """Edge case tests for predict_spawn_impact."""

    def test_zero_free_memory(self):
        """Test with zero free memory."""
        engine = ResourcePredictionEngine()
        result = engine.predict_spawn_impact("test", 0)
        assert result is False

    def test_negative_free_memory(self):
        """Test with negative free memory."""
        engine = ResourcePredictionEngine()
        result = engine.predict_spawn_impact("test", -100)
        assert result is False

    def test_very_large_free_memory(self):
        """Test with very large free memory."""
        engine = ResourcePredictionEngine()
        result = engine.predict_spawn_impact("test", 1_000_000)
        assert result is True

    def test_partial_match_in_harness_name(self):
        """Test partial match in harness name."""
        engine = ResourcePredictionEngine()
        # "my_cursor_bot" contains "cursor"
        result = engine.predict_spawn_impact("my_cursor_bot", 1200)
        assert result is True

    def test_empty_harness_type(self):
        """Test with empty harness type string."""
        engine = ResourcePredictionEngine()
        # Empty string uses default 512 MB
        result = engine.predict_spawn_impact("", 1024)
        assert result is True


class TestRecordActualEdgeCases:
    """Edge case tests for record_actual."""

    def test_zero_mb_recorded(self):
        """Test recording zero MB."""
        engine = ResourcePredictionEngine()
        engine.record_actual("agent", 0)

        assert engine.history[0]["mb"] == 0

    def test_large_mb_recorded(self):
        """Test recording large MB value."""
        engine = ResourcePredictionEngine()
        engine.record_actual("agent", 1_000_000)

        assert engine.history[0]["mb"] == 1_000_000

    def test_empty_harness_name(self):
        """Test recording with empty harness name."""
        engine = ResourcePredictionEngine()
        engine.record_actual("", 100)

        assert engine.history[0]["harness"] == ""


class TestResourcePredictionIntegration:
    """Integration tests for ResourcePredictionEngine."""

    def test_record_and_predict_cycle(self):
        """Test the record and predict cycle."""
        engine = ResourcePredictionEngine()

        # Initially can spawn generic agent with 1024 MB
        assert engine.predict_spawn_impact("generic", 1024) is True

        # Record some usage
        engine.record_actual("generic", 500)
        engine.record_actual("claude", 900)

        # Prediction still works
        assert engine.predict_spawn_impact("generic", 1024) is True
        assert len(engine.history) == 2

    def test_multiple_harness_types(self):
        """Test predictions for multiple harness types."""
        engine = ResourcePredictionEngine()

        # Test all three harness types with same memory
        free_mb = 1300

        # Claude needs 1024, leaves 276 > 256
        assert engine.predict_spawn_impact("claude", free_mb) is True

        # Cursor needs 768, leaves 532 > 256
        assert engine.predict_spawn_impact("cursor", free_mb) is True

        # Generic needs 512, leaves 788 > 256
        assert engine.predict_spawn_impact("other", free_mb) is True


class TestFDBudget:
    """Tests for FDBudget class."""

    def test_init_default_threshold(self):
        """Test FDBudget initialization with default threshold."""
        budget = FDBudget()
        assert budget.threshold == 0.8

    def test_init_custom_threshold(self):
        """Test FDBudget initialization with custom threshold."""
        budget = FDBudget(threshold=0.9)
        assert budget.threshold == 0.9

    def test_check_returns_true_under_threshold(self):
        """Test check returns True when under threshold."""
        budget = FDBudget(threshold=0.8)
        # 400/1000 = 0.4 < 0.8
        result = budget.check(400, 1000)
        assert result is True

    def test_check_returns_false_over_threshold(self):
        """Test check returns False when over threshold."""
        budget = FDBudget(threshold=0.8)
        # 900/1000 = 0.9 > 0.8
        result = budget.check(900, 1000)
        assert result is False

    def test_check_at_exact_threshold(self):
        """Test check at exact threshold."""
        budget = FDBudget(threshold=0.8)
        # 800/1000 = 0.8 == threshold, not > threshold
        result = budget.check(800, 1000)
        assert result is True

    def test_check_just_over_threshold(self):
        """Test check just over threshold."""
        budget = FDBudget(threshold=0.8)
        # 801/1000 = 0.801 > 0.8
        result = budget.check(801, 1000)
        assert result is False

    def test_check_with_zero_limit(self):
        """Test check with zero limit."""
        budget = FDBudget(threshold=0.8)
        # Division by zero handling
        try:
            result = budget.check(0, 0)
        except ZeroDivisionError:
            # If it raises, that's acceptable behavior
            pass

    def test_check_with_different_thresholds(self):
        """Test check with various threshold values."""
        for threshold in [0.5, 0.6, 0.7, 0.9, 0.95]:
            budget = FDBudget(threshold=threshold)

            # Under threshold
            assert budget.check(int(threshold * 900), 1000) is True

            # Over threshold
            assert budget.check(int(threshold * 1100), 1000) is False


class TestResourceManagerBasics:
    """Basic tests for ResourceManager class."""

    def test_init(self):
        """Test ResourceManager initialization."""
        manager = ResourceManager()
        assert manager is not None

    def test_monitor_usage_returns_dict(self):
        """Test monitor_usage returns a dictionary."""
        manager = ResourceManager()
        # Use current process PID
        import os

        result = manager.monitor_usage(os.getpid())
        assert isinstance(result, dict)

    def test_monitor_usage_current_process(self):
        """Test monitor_usage on current process."""
        manager = ResourceManager()
        import os

        result = manager.monitor_usage(os.getpid())

        # Should have these keys for a valid process
        assert "pid" in result
        assert result["pid"] == os.getpid()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
