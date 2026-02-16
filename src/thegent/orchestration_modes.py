"""Multi-agent orchestration mode catalog (G-KD-04).

Formalizes orchestration patterns per Kush docs D-D and Kagentop MultiAgentOrchestration.
Mode selection policy tied to risk, urgency, and confidence.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class MultiAgentMode(StrEnum):
    """Canonical multi-agent orchestration modes."""

    SEQUENTIAL_DELEGATION = "sequential_delegation"
    PARALLEL_CONSENSUS = "parallel_consensus"
    REVIEW_LOOP = "review_loop"


@dataclass
class ModeEntry:
    """Catalog entry for a multi-agent mode."""

    mode: MultiAgentMode
    description: str
    phases: list[str]
    use_case: str
    risk_profile: str  # low, medium, high
    selection_hint: str


MODE_CATALOG: list[ModeEntry] = [
    ModeEntry(
        mode=MultiAgentMode.SEQUENTIAL_DELEGATION,
        description="Step-wise specialization: each agent hands off to the next in sequence",
        phases=["planner", "operator", "operator", "..."],
        use_case="Multi-step workflows where each step requires different expertise",
        risk_profile="medium",
        selection_hint="Use when steps have clear dependencies and sequential ordering",
    ),
    ModeEntry(
        mode=MultiAgentMode.PARALLEL_CONSENSUS,
        description="Independent solution synthesis: multiple agents run in parallel, result aggregated",
        phases=["operator", "operator", "..."],
        use_case="Critical tasks requiring quorum or consensus (e.g. low-confidence escalation)",
        risk_profile="low",
        selection_hint="Use when confidence is low or task requires independent verification",
    ),
    ModeEntry(
        mode=MultiAgentMode.REVIEW_LOOP,
        description="Planner/Operator/Reviewer enforcement: explicit phase gates with approval",
        phases=["planner", "operator", "reviewer"],
        use_case="Governance-heavy workflows with explicit review gates",
        risk_profile="high",
        selection_hint="Use when policy requires planner→operator→reviewer phase enforcement",
    ),
]


def get_mode(mode_id: str) -> ModeEntry | None:
    """Return mode entry by id, or None if not found."""
    try:
        m = MultiAgentMode(mode_id)
        return next((e for e in MODE_CATALOG if e.mode == m), None)
    except ValueError:
        return None


def list_modes() -> list[dict[str, Any]]:
    """Return all modes for CLI/MCP discovery."""
    return [
        {
            "mode": e.mode.value,
            "description": e.description,
            "phases": e.phases,
            "use_case": e.use_case,
            "risk_profile": e.risk_profile,
            "selection_hint": e.selection_hint,
        }
        for e in MODE_CATALOG
    ]


def suggest_mode(risk: str = "medium", urgency: str = "normal", confidence: float = 0.8) -> MultiAgentMode:
    """Suggest mode based on risk, urgency, and confidence (mode selection policy)."""
    if confidence < 0.5:
        return MultiAgentMode.PARALLEL_CONSENSUS
    if risk == "high" and urgency != "critical":
        return MultiAgentMode.REVIEW_LOOP
    return MultiAgentMode.SEQUENTIAL_DELEGATION


class ConflictArbitrator:
    """WP-1006: Arbitration rules and quorum policy for multi-agent consensus."""

    def __init__(self, quorum_threshold: float = 0.6) -> None:
        self.quorum_threshold = quorum_threshold

    def detect_conflicts(self, results: list[Any]) -> list[str]:
        """Detect conflicts between multiple agent outputs."""
        # Simple implementation: compare summary/status
        conflicts = []
        if not results:
            return conflicts

        base = results[0]
        for i, res in enumerate(results[1:], 1):
            if res.csm.status != base.csm.status:
                conflicts.append(f"Status mismatch between agent 0 and {i}")
        return conflicts

    def arbitrate(self, results: list[Any]) -> Any:
        """Arbitrate between conflicting results using quorum policy."""
        if not results:
            return None

        # Majority vote on status
        votes: dict[str, int] = {}
        for res in results:
            s = res.csm.status.value
            votes[s] = votes.get(s, 0) + 1

        winner = max(votes.items(), key=lambda x: x[1])
        if winner[1] / len(results) >= self.quorum_threshold:
            # Return first result that matches winner
            return next(res for res in results if res.csm.status.value == winner[0])

        return results[0]  # Default to first if no quorum


def calculate_risk_score(prompt: str, lane: str) -> float:
    """WP-2008: Calculate risk score for a task to trigger oversight."""
    score = 0.0

    # High-risk keywords
    high_risk = ["delete", "remove", "drop", "purge", "production", "security", "credentials"]
    if any(kw in prompt.lower() for kw in high_risk):
        score += 0.5

    # Lane multiplier
    if lane == "critical":
        score += 0.4
    elif lane == "recovery":
        score += 0.2

    return min(1.0, score)
