"""Mutation spike anomaly detector for observing mutation rate anomalies.

Detects anomalous spikes in mutation counts relative to a rolling baseline.

FR traceability: WL-285 (Mutation Spike Anomaly Detector)
"""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SpikeConfig:
    """Configuration for spike detection.

    Attributes:
        window_size: Size of the rolling window (default: 10).
        spike_multiplier: Threshold multiplier for baseline (default: 3.0).
        min_samples: Minimum samples required for baseline (default: 3).
    """

    window_size: int = 10
    spike_multiplier: float = 3.0
    min_samples: int = 3


class MutationSpikeDetector:
    """Detects anomalous spikes in mutation counts.

    Maintains a rolling window of mutation counts and compares against
    the baseline mean.
    """

    def __init__(self, config: SpikeConfig | None = None) -> None:
        """Initialize the detector with optional configuration.

        Args:
            config: SpikeConfig for customization, or None to use defaults.
        """
        if config is None:
            config = SpikeConfig()
        self.config = config
        self._window: deque[int] = deque(maxlen=config.window_size)

    def record(self, count: int) -> None:
        """Record a mutation count in the window.

        Args:
            count: The mutation count to record.
        """
        self._window.append(count)

    def baseline(self) -> float | None:
        """Get the baseline (mean) of recorded counts.

        Returns:
            The mean of the recorded counts, or None if fewer than min_samples
            have been recorded.
        """
        if len(self._window) < self.config.min_samples:
            return None
        return sum(self._window) / len(self._window)

    def is_spike(self, count: int) -> bool:
        """Check if a count represents a spike relative to baseline.

        A spike is detected when:
        - count > baseline * spike_multiplier AND
        - len(window) >= min_samples

        Otherwise returns False.

        Args:
            count: The mutation count to check.

        Returns:
            True if the count is a spike, False otherwise.
        """
        if len(self._window) < self.config.min_samples:
            return False

        baseline_val = self.baseline()
        if baseline_val is None:
            return False

        return count > baseline_val * self.config.spike_multiplier

    def check_and_record(self, count: int) -> tuple[bool, float | None]:
        """Check for spike BEFORE recording, then record the count.

        Args:
            count: The mutation count to check and record.

        Returns:
            A tuple of (is_spike_before_record, baseline_before_record).
        """
        is_spike_before = self.is_spike(count)
        baseline_before = self.baseline()

        self.record(count)

        return (is_spike_before, baseline_before)
