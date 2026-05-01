"""STUB MODULE - thegent.commands.doctor

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations

from typing import Any


class DoctorCheck:
    """Doctor check implementation."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.passed = False

    def run(self) -> dict[str, Any]:
        """Run the check."""
        return {"name": self.name, "passed": self.passed}


class DoctorRunner:
    """Runner for doctor checks."""

    def __init__(self) -> None:
        self.checks: list[DoctorCheck] = []

    def add_check(self, check: DoctorCheck) -> None:
        """Add a check to run."""
        self.checks.append(check)

    def run_all(self) -> list[dict[str, Any]]:
        """Run all checks."""
        return [check.run() for check in self.checks]


__all__ = ["DoctorCheck", "DoctorRunner"]
