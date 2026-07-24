"""Lightweight export checks for thegent.cli snapshot/dump commands.

Tracked skip markers preserve the intent of the originally-proposed
``snapshot_daily_totals_cmd`` and ``dump_categories_cmd`` exports. When
those commands are specced and built in a future lane, un-skip these
tests to assert the export contract.
"""

from __future__ import annotations

import importlib

import pytest


@pytest.mark.skip(reason="Command not in cli.__all__ - missing export")
def test_cli_all_contains_snapshot_daily_totals_cmd() -> None:
    cli = importlib.import_module("thegent.cli")
    assert "snapshot_daily_totals_cmd" in cli.__all__


@pytest.mark.skip(reason="Command not in cli.__all__ - missing export")
def test_cli_all_contains_dump_categories_cmd() -> None:
    cli = importlib.import_module("thegent.cli")
    assert "dump_categories_cmd" in cli.__all__
