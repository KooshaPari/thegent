# @trace WL-161
"""Tests for Board-ID-First Reconciliation Policy.

Validates that reconciliation always uses board-id as the primary key,
never title-based matching, with configurable fallback behavior.
"""

from __future__ import annotations

import pytest

from thegent.integrations.reconciliation_policy import (
    ReconciliationMode,
    ReconciliationPolicy,
    create_default_policy,
)


@pytest.mark.requirement("WL-161")
def test_reconciliation_policy_default_mode():
    """Test that default policy uses board_id_first mode."""
    policy = ReconciliationPolicy()
    assert policy.mode == ReconciliationMode.BOARD_ID_FIRST
    assert policy.title_fallback_enabled is False


@pytest.mark.requirement("WL-161")
def test_reconciliation_policy_rejects_title_only_record():
    """Test that policy rejects title-only records by default."""
    policy = ReconciliationPolicy(title_fallback_enabled=False)
    record = {"title": "My Issue"}

    with pytest.raises(ValueError, match="title-only records are rejected"):
        policy.validate_record(record)


@pytest.mark.requirement("WL-161")
def test_reconciliation_policy_accepts_board_id_record():
    """Test that policy accepts records with board_id."""
    policy = ReconciliationPolicy(title_fallback_enabled=False)
    record = {"board_id": "123", "title": "My Issue"}

    assert policy.validate_record(record) is True


@pytest.mark.requirement("WL-161")
def test_reconciliation_policy_with_fallback_enabled():
    """Test that fallback mode allows title-only records."""
    policy = ReconciliationPolicy(title_fallback_enabled=True)
    record = {"title": "My Issue"}

    assert policy.validate_record(record) is True


@pytest.mark.requirement("WL-161")
def test_reconciliation_policy_rejects_empty_record():
    """Test that policy rejects records with neither board_id nor title."""
    policy = ReconciliationPolicy(title_fallback_enabled=True)
    record = {}

    with pytest.raises(ValueError, match="neither board_id nor title"):
        policy.validate_record(record)


@pytest.mark.requirement("WL-161")
def test_reconciliation_policy_rejects_non_dict():
    """Test that policy rejects non-dictionary inputs."""
    policy = ReconciliationPolicy()

    with pytest.raises(ValueError, match="must be a dictionary"):
        policy.validate_record("not a dict")


@pytest.mark.requirement("WL-161")
def test_reconciliation_policy_requires_board_id():
    """Test that requires_board_id always returns True for all modes."""
    policy = ReconciliationPolicy(mode=ReconciliationMode.BOARD_ID_FIRST)
    record = {"board_id": "123"}
    assert policy.requires_board_id(record) is True


@pytest.mark.requirement("WL-161")
def test_reconciliation_policy_strict_mode():
    """Test that strict mode requires board_id."""
    policy = ReconciliationPolicy(mode=ReconciliationMode.STRICT)
    record = {"board_id": "123"}
    assert policy.requires_board_id(record) is True


@pytest.mark.requirement("WL-161")
def test_create_default_policy():
    """Test the factory function for default policy."""
    policy = create_default_policy()
    assert policy.mode == ReconciliationMode.BOARD_ID_FIRST
    assert policy.title_fallback_enabled is False

    # Should reject title-only
    with pytest.raises(ValueError):
        policy.validate_record({"title": "test"})

    # Should accept board_id
    assert policy.validate_record({"board_id": "123"}) is True
