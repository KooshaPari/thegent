"""Health check utilities."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class HealthChecker:
    """Health check system."""

    def __init__(self):
        """Initialize health checker."""
        self.checks: dict[str, callable] = {}

    def register_check(self, name: str, check_fn: callable) -> None:
        """Register a health check.

        Args:
            name: Check name
            check_fn: Check function
        """
        self.checks[name] = check_fn

    def _run_single_check(self, name: str, check_fn: callable) -> dict[str, Any]:
        """Run a single health check and return the result."""
        try:
            return {"status": "ok", "result": check_fn()}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def run_checks(self) -> dict[str, Any]:
        """Run all health checks.

        Returns:
            Health check results
        """
        results = {}
        for name, check_fn in self.checks.items():
            results[name] = self._run_single_check(name, check_fn)
        return results
