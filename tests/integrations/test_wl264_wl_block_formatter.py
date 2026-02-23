"""Tests for WL-264 WL block formatter."""

from __future__ import annotations

import pytest

from thegent.integrations.wl_block_formatter import normalize_wl_block


@pytest.mark.requirement("WL-264")
def test_normalize_wl_block_orders_metadata_fields() -> None:
    block = """
### [WL-264] WL Block Formatter
**Priority:** P2
**Status:** BACKLOG
**Area:** formatting
**Blocked by:** none
**Effort:** S

Add strict formatter for WL block structure and metadata normalization.
"""
    normalized = normalize_wl_block(block)
    assert normalized.splitlines()[1] == "**Status:** BACKLOG"
    assert normalized.splitlines()[2] == "**Priority:** P2"


@pytest.mark.requirement("WL-264")
def test_normalize_wl_block_rejects_missing_required_fields() -> None:
    block = """
### [WL-264] WL Block Formatter
**Status:** BACKLOG
"""
    with pytest.raises(ValueError, match="missing required metadata"):
        normalize_wl_block(block)
