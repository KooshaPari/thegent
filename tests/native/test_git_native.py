"""Tests for GitNative Rust-backed git operations (BKM-06).

Tests mock thegent_git (Rust PyO3 extension) so they run without a compiled binary.
The GitNative class requires thegent_git; these tests verify the Python-side logic only.

@trace FR-GIT-001
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Module-level mocks: must be injected BEFORE any thegent imports so that
# thegent.native.__init__ (which eagerly imports JsonlParser and WatcherDaemon)
# does not attempt to load absent Rust PyO3 extensions.
# ---------------------------------------------------------------------------
_RUST_EXTENSIONS = (
    "thegent_git",
    "thegent_jsonl",
    "thegent_discovery",
    "thegent_shm",
    "thegent_crypto",
    "thegent_zmx",
)
_originals: dict[str, object] = {}
for _ext in _RUST_EXTENSIONS:
    _originals[_ext] = sys.modules.get(_ext)
    # Always force mocks for deterministic unit behavior, even when native
    # extensions are installed in the active environment.
    sys.modules[_ext] = MagicMock()

# Configure realistic defaults for thegent_git
_GIT_MOCK: MagicMock = sys.modules["thegent_git"]  # type: ignore[assignment]
_GIT_MOCK.get_head_sha.return_value = "a" * 40
_GIT_MOCK.get_branch_name.return_value = "main"
_GIT_MOCK.get_status.return_value = {"modified": [], "untracked": [], "staged": []}
_GIT_MOCK.diff_stats.return_value = (0, 0, 0)

REPO_ROOT = Path(__file__).parents[2]
REPO_PATH = str(REPO_ROOT)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module", autouse=True)
def mock_thegent_git_module() -> MagicMock:  # type: ignore[return]
    """Return the already-injected thegent_git MagicMock so tests can
    configure specific return values.  The module-level injection above
    ensures the mock is in place before any thegent import during collection.
    """
    return _GIT_MOCK  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Unit: GitNative.head()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGitNativeHead:
    """@trace FR-GIT-001"""

    def test_returns_sha_and_branch(self, mock_thegent_git_module: MagicMock) -> None:
        mock_thegent_git_module.get_head_sha.return_value = "a" * 40
        mock_thegent_git_module.get_branch_name.return_value = "main"

        from thegent.native.git_native import GitNative

        gn = GitNative(REPO_PATH)
        result = gn.head()

        assert result == {"sha": "a" * 40, "branch": "main"}

    def test_none_sha_becomes_empty_string(self, mock_thegent_git_module: MagicMock) -> None:
        mock_thegent_git_module.get_head_sha.return_value = None
        mock_thegent_git_module.get_branch_name.return_value = "main"

        from thegent.native.git_native import GitNative

        gn = GitNative(REPO_PATH)
        result = gn.head()

        assert result["sha"] == ""

    def test_none_branch_becomes_HEAD(self, mock_thegent_git_module: MagicMock) -> None:
        mock_thegent_git_module.get_head_sha.return_value = "b" * 40
        mock_thegent_git_module.get_branch_name.return_value = None

        from thegent.native.git_native import GitNative

        gn = GitNative(REPO_PATH)
        result = gn.head()

        assert result["branch"] == "HEAD"

    def test_calls_rust_with_repo_path(self, mock_thegent_git_module: MagicMock) -> None:
        mock_thegent_git_module.get_head_sha.reset_mock()
        mock_thegent_git_module.get_branch_name.reset_mock()
        mock_thegent_git_module.get_head_sha.return_value = "c" * 40
        mock_thegent_git_module.get_branch_name.return_value = "feat/test"

        from thegent.native.git_native import GitNative

        gn = GitNative(REPO_PATH)
        gn.head()

        mock_thegent_git_module.get_head_sha.assert_called_once_with(REPO_PATH)
        mock_thegent_git_module.get_branch_name.assert_called_once_with(REPO_PATH)


# ---------------------------------------------------------------------------
# Unit: GitNative.status()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGitNativeStatus:
    """@trace FR-GIT-001"""

    def test_returns_status_from_rust(self, mock_thegent_git_module: MagicMock) -> None:
        expected = {"modified": ["a.py"], "untracked": ["b.py"], "staged": []}
        mock_thegent_git_module.get_status.return_value = expected

        from thegent.native.git_native import GitNative

        gn = GitNative(REPO_PATH)
        result = gn.status()

        assert result == expected

    def test_delegates_to_rust_with_path(self, mock_thegent_git_module: MagicMock) -> None:
        mock_thegent_git_module.get_status.reset_mock()
        mock_thegent_git_module.get_status.return_value = {
            "modified": [],
            "untracked": [],
            "staged": [],
        }

        from thegent.native.git_native import GitNative

        gn = GitNative(REPO_PATH)
        gn.status()

        mock_thegent_git_module.get_status.assert_called_once_with(REPO_PATH)

    def test_returns_required_keys(self, mock_thegent_git_module: MagicMock) -> None:
        mock_thegent_git_module.get_status.return_value = {
            "modified": [],
            "untracked": [],
            "staged": [],
        }

        from thegent.native.git_native import GitNative

        gn = GitNative(REPO_PATH)
        result = gn.status()

        for key in ("modified", "untracked", "staged"):
            assert key in result
            assert isinstance(result[key], list)


# ---------------------------------------------------------------------------
# Unit: GitNative.diff_stat() — stub implementation
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGitNativeDiffStat:
    """diff_stat consumes the new native diff_stats API with string fallback."""

    def test_returns_required_keys(self, mock_thegent_git_module: MagicMock) -> None:
        from thegent.native.git_native import GitNative

        gn = GitNative(REPO_PATH)
        result = gn.diff_stat()

        assert "files_changed" in result
        assert "insertions" in result
        assert "deletions" in result

    def test_values_are_non_negative_ints(self, mock_thegent_git_module: MagicMock) -> None:
        from thegent.native.git_native import GitNative

        gn = GitNative(REPO_PATH)
        result = gn.diff_stat()

        assert isinstance(result["files_changed"], int)
        assert isinstance(result["insertions"], int)
        assert isinstance(result["deletions"], int)
        assert all(v >= 0 for v in result.values())

    def test_uses_native_diff_stats_tuple(self, mock_thegent_git_module: MagicMock) -> None:
        from thegent.native.git_native import GitNative

        mock_thegent_git_module.diff_stats.return_value = (2, 4, 6)

        gn = GitNative()
        result = gn.diff_stat()
        mock_thegent_git_module.diff_stats.assert_called_once_with(REPO_PATH)
        assert result == {"files_changed": 2, "insertions": 4, "deletions": 6}

    def test_falls_back_to_diff_stat_string(self, mock_thegent_git_module: MagicMock) -> None:
        from thegent.native.git_native import GitNative

        mock_thegent_git_module.diff_stats = None  # type: ignore[assignment]
        mock_thegent_git_module.diff_stat.return_value = "3 files changed, 8 insertions(+), 1 deletion(-)"

        gn = GitNative(REPO_PATH)
        result = gn.diff_stat()
        mock_thegent_git_module.diff_stat.assert_called_once_with("HEAD", REPO_PATH)
        assert result == {"files_changed": 3, "insertions": 8, "deletions": 1}


# ---------------------------------------------------------------------------
# Unit: GitNative.__init__
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGitNativeInit:
    """@trace FR-GIT-001"""

    def test_default_repo_path_is_dot(self, mock_thegent_git_module: MagicMock) -> None:
        from thegent.native.git_native import GitNative

        gn = GitNative()
        assert gn.repo_path == "."

    def test_accepts_string_path(self, mock_thegent_git_module: MagicMock) -> None:
        from thegent.native.git_native import GitNative

        gn = GitNative(REPO_PATH)
        assert gn.repo_path == REPO_PATH

    def test_accepts_pathlib_path(self, mock_thegent_git_module: MagicMock) -> None:
        from thegent.native.git_native import GitNative

        gn = GitNative(REPO_ROOT)
        assert gn.repo_path == str(REPO_ROOT)
