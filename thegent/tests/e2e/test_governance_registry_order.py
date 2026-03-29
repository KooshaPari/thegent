"""Contract tests for deterministic governance registry ordering."""

from __future__ import annotations

from tests.e2e.test_split_hygiene import (
    REPO_ROOT,
    REQUIRED_E2E_GOVERNANCE_FILES,
)


def _required_file_relpaths() -> list[str]:
    return [str(path.relative_to(REPO_ROOT)) for path in REQUIRED_E2E_GOVERNANCE_FILES]


def test_required_e2e_governance_files_are_lexicographically_sorted() -> None:
    relpaths = _required_file_relpaths()
    assert relpaths == sorted(relpaths)


def test_required_e2e_governance_files_have_no_duplicates() -> None:
    relpaths = _required_file_relpaths()
    assert len(relpaths) == len(set(relpaths))
