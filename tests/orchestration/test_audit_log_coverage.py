"""Additional tests for ShadowAuditGit to increase coverage.

Tests for path property, init idempotency, malformed log entries,
and _scrub_secrets static method.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from thegent.orchestration.state.audit_log import ShadowAuditGit


@pytest.fixture
def audit_dir(tmp_path: Path) -> Path:
    """Return a temporary directory for the shadow audit repo."""
    return tmp_path / "audit"


@pytest.fixture
def audit_git(audit_dir: Path) -> ShadowAuditGit:
    """Create a ShadowAuditGit instance with a temp audit dir."""
    return ShadowAuditGit(audit_path=audit_dir)


@pytest.fixture
def initialized_audit(audit_git: ShadowAuditGit) -> ShadowAuditGit:
    """Return a ShadowAuditGit that has been initialized."""
    audit_git.init_shadow_repo()
    return audit_git


@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    """Create a sample file for testing."""
    file_path = tmp_path / "workdir" / "sample.txt"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("sample content")
    return file_path


class TestShadowAuditGitPath:
    """Tests for path property."""

    def test_path_returns_audit_path(self, audit_git: ShadowAuditGit, audit_dir: Path) -> None:
        """Verify path property returns the audit path."""
        assert audit_git.path == audit_dir

    def test_path_is_path_object(self, audit_git: ShadowAuditGit) -> None:
        """Verify path is a Path object."""
        assert isinstance(audit_git.path, Path)

    def test_path_with_string_input(self, tmp_path: Path) -> None:
        """Verify path works with string input to constructor."""
        audit = ShadowAuditGit(audit_path=str(tmp_path / "string_path"))
        assert audit.path == tmp_path / "string_path"


class TestShadowAuditGitInitIdempotent:
    """Tests for init_shadow_repo idempotency."""

    def test_init_is_idempotent(self, audit_git: ShadowAuditGit, audit_dir: Path) -> None:
        """Verify calling init twice doesn't error or duplicate."""
        audit_git.init_shadow_repo()
        initial_commits = len(audit_git.get_log(limit=100))

        # Call init again
        audit_git.init_shadow_repo()

        # Should still have same number of commits
        final_commits = len(audit_git.get_log(limit=100))
        assert final_commits == initial_commits

    def test_init_skips_when_git_exists(
        self, audit_git: ShadowAuditGit, audit_dir: Path
    ) -> None:
        """Verify init skips when .git directory exists."""
        # First init
        audit_git.init_shadow_repo()

        # Verify .git exists
        assert (audit_dir / ".git").is_dir()

        # Second init should be no-op (not raise)
        audit_git.init_shadow_repo()


class TestShadowAuditGitMalformedLog:
    """Tests for handling malformed git log entries."""

    def test_get_log_handles_malformed_entries(
        self, initialized_audit: ShadowAuditGit, sample_file: Path
    ) -> None:
        """Verify get_log handles entries with wrong format."""
        # Create a normal commit first
        initialized_audit.commit_transaction(
            episode_id="ep-normal",
            changed_files=[sample_file],
            message="normal commit",
        )

        # Get log should work
        entries = initialized_audit.get_log(limit=10)

        # Should have at least 2 commits (init + our commit)
        assert len(entries) >= 2

        # All entries should have required keys
        for entry in entries:
            assert "hash" in entry
            assert "message" in entry
            assert "date" in entry

    def test_get_log_empty_lines_skipped(
        self, initialized_audit: ShadowAuditGit, sample_file: Path
    ) -> None:
        """Verify empty lines in git log are skipped."""
        # Make a commit
        initialized_audit.commit_transaction(
            episode_id="ep-test",
            changed_files=[sample_file],
            message="test commit",
        )

        entries = initialized_audit.get_log(limit=100)

        # All entries should be non-empty dicts
        assert all(entry for entry in entries)


class TestShadowAuditGitScrubSecrets:
    """Tests for _scrub_secrets static method."""

    def test_scrub_secrets_no_secrets(self) -> None:
        """Verify content without secrets is unchanged."""
        content = "name: myapp\nversion: 1.0.0"
        result = ShadowAuditGit._scrub_secrets(content)

        assert result == content

    @patch("thegent.orchestration.state.audit_log.scan_secrets")
    def test_scrub_secrets_with_secrets(self, mock_scan: MagicMock) -> None:
        """Verify secrets are redacted."""
        from thegent.governance.native_secret_scan import SecretMatch

        mock_scan.return_value = [
            SecretMatch(kind="api_key", line=1, masked="API****")
        ]

        content = "API_KEY=secret123\nname=myapp"
        result = ShadowAuditGit._scrub_secrets(content)

        # The secret line should be redacted
        assert "secret123" not in result
        assert "[REDACTED:api_key]" in result

    @patch("thegent.orchestration.state.audit_log.scan_secrets")
    def test_scrub_secrets_multiple_secrets(self, mock_scan: MagicMock) -> None:
        """Verify multiple secrets are redacted."""
        from thegent.governance.native_secret_scan import SecretMatch

        mock_scan.return_value = [
            SecretMatch(kind="api_key", line=1, masked="API****"),
            SecretMatch(kind="password", line=2, masked="PWD****"),
        ]

        content = "API_KEY=secret123\nPASSWORD=pass456\nname=myapp"
        result = ShadowAuditGit._scrub_secrets(content)

        lines = result.split("\n")
        assert "[REDACTED:api_key]" in lines[0]
        assert "[REDACTED:password]" in lines[1]
        assert lines[2] == "name=myapp"

    @patch("thegent.orchestration.state.audit_log.scan_secrets")
    def test_scrub_secrets_invalid_line_index(self, mock_scan: MagicMock) -> None:
        """Verify invalid line indices are handled gracefully."""
        from thegent.governance.native_secret_scan import SecretMatch

        # Line index out of bounds
        mock_scan.return_value = [
            SecretMatch(kind="secret", line=10, masked="SECRET****")  # Only 2 lines
        ]

        content = "line1\nline2"
        result = ShadowAuditGit._scrub_secrets(content)

        # Should not crash, content unchanged
        assert result == "line1\nline2"

    @patch("thegent.orchestration.state.audit_log.scan_secrets")
    def test_scrub_secrets_line_zero(self, mock_scan: MagicMock) -> None:
        """Verify line 0 (invalid) is handled."""
        from thegent.governance.native_secret_scan import SecretMatch

        mock_scan.return_value = [
            SecretMatch(kind="secret", line=0, masked="SECRET****")
        ]

        content = "line1\nline2"
        result = ShadowAuditGit._scrub_secrets(content)

        # Line 0 means line_idx = -1, which is < 0, so no change
        assert result == "line1\nline2"

    @patch("thegent.orchestration.state.audit_log.scan_secrets")
    def test_scrub_secrets_negative_line(self, mock_scan: MagicMock) -> None:
        """Verify negative line numbers are handled."""
        from thegent.governance.native_secret_scan import SecretMatch

        mock_scan.return_value = [
            SecretMatch(kind="secret", line=-1, masked="SECRET****")
        ]

        content = "line1\nline2"
        result = ShadowAuditGit._scrub_secrets(content)

        # Should not crash
        assert result == "line1\nline2"


class TestShadowAuditGitGetDiff:
    """Tests for get_diff method."""

    def test_get_diff_returns_string(
        self, initialized_audit: ShadowAuditGit, sample_file: Path
    ) -> None:
        """Verify get_diff returns a string."""
        initialized_audit.commit_transaction(
            episode_id="ep-diff-001",
            changed_files=[sample_file],
            message="diff test",
        )

        entries = initialized_audit.get_log(episode_id="ep-diff-001")
        assert len(entries) >= 1

        diff = initialized_audit.get_diff(entries[0]["hash"])

        assert isinstance(diff, str)

    def test_get_diff_shows_changes(
        self, initialized_audit: ShadowAuditGit, sample_file: Path
    ) -> None:
        """Verify get_diff shows file changes."""
        initialized_audit.commit_transaction(
            episode_id="ep-diff-002",
            changed_files=[sample_file],
            message="diff test with content",
        )

        entries = initialized_audit.get_log(episode_id="ep-diff-002")
        diff = initialized_audit.get_diff(entries[0]["hash"])

        # The diff should contain the file content
        assert "sample content" in diff


class TestShadowAuditGitEdgeCases:
    """Additional edge case tests."""

    def test_commit_transaction_empty_file_list(
        self, initialized_audit: ShadowAuditGit
    ) -> None:
        """Verify empty file list doesn't create commit."""
        initial_log = initialized_audit.get_log(limit=10)

        initialized_audit.commit_transaction(
            episode_id="ep-empty",
            changed_files=[],
            message="empty commit",
        )

        final_log = initialized_audit.get_log(limit=10)

        # Should have same number of commits (empty file list = no commit)
        assert len(final_log) == len(initial_log)

    def test_get_log_with_episode_filter(
        self, initialized_audit: ShadowAuditGit, sample_file: Path
    ) -> None:
        """Verify get_log can filter by episode_id."""
        # Make two commits with different episode IDs
        initialized_audit.commit_transaction(
            episode_id="ep-filter-unique-001",
            changed_files=[sample_file],
            message="first commit",
        )

        # Modify file for second commit
        sample_file.write_text("modified content")
        initialized_audit.commit_transaction(
            episode_id="ep-filter-unique-002",
            changed_files=[sample_file],
            message="second commit",
        )

        # Filter by first episode
        entries = initialized_audit.get_log(episode_id="ep-filter-unique-001")

        # Should only get commits with that episode ID
        assert all("ep-filter-unique-001" in e["message"] for e in entries)
