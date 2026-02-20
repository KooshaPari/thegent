"""Adaptive hierarchical/P2P coordination strategy.

Switches between hierarchical (tree-based) and P2P (mesh) coordination
modes based on swarm size and average agent load.

Mode selection:
  HIERARCHICAL  — swarm_size < THGENT_HIER_THRESHOLD (default 5) OR avg_load < 0.3
  P2P           — swarm_size >= threshold AND avg_load >= 0.7
  ADAPTIVE      — gradual blend in the range [0.3, 0.7) avg_load

Routing:
  HIERARCHICAL  — always delegate to agents[0] (coordinator)
  P2P           — round-robin across all agents
  ADAPTIVE      — weighted blend: probabilistically picks coordinator vs
                  round-robin based on avg_load
"""

from __future__ import annotations

import logging
import os
import random
from dataclasses import dataclass
from enum import Enum

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------

_DEFAULT_HIER_THRESHOLD = 5


def _hier_threshold() -> int:
    """Return swarm-size threshold; read from env at call time (monkeypatch-safe)."""
    raw = os.environ.get("THGENT_HIER_THRESHOLD", "")
    if raw.strip():
        try:
            value = int(raw.strip())
        except ValueError:
            _log.warning("THGENT_HIER_THRESHOLD=%r is not a valid integer; using default %d", raw, _DEFAULT_HIER_THRESHOLD)
            return _DEFAULT_HIER_THRESHOLD
        if value < 1:
            _log.warning("THGENT_HIER_THRESHOLD=%d is < 1; using default %d", value, _DEFAULT_HIER_THRESHOLD)
            return _DEFAULT_HIER_THRESHOLD
        return value
    return _DEFAULT_HIER_THRESHOLD


# ---------------------------------------------------------------------------
# Enums and dataclasses
# ---------------------------------------------------------------------------


class CoordinationMode(Enum):
    """Available coordination modes."""

    HIERARCHICAL = "hierarchical"
    P2P = "p2p"
    ADAPTIVE = "adaptive"


@dataclass
class CoordinationMetrics:
    """Snapshot of a routing decision."""

    mode: CoordinationMode
    swarm_size: int
    avg_load: float
    routed_to: str


# ---------------------------------------------------------------------------
# Strategy
# ---------------------------------------------------------------------------


class HybridCoordinationStrategy:
    """Adaptive coordination strategy that blends hierarchical and P2P routing.

    Usage::

        strategy = HybridCoordinationStrategy()
        mode = strategy.select_mode(swarm_size=8, avg_load=0.65)
        agent = strategy.route_task("task-1", agents, mode)
    """

    # Load thresholds for mode selection (class-level for testability)
    LOW_LOAD_THRESHOLD: float = 0.3
    HIGH_LOAD_THRESHOLD: float = 0.7

    def __init__(self, *, seed: int | None = None) -> None:
        """Initialise strategy.

        Args:
            seed: Optional RNG seed for deterministic ADAPTIVE routing in tests.
        """
        self._rng = random.Random(seed)  # noqa: S311 -- non-cryptographic routing, determinism for tests
        # Per-agent round-robin counter for P2P mode
        self._rr_index: int = 0

    # ------------------------------------------------------------------
    # Mode selection
    # ------------------------------------------------------------------

    def select_mode(self, swarm_size: int, avg_load: float) -> CoordinationMode:
        """Select the coordination mode based on swarm size and average load.

        Args:
            swarm_size: Number of agents currently in the swarm.
            avg_load: Average load across agents (0.0 – 1.0).

        Returns:
            The appropriate :class:`CoordinationMode`.
        """
        threshold = _hier_threshold()

        # HIERARCHICAL when small swarm OR very low load
        if swarm_size < threshold or avg_load < self.LOW_LOAD_THRESHOLD:
            _log.debug(
                "select_mode → HIERARCHICAL (swarm_size=%d, threshold=%d, avg_load=%.3f)",
                swarm_size,
                threshold,
                avg_load,
            )
            return CoordinationMode.HIERARCHICAL

        # P2P when swarm is large AND load is high
        if avg_load >= self.HIGH_LOAD_THRESHOLD:
            _log.debug(
                "select_mode → P2P (swarm_size=%d, avg_load=%.3f)",
                swarm_size,
                avg_load,
            )
            return CoordinationMode.P2P

        # In-between: ADAPTIVE blend
        _log.debug(
            "select_mode → ADAPTIVE (swarm_size=%d, avg_load=%.3f)",
            swarm_size,
            avg_load,
        )
        return CoordinationMode.ADAPTIVE

    # ------------------------------------------------------------------
    # Task routing
    # ------------------------------------------------------------------

    def route_task(
        self,
        task_id: str,
        agents: list[str],
        mode: CoordinationMode,
        avg_load: float = 0.5,
    ) -> str:
        """Route a task to an agent according to the given mode.

        Args:
            task_id: Identifier of the task being routed.
            agents: Ordered list of available agent IDs. Must be non-empty.
            mode: The :class:`CoordinationMode` to apply.
            avg_load: Current average load (used only in ADAPTIVE mode for
                weighting; defaults to 0.5).

        Returns:
            The chosen agent ID.

        Raises:
            ValueError: If *agents* is empty.
        """
        if not agents:
            raise ValueError(f"Cannot route task '{task_id}': agents list is empty")

        if mode == CoordinationMode.HIERARCHICAL:
            chosen = self._route_hierarchical(agents)
        elif mode == CoordinationMode.P2P:
            chosen = self._route_p2p(agents)
        elif mode == CoordinationMode.ADAPTIVE:
            chosen = self._route_adaptive(agents, avg_load)
        else:
            # Defensive fallback — should never happen with Enum exhaustion
            _log.warning("Unknown mode %r; falling back to HIERARCHICAL", mode)
            chosen = self._route_hierarchical(agents)

        _log.debug("route_task '%s' → '%s' via %s", task_id, chosen, mode.value)
        return chosen

    # ------------------------------------------------------------------
    # Routing helpers
    # ------------------------------------------------------------------

    def _route_hierarchical(self, agents: list[str]) -> str:
        """Return the coordinator agent (index 0)."""
        return agents[0]

    def _route_p2p(self, agents: list[str]) -> str:
        """Round-robin among all agents."""
        chosen = agents[self._rr_index % len(agents)]
        self._rr_index += 1
        return chosen

    def _route_adaptive(self, agents: list[str], avg_load: float) -> str:
        """Weighted blend: higher load → more P2P; lower load → more hierarchical.

        The probability of choosing P2P grows linearly from 0 at
        ``LOW_LOAD_THRESHOLD`` to 1 at ``HIGH_LOAD_THRESHOLD``.
        """
        load_range = self.HIGH_LOAD_THRESHOLD - self.LOW_LOAD_THRESHOLD
        # Clamp avg_load to the adaptive band
        clamped = max(self.LOW_LOAD_THRESHOLD, min(avg_load, self.HIGH_LOAD_THRESHOLD))
        p2p_weight = (clamped - self.LOW_LOAD_THRESHOLD) / load_range  # [0, 1]

        if self._rng.random() < p2p_weight:
            return self._route_p2p(agents)
        return self._route_hierarchical(agents)

    # ------------------------------------------------------------------
    # Convenience: select + route in one call
    # ------------------------------------------------------------------

    def coordinate(
        self,
        task_id: str,
        agents: list[str],
        swarm_size: int,
        avg_load: float,
    ) -> CoordinationMetrics:
        """Select mode, route the task, and return :class:`CoordinationMetrics`.

        Args:
            task_id: Task identifier.
            agents: Available agent IDs (non-empty).
            swarm_size: Total swarm size (may differ from ``len(agents)``).
            avg_load: Average agent load (0.0 – 1.0).

        Returns:
            :class:`CoordinationMetrics` with the routing decision.
        """
        mode = self.select_mode(swarm_size, avg_load)
        routed_to = self.route_task(task_id, agents, mode, avg_load=avg_load)
        return CoordinationMetrics(
            mode=mode,
            swarm_size=swarm_size,
            avg_load=avg_load,
            routed_to=routed_to,
        )
