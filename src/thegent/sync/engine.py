"""Sync engine guardrails.

# @trace WL-208
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SyncEngineConfig:
    """Core per-cycle sync guardrails."""

    max_changes_per_cycle: int


def enforce_max_changes_per_cycle(*, attempted_changes: int, config: SyncEngineConfig) -> None:
    """Fail loudly when attempted writes exceed configured guardrail."""
    if config.max_changes_per_cycle <= 0:
        raise ValueError("max_changes_per_cycle must be positive")
    if attempted_changes > config.max_changes_per_cycle:
        raise RuntimeError(
            f"max changes exceeded: attempted={attempted_changes} max={config.max_changes_per_cycle}"
        )

