"""Conflict triage categories and routing for governance workflows.

Classifies conflicts by severity/category and assigns owner routing metadata,
enabling intelligent escalation and assignment in multi-tenant environments.

# @trace WL-269
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TriageCategory(Enum):
    """Conflict triage categories for routing and escalation.

    Attributes:
        AUTO_RESOLVE: Conflict can be automatically resolved (e.g., timestamp conflicts).
        MANUAL_REVIEW: Conflict requires human review before resolution.
        ESCALATE: Conflict must be escalated to senior engineering or governance.
    """

    AUTO_RESOLVE = "auto_resolve"
    MANUAL_REVIEW = "manual_review"
    ESCALATE = "escalate"


@dataclass
class ConflictTriageRule:
    """Rule for classifying a specific field's conflicts.

    Attributes:
        field_name: Name of the field subject to triage.
        category: The TriageCategory assigned to conflicts on this field.
    """

    field_name: str
    category: TriageCategory


class ConflictTriageEngine:
    """Engine for classifying and routing conflicts by severity.

    Manages a registry of triage rules and provides methods to classify conflicts
    on specific fields and batch-triage multiple fields.
    """

    def __init__(self):
        """Initialize the conflict triage engine with an empty rule registry."""
        self._rules: dict[str, ConflictTriageRule] = {}

    def add_rule(self, field_name: str, category: TriageCategory) -> ConflictTriageRule:
        """Add a triage rule for a specific field.

        Args:
            field_name: Name of the field.
            category: The TriageCategory to assign.

        Returns:
            The created ConflictTriageRule.
        """
        rule = ConflictTriageRule(field_name=field_name, category=category)
        self._rules[field_name] = rule

        logger.debug(f"Added triage rule for field '{field_name}': {category.value}")

        return rule

    def triage(self, field_name: str) -> TriageCategory:
        """Determine the triage category for conflicts on a field.

        Returns the category from the rule if one exists, otherwise defaults
        to MANUAL_REVIEW.

        Args:
            field_name: Name of the field.

        Returns:
            The TriageCategory for the field (default: MANUAL_REVIEW).
        """
        rule = self._rules.get(field_name)

        if rule is None:
            logger.debug(f"No triage rule for field '{field_name}'; defaulting to MANUAL_REVIEW")
            return TriageCategory.MANUAL_REVIEW

        logger.debug(f"Triaged field '{field_name}': {rule.category.value}")
        return rule.category

    def triage_all(self, fields: list[str]) -> dict[str, TriageCategory]:
        """Triage multiple fields at once.

        Args:
            fields: List of field names to triage.

        Returns:
            Dictionary mapping each field name to its TriageCategory.
        """
        result = {}
        for field_name in fields:
            result[field_name] = self.triage(field_name)

        logger.debug(f"Triaged {len(result)} fields")
        return result
