"""Tests for WL-167: Remote Archive/Delete Policy.

Verifies that ArchiveAction enum has correct values,
RemoteArchivePolicy manages per-connector policies,
and apply() correctly groups items by action.

# @trace WL-167
"""

from __future__ import annotations

import pytest

from thegent.integrations.remote_archive_policy import (
    ArchiveAction,
    RemoteArchivePolicy,
)


class TestArchiveAction:
    """WL-167: ArchiveAction enum."""

    @pytest.mark.requirement("WL-167")
    def test_archive_action_values(self):
        """ArchiveAction has ARCHIVE, DELETE, and SKIP members."""
        assert ArchiveAction.ARCHIVE.value == "archive"
        assert ArchiveAction.DELETE.value == "delete"
        assert ArchiveAction.SKIP.value == "skip"

    @pytest.mark.requirement("WL-167")
    def test_archive_action_membership(self):
        """All expected actions are present in enum."""
        actions = {a.value for a in ArchiveAction}
        assert actions == {"archive", "delete", "skip"}


class TestRemoteArchivePolicy:
    """WL-167: RemoteArchivePolicy initialization and operations."""

    @pytest.mark.requirement("WL-167")
    def test_initialization_default_action(self):
        """RemoteArchivePolicy initializes with default action SKIP."""
        policy = RemoteArchivePolicy()

        # Check by applying to a connector with no specific policy
        result = policy.apply("unknown-connector", ["item1"])
        assert "skip" in result

    @pytest.mark.requirement("WL-167")
    def test_initialization_custom_default_action(self):
        """RemoteArchivePolicy can be initialized with custom default action."""
        policy = RemoteArchivePolicy(default_action=ArchiveAction.DELETE)

        result = policy.apply("new-connector", ["item1"])
        assert "delete" in result

    @pytest.mark.requirement("WL-167")
    def test_set_policy(self):
        """set_policy() stores connector-specific action."""
        policy = RemoteArchivePolicy()

        policy.set_policy("connector-a", ArchiveAction.ARCHIVE)

        # Verify by getting the action
        action = policy.get_action("connector-a")
        assert action == ArchiveAction.ARCHIVE

    @pytest.mark.requirement("WL-167")
    def test_get_action_configured(self):
        """get_action() returns configured action for connector."""
        policy = RemoteArchivePolicy(default_action=ArchiveAction.SKIP)
        policy.set_policy("my-connector", ArchiveAction.DELETE)

        action = policy.get_action("my-connector")

        assert action == ArchiveAction.DELETE

    @pytest.mark.requirement("WL-167")
    def test_get_action_unconfigured_uses_default(self):
        """get_action() returns default for unconfigured connector."""
        policy = RemoteArchivePolicy(default_action=ArchiveAction.ARCHIVE)

        action = policy.get_action("unconfigured-connector")

        assert action == ArchiveAction.ARCHIVE

    @pytest.mark.requirement("WL-167")
    def test_set_policy_overwrites(self):
        """set_policy() can overwrite existing connector policy."""
        policy = RemoteArchivePolicy()
        policy.set_policy("connector-x", ArchiveAction.DELETE)
        policy.set_policy("connector-x", ArchiveAction.ARCHIVE)

        action = policy.get_action("connector-x")

        assert action == ArchiveAction.ARCHIVE

    @pytest.mark.requirement("WL-167")
    def test_apply_single_item(self):
        """apply() groups single item under configured action."""
        policy = RemoteArchivePolicy()
        policy.set_policy("conn-a", ArchiveAction.ARCHIVE)

        result = policy.apply("conn-a", ["item-1"])

        assert result == {"archive": ["item-1"]}

    @pytest.mark.requirement("WL-167")
    def test_apply_multiple_items(self):
        """apply() groups multiple items under same action."""
        policy = RemoteArchivePolicy()
        policy.set_policy("conn-b", ArchiveAction.DELETE)

        result = policy.apply("conn-b", ["item-1", "item-2", "item-3"])

        assert result == {"delete": ["item-1", "item-2", "item-3"]}

    @pytest.mark.requirement("WL-167")
    def test_apply_empty_items_list(self):
        """apply() handles empty items list."""
        policy = RemoteArchivePolicy()
        policy.set_policy("conn-c", ArchiveAction.SKIP)

        result = policy.apply("conn-c", [])

        assert result == {"skip": []}

    @pytest.mark.requirement("WL-167")
    def test_apply_uses_default_action(self):
        """apply() uses default action when connector not configured."""
        policy = RemoteArchivePolicy(default_action=ArchiveAction.ARCHIVE)

        result = policy.apply("new-conn", ["item-x"])

        assert result == {"archive": ["item-x"]}

    @pytest.mark.requirement("WL-167")
    def test_apply_multiple_connectors_independent(self):
        """apply() treats different connectors independently."""
        policy = RemoteArchivePolicy(default_action=ArchiveAction.SKIP)
        policy.set_policy("conn-1", ArchiveAction.ARCHIVE)
        policy.set_policy("conn-2", ArchiveAction.DELETE)

        result1 = policy.apply("conn-1", ["a", "b"])
        result2 = policy.apply("conn-2", ["c", "d"])
        result3 = policy.apply("conn-3", ["e"])

        assert result1 == {"archive": ["a", "b"]}
        assert result2 == {"delete": ["c", "d"]}
        assert result3 == {"skip": ["e"]}
