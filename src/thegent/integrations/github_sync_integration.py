"""GitHub Sync Integration Tests (WL-178): Integration test suite for GitHub sync operations.

@trace WL-178

Provides a framework for integration testing GitHub pull/push behavior against
mocked GitHub CLI responses. This module defines test result tracking and a test
suite runner for validating GitHub sync functionality.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class SyncTestResult:
    """Result of a single GitHub sync integration test.

    Attributes:
        test_name: Name of the test that was executed.
        passed: Whether the test passed (True) or failed (False).
        details: Optional details about the test result (e.g., error message).
    """

    test_name: str
    passed: bool
    details: str = ""


class GitHubSyncIntegrationSuite:
    """Integration test suite for GitHub sync operations.

    Provides methods to register and execute integration tests against mocked
    GitHub CLI responses. Tests can be added dynamically and executed to
    validate pull/push behavior.

    Example:
        >>> suite = GitHubSyncIntegrationSuite()
        >>> suite.add_test("test_pull", lambda: mock_pull_request())
        >>> results = suite.run_all()
        >>> summary = suite.summary(results)
        >>> print(f"Passed: {summary['passed']}, Failed: {summary['failed']}")
    """

    def __init__(self) -> None:
        """Initialize the integration test suite."""
        self._tests: list[tuple[str, Callable[[], bool], str]] = []

    def add_test(self, name: str, test_fn: Callable[[], bool], details: str = "") -> None:
        """Register a new integration test.

        Args:
            name: Name of the test (e.g., 'test_pull_open_pr').
            test_fn: Callable that returns True if test passes, False otherwise.
            details: Optional details about the test setup or expectations.
        """
        self._tests.append((name, test_fn, details))

    def run_all(self) -> list[SyncTestResult]:
        """Execute all registered tests.

        Returns:
            List of SyncTestResult objects, one for each test execution.
            Failed tests will have passed=False and details describing the failure.
        """
        results: list[SyncTestResult] = []
        for test_name, test_fn, test_details in self._tests:
            try:
                passed = test_fn()
                result = SyncTestResult(test_name=test_name, passed=passed, details=test_details)
            except Exception as e:
                result = SyncTestResult(
                    test_name=test_name,
                    passed=False,
                    details=f"Exception: {str(e)}",
                )
            results.append(result)
        return results

    @staticmethod
    def summary(results: list[SyncTestResult]) -> dict[str, int]:
        """Generate a summary of test results.

        Args:
            results: List of SyncTestResult objects.

        Returns:
            Dictionary with keys 'passed' and 'failed' containing counts.
        """
        passed_count = sum(1 for r in results if r.passed)
        failed_count = len(results) - passed_count
        return {"passed": passed_count, "failed": failed_count}
