"""Smoke checks for native extension bootstrap/import.

The Rust extensions ``thegent_git`` and ``thegent_jsonl`` are optional;
they are not built in a pure-Python dev environment. This test module
imports them lazily so the test suite can run cleanly without the
extensions and skip the smoke tests when they are absent.
"""

from __future__ import annotations

import pytest

thegent_git = pytest.importorskip("thegent_git")
thegent_jsonl = pytest.importorskip("thegent_jsonl")


def test_import_thegent_git() -> None:
    assert thegent_git is not None


def test_import_thegent_jsonl() -> None:
    assert thegent_jsonl is not None
