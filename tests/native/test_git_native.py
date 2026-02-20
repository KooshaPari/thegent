"""Tests for GitNative fallback path (BKM-06).

These tests exercise the pure-Python git subprocess fallback so they work
regardless of whether the thegent-git Rust binary is compiled.

FR-GIT-001  @trace FR-GIT-001
"""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from thegent.native.git_native import (
    GitNative,
    _git_diff_stat_fallback,
    _git_head_fallback,
    _git_status_fallback,
    _run_binary,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parents[2]  # thegent project root (is a git repo)
REPO_PATH = str(REPO_ROOT)


# ---------------------------------------------------------------------------
# Unit: fallback functions against the real git repo
# ---------------------------------------------------------------------------


class TestGitHeadFallback:
    """@trace FR-GIT-001"""

    def test_returns_non_empty_sha(self) -> None:
        result = _git_head_fallback(REPO_PATH)
        assert "sha" in result
        assert len(result["sha"]) == 40, f"Expected 40-char SHA, got: {result['sha']}"

    def test_branch_is_string(self) -> None:
        result = _git_head_fallback(REPO_PATH)
        assert "branch" in result
        assert isinstance(result["branch"], str)
        assert len(result["branch"]) > 0

    def test_bad_repo_returns_empty_sha(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            result = _git_head_fallback(tmp)
        assert result["sha"] == ""
        assert result["branch"] == "HEAD"


class TestGitStatusFallback:
    """@trace FR-GIT-001"""

    def test_returns_required_keys(self) -> None:
        result = _git_status_fallback(REPO_PATH)
        assert "modified" in result
        assert "untracked" in result
        assert "staged" in result

    def test_lists_are_lists(self) -> None:
        result = _git_status_fallback(REPO_PATH)
        assert isinstance(result["modified"], list)
        assert isinstance(result["untracked"], list)
        assert isinstance(result["staged"], list)

    def test_bad_repo_returns_empty_lists(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            result = _git_status_fallback(tmp)
        assert result == {"modified": [], "untracked": [], "staged": []}

    def test_porcelain_parsing_modified(self) -> None:
        """Porcelain parser correctly identifies 'M ' as modified (unstaged)."""
        fake_output = " M src/foo.py\nA  src/bar.py\n?? scratch.txt\n"
        with patch("subprocess.check_output", return_value=fake_output):
            result = _git_status_fallback(REPO_PATH)
        assert "src/foo.py" in result["modified"]
        assert "src/bar.py" in result["staged"]
        assert "scratch.txt" in result["untracked"]

    def test_porcelain_parsing_deleted(self) -> None:
        """Porcelain parser correctly identifies ' D' as unstaged deletion."""
        fake_output = " D old_file.py\n"
        with patch("subprocess.check_output", return_value=fake_output):
            result = _git_status_fallback(REPO_PATH)
        assert "old_file.py" in result["modified"]


class TestGitDiffStatFallback:
    """@trace FR-GIT-001"""

    def test_returns_required_keys(self) -> None:
        result = _git_diff_stat_fallback(REPO_PATH)
        assert "files_changed" in result
        assert "insertions" in result
        assert "deletions" in result

    def test_values_are_ints(self) -> None:
        result = _git_diff_stat_fallback(REPO_PATH)
        assert isinstance(result["files_changed"], int)
        assert isinstance(result["insertions"], int)
        assert isinstance(result["deletions"], int)

    def test_values_non_negative(self) -> None:
        result = _git_diff_stat_fallback(REPO_PATH)
        assert result["files_changed"] >= 0
        assert result["insertions"] >= 0
        assert result["deletions"] >= 0

    def test_bad_repo_returns_zeros(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            result = _git_diff_stat_fallback(tmp)
        assert result == {"files_changed": 0, "insertions": 0, "deletions": 0}

    def test_stat_line_parsing(self) -> None:
        """Git stat summary line is parsed correctly."""
        fake_output = (
            " src/foo.py | 10 +++++-----\n"
            " 1 file changed, 5 insertions(+), 5 deletions(-)\n"
        )
        with patch("subprocess.check_output", return_value=fake_output):
            result = _git_diff_stat_fallback(REPO_PATH)
        assert result["files_changed"] == 1
        assert result["insertions"] == 5
        assert result["deletions"] == 5

    def test_stat_insertions_only(self) -> None:
        fake_output = " 3 files changed, 42 insertions(+)\n"
        with patch("subprocess.check_output", return_value=fake_output):
            result = _git_diff_stat_fallback(REPO_PATH)
        assert result["files_changed"] == 3
        assert result["insertions"] == 42
        assert result["deletions"] == 0


# ---------------------------------------------------------------------------
# Unit: _run_binary — binary discovery and delegation
# ---------------------------------------------------------------------------


class TestRunBinary:
    """@trace FR-GIT-001"""

    def test_returns_none_when_binary_missing(self) -> None:
        with patch("thegent.native.git_native._find_binary", return_value=None):
            assert _run_binary("head", REPO_PATH) is None

    def test_returns_none_on_nonzero_exit(self) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 2
        mock_result.stderr = "not a git repository"
        with patch("thegent.native.git_native._find_binary", return_value="/usr/bin/thegent-git"):
            with patch("subprocess.run", return_value=mock_result):
                assert _run_binary("head", REPO_PATH) is None

    def test_returns_parsed_json_on_success(self) -> None:
        payload = {"sha": "a" * 40, "branch": "main"}
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(payload) + "\n"
        with patch("thegent.native.git_native._find_binary", return_value="/usr/bin/thegent-git"):
            with patch("subprocess.run", return_value=mock_result):
                result = _run_binary("head", REPO_PATH)
        assert result == payload

    def test_returns_none_on_invalid_json(self) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "not json"
        with patch("thegent.native.git_native._find_binary", return_value="/usr/bin/thegent-git"):
            with patch("subprocess.run", return_value=mock_result):
                assert _run_binary("head", REPO_PATH) is None

    def test_returns_none_on_timeout(self) -> None:
        with patch("thegent.native.git_native._find_binary", return_value="/usr/bin/thegent-git"):
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("thegent-git", 10)):
                assert _run_binary("head", REPO_PATH) is None


# ---------------------------------------------------------------------------
# Integration: GitNative class — binary unavailable, all fallback
# ---------------------------------------------------------------------------


class TestGitNativeFallbackPath:
    """Integration tests for GitNative when binary is unavailable. @trace FR-GIT-001"""

    @pytest.fixture(autouse=True)
    def force_fallback(self):
        """Ensure the native binary is not found so the fallback path is exercised."""
        with patch("thegent.native.git_native._find_binary", return_value=None):
            yield

    def test_head_returns_sha_and_branch(self) -> None:
        gn = GitNative(REPO_PATH)
        result = gn.head()
        assert len(result["sha"]) == 40
        assert isinstance(result["branch"], str)

    def test_status_returns_correct_keys(self) -> None:
        gn = GitNative(REPO_PATH)
        result = gn.status()
        for key in ("modified", "untracked", "staged"):
            assert key in result
            assert isinstance(result[key], list)

    def test_diff_stat_returns_ints(self) -> None:
        gn = GitNative(REPO_PATH)
        result = gn.diff_stat()
        for key in ("files_changed", "insertions", "deletions"):
            assert key in result
            assert isinstance(result[key], int)
            assert result[key] >= 0

    def test_default_path_is_current_dir(self) -> None:
        gn = GitNative()
        assert gn.repo_path == "."

    def test_path_as_pathlib(self) -> None:
        gn = GitNative(REPO_ROOT)
        result = gn.head()
        assert len(result["sha"]) == 40


# ---------------------------------------------------------------------------
# Integration: GitNative class — binary present and returns valid JSON
# ---------------------------------------------------------------------------


class TestGitNativeBinaryPath:
    """Integration tests for GitNative when binary responds correctly. @trace FR-GIT-001"""

    def _mock_binary_result(self, payload: dict) -> MagicMock:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(payload) + "\n"
        return mock_result

    def test_head_uses_binary_result(self) -> None:
        expected = {"sha": "b" * 40, "branch": "feat/bkm-06"}
        with patch("thegent.native.git_native._run_binary", return_value=expected):
            gn = GitNative(REPO_PATH)
            result = gn.head()
        assert result == expected

    def test_status_uses_binary_result(self) -> None:
        expected = {"modified": ["a.py"], "untracked": [], "staged": ["b.py"]}
        with patch("thegent.native.git_native._run_binary", return_value=expected):
            gn = GitNative(REPO_PATH)
            result = gn.status()
        assert result == expected

    def test_diff_stat_uses_binary_result(self) -> None:
        expected = {"files_changed": 3, "insertions": 7, "deletions": 2}
        with patch("thegent.native.git_native._run_binary", return_value=expected):
            gn = GitNative(REPO_PATH)
            result = gn.diff_stat()
        assert result == expected

    def test_falls_back_when_binary_fails(self) -> None:
        """If _run_binary returns None (e.g. binary exits non-zero), GitNative uses git subprocess fallback."""
        # Patch _run_binary directly to simulate binary failure without
        # affecting subprocess.check_output (which the fallback uses).
        with patch("thegent.native.git_native._run_binary", return_value=None):
            gn = GitNative(REPO_PATH)
            result = gn.head()
        # Fallback returns real data from the actual git repository.
        assert len(result["sha"]) == 40
        assert isinstance(result["branch"], str)
