"""Tests for WL-256: No-Op Fast Path.

Tests the fast-path mechanism for skipping unchanged sync cycles.

# @trace WL-256
"""

from __future__ import annotations

import pytest


@pytest.mark.requirement("WL-256")
class TestNoOpResult:
    """Tests for NoOpResult dataclass."""

    def test_create_skipped_result(self):
        """# @trace WL-256 — NoOpResult can be created with skipped=True."""
        from thegent.integrations.noop_fast_path import NoOpResult

        result = NoOpResult(skipped=True, reason="test")
        assert result.skipped is True
        assert result.reason == "test"

    def test_create_not_skipped_result(self):
        """# @trace WL-256 — NoOpResult can be created with skipped=False."""
        from thegent.integrations.noop_fast_path import NoOpResult

        result = NoOpResult(skipped=False, reason="changes found")
        assert result.skipped is False
        assert result.reason == "changes found"

    def test_default_reason_empty_string(self):
        """# @trace WL-256 — NoOpResult default reason is empty string."""
        from thegent.integrations.noop_fast_path import NoOpResult

        result = NoOpResult(skipped=True)
        assert result.reason == ""


@pytest.mark.requirement("WL-256")
class TestNoOpFastPath:
    """Tests for NoOpFastPath."""

    def test_init_enabled_by_default(self):
        """# @trace WL-256 — NoOpFastPath is enabled by default."""
        from thegent.integrations.noop_fast_path import NoOpFastPath

        fast_path = NoOpFastPath()
        assert fast_path.is_enabled() is True

    def test_init_disabled(self):
        """# @trace WL-256 — NoOpFastPath can be disabled on init."""
        from thegent.integrations.noop_fast_path import NoOpFastPath

        fast_path = NoOpFastPath(enabled=False)
        assert fast_path.is_enabled() is False

    def test_check_returns_no_op_when_condition_true(self):
        """# @trace WL-256 — check returns skipped=True when condition_fn returns True."""
        from thegent.integrations.noop_fast_path import NoOpFastPath

        fast_path = NoOpFastPath(enabled=True)
        result = fast_path.check("item-1", lambda: True)

        assert result.skipped is True
        assert "no changes" in result.reason

    def test_check_returns_not_skipped_when_condition_false(self):
        """# @trace WL-256 — check returns skipped=False when condition_fn returns False."""
        from thegent.integrations.noop_fast_path import NoOpFastPath

        fast_path = NoOpFastPath(enabled=True)
        result = fast_path.check("item-1", lambda: False)

        assert result.skipped is False
        assert "changes" in result.reason

    def test_check_returns_not_skipped_when_disabled(self):
        """# @trace WL-256 — check returns skipped=False when fast path is disabled."""
        from thegent.integrations.noop_fast_path import NoOpFastPath

        fast_path = NoOpFastPath(enabled=False)
        result = fast_path.check("item-1", lambda: True)

        assert result.skipped is False
        assert "disabled" in result.reason

    def test_check_with_multiple_items(self):
        """# @trace WL-256 — check correctly evaluates each item independently."""
        from thegent.integrations.noop_fast_path import NoOpFastPath

        fast_path = NoOpFastPath(enabled=True)
        result1 = fast_path.check("item-1", lambda: True)
        result2 = fast_path.check("item-2", lambda: False)
        result3 = fast_path.check("item-3", lambda: True)

        assert result1.skipped is True
        assert result2.skipped is False
        assert result3.skipped is True

    def test_check_calls_condition_function(self):
        """# @trace WL-256 — check invokes the condition function."""
        from thegent.integrations.noop_fast_path import NoOpFastPath

        fast_path = NoOpFastPath(enabled=True)
        call_count = {"n": 0}

        def condition_fn():
            call_count["n"] += 1
            return True

        fast_path.check("item-1", condition_fn)
        assert call_count["n"] == 1

    def test_is_enabled_reflects_init_state(self):
        """# @trace WL-256 — is_enabled reflects the init state."""
        from thegent.integrations.noop_fast_path import NoOpFastPath

        enabled = NoOpFastPath(enabled=True)
        disabled = NoOpFastPath(enabled=False)

        assert enabled.is_enabled() is True
        assert disabled.is_enabled() is False

    def test_disabled_fast_path_still_evaluates_condition(self):
        """# @trace WL-256 — disabled fast path still evaluates condition_fn."""
        from thegent.integrations.noop_fast_path import NoOpFastPath

        fast_path = NoOpFastPath(enabled=False)
        call_count = {"n": 0}

        def condition_fn():
            call_count["n"] += 1
            return True

        fast_path.check("item-1", condition_fn)
        # Condition is not called when disabled
        assert call_count["n"] == 0
