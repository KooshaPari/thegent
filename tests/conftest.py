"""Pytest configuration for thegent.

WP-DX1: Coverage context per test for coverage-based test selection.
When pytest-cov runs with context, each test's coverage is tagged for
building a file->tests index (scripts/build_coverage_index.py).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src/ is in Python path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import pytest

# Ensure pytest-asyncio loads so async tests run (not skipped) when using python -m pytest
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(autouse=True)
def _coverage_context(request: pytest.FixtureRequest) -> None:
    """Set coverage context per test for coverage-based test selection (WP-DX1)."""
    try:
        import coverage

        cov = coverage.Coverage.current()
        if cov is not None:
            cov.switch_context(request.node.nodeid)
    except Exception:
        pass
