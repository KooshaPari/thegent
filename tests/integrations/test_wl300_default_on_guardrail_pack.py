"""Tests for WL-300 default-on guardrail pack migration."""

from __future__ import annotations

import pytest

from thegent.integrations.guardrail_pack_migration import (
    build_default_guardrail_pack,
    migrate_to_default_on_pack,
)


@pytest.mark.requirement("WL-300")
def test_default_guardrail_pack_is_enabled_by_default() -> None:
    pack = build_default_guardrail_pack()
    assert pack["input_guardrails_enabled"] is True
    assert pack["require_explicit_destructive_confirmation"] is True


@pytest.mark.requirement("WL-300")
def test_migrate_to_default_on_pack_adds_missing_keys_and_preserves_existing() -> None:
    result = migrate_to_default_on_pack({"input_guardrails_enabled": False})
    assert result.merged_config["input_guardrails_enabled"] is False
    assert "prompt_max_chars" in result.added_keys
