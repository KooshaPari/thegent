"""Tests for WL-296 restore verifier."""

from __future__ import annotations

import pytest

from thegent.integrations.restore_verifier import verify_restore_output


@pytest.mark.requirement("WL-296")
def test_verify_restore_output_matches_identical_payloads() -> None:
    expected = {"a": 1, "b": {"x": [1, 2, 3]}}
    restored = {"b": {"x": [1, 2, 3]}, "a": 1}

    result = verify_restore_output(expected, restored)
    assert result.matches is True
    assert result.expected_hash == result.restored_hash


@pytest.mark.requirement("WL-296")
def test_verify_restore_output_detects_mismatch() -> None:
    result = verify_restore_output({"a": 1}, {"a": 2})
    assert result.matches is False
