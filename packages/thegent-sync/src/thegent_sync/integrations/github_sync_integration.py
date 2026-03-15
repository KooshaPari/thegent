"""Small synchronous GitHub integration test harness."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

__all__ = ["GitHubSyncIntegrationSuite", "SyncTestResult"]


@dataclass(frozen=True, slots=True)
class SyncTestResult:
    """Result of a single GitHub sync integration test."""

    test_name: str
    passed: bool
    details: str = ""


class GitHubSyncIntegrationSuite:
    """Register and execute small deterministic GitHub sync checks."""

    def __init__(self) -> None:
        self._tests: list[tuple[str, Callable[[], bool], str]] = []

    def add_test(self, test_name: str, test_fn: Callable[[], bool], *, details: str = "") -> None:
        self._tests.append((test_name, test_fn, details))

    def run_all(self) -> list[SyncTestResult]:
        results: list[SyncTestResult] = []
        for test_name, test_fn, details in self._tests:
            try:
                passed = bool(test_fn())
                result_details = details
            except Exception as exc:
                passed = False
                result_details = f"Exception: {exc}"
            results.append(SyncTestResult(test_name=test_name, passed=passed, details=result_details))
        return results

    @staticmethod
    def summary(results: list[SyncTestResult]) -> dict[str, int]:
        passed = sum(1 for result in results if result.passed)
        return {"passed": passed, "failed": len(results) - passed}
