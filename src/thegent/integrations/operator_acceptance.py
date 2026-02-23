"""Operator Acceptance Test tracking and reporting.

WL-259: Operator Acceptance Tests
Provides suite management for operator acceptance tests with pass/fail/pending tracking.

# @trace WL-259
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AcceptanceTest:
    """A single operator acceptance test with name, description, and status."""

    name: str
    description: str
    passed: bool | None = None


class OperatorAcceptanceSuite:
    """Manages a suite of operator acceptance tests."""

    def __init__(self) -> None:
        """Initialize an empty acceptance test suite."""
        self._tests: dict[str, AcceptanceTest] = {}

    def add(self, name: str, description: str) -> AcceptanceTest:
        """Add a new acceptance test to the suite.

        Args:
            name: Unique name of the test.
            description: Human-readable description of the test.

        Returns:
            The newly created AcceptanceTest.

        Raises:
            ValueError: If a test with this name already exists.
        """
        if name in self._tests:
            raise ValueError(f"Test '{name}' already exists in suite")
        test = AcceptanceTest(name=name, description=description)
        self._tests[name] = test
        return test

    def mark_passed(self, name: str) -> None:
        """Mark a test as passed.

        Args:
            name: Name of the test to mark as passed.

        Raises:
            KeyError: If test with given name does not exist.
        """
        if name not in self._tests:
            raise KeyError(f"Test '{name}' not found in suite")
        self._tests[name].passed = True

    def mark_failed(self, name: str) -> None:
        """Mark a test as failed.

        Args:
            name: Name of the test to mark as failed.

        Raises:
            KeyError: If test with given name does not exist.
        """
        if name not in self._tests:
            raise KeyError(f"Test '{name}' not found in suite")
        self._tests[name].passed = False

    def results(self) -> list[AcceptanceTest]:
        """Get all tests in the suite.

        Returns:
            List of all AcceptanceTest objects, sorted by name.
        """
        return sorted(self._tests.values(), key=lambda t: t.name)

    def summary(self) -> dict[str, int]:
        """Get a summary of test results.

        Returns:
            Dictionary with keys "passed", "failed", "pending" and their counts.
        """
        passed = sum(1 for t in self._tests.values() if t.passed is True)
        failed = sum(1 for t in self._tests.values() if t.passed is False)
        pending = sum(1 for t in self._tests.values() if t.passed is None)
        return {"passed": passed, "failed": failed, "pending": pending}
