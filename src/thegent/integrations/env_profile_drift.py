"""Environment profile drift validation for config parity checking.

Validate config parity/drift across dev/staging/prod autosync profiles.

# @trace WL-246
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EnvDriftIssue:
    """Represents a single environment variable drift issue."""

    key: str
    expected: str | None
    actual: str | None


class EnvProfileDriftValidator:
    """Validates environment variable drift against a profile."""

    def __init__(self) -> None:
        """Initialize the environment profile drift validator."""
        self._profile: dict[str, str] = {}
        logger.debug("Initialized environment profile drift validator")

    def set_profile(self, profile: dict[str, str]) -> None:
        """Set the expected environment variable profile.

        Args:
            profile: Dictionary of expected environment variables and their values.
        """
        self._profile = profile.copy()
        logger.debug(f"Set environment profile with {len(self._profile)} variables")

    def validate(self, env: dict[str, str]) -> list[EnvDriftIssue]:
        """Validate environment variables against the profile.

        Identifies missing, mismatched, and unexpected variables.

        Args:
            env: Dictionary of actual environment variables.

        Returns:
            List of EnvDriftIssue objects representing drift.
        """
        issues: list[EnvDriftIssue] = []

        # Check for expected variables missing or mismatched in actual
        for key, expected_value in self._profile.items():
            actual_value = env.get(key)
            if actual_value is None:
                issues.append(EnvDriftIssue(key=key, expected=expected_value, actual=None))
            elif actual_value != expected_value:
                issues.append(
                    EnvDriftIssue(key=key, expected=expected_value, actual=actual_value)
                )

        # Check for unexpected variables in actual
        for key in env:
            if key not in self._profile:
                issues.append(EnvDriftIssue(key=key, expected=None, actual=env[key]))

        logger.debug(f"Found {len(issues)} drift issues out of {len(self._profile)} profile variables")
        return issues

    def is_valid(self, env: dict[str, str]) -> bool:
        """Check if environment variables match the profile.

        Args:
            env: Dictionary of actual environment variables.

        Returns:
            True if no drift issues are found, False otherwise.
        """
        issues = self.validate(env)
        return len(issues) == 0
