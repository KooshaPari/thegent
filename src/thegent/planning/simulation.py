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
            confidence_p50=exp,
            confidence_p90=exp + (1.28 * (var**0.5)),
        )
    return results


def simulate_monte_carlo(nodes: list[PERTNode], iterations: int = 1000) -> dict[str, dict[str, float]]:
    """WP-8002: Monte Carlo simulation for task durations using triangular distribution."""
    import random

    from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

    task_histories: dict[str, list[float]] = {n.task_id: [] for n in nodes}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Simulating durations...", total=iterations)
        for _ in range(iterations):
            for n in nodes:
                # Triangular distribution: lower, mode, upper
                val = random.triangular(n.optimistic_days, n.pessimistic_days, n.most_likely_days)  # noqa: S311 -- Monte Carlo sampling, not cryptographic; statistical sampling only
                task_histories[n.task_id].append(val)
            progress.update(task, advance=1)

    stats: dict[str, dict[str, float]] = {}
    for tid, history in task_histories.items():
        sorted_history = sorted(history)
        stats[tid] = {
            "p50": sorted_history[int(iterations * 0.5)],
            "p80": sorted_history[int(iterations * 0.8)],
            "p95": sorted_history[int(iterations * 0.95)],
            "avg": sum(history) / iterations,
        }
    return stats


def extract_plan_graph(dag: Any) -> list[PERTNode]:
    """WP-8001: Extract PERT nodes from a DagDocument."""
    nodes = []
    for t in dag.tasks:
        # Default durations if not provided in metadata
        meta = t.get("metadata", {})
        nodes.append(
            PERTNode(
                task_id=t["id"],
                optimistic_days=meta.get("opt_days", 1.0),
                most_likely_days=meta.get("ml_days", 2.0),
                pessimistic_days=meta.get("pess_days", 5.0),
                predecessors=t.get("depends_on", []),
            )
        )
    return nodes


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
    _: dict[str, Any],
) -> list[ContentionResult]:
    """Identify resource contention windows (D2 stub)."""
    return []


def analyze_bottlenecks(nodes: list[PERTNode], mc_stats: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    """WP-8003: Identify top bottlenecks and tasks with no slack."""
    bottlenecks = []
    for n in nodes:
        stats = mc_stats.get(n.task_id, {})
        # A bottleneck is a task with high variance or high p95/avg ratio
        variance_score = (stats.get("p95", 0) - stats.get("p50", 0)) / max(0.1, stats.get("avg", 1))
        if variance_score > 1.5:
            bottlenecks.append(
                {
                    "task_id": n.task_id,
                    "type": "high_variance",
                    "score": variance_score,
                    "reason": "Duration highly uncertain (Monte Carlo p95 vs p50)",
                }
            )

    # Dependency-based bottleneck: many children
    child_counts: dict[str, int] = {}
    for n in nodes:
        for p in n.predecessors:
            child_counts[p] = child_counts.get(p, 0) + 1

    for tid, count in child_counts.items():
        if count >= 3:
            bottlenecks.append(
                {
                    "task_id": tid,
                    "type": "critical_dependency",
                    "score": float(count),
                    "reason": f"Gates {count} downstream tasks",
                }
            )

    return sorted(bottlenecks, key=lambda x: x["score"], reverse=True)


def suggest_reschedules(bottlenecks: list[dict[str, Any]]) -> list[str]:
    """WP-8004: Recommendations for rescheduling or resource reallocation."""
    recs = []
    for b in bottlenecks:
        if b["type"] == "high_variance":
            recs.append(f"Task {b['task_id']}: Highly uncertain. Recommend splitting or adding redundant providers.")
        elif b["type"] == "critical_dependency":
            recs.append(f"Task {b['task_id']}: Critical bottleneck. Prioritize resources and ensure early start.")
    return recs


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

    # WP-8005: Predictive model for continuity
    now = datetime.now(UTC)
    for t in input.open_tasks:
        tid = t.get("id", t.get("task_id", "unknown"))

        # Factor 1: Snapshot staleness
        age = input.snapshot_freshness.get(tid)
        if isinstance(age, datetime):
            age_utc = age if age.tzinfo else age.replace(tzinfo=UTC)
            delta_h = (now - age_utc).total_seconds() / 3600.0
            if delta_h > 4:
                risk += 0.1 * (delta_h / 4)
                factors.append(f"Stale snapshot: {tid} ({delta_h:.1f}h old)")

        # Factor 2: Lack of owner coverage
        owners = input.owner_coverage.get(tid, [])
        if len(owners) < 2:
            risk += 0.2
            factors.append(f"Low owner redundancy: {tid} (only {len(owners)} owner)")

        if risk > 0.4:
            high_risk.append(tid)

    risk = min(1.0, risk)
    if risk > 0.5:
        recs.append("Recommend immediate shift handoff and snapshot refresh.")
    return ContinuityRiskResult(risk, factors, high_risk, recs)


def continuity_risk_predictor(registry: Any) -> dict[str, Any]:
    """WP-11007: Predicts continuity risk before predicted shift or stall events."""
    # Simplified prediction based on recent history
    runs = registry.list_runs(limit=50)
    failed_handoffs = sum(1 for r in runs if r.get("error_class") == "handoff_failure")

    risk_level = "low"
    if failed_handoffs > 2:
        risk_level = "high"
    elif failed_handoffs > 0:
        risk_level = "medium"

    return {
        "risk_level": risk_level,
        "failed_handoff_count": failed_handoffs,
        "warning": "Continuity risk predicted for upcoming shift."
        if risk_level != "low"
        else "No immediate continuity risk.",
    }


def surge_watcher(recent_runs: list[dict[str, Any]], threshold: int = 50) -> dict[str, Any]:
    """WP-8006: Monitor surge in runs and recommend safe-mode."""
    # ... previous implementation ...
    return {
        "surge": len(recent_runs) > threshold,
        "recommendation": "safe-mode" if len(recent_runs) > threshold else "normal",
    }


class BudgetGuard:
    """WP-8007: Adaptive routing budget guard based on predictive load."""

    def __init__(self, daily_budget_usd: float) -> None:
        self.daily_budget_usd = daily_budget_usd

    def should_throttle(self, current_spend: float, predicted_load_pct: float) -> dict[str, Any]:
        """Determine if we should throttle non-critical tasks."""
        remaining = self.daily_budget_usd - current_spend
        usage_pct = current_spend / self.daily_budget_usd

        # If spend > 80% and predicted load is high, throttle
        throttle = False
        reason = "Budget healthy"

        if usage_pct > 0.8 and predicted_load_pct > 0.5:
            throttle = True
            reason = f"High budget utilization ({usage_pct:.1%}) and high predicted load."

        return {
            "throttle": throttle,
            "reason": reason,
            "remaining_usd": remaining,
            "action": "DEFER_NON_CRITICAL" if throttle else "ALLOW_ALL",
        }


class RunbookAuthor:
    """WP-8008: Simulation-backed runbook generation."""

    # ... previous implementation ...


class InterventionPolicy:
    """WP-8009: Governance for semi-automated intervention decisions."""

    def evaluate_intervention(self, risk_score: float, confidence: float) -> str:
        """Return the required oversight level for an intervention."""
        if risk_score > 0.8:
            return "HUMAN_OVERSIGHT_REQUIRED"
        if confidence < 0.6:
            return "PEER_REVIEW_REQUIRED"
        return "AUTO_APPROVE"


class ForecastAuditor:
    """WP-8010/11002: Audit and calibration of hardened duration forecasts."""

    def __init__(self) -> None:
        self.actuals: list[tuple[float, float]] = []  # (predicted, actual)
        self._forecast_quality_log: list[dict[str, Any]] = []

    def record_actual(self, predicted: float, actual: float, task_id: str = "unknown") -> None:
        """Record a data point for calibration and quality tracking."""
        self.actuals.append((predicted, actual))
        error = abs(predicted - actual) / max(0.1, actual)
        self._forecast_quality_log.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "task_id": task_id,
                "predicted": predicted,
                "actual": actual,
                "error_pct": error * 100.0,
            }
        )

    def get_calibration_error(self) -> float:
        """Calculate Mean Absolute Percentage Error (MAPE)."""
        if not self.actuals:
            return 0.0
        errors = [abs(p - a) / max(0.1, a) for p, a in self.actuals]
        return sum(errors) / len(errors)

    def get_bias(self) -> float:
        """Calculate prediction bias (p - a). Positive means over-optimistic/long?"""
        if not self.actuals:
            return 0.0
        return sum(p - a for p, a in self.actuals) / len(self.actuals)

    def check_drift(self, threshold: float = 0.2) -> bool:
        """WP-11002: Check if forecast quality has drifted beyond threshold over 14 days (simplified)."""
        if len(self._forecast_quality_log) < 20:
            return False

        recent = self._forecast_quality_log[-10:]
        recent_mape = sum(e["error_pct"] for e in recent) / 1000.0

        return recent_mape > threshold
