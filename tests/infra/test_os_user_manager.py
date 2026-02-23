"""Unit tests for os user management API."""

import pytest

from thegent.infra.os_user_manager import OSUser, OSUserManager


def test_create_user_returns_existing_user_info(monkeypatch):
    """Existing users should return cached info without creating users."""
    manager = OSUserManager()
    expected = OSUser(username="tg_tenant", is_created=True)
    monkeypatch.setattr(manager, "_user_exists", lambda _name: True)
    monkeypatch.setattr(manager, "_get_user_info", lambda _name: expected)

    result = manager.create_user("tenant")

    assert result == expected


def test_create_user_raises_for_unsupported_os(monkeypatch):
    """Unsupported OS families should raise a clear RuntimeError."""
    manager = OSUserManager()
    monkeypatch.setattr(manager, "os_type", "plan9")
    monkeypatch.setattr(manager, "_user_exists", lambda _name: False)
    with pytest.raises(RuntimeError, match="not supported on plan9"):
        manager.create_user("tenant")


def test_delete_user_returns_true_when_missing(monkeypatch):
    """Deleting a non-existent user should be a no-op."""
    manager = OSUserManager()
    monkeypatch.setattr(manager, "_user_exists", lambda _name: False)

    assert manager.delete_user("tenant") is True
