"""Simulation and sandbox implementations."""

from thegent.simulation.replay import (
    ReplayEvent,
    ReplaySession,
    SimulationReplayEngine,
)

# Backward-compatible alias: the legacy class was named SimulationReplay.
SimulationReplay = SimulationReplayEngine

__all__ = [
    "ReplayEvent",
    "ReplaySession",
    "SimulationReplay",
    "SimulationReplayEngine",
]
