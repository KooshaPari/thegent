"""CI benchmark gates for performance regression detection.

Manages performance benchmark thresholds and validation against
actual measured results to detect regressions.

FR traceability: WL-275 (CI Benchmark Gates)
# @trace WL-275
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkGate:
    """A performance benchmark gate with threshold and result."""

    name: str
    threshold_ms: float
    actual_ms: float | None = None


class CIBenchmarkGates:
    """Manages CI benchmark gates and regression detection."""

    def __init__(self) -> None:
        """Initialize the CI benchmark gates manager."""
        self._gates: dict[str, BenchmarkGate] = {}
        logger.debug("Initialized CI benchmark gates")

    def add_gate(self, name: str, threshold_ms: float) -> BenchmarkGate:
        """Add a benchmark gate with a performance threshold.

        Args:
            name: Name of the benchmark gate.
            threshold_ms: Performance threshold in milliseconds.

        Raises:
            ValueError: If threshold_ms < 1.0.
        """
        if threshold_ms < 1.0:
            raise ValueError("threshold_ms must be >= 1.0")

        gate = BenchmarkGate(name=name, threshold_ms=threshold_ms)
        self._gates[name] = gate
        logger.debug(f"Added benchmark gate: {name} ({threshold_ms}ms)")
        return gate

    def record_result(self, name: str, actual_ms: float) -> None:
        """Record actual measurement result for a benchmark gate.

        Args:
            name: Name of the benchmark gate.
            actual_ms: Actual measured time in milliseconds.

        Raises:
            ValueError: If gate not found or actual_ms < 0.
        """
        if actual_ms < 0.0:
            raise ValueError("actual_ms must be >= 0.0")

        gate = self._gates.get(name)
        if gate is None:
            raise ValueError(f"Benchmark gate not found: {name}")

        gate.actual_ms = actual_ms
        logger.debug(f"Recorded result for {name}: {actual_ms}ms")

    def evaluate(self) -> list[BenchmarkGate]:
        """Get all benchmark gates with their results.

        Returns:
            List of all BenchmarkGate objects (with or without results).
        """
        return list(self._gates.values())

    def failed_gates(self) -> list[BenchmarkGate]:
        """Get benchmark gates that exceeded their thresholds.

        Returns:
            List of BenchmarkGate objects where actual_ms > threshold_ms.
        """
        return [
            gate
            for gate in self._gates.values()
            if gate.actual_ms is not None and gate.actual_ms > gate.threshold_ms
        ]

    def passed(self) -> bool:
        """Check if all gates passed (no regressions detected).

        Returns:
            True if no gates exceeded thresholds, False otherwise.
        """
        return len(self.failed_gates()) == 0
