"""Hardening invariants for ``governance.overrides`` — AUDIT-N+70.

22 invariants FR-GOV-OVR-001 .. FR-GOV-OVR-022 covering
PolicyOverridePathError, _validate_policy_id, PolicyOverride dataclass,
OverrideManager (apply, get, cleanup, traversal, save).

Source: src/thegent/governance/overrides.py

@trace AUDIT-N+70  FR-GOV-OVR-001..022
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import pytest

from thegent.governance.overrides import (
    OverrideManager,
    PolicyOverride,
    PolicyOverridePathError,
    _validate_policy_id,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# FR-GOV-OVR-001
# ---------------------------------------------------------------------------


class TestFRGOVOVR001PolicyOverridePathErrorSubclass:
    def test_is_valueerror_subclass(self) -> None:
        assert issubclass(PolicyOverridePathError, ValueError)


# ---------------------------------------------------------------------------
# FR-GOV-OVR-002
# ---------------------------------------------------------------------------


class TestFRGOVOVR002ValidatePolicyIdRejectsEmpty:
    def test_empty_string(self) -> None:
        with pytest.raises(PolicyOverridePathError, match="non-empty"):
            _validate_policy_id("")


# ---------------------------------------------------------------------------
# FR-GOV-OVR-003
# ---------------------------------------------------------------------------


class TestFRGOVOVR003ValidatePolicyIdRejectsSlash:
    def test_forward_slash(self) -> None:
        with pytest.raises(PolicyOverridePathError, match="path separator"):
            _validate_policy_id("foo/bar")

    def test_backslash(self) -> None:
        with pytest.raises(PolicyOverridePathError, match="path separator"):
            _validate_policy_id("foo\\bar")


# ---------------------------------------------------------------------------
# FR-GOV-OVR-004
# ---------------------------------------------------------------------------


class TestFRGOVOVR004ValidatePolicyIdRejectsDotDot:
    def test_dotdot(self) -> None:
        with pytest.raises(PolicyOverridePathError, match="\\.\\."):
            _validate_policy_id("..")

    def test_dotdot_in_middle(self) -> None:
        with pytest.raises(PolicyOverridePathError, match="\\.\\."):
            _validate_policy_id("foo/../bar")


# ---------------------------------------------------------------------------
# FR-GOV-OVR-005
# ---------------------------------------------------------------------------


class TestFRGOVOVR005ValidatePolicyIdRejectsNulByte:
    def test_nul_byte(self) -> None:
        with pytest.raises(PolicyOverridePathError, match="NUL byte"):
            _validate_policy_id("foo\x00bar")


# ---------------------------------------------------------------------------
# FR-GOV-OVR-006
# ---------------------------------------------------------------------------


class TestFRGOVOVR006ValidatePolicyIdRejectsNonString:
    def test_none(self) -> None:
        with pytest.raises(PolicyOverridePathError, match="must be a string"):
            _validate_policy_id(None)  # type: ignore[arg-type]

    def test_int(self) -> None:
        with pytest.raises(PolicyOverridePathError, match="must be a string"):
            _validate_policy_id(42)  # type: ignore[arg-type]

    def test_list(self) -> None:
        with pytest.raises(PolicyOverridePathError, match="must be a string"):
            _validate_policy_id(["a"])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# FR-GOV-OVR-007
# ---------------------------------------------------------------------------


class TestFRGOVOVR007ValidatePolicyIdAcceptsValid:
    def test_simple_id(self) -> None:
        _validate_policy_id("policy-alpha")

    def test_with_numbers(self) -> None:
        _validate_policy_id("policy_123")

    def test_with_dots(self) -> None:
        # single dots are fine
        _validate_policy_id("a.b.c")


# ---------------------------------------------------------------------------
# FR-GOV-OVR-008
# ---------------------------------------------------------------------------


class TestFRGOVOVR008PolicyOverrideStoresAllFields:
    def test_all_fields(self, tmp_path: Path) -> None:
        now = time.time()
        override = PolicyOverride(
            policy_id="p1",
            reason="test",
            by="admin",
            expires_at=now + 3600,
            created_at=now,
            metadata={"k": "v"},
        )
        assert override.policy_id == "p1"
        assert override.reason == "test"
        assert override.by == "admin"
        assert override.expires_at == now + 3600
        assert override.created_at == now
        assert override.metadata == {"k": "v"}


# ---------------------------------------------------------------------------
# FR-GOV-OVR-009
# ---------------------------------------------------------------------------


class TestFRGOVOVR009PolicyOverrideIsActiveFuture:
    def test_active_when_future(self) -> None:
        override = PolicyOverride(
            policy_id="p1",
            reason="r",
            by="a",
            expires_at=time.time() + 9999,
            created_at=time.time(),
            metadata={},
        )
        assert override.is_active() is True


# ---------------------------------------------------------------------------
# FR-GOV-OVR-010
# ---------------------------------------------------------------------------


class TestFRGOVOVR010PolicyOverrideIsActivePast:
    def test_inactive_when_past(self) -> None:
        override = PolicyOverride(
            policy_id="p1",
            reason="r",
            by="a",
            expires_at=time.time() - 1,
            created_at=time.time() - 3600,
            metadata={},
        )
        assert override.is_active() is False


# ---------------------------------------------------------------------------
# FR-GOV-OVR-011
# ---------------------------------------------------------------------------


class TestFRGOVOVR011ApplyOverrideCreatesOverride:
    def test_creates_and_persists(self, tmp_path: Path) -> None:
        mgr = OverrideManager(_make_settings(tmp_path))
        result = mgr.apply_override("test-policy", "because", "tester")
        assert result.policy_id == "test-policy"
        assert result.reason == "because"
        assert result.by == "tester"
        # File should exist on disk
        p = tmp_path / "overrides" / "test-policy.json"
        assert p.exists()


# ---------------------------------------------------------------------------
# FR-GOV-OVR-012
# ---------------------------------------------------------------------------


class TestFRGOVOVR012GetOverrideReturnsActive:
    def test_returns_active(self, tmp_path: Path) -> None:
        mgr = OverrideManager(_make_settings(tmp_path))
        mgr.apply_override("active-p", "r", "a", duration_minutes=60)
        found = mgr.get_override("active-p")
        assert found is not None
        assert found.policy_id == "active-p"


# ---------------------------------------------------------------------------
# FR-GOV-OVR-013
# ---------------------------------------------------------------------------


class TestFRGOVOVR013GetOverrideReturnsNoneForExpired:
    def test_returns_none_when_expired(self, tmp_path: Path) -> None:
        mgr = OverrideManager(_make_settings(tmp_path))
        mgr.apply_override("expired-p", "r", "a", duration_minutes=60)
        # Backdate the file so it's expired
        p = tmp_path / "overrides" / "expired-p.json"
        data = json.loads(p.read_text())
        data["expires_at"] = time.time() - 100
        p.write_text(json.dumps(data))
        found = mgr.get_override("expired-p")
        assert found is None
        # File should have been cleaned up
        assert not p.exists()


# ---------------------------------------------------------------------------
# FR-GOV-OVR-014
# ---------------------------------------------------------------------------


class TestFRGOVOVR014GetOverrideReturnsNoneForUnsafePolicyId:
    def test_returns_none_for_dotdot(self, tmp_path: Path) -> None:
        mgr = OverrideManager(_make_settings(tmp_path))
        assert mgr.get_override("..") is None

    def test_returns_none_for_slash(self, tmp_path: Path) -> None:
        mgr = OverrideManager(_make_settings(tmp_path))
        assert mgr.get_override("a/b") is None

    def test_returns_none_for_empty(self, tmp_path: Path) -> None:
        mgr = OverrideManager(_make_settings(tmp_path))
        assert mgr.get_override("") is None


# ---------------------------------------------------------------------------
# FR-GOV-OVR-015
# ---------------------------------------------------------------------------


class TestFRGOVOVR015CleanupExpiredRemovesExpired:
    def test_removes_expired(self, tmp_path: Path) -> None:
        mgr = OverrideManager(_make_settings(tmp_path))
        mgr.apply_override("to-expire", "r", "a", duration_minutes=1)
        p = tmp_path / "overrides" / "to-expire.json"
        # Force expiry
        data = json.loads(p.read_text())
        data["expires_at"] = time.time() - 100
        p.write_text(json.dumps(data))
        removed = mgr.cleanup_expired()
        assert removed == 1
        assert not p.exists()


# ---------------------------------------------------------------------------
# FR-GOV-OVR-016
# ---------------------------------------------------------------------------


class TestFRGOVOVR016CleanupExpiredReturnsCount:
    def test_returns_correct_count(self, tmp_path: Path) -> None:
        mgr = OverrideManager(_make_settings(tmp_path))
        # Create 3 expired overrides
        for i in range(3):
            mgr.apply_override(f"expired-{i}", "r", "a", duration_minutes=1)
            p = tmp_path / "overrides" / f"expired-{i}.json"
            data = json.loads(p.read_text())
            data["expires_at"] = time.time() - 100
            p.write_text(json.dumps(data))
        count = mgr.cleanup_expired()
        assert count == 3

    def test_returns_zero_when_none_expired(self, tmp_path: Path) -> None:
        mgr = OverrideManager(_make_settings(tmp_path))
        mgr.apply_override("alive", "r", "a", duration_minutes=60)
        count = mgr.cleanup_expired()
        assert count == 0


# ---------------------------------------------------------------------------
# FR-GOV-OVR-017
# ---------------------------------------------------------------------------


class TestFRGOVOVR017IsTraversalFilenameDetectsDotDot:
    def test_dotdot_before_extension(self) -> None:
        # "..backup.json" → stem is "..backup", which contains ".."
        assert OverrideManager._is_traversal_filename(Path("..backup.json")) is True

    def test_dotdot_in_middle(self) -> None:
        assert OverrideManager._is_traversal_filename(Path("a..b.json")) is True

    def test_literal_dotdot(self) -> None:
        assert OverrideManager._is_traversal_filename(Path("..")) is True

    def test_safe_prefix_not_dotdot(self) -> None:
        # "..json" → stem is ".", does NOT contain ".." as substring
        assert OverrideManager._is_traversal_filename(Path("..json")) is False


# ---------------------------------------------------------------------------
# FR-GOV-OVR-018
# ---------------------------------------------------------------------------


class TestFRGOVOVR018IsTraversalFilenameDetectsSlash:
    def test_backslash(self) -> None:
        # On POSIX, backslash is a valid char in filenames, so Path preserves it
        assert OverrideManager._is_traversal_filename(Path("a\\b.json")) is True

    def test_nul_byte(self) -> None:
        assert OverrideManager._is_traversal_filename(Path("a\x00b.json")) is True

    def test_safe_name(self) -> None:
        assert OverrideManager._is_traversal_filename(Path("policy.json")) is False

    def test_empty_name(self) -> None:
        assert OverrideManager._is_traversal_filename(Path()) is True


# ---------------------------------------------------------------------------
# FR-GOV-OVR-019
# ---------------------------------------------------------------------------


class TestFRGOVOVR019SaveOverrideRevalidatesPolicyId:
    def test_rejects_unsafe_policy_id(self, tmp_path: Path) -> None:
        mgr = OverrideManager(_make_settings(tmp_path))
        bad_override = PolicyOverride(
            policy_id="../escape",
            reason="r",
            by="a",
            expires_at=time.time() + 999,
            created_at=time.time(),
            metadata={},
        )
        with pytest.raises(PolicyOverridePathError, match="\\.\\."):
            mgr._save_override(bad_override)

    def test_rejects_nul_byte(self, tmp_path: Path) -> None:
        mgr = OverrideManager(_make_settings(tmp_path))
        bad_override = PolicyOverride(
            policy_id="bad\x00name",
            reason="r",
            by="a",
            expires_at=time.time() + 999,
            created_at=time.time(),
            metadata={},
        )
        with pytest.raises(PolicyOverridePathError, match="NUL byte"):
            mgr._save_override(bad_override)


# ---------------------------------------------------------------------------
# FR-GOV-OVR-020
# ---------------------------------------------------------------------------


class TestFRGOVOVR020ApplyOverrideDefaultDuration60:
    def test_default_duration_is_60_minutes(self, tmp_path: Path) -> None:
        mgr = OverrideManager(_make_settings(tmp_path))
        before = time.time()
        result = mgr.apply_override("dur-test", "r", "a")
        after = time.time()
        # expires_at should be between 59.9 and 60.1 minutes from now
        expected_min = before + 60 * 60 - 1
        expected_max = after + 60 * 60 + 1
        assert expected_min <= result.expires_at <= expected_max


# ---------------------------------------------------------------------------
# FR-GOV-OVR-021
# ---------------------------------------------------------------------------


class TestFRGOVOVR021PolicyOverrideMetadataDefault:
    def test_metadata_defaults_to_empty_dict(self) -> None:
        override = PolicyOverride(
            policy_id="p",
            reason="r",
            by="a",
            expires_at=time.time(),
            created_at=time.time(),
            metadata={},
        )
        assert override.metadata == {}

    def test_none_metadata_becomes_empty_dict(self, tmp_path: Path) -> None:
        mgr = OverrideManager(_make_settings(tmp_path))
        result = mgr.apply_override("meta-test", "r", "a", metadata=None)
        assert result.metadata == {}


# ---------------------------------------------------------------------------
# FR-GOV-OVR-022
# ---------------------------------------------------------------------------


class TestFRGOVOVR022OverrideDirIsSessionDirOverrides:
    def test_override_dir(self, tmp_path: Path) -> None:
        mgr = OverrideManager(_make_settings(tmp_path))
        assert mgr.override_dir == tmp_path / "overrides"
        assert mgr.override_dir.is_dir()


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


class _FakeSettings:
    """Minimal stand-in for ThegentSettings with a ``session_dir`` attribute."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir


def _make_settings(session_dir: Path) -> Any:
    return _FakeSettings(session_dir)
