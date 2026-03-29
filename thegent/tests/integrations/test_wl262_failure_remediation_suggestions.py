"""Tests for WL-262 failure remediation suggestions."""

from __future__ import annotations

import pytest

from thegent.integrations.remediation_suggestions import suggest_remediation


@pytest.mark.requirement("WL-262")
def test_known_failure_code_returns_deterministic_suggestion() -> None:
    suggestion = suggest_remediation("AUTH_MISSING")
    assert "credentials" in suggestion.lower()


@pytest.mark.requirement("WL-262")
def test_unknown_failure_code_returns_fallback_message() -> None:
    suggestion = suggest_remediation("SOME_NEW_ERROR")
    assert "doctor" in suggestion.lower()
