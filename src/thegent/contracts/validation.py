"""Semantic Validation Layer for agent structured messages.

Enforces invariants and cross-tag logic for CanonicalStructuredMessage (CSM).
"""

from collections.abc import Callable
from typing import Any

from thegent.contracts.csm import CanonicalStructuredMessage, CSMPhase, CSMStatus


class SemanticValidationError(Exception):
    """Raised when a CSM fails semantic validation."""


class InvariantViolation(SemanticValidationError):
    """Raised when a specific invariant is violated."""


def validate_csm(csm: CanonicalStructuredMessage) -> list[str]:
    """Perform semantic validation on a CSM.

    Returns:
        List of validation issue strings. Empty if valid.
    """
    issues: list[str] = []

    # 1. Status vs Progress
    if csm.status == CSMStatus.COMPLETED and csm.progress < 1.0:
        issues.append("Status is COMPLETED but progress is < 1.0")
    if csm.status == CSMStatus.PENDING and csm.progress > 0.0:
        issues.append("Status is PENDING but progress is > 0.0")
    if csm.status == CSMStatus.IN_PROGRESS and (csm.progress < 0.0 or csm.progress >= 1.0):
        issues.append("Status is IN_PROGRESS but progress must be in [0, 1)")
    if csm.progress < 0.0 or csm.progress > 1.0:
        issues.append("Progress must be in [0, 1]")

    # 2. Summary Requirements
    if csm.status == CSMStatus.COMPLETED and not csm.summary:
        issues.append("Status is COMPLETED but summary is empty")

    # 3. FAILED status: should have evidence of failure (issues or blockers)
    if csm.status == CSMStatus.FAILED and not csm.issues and not csm.decision_reason_code and not csm.blockers:
        issues.append("Status is FAILED but issues, blockers and decision_reason_code are empty")

    # 4. Confidence Level validation
    if csm.confidence_level < 0.0 or csm.confidence_level > 1.0:
        issues.append("Confidence level must be in [0, 1]")

    # 5. Blockers vs Status
    if csm.blockers and csm.status == CSMStatus.COMPLETED:
        issues.append("Status is COMPLETED but active blockers are present")

    # 6. Phase-specific rules (phase-aware validators)
    if csm.phase == CSMPhase.REVIEWER and not csm.decision_reason_code:
        issues.append("Phase is REVIEWER but decision_reason_code is missing")
    if csm.phase == CSMPhase.PLANNER and csm.status == CSMStatus.COMPLETED and not csm.objective:
        issues.append("Phase is PLANNER and COMPLETED but objective is empty")
    if (
        csm.phase == CSMPhase.OPERATOR
        and csm.status == CSMStatus.COMPLETED
        and not csm.actions_completed
        and not csm.summary
    ):
        issues.append("Phase is OPERATOR and COMPLETED but actions_completed and summary are empty")

    return issues


def ensure_valid_csm(csm: CanonicalStructuredMessage) -> None:
    """Raise InvariantViolation if CSM is semantically invalid."""
    issues = validate_csm(csm)
    if issues:
        raise InvariantViolation(f"CSM semantic validation failed: {'; '.join(issues)}")


class SemanticPolicyEngine:
    """WP-7005: Policy layer for semantic validation of agent outputs."""

    def __init__(self, strict: bool = False) -> None:
        self.strict = strict
        self._rules: list[Callable[[CanonicalStructuredMessage], list[str]]] = []

    def add_rule(self, rule: Callable[[CanonicalStructuredMessage], list[str]]) -> None:
        """Register a custom validation rule."""
        self._rules.append(rule)

    def evaluate(self, csm: CanonicalStructuredMessage) -> dict[str, Any]:
        """Evaluate CSM against all semantic rules.

        Returns:
            Dict with 'allowed', 'issues', 'drift_detected'.
        """
        issues = validate_csm(csm)
        for rule in self._rules:
            issues.extend(rule(csm))

        drift_detected = False
        # Simple drift detection: if confidence changed significantly from metadata
        # (Assuming metadata might store expected confidence)
        prev_conf = None
        meta = getattr(csm, "metadata", None)
        if isinstance(meta, dict):
            prev_conf = meta.get("expected_confidence")
        if prev_conf is not None and abs(csm.confidence_level - prev_conf) > 0.3:
            drift_detected = True

        allowed = not issues if self.strict else True

        return {
            "allowed": allowed,
            "issues": issues,
            "drift_detected": drift_detected,
            "policy_version": "v1.0",
        }
