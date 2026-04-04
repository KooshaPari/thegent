"""Unit tests for sync engine guardrails.

# @trace WL-208
"""

from __future__ import annotations

import pytest
from thegent.sync.engine import SyncEngineConfig, enforce_max_changes_per_cycle


@pytest.mark.requirement("WL-208")
def test_max_changes_allows_equal_limit():
    config = SyncEngineConfig(max_changes_per_cycle=5)
    enforce_max_changes_per_cycle(attempted_changes=5, config=config)


@pytest.mark.requirement("WL-208")
def test_max_changes_raises_when_exceeded():
    config = SyncEngineConfig(max_changes_per_cycle=3)
    with pytest.raises(RuntimeError, match="max changes exceeded"):
        enforce_max_changes_per_cycle(attempted_changes=4, config=config)


@pytest.mark.requirement("WL-208")
def test_max_changes_rejects_non_positive_config():
    config = SyncEngineConfig(max_changes_per_cycle=0)
    with pytest.raises(ValueError, match="must be positive"):
        enforce_max_changes_per_cycle(attempted_changes=1, config=config)
