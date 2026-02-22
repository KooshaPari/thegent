"""Startup scope and reachability validation for integrations.

# @trace WL-192
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StartupValidationResult:
    """Result of startup validation.

    Attributes:
        passed: Whether all validations passed.
        errors: List of error messages.
        warnings: List of warning messages.
    """

    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class StartupValidator:
    """Validator for startup configuration and connectivity."""

    def check_auth_scopes(self, required_scopes: list[str], available_scopes: list[str]) -> bool:
        """Check that all required scopes are available.

        Args:
            required_scopes: List of scopes that must be available.
            available_scopes: List of scopes that are available.

        Returns:
            True if all required scopes are available, False otherwise.
        """
        available_set = set(available_scopes)
        required_set = set(required_scopes)
        return required_set.issubset(available_set)

    def check_endpoint_reachability(self, endpoints: list[str]) -> dict[str, bool]:
        """Check reachability of endpoints.

        This is a stub implementation that returns all endpoints as reachable.
        In production, this would perform actual network checks.

        Args:
            endpoints: List of endpoint URLs to check.

        Returns:
            Dictionary mapping endpoint URL to reachability status.
        """
        return dict.fromkeys(endpoints, True)

    def validate_all(self, config: dict) -> StartupValidationResult:
        """Validate all startup configuration.

        Args:
            config: Configuration dictionary with optional keys:
                - 'required_scopes': list of required auth scopes
                - 'available_scopes': list of available auth scopes
                - 'endpoints': list of endpoints to validate

        Returns:
            StartupValidationResult with validation status.
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Validate scopes if provided
        required_scopes = config.get("required_scopes", [])
        available_scopes = config.get("available_scopes", [])

        if required_scopes or available_scopes:
            if not self.check_auth_scopes(required_scopes, available_scopes):
                missing = set(required_scopes) - set(available_scopes)
                errors.append(f"Missing required scopes: {', '.join(sorted(missing))}")

        # Validate endpoints if provided
        endpoints = config.get("endpoints", [])
        if endpoints:
            reachability = self.check_endpoint_reachability(endpoints)
            unreachable = [ep for ep, reachable in reachability.items() if not reachable]
            if unreachable:
                warnings.append(f"Unreachable endpoints: {', '.join(unreachable)}")

        passed = len(errors) == 0
        return StartupValidationResult(passed=passed, errors=errors, warnings=warnings)
