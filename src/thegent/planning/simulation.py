"""Planning simulation overlays: PERT, resource contention, continuity risk (G-CA-04).

Design: docs/PLANNING_SIMULATION_DESIGN.md
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


# --- D1: PERT ---

@dataclass
class PERTNode:
    """Task node for PERT analysis."""

    task_id: str
    optimistic_days: float
    most_likely_days: float
    pessimistic_days: float
    predecessors: list[str]


@dataclass
class PERTResult:
    """PERT analysis result per task."""

    task_id: str
    expected_duration: float
    variance: float
    critical_path: bool
    total_float: float
    confidence_p50: float
    confidence_p90: float


def pert_forward_pass(nodes: list[PERTNode]) -> dict[str, PERTResult]:
    """Compute expected duration, variance, critical path (D1 stub)."""
    results: dict[str, PERTResult] = {}
    for n in nodes:
        exp = (n.optimistic_days + 4 * n.most_likely_days + n.pessimistic_days) / 6.0
        var = ((n.pessimistic_days - n.optimistic_days) / 6.0) ** 2
        results[n.task_id] = PERTResult(
            task_id=n.task_id,
            expected_duration=exp,
            variance=var,
            critical_path=False,
            total_float=0.0,
            confidence_p50=0.5,
            confidence_p90=0.9,
        )
    return results


# --- D2: Resource contention ---

@dataclass
class ResourceProfile:
    """Resource capacity definition."""

    resource_id: str
    capacity: float
    unit: str = "concurrent"


@dataclass
class TaskResourceDemand:
    """Task demand for a resource."""

    task_id: str
    resource_id: str
    demand: float
    start_float: float
    duration_float: float


@dataclass
class ContentionResult:
    """Resource contention analysis result."""

    resource_id: str
    time_window: tuple[float, float]
    peak_demand: float
    capacity: float
    contention_ratio: float
    affected_tasks: list[str]


def simulate_resource_contention(
    tasks: list[Any],
    resources: list[ResourceProfile],
    schedule: dict[str, Any],
) -> list[ContentionResult]:
    """Identify resource contention windows (D2 stub)."""
    return []


# --- D3: Continuity risk ---

@dataclass
class ContinuityRiskInput:
    """Input for continuity risk scoring."""

    open_tasks: list[dict[str, Any]]
    handoff_windows: list[tuple[datetime, datetime]]
    snapshot_freshness: dict[str, datetime]
    owner_coverage: dict[str, list[str]]


@dataclass
class ContinuityRiskResult:
    """Continuity risk score and factors."""

    risk_score: float
    factors: list[str]
    high_risk_tasks: list[str]
    recommendations: list[str]


def score_continuity_risk(input: ContinuityRiskInput) -> ContinuityRiskResult:
    """Compute continuity risk for shift handoff (D3 stub)."""
    risk = 0.0
    factors: list[str] = []
    high_risk: list[str] = []
    recs: list[str] = []
    if not input.open_tasks:
        return ContinuityRiskResult(0.0, [], [], [])
    # Stub: risk increases with open tasks and stale snapshots
    for t in input.open_tasks:
        tid = t.get("id", t.get("task_id", "unknown"))
        age = input.snapshot_freshness.get(tid)
        if isinstance(age, datetime):
            now = datetime.now(UTC)
            age_utc = age if age.tzinfo else age.replace(tzinfo=UTC)
            delta = (now - age_utc).total_seconds() / 3600.0
            if delta > 24:
                risk += 0.2
                factors.append(f"Stale snapshot: {tid} ({delta:.0f}h old)")
                high_risk.append(tid)
    risk = min(1.0, risk)
    if risk > 0.5:
        recs.append("Refresh snapshots before handoff")
    return ContinuityRiskResult(risk, factors, high_risk, recs)
