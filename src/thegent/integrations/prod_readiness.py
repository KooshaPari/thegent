"""Production readiness gate for pre-release validation.

# @trace WL-220
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass
class ReadinessCheck:
    """Represents a single readiness check result.

    Attributes:
        name: Name of the check.
        passed: Whether the check passed.
        message: Optional message with details about the check result.
    """

    name: str
    passed: bool
    message: str = ""


class ProductionReadinessGate:
    """Gate to validate production readiness before release."""

    REQUIRED: ClassVar[list[str]] = [
        "connector_auth",
        "mapping_config",
        "startup_validation",
        "rollback_ready",
        "monitoring_active",
        "compliance_baseline",
    ]

    def __init__(self) -> None:
        """Initialize the production readiness gate."""
        self._checks: dict[str, ReadinessCheck] = {}

    def add(self, check: ReadinessCheck) -> None:
        """Add a readiness check result.

        Args:
            check: The ReadinessCheck to add.
        """
        self._checks[check.name] = check

    def evaluate(self) -> bool:
        """Evaluate production readiness.

        Returns:
            True if ALL required checks are present and passed, False otherwise.
        """
        for required_check in self.REQUIRED:
            if required_check not in self._checks:
                return False
            if not self._checks[required_check].passed:
                return False
        return True

    def missing_checks(self) -> list[str]:
        """Get list of required checks that have not been added.

        Returns:
            List of missing check names.
        """
        return [
            check_name
            for check_name in self.REQUIRED
            if check_name not in self._checks
        ]

    def failed_checks(self) -> list[str]:
        """Get list of checks that were added but failed.

        Returns:
            List of failed check names.
        """
        return [
            check_name
            for check_name in self._checks
            if not self._checks[check_name].passed
        ]

    def report(self) -> dict:
        """Generate a readiness report.

        Returns:
            Dictionary with keys:
            - 'ready': bool indicating overall readiness
            - 'passed': list of passed check names
            - 'failed': list of failed check names
            - 'missing': list of missing check names
        """
        ready = self.evaluate()
        passed = [
            check_name
            for check_name in self._checks
            if self._checks[check_name].passed
        ]

        return {
            "ready": ready,
            "passed": passed,
            "failed": self.failed_checks(),
            "missing": self.missing_checks(),
        }
