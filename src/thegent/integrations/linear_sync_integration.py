"""Linear Sync Integration Tests (WL-179): Integration test suite for Linear sync operations.

@trace WL-179

Provides a framework for integration testing Linear GraphQL cycle behavior with
deterministic fixtures. This module defines test result tracking and a test suite
runner for validating Linear sync functionality.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class LinearSyncTestResult:
    """Result of a single Linear sync integration test.

    Attributes:
        test_name: Name of the test that was executed.
        passed: Whether the test passed (True) or failed (False).
        details: Optional details about the test result (e.g., error message).
    """

    test_name: str
    passed: bool
    details: str = ""


class LinearSyncIntegrationSuite:
    """Integration test suite for Linear sync operations.

    Provides methods to register and execute integration tests against mocked
    Linear GraphQL responses. Tests can be added dynamically and executed to
    validate cycle behavior and synchronization logic.

    Example:
        >>> suite = LinearSyncIntegrationSuite()
        >>> suite.add_test("test_cycle_query", lambda: mock_cycle_query())
        >>> results = suite.run_all()
        >>> summary = suite.summary(results)
        >>> print(f"Passed: {summary['passed']}, Failed: {summary['failed']}")
    """

    def __init__(self) -> None:
        """Initialize the integration test suite."""
        self._tests: list[tuple[str, Callable[[], bool], str]] = []

    def add_test(
        self, name: str, test_fn: Callable[[], bool], details: str = ""
    ) -> None:
        """Register a new integration test.

        Args:
            name: Name of the test (e.g., 'test_cycle_status').
            test_fn: Callable that returns True if test passes, False otherwise.
            details: Optional details about the test setup or expectations.
        """
        self._tests.append((name, test_fn, details))

    def run_all(self) -> list[LinearSyncTestResult]:
        """Execute all registered tests.

        Returns:
            List of LinearSyncTestResult objects, one for each test execution.
            Failed tests will have passed=False and details describing the failure.
        """
        results: list[LinearSyncTestResult] = []
        for test_name, test_fn, test_details in self._tests:
            try:
                passed = test_fn()
                result = LinearSyncTestResult(
                    test_name=test_name, passed=passed, details=test_details
                )
            except Exception as e:
                result = LinearSyncTestResult(
                    test_name=test_name,
                    passed=False,
                    details=f"Exception: {str(e)}",
                )
            results.append(result)
        return results

    @staticmethod
    def summary(results: list[LinearSyncTestResult]) -> dict[str, int]:
        """Generate a summary of test results.

        Args:
            results: List of LinearSyncTestResult objects.

        Returns:
            Dictionary with keys 'passed' and 'failed' containing counts.
        """
        passed_count = sum(1 for r in results if r.passed)
        failed_count = len(results) - passed_count
        return {"passed": passed_count, "failed": failed_count}
