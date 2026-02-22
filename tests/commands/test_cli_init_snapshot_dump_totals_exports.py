"""Lightweight export checks for thegent.cli snapshot/dump commands."""

from __future__ import annotations

import importlib


def test_cli_exports_snapshot_daily_totals_cmd() -> None:
    cli = importlib.import_module("thegent.cli")
    assert hasattr(cli, "snapshot_daily_totals_cmd")


def test_cli_exports_dump_categories_cmd() -> None:
    cli = importlib.import_module("thegent.cli")
    assert hasattr(cli, "dump_categories_cmd")


def test_cli_all_contains_snapshot_daily_totals_cmd() -> None:
    cli = importlib.import_module("thegent.cli")
    assert "snapshot_daily_totals_cmd" in cli.__all__


def test_cli_all_contains_dump_categories_cmd() -> None:
    cli = importlib.import_module("thegent.cli")
    assert "dump_categories_cmd" in cli.__all__


def test_exported_objects_are_callable() -> None:
    cli = importlib.import_module("thegent.cli")
    assert callable(cli.snapshot_daily_totals_cmd)
    assert callable(cli.dump_categories_cmd)
