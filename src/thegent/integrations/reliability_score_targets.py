"""Reliability score targets and evaluation helpers.

# @trace WL-299
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReliabilityInputs:
    """Reliability signals normalized to [0,1]."""

    success_rate: float
    low_conflict_rate: float
    sla_hit_rate: float


@dataclass(frozen=True)
class ReliabilityTargets:
    """Target score thresholds over rollout phases."""

    warning: int = 70
    healthy: int = 85
    excellent: int = 95



def _bounded(value: float) -> float:
    if not 0.0 <= value <= 1.0:
        raise ValueError("reliability inputs must be within [0,1]")
    return value


def compute_reliability_score(inputs: ReliabilityInputs) -> int:
    """Compute reliability score [0..100] using fixed deterministic weights."""
    success = _bounded(inputs.success_rate)
    conflicts = _bounded(inputs.low_conflict_rate)
    sla = _bounded(inputs.sla_hit_rate)

    weighted = (0.5 * success) + (0.3 * conflicts) + (0.2 * sla)
    return round(weighted * 100)


def classify_reliability(score: int, targets: ReliabilityTargets) -> str:
    """Classify score against target bands."""
    if not 0 <= score <= 100:
        raise ValueError("score must be within [0,100]")
    if targets.warning > targets.healthy or targets.healthy > targets.excellent:
        raise ValueError("targets must be monotonic warning <= healthy <= excellent")

    if score >= targets.excellent:
        return "excellent"
    if score >= targets.healthy:
        return "healthy"
    if score >= targets.warning:
        return "warning"
    return "critical"
