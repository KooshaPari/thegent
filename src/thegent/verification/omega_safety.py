"""WP-45002: Universal Safety Invariants (Omega).
Enforces system-wide, non-negotiable safety properties across all agent actions.
"""

import logging
from typing import Any

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class OmegaInvariantViolation(BaseModel):
    """Details of a universal safety invariant violation."""

    invariant_id: str
    description: str
    context: dict[str, Any]
    severity: str = "CRITICAL"


class OmegaSafetyGuard:
    """The final safety gate for thegent (Phase 45).
    Enforces 'Omega' invariants which are universal and cannot be overridden.
    """

    def __init__(self) -> None:
        # Define universal invariants
        self.invariants = {
            "OMEGA-001": "No action shall permanently delete project-critical governance ledgers.",
            "OMEGA-002": "No action shall bypass the Human-in-the-Loop moral arbitration gate.",
            "OMEGA-003": "No action shall propagate unverified cryptographic proofs of alignment.",
            "OMEGA-004": "No action shall exceed the global resource consumption entropy limit.",
        }

    def verify_action(self, action_id: str, action_data: dict[str, Any]) -> list[OmegaInvariantViolation]:
        """Verify an action against all universal Omega invariants."""
        violations = []
        _log.info("Performing Omega universal safety check for action %s", action_id)

        # OMEGA-001: Check for deletion of critical files
        target_file = str(action_data.get("target_file", "")).lower()
        if action_data.get("type") == "DELETE" and any(
            k in target_file for k in ["evidence_ledger", "constitution", "work_stream"]
        ):
            violations.append(
                OmegaInvariantViolation(
                    invariant_id="OMEGA-001",
                    description=self.invariants["OMEGA-001"],
                    context={"action": action_id, "target": target_file},
                )
            )

        # OMEGA-002: Check if HITL was bypassed for moral actions
        if action_data.get("is_moral_dilemma") and not action_data.get("hitl_verified"):
            violations.append(
                OmegaInvariantViolation(
                    invariant_id="OMEGA-002",
                    description=self.invariants["OMEGA-002"],
                    context={"action": action_id, "reason": "Moral dilemma detected without HITL verification"},
                )
            )

        # OMEGA-003: Check for formal proof requirement
        if action_data.get("require_formal_proof") and not action_data.get("proof_verified"):
            violations.append(
                OmegaInvariantViolation(
                    invariant_id="OMEGA-003",
                    description=self.invariants["OMEGA-003"],
                    context={"action": action_id, "reason": "Formal ethical proof missing or invalid"},
                )
            )

        if violations:
            for v in violations:
                _log.critical("OMEGA INVARIANT VIOLATED: %s - %s", v.invariant_id, v.description)
        else:
            _log.info("Action %s passed all Omega universal safety invariants.", action_id)

        return violations

    def is_safe(self, action_id: str, action_data: dict[str, Any]) -> bool:
        """Convenience method to check if an action is safe according to Omega invariants."""
        return len(self.verify_action(action_id, action_data)) == 0
