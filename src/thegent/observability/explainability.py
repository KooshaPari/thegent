"""WP-9002: Explainability stack (summary/detail/trace).

Provides a structured way to generate and present explanations for agent decisions
at three levels of detail.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class DetailLevel(StrEnum):
    SUMMARY = "summary"  # Concise overview
    DETAIL = "detail"  # Full logic and context
    TRACE = "trace"  # Raw events and logs


@dataclass
class Explanation:
    """A single decision explanation at multiple levels."""

    summary: str
    detail: str
    trace: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ExplainabilityEngine:
    """Stack for managing and rendering progressive disclosure explanations."""

    def __init__(self) -> None:
        self._explanations: dict[str, Explanation] = {}

    def record_decision(self, decision_id: str, explanation: Explanation) -> None:
        """Register an explanation for a specific decision."""
        self._explanations[decision_id] = explanation

    def get_explanation(self, decision_id: str, level: DetailLevel = DetailLevel.SUMMARY) -> str:
        """Return the explanation string for the requested level."""
        exp = self._explanations.get(decision_id)
        if not exp:
            return "No explanation available."

        if level == DetailLevel.SUMMARY:
            return exp.summary
        if level == DetailLevel.DETAIL:
            return exp.detail
        if level == DetailLevel.TRACE:
            return "TRACE:\n" + "\n".join(exp.trace)

        return exp.summary

    def render_all(self, decision_id: str) -> str:
        """Render a progressive disclosure view of the explanation."""
        exp = self._explanations.get(decision_id)
        if not exp:
            return "No explanation available."

        return f"""[SUMMARY]
{exp.summary}

[DETAILS]
{exp.detail}

[TRACE]
{self.get_explanation(decision_id, DetailLevel.TRACE)}
"""
