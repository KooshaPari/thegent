"""Tests for WP-3007: Trust boundary checks."""

from unittest.mock import MagicMock

import pytest

from thegent.config import ThegentSettings
from thegent.governance.trust import TrustBoundaryChecker, TrustLevel


@pytest.fixture
def mock_settings():
    return MagicMock(spec=ThegentSettings)


def test_trust_checker_denies_sensitive_to_external(mock_settings):
    checker = TrustBoundaryChecker(mock_settings)

    # copilot is EXTERNAL
    res = checker.evaluate_routing("The api_key is xyz123", "copilot")
    assert res["allowed"] is False
    assert "Sensitive data" in res["reason"]

    # interactive_agent is INTERNAL
    res = checker.evaluate_routing("The api_key is xyz123", "interactive_agent")
    assert res["allowed"] is True


def test_trust_checker_allows_non_sensitive_to_external(mock_settings):
    checker = TrustBoundaryChecker(mock_settings)

    res = checker.evaluate_routing("List all files in directory", "copilot")
    assert res["allowed"] is True


def test_trust_checker_agent_trust_levels(mock_settings):
    checker = TrustBoundaryChecker(mock_settings)

    assert checker.get_agent_trust("interactive_agent") == TrustLevel.INTERNAL
    assert checker.get_agent_trust("gemini") == TrustLevel.EXTERNAL
    assert checker.get_agent_trust("unknown") == TrustLevel.EXTERNAL
