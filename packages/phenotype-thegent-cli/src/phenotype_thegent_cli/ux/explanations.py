"""WP-4002: Concise and detailed explanation tiers."""

import enum
import logging
from typing import Any

from phenotype_thegent_core.config import ThegentSettings

_log = logging.getLogger(__name__)


class ExplanationTier(enum.StrEnum):
    """Tier of explanation detail."""

    CONCISE = "concise"
    BALANCED = "balanced"
    DETAILED = "detailed"
    DEBUG = "debug"


class ExplanationGenerator:
    """Generates explanations for agent decisions at different levels of detail."""

    def __init__(self, settings: ThegentSettings) -> None:
        self.settings = settings

    def generate_explanation(self, data: dict[str, Any], tier: ExplanationTier = ExplanationTier.BALANCED) -> str:
        """Generate an explanation based on data and requested tier."""
        intent = data.get("intent", "No intent provided")
        decisions = data.get("decisions", [])
        risks = data.get("risks", [])

        if tier == ExplanationTier.CONCISE:
            return f"Summary: {intent}. {len(decisions)} decisions made."

        if tier == ExplanationTier.BALANCED:
            explanation = f"Goal: {intent}\n"
            if decisions:
                explanation += f"Key Decisions: {', '.join(decisions[:3])}\n"
            if risks:
                explanation += f"Top Risks: {', '.join(risks[:2])}\n"
            return explanation

        if tier == ExplanationTier.DETAILED:
            explanation = f"### Decision Rationale\n**Goal:** {intent}\n\n"
            explanation += "**Decisions Made:**\n"
            for d in decisions:
                explanation += f"- {d}\n"

            explanation += "\n**Risks Identified:**\n"
            for r in risks:
                explanation += f"- {r}\n"
            return explanation

        # Debug tier includes everything
        return f"DEBUG: {data}"
