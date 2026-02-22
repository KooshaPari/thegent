"""Enterprise rollout scorecard for release readiness assessment.

Tracks completion of required checks and provides go/no-go decision for release.

FR traceability: WL-320 (Enterprise Rollout Scorecard)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import ClassVar

logger = logging.getLogger(__name__)


@dataclass
class ScorecardCheck:
    """A single check in a rollout scorecard.

    Attributes:
        name: Name of the check.
        passed: Whether the check passed.
        details: Additional details about the check result.
    """

    name: str
    passed: bool
    details: str = ""


class RolloutScorecard:
    """Enterprise rollout scorecard for release readiness assessment.

    Tracks required checks and computes overall readiness score.
    """

    REQUIRED_CHECKS: ClassVar[list[str]] = [
        "auth_scopes",
        "startup_validation",
        "mapping_validated",
        "conflict_guardrails",
        "rate_limit_configured",
        "rollback_snapshot",
        "compliance_snapshot",
        "drift_baseline",
    ]

    def __init__(self) -> None:
        """Initialize an empty scorecard."""
        self._checks: dict[str, ScorecardCheck] = {}

    def add_check(self, name: str, passed: bool, details: str = "") -> None:
        """Add a check result to the scorecard.

        Args:
            name: Name of the check.
            passed: Whether the check passed.
            details: Optional additional details about the check.
        """
        self._checks[name] = ScorecardCheck(name=name, passed=passed, details=details)

    def score(self) -> float:
        """Calculate the readiness score as a fraction of required checks passed.

        Checks that have not been added are counted as failed.

        Returns:
            A fraction from 0.0 to 1.0 representing the fraction of required checks
            that have been passed.
        """
        passed_count = 0
        for check_name in self.REQUIRED_CHECKS:
            if check_name in self._checks and self._checks[check_name].passed:
                passed_count += 1

        return passed_count / len(self.REQUIRED_CHECKS)

    def is_go(self) -> bool:
        """Determine if rollout is approved (go/no-go decision).

        Returns True if and only if all required checks have been added and passed.

        Returns:
            True if all required checks passed, False otherwise.
        """
        return self.score() == 1.0

    def summary(self) -> dict:
        """Get a summary of the scorecard.

        Returns:
            A dictionary with keys:
            - "score": float from 0.0 to 1.0
            - "go": bool indicating if rollout is approved
            - "checks": list of check dictionaries with name, passed, details
        """
        checks_list = []
        for check_name in self.REQUIRED_CHECKS:
            if check_name in self._checks:
                check = self._checks[check_name]
                checks_list.append(
                    {
                        "name": check.name,
                        "passed": check.passed,
                        "details": check.details,
                    }
                )
            else:
                checks_list.append(
                    {
                        "name": check_name,
                        "passed": False,
                        "details": "",
                    }
                )

        return {
            "score": self.score(),
            "go": self.is_go(),
            "checks": checks_list,
        }
