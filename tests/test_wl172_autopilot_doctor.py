"""Tests for WL-172 Autopilot Doctor Command.

# @trace WL-172
"""

from __future__ import annotations

import pytest

from thegent.integrations.autopilot_doctor import AutopilotDoctor, DoctorCheck


@pytest.mark.requirement("WL-172")
class TestDoctorCheck:
    """Tests for DoctorCheck dataclass."""

    def test_doctor_check_creation(self) -> None:
        """DoctorCheck can be created with required fields."""
        check = DoctorCheck(name="test", passed=True)
        assert check.name == "test"
        assert check.passed is True
        assert check.message == ""

    def test_doctor_check_with_message(self) -> None:
        """DoctorCheck can include an optional message."""
        check = DoctorCheck(name="test", passed=False, message="Something failed")
        assert check.name == "test"
        assert check.passed is False
        assert check.message == "Something failed"


@pytest.mark.requirement("WL-172")
class TestAutopilotDoctor:
    """Tests for AutopilotDoctor class."""

    def test_add_check(self) -> None:
        """add_check registers a health check."""
        doctor = AutopilotDoctor()

        def check_fn() -> bool:
            return True

        doctor.add_check("connectivity", check_fn, "Checking network connectivity")
        # Verify it was registered by running checks
        results = doctor.run()
        assert len(results) == 1
        assert results[0].name == "connectivity"

    def test_run_empty(self) -> None:
        """run() returns empty list when no checks registered."""
        doctor = AutopilotDoctor()
        results = doctor.run()
        assert results == []

    def test_run_single_check_pass(self) -> None:
        """run() returns passing check result."""
        doctor = AutopilotDoctor()
        doctor.add_check("test", lambda: True, "Test message")

        results = doctor.run()
        assert len(results) == 1
        assert results[0].name == "test"
        assert results[0].passed is True
        assert results[0].message == "Test message"

    def test_run_single_check_fail(self) -> None:
        """run() returns failing check result."""
        doctor = AutopilotDoctor()
        doctor.add_check("test", lambda: False, "Test failed")

        results = doctor.run()
        assert len(results) == 1
        assert results[0].name == "test"
        assert results[0].passed is False
        assert results[0].message == "Test failed"

    def test_run_multiple_checks(self) -> None:
        """run() executes multiple checks and returns all results."""
        doctor = AutopilotDoctor()
        doctor.add_check("check1", lambda: True)
        doctor.add_check("check2", lambda: False)
        doctor.add_check("check3", lambda: True)

        results = doctor.run()
        assert len(results) == 3
        assert results[0].passed is True
        assert results[1].passed is False
        assert results[2].passed is True

    def test_all_passed_empty_list(self) -> None:
        """all_passed returns True for empty list."""
        assert AutopilotDoctor.all_passed([]) is True

    def test_all_passed_all_true(self) -> None:
        """all_passed returns True when all checks pass."""
        checks = [
            DoctorCheck("check1", True),
            DoctorCheck("check2", True),
        ]
        assert AutopilotDoctor.all_passed(checks) is True

    def test_all_passed_one_false(self) -> None:
        """all_passed returns False when any check fails."""
        checks = [
            DoctorCheck("check1", True),
            DoctorCheck("check2", False),
            DoctorCheck("check3", True),
        ]
        assert AutopilotDoctor.all_passed(checks) is False

    def test_all_passed_all_false(self) -> None:
        """all_passed returns False when all checks fail."""
        checks = [
            DoctorCheck("check1", False),
            DoctorCheck("check2", False),
        ]
        assert AutopilotDoctor.all_passed(checks) is False
