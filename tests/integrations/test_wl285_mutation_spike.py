"""Tests for thegent.integrations.mutation_spike — Mutation spike anomaly detector.

@trace WL-285
"""

from __future__ import annotations

import pytest

from thegent.integrations.mutation_spike import (
    MutationSpikeDetector,
    SpikeConfig,
)


class TestSpikeConfig:
    """Test SpikeConfig dataclass. @trace WL-285"""

    @pytest.mark.requirement("WL-285")
    def test_default_values(self) -> None:
        """SpikeConfig has expected default values."""
        config = SpikeConfig()
        assert config.window_size == 10
        assert config.spike_multiplier == 3.0
        assert config.min_samples == 3

    @pytest.mark.requirement("WL-285")
    def test_custom_values(self) -> None:
        """SpikeConfig can be customized."""
        config = SpikeConfig(window_size=20, spike_multiplier=2.5, min_samples=5)
        assert config.window_size == 20
        assert config.spike_multiplier == 2.5
        assert config.min_samples == 5


class TestMutationSpikeDetectorInit:
    """Test MutationSpikeDetector initialization. @trace WL-285"""

    @pytest.mark.requirement("WL-285")
    def test_init_with_default_config(self) -> None:
        """Detector initializes with default config."""
        detector = MutationSpikeDetector()
        assert detector.config.window_size == 10
        assert detector.config.spike_multiplier == 3.0
        assert detector.config.min_samples == 3

    @pytest.mark.requirement("WL-285")
    def test_init_with_custom_config(self) -> None:
        """Detector can be initialized with custom config."""
        config = SpikeConfig(window_size=20, spike_multiplier=2.0, min_samples=2)
        detector = MutationSpikeDetector(config)
        assert detector.config.window_size == 20
        assert detector.config.spike_multiplier == 2.0
        assert detector.config.min_samples == 2


class TestMutationSpikeDetectorRecord:
    """Test MutationSpikeDetector.record() method. @trace WL-285"""

    @pytest.mark.requirement("WL-285")
    def test_record_single_count(self) -> None:
        """Can record a single count."""
        detector = MutationSpikeDetector()
        detector.record(5)
        # No assertion needed; just verify no exception

    @pytest.mark.requirement("WL-285")
    def test_record_multiple_counts(self) -> None:
        """Can record multiple counts."""
        detector = MutationSpikeDetector()
        detector.record(5)
        detector.record(10)
        detector.record(7)
        # No assertion needed; just verify no exception


class TestMutationSpikeDetectorBaseline:
    """Test MutationSpikeDetector.baseline() method. @trace WL-285"""

    @pytest.mark.requirement("WL-285")
    def test_baseline_insufficient_samples(self) -> None:
        """baseline() returns None with fewer than min_samples."""
        detector = MutationSpikeDetector()
        detector.record(5)
        detector.record(10)

        assert detector.baseline() is None

    @pytest.mark.requirement("WL-285")
    def test_baseline_exact_min_samples(self) -> None:
        """baseline() works with exactly min_samples."""
        detector = MutationSpikeDetector()
        detector.record(3)
        detector.record(6)
        detector.record(9)

        baseline = detector.baseline()
        assert baseline == 6.0

    @pytest.mark.requirement("WL-285")
    def test_baseline_multiple_samples(self) -> None:
        """baseline() correctly computes mean."""
        detector = MutationSpikeDetector()
        detector.record(10)
        detector.record(20)
        detector.record(30)
        detector.record(40)

        baseline = detector.baseline()
        assert baseline == 25.0

    @pytest.mark.requirement("WL-285")
    def test_baseline_empty_detector(self) -> None:
        """baseline() returns None for empty detector."""
        detector = MutationSpikeDetector()
        assert detector.baseline() is None


class TestMutationSpikeDetectorIsSpike:
    """Test MutationSpikeDetector.is_spike() method. @trace WL-285"""

    @pytest.mark.requirement("WL-285")
    def test_is_spike_insufficient_samples(self) -> None:
        """is_spike() returns False with insufficient samples."""
        detector = MutationSpikeDetector()
        detector.record(5)
        detector.record(10)

        # Not enough samples yet
        assert detector.is_spike(100) is False

    @pytest.mark.requirement("WL-285")
    def test_is_spike_no_spike(self) -> None:
        """is_spike() returns False for normal values."""
        detector = MutationSpikeDetector()
        detector.record(10)
        detector.record(10)
        detector.record(10)

        # Baseline is 10, count of 20 < 10*3.0
        assert detector.is_spike(20) is False

    @pytest.mark.requirement("WL-285")
    def test_is_spike_detected(self) -> None:
        """is_spike() returns True for spikes above threshold."""
        detector = MutationSpikeDetector()
        detector.record(10)
        detector.record(10)
        detector.record(10)

        # Baseline is 10, count of 31 > 10*3.0
        assert detector.is_spike(31) is True

    @pytest.mark.requirement("WL-285")
    def test_is_spike_boundary(self) -> None:
        """is_spike() at exact boundary."""
        detector = MutationSpikeDetector()
        detector.record(10)
        detector.record(10)
        detector.record(10)

        # Baseline is 10, threshold is 30
        assert detector.is_spike(30) is False
        assert detector.is_spike(30.1) is True

    @pytest.mark.requirement("WL-285")
    def test_is_spike_empty_detector(self) -> None:
        """is_spike() returns False for empty detector."""
        detector = MutationSpikeDetector()
        assert detector.is_spike(100) is False

    @pytest.mark.requirement("WL-285")
    def test_is_spike_custom_multiplier(self) -> None:
        """is_spike() respects custom spike_multiplier."""
        config = SpikeConfig(spike_multiplier=2.0, min_samples=2)
        detector = MutationSpikeDetector(config)
        detector.record(10)
        detector.record(10)

        # Baseline is 10, threshold is 20
        assert detector.is_spike(20) is False
        assert detector.is_spike(20.1) is True


class TestMutationSpikeDetectorCheckAndRecord:
    """Test MutationSpikeDetector.check_and_record() method. @trace WL-285"""

    @pytest.mark.requirement("WL-285")
    def test_check_and_record_insufficient_samples(self) -> None:
        """check_and_record returns (False, None) with insufficient samples."""
        detector = MutationSpikeDetector()
        detector.record(5)
        detector.record(10)

        is_spike, baseline_before = detector.check_and_record(100)

        assert is_spike is False
        assert baseline_before is None

    @pytest.mark.requirement("WL-285")
    def test_check_and_record_no_spike(self) -> None:
        """check_and_record correctly reports no spike."""
        detector = MutationSpikeDetector()
        detector.record(10)
        detector.record(10)
        detector.record(10)

        is_spike, baseline_before = detector.check_and_record(20)

        assert is_spike is False
        assert baseline_before == 10.0

    @pytest.mark.requirement("WL-285")
    def test_check_and_record_spike(self) -> None:
        """check_and_record correctly detects spike."""
        detector = MutationSpikeDetector()
        detector.record(10)
        detector.record(10)
        detector.record(10)

        is_spike, baseline_before = detector.check_and_record(31)

        assert is_spike is True
        assert baseline_before == 10.0

    @pytest.mark.requirement("WL-285")
    def test_check_and_record_modifies_window(self) -> None:
        """check_and_record adds count to window."""
        detector = MutationSpikeDetector()
        detector.record(10)
        detector.record(10)
        detector.record(10)

        detector.check_and_record(20)

        # Window should now have 4 items, baseline should be 12.5
        assert detector.baseline() == 12.5

    @pytest.mark.requirement("WL-285")
    def test_check_and_record_baseline_changes(self) -> None:
        """check_and_record uses baseline BEFORE adding new count."""
        detector = MutationSpikeDetector()
        detector.record(10)
        detector.record(10)
        detector.record(10)

        _baseline_before = 10.0
        detector.record(50)  # Manually add outlier
        baseline_after = 20.0  # (10 + 10 + 10 + 50) / 4

        # Now check_and_record should use updated baseline
        _is_spike, recorded_baseline = detector.check_and_record(30)

        # recorded_baseline should reflect state BEFORE this call
        assert recorded_baseline == baseline_after

    @pytest.mark.requirement("WL-285")
    def test_check_and_record_sequential_calls(self) -> None:
        """Multiple check_and_record calls work correctly."""
        detector = MutationSpikeDetector()
        detector.record(10)
        detector.record(10)
        detector.record(10)

        # First call: baseline=10, count=20, no spike
        is_spike_1, baseline_1 = detector.check_and_record(20)
        assert is_spike_1 is False
        assert baseline_1 == 10.0

        # Second call: baseline=12.5 (avg of 10,10,10,20), count=30, no spike
        is_spike_2, baseline_2 = detector.check_and_record(30)
        assert is_spike_2 is False
        assert baseline_2 == 12.5

        # Third call: baseline=16 (avg of 10,10,10,20,30), count=49, is spike (49 > 16*3)
        is_spike_3, baseline_3 = detector.check_and_record(49)
        assert is_spike_3 is True
        assert baseline_3 == 16.0

    @pytest.mark.requirement("WL-285")
    def test_check_and_record_window_overflow(self) -> None:
        """check_and_record respects window_size limit."""
        config = SpikeConfig(window_size=3)
        detector = MutationSpikeDetector(config)

        # Fill window
        detector.record(10)
        detector.record(10)
        detector.record(10)

        # Add one more (should push out first 10)
        detector.check_and_record(20)

        # Baseline should be (10 + 10 + 20) / 3 = 13.33
        baseline = detector.baseline()
        assert abs(baseline - 40 / 3) < 0.01
