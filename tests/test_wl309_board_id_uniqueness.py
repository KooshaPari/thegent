"""Tests for WL-309: Strict Board-ID Uniqueness.

# @trace WL-309
"""

from __future__ import annotations

import pytest

from thegent.integrations.board_id_uniqueness import (
    BoardIdUniquenessPolicy,
    DuplicateBoardIdError,
    UniquenesEnforcer,
)


class TestBoardIdUniquenessPolicy:
    """WL-309: BoardIdUniquenessPolicy dataclass."""

    @pytest.mark.requirement("WL-309")
    def test_default_policy(self):
        """# @trace WL-309 — BoardIdUniquenessPolicy has correct defaults."""
        policy = BoardIdUniquenessPolicy()

        assert policy.enforce_global_uniqueness is True

    @pytest.mark.requirement("WL-309")
    def test_custom_policy(self):
        """# @trace WL-309 — BoardIdUniquenessPolicy accepts custom values."""
        policy = BoardIdUniquenessPolicy(enforce_global_uniqueness=False)

        assert policy.enforce_global_uniqueness is False


class TestUniquenesEnforcer:
    """WL-309: UniquenesEnforcer class."""

    @pytest.mark.requirement("WL-309")
    def test_enforcer_initialization_default_policy(self):
        """# @trace WL-309 — UniquenesEnforcer initializes with default policy."""
        enforcer = UniquenesEnforcer()

        assert enforcer.policy is not None
        assert enforcer.policy.enforce_global_uniqueness is True

    @pytest.mark.requirement("WL-309")
    def test_enforcer_initialization_custom_policy(self):
        """# @trace WL-309 — UniquenesEnforcer accepts custom policy."""
        policy = BoardIdUniquenessPolicy(enforce_global_uniqueness=False)
        enforcer = UniquenesEnforcer(policy=policy)

        assert enforcer.policy.enforce_global_uniqueness is False

    @pytest.mark.requirement("WL-309")
    def test_register_id_first_time(self):
        """# @trace WL-309 — register_id succeeds for new ID."""
        enforcer = UniquenesEnforcer()

        # Should not raise
        enforcer.register_id("BOARD-001")

        assert enforcer.is_registered("BOARD-001") is True

    @pytest.mark.requirement("WL-309")
    def test_register_id_duplicate_raises_error(self):
        """# @trace WL-309 — register_id raises DuplicateBoardIdError for duplicate."""
        enforcer = UniquenesEnforcer()

        enforcer.register_id("BOARD-002")

        with pytest.raises(DuplicateBoardIdError, match="already registered"):
            enforcer.register_id("BOARD-002")

    @pytest.mark.requirement("WL-309")
    def test_register_id_multiple_unique_ids(self):
        """# @trace WL-309 — register_id accepts multiple unique IDs."""
        enforcer = UniquenesEnforcer()

        enforcer.register_id("BOARD-A")
        enforcer.register_id("BOARD-B")
        enforcer.register_id("BOARD-C")

        assert enforcer.is_registered("BOARD-A") is True
        assert enforcer.is_registered("BOARD-B") is True
        assert enforcer.is_registered("BOARD-C") is True

    @pytest.mark.requirement("WL-309")
    def test_register_id_with_context(self):
        """# @trace WL-309 — register_id accepts optional context."""
        enforcer = UniquenesEnforcer()

        context = {"source": "github", "project": "my-project"}
        enforcer.register_id("BOARD-003", context=context)

        assert enforcer.is_registered("BOARD-003") is True

    @pytest.mark.requirement("WL-309")
    def test_register_id_with_enforcement_disabled(self):
        """# @trace WL-309 — register_id allows duplicates when enforcement disabled."""
        policy = BoardIdUniquenessPolicy(enforce_global_uniqueness=False)
        enforcer = UniquenesEnforcer(policy=policy)

        enforcer.register_id("BOARD-004")
        # Should not raise even though duplicate
        enforcer.register_id("BOARD-004")

        assert enforcer.is_registered("BOARD-004") is True

    @pytest.mark.requirement("WL-309")
    def test_is_registered_unregistered_id(self):
        """# @trace WL-309 — is_registered returns False for unregistered IDs."""
        enforcer = UniquenesEnforcer()

        assert enforcer.is_registered("BOARD-999") is False

    @pytest.mark.requirement("WL-309")
    def test_reset_clears_registry(self):
        """# @trace WL-309 — reset() clears all registered IDs."""
        enforcer = UniquenesEnforcer()

        enforcer.register_id("BOARD-X")
        enforcer.register_id("BOARD-Y")
        enforcer.register_id("BOARD-Z")

        assert enforcer.is_registered("BOARD-X") is True
        assert enforcer.is_registered("BOARD-Y") is True

        enforcer.reset()

        assert enforcer.is_registered("BOARD-X") is False
        assert enforcer.is_registered("BOARD-Y") is False
        assert enforcer.is_registered("BOARD-Z") is False

    @pytest.mark.requirement("WL-309")
    def test_reset_allows_reregistration(self):
        """# @trace WL-309 — after reset(), can re-register same IDs."""
        enforcer = UniquenesEnforcer()

        enforcer.register_id("BOARD-REG")
        enforcer.reset()

        # Should succeed after reset
        enforcer.register_id("BOARD-REG")

        assert enforcer.is_registered("BOARD-REG") is True

    @pytest.mark.requirement("WL-309")
    def test_duplicate_error_message(self):
        """# @trace WL-309 — DuplicateBoardIdError has clear message."""
        enforcer = UniquenesEnforcer()

        enforcer.register_id("BOARD-MSG")

        with pytest.raises(DuplicateBoardIdError) as exc_info:
            enforcer.register_id("BOARD-MSG")

        error_message = str(exc_info.value)
        assert "BOARD-MSG" in error_message
        assert "already registered" in error_message
