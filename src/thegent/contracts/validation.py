"""Semantic Validation Layer for agent structured messages.

Enforces invariants and cross-tag logic for CanonicalStructuredMessage (CSM).
"""

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

    # 2. Summary Requirements
    if csm.status == CSMStatus.COMPLETED and not csm.summary:
        issues.append("Status is COMPLETED but summary is empty")

    # 3. FAILED status: should have evidence of failure
    if csm.status == CSMStatus.FAILED and not csm.issues and not csm.decision_reason_code:
        issues.append("Status is FAILED but issues and decision_reason_code are empty")

    # 4. Phase-specific rules (phase-aware validators)
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
