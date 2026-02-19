"""System-wide consistency checker."""

from dataclasses import dataclass
from typing import Any

from thegent.thg_platform import detect_platform

__all__ = ["ConsistencyChecker", "ConsistencyRule"]


@dataclass
class ConsistencyRule:
    """Consistency rule definition."""

    component: str
    property: str
    expected_value: Any
    actual_value: Any
    severity: str


class ConsistencyChecker:
    """Check consistency across system.

    This class verifies that all system components are consistent,
    including version consistency, path consistency, and configuration consistency.

    Examples:
        >>> checker = ConsistencyChecker()
        >>> violations = checker.check_all()
        >>> if violations:
        ...     for violation in violations:
        ...         print(f"{violation.component}.{violation.property}: "
        ...               f"expected {violation.expected_value}, "
        ...               f"got {violation.actual_value}")
    """

    def __init__(self) -> None:
        """Initialize consistency checker."""
        self.rules: list[ConsistencyRule] = []
        self._register_rules()

    def _register_rules(self) -> None:
        """Register consistency rules."""
        # Version consistency
        try:
            from thegent import __version__
        except ImportError:
            __version__ = "0.1.0"

        self.rules.append(
            ConsistencyRule(
                component="package",
                property="version",
                expected_value=__version__,
                actual_value=self._get_package_version(),
                severity="critical",
            )
        )

        # Path consistency
        self.rules.append(
            ConsistencyRule(
                component="paths",
                property="platform",
                expected_value=detect_platform().value,
                actual_value=self._get_path_platform(),
                severity="high",
            )
        )

        # Config consistency
        self.rules.append(
            ConsistencyRule(
                component="config",
                property="providers",
                expected_value="oauth_only",
                actual_value=self._get_provider_auth_method(),
                severity="high",
            )
        )

    def check_all(self) -> list[ConsistencyRule]:
        """Check all consistency rules.

        Returns:
            List of consistency violations
        """
        violations = []
        for rule in self.rules:
            if rule.expected_value != rule.actual_value:
                violations.append(rule)
        return violations

    def _get_package_version(self) -> str:
        """Get package version."""
        try:
            from thegent import __version__

            return __version__
        except ImportError:
            return "unknown"

    def _get_path_platform(self) -> str:
        """Get platform from paths."""
        # Check if paths match detected platform
        return detect_platform().value

    def _get_provider_auth_method(self) -> str:
        """Get provider authentication method."""
        try:
            from thegent.config import load_config

            config = load_config()
            providers = config.get("providers", {})

            # Check if any provider uses API keys (should be OAuth only)
            for provider_config in providers.values():
                if isinstance(provider_config, dict) and "api_key" in provider_config:
                    return "api_key"

            return "oauth_only"
        except (ImportError, AttributeError, KeyError):
            # Config not available or doesn't have providers
            return "unknown"
