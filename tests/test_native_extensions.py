"""Smoke checks for native extension bootstrap/import."""

from __future__ import annotations

import thegent_git
import thegent_jsonl


def test_import_thegent_git() -> None:
    assert thegent_git is not None


def test_import_thegent_jsonl() -> None:
    assert thegent_jsonl is not None
