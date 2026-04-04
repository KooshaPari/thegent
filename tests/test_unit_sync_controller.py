"""Unit tests for sync freeze/unfreeze controls.

# @trace WL-206
"""

from __future__ import annotations

import pytest
from thegent.sync.controller import SyncController


@pytest.mark.requirement("WL-206")
def test_freeze_then_unfreeze(tmp_path):
    controller = SyncController(tmp_path / "freeze.json")
    state = controller.freeze(reason="maintenance", actor="lane7")
    assert state.reason == "maintenance"
    assert controller.is_frozen() is True

    controller.unfreeze(actor="lane7")
    assert controller.is_frozen() is False


@pytest.mark.requirement("WL-206")
def test_assert_writes_allowed_raises_when_frozen(tmp_path):
    controller = SyncController(tmp_path / "freeze.json")
    controller.freeze(reason="incident", actor="lane7")
    with pytest.raises(RuntimeError, match="sync writes frozen"):
        controller.assert_writes_allowed()
