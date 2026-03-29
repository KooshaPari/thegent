"""Tests for batch_ops module.

# @trace FR-DX-001
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.requirement("FR-DX-001")
class TestBatchRead:
    """Tests for batch_read."""

    def test_read_multiple_files(self, tmp_path: Path) -> None:
        """Read multiple files and return dict mapping paths to contents."""
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("alpha")
        f2.write_text("bravo")

        from thegent.utils.batch_ops import batch_read

        result = batch_read([f1, f2])
        assert result[f1] == "alpha"
        assert result[f2] == "bravo"

    def test_read_empty_list(self) -> None:
        """Empty input returns empty dict."""
        from thegent.utils.batch_ops import batch_read

        assert batch_read([]) == {}

    def test_read_nonexistent_raises(self, tmp_path: Path) -> None:
        """Reading a nonexistent file raises FileNotFoundError."""
        from thegent.utils.batch_ops import batch_read

        with pytest.raises(FileNotFoundError):
            batch_read([tmp_path / "does_not_exist.txt"])


@pytest.mark.requirement("FR-DX-001")
class TestBatchWrite:
    """Tests for batch_write."""

    def test_write_multiple_files(self, tmp_path: Path) -> None:
        """Write multiple files from list of tuples."""
        f1 = tmp_path / "x.txt"
        f2 = tmp_path / "y.txt"

        from thegent.utils.batch_ops import batch_write

        batch_write([(f1, "x-content"), (f2, "y-content")])
        assert f1.read_text() == "x-content"
        assert f2.read_text() == "y-content"

    def test_write_creates_parent_dirs(self, tmp_path: Path) -> None:
        """Parent directories are created if missing."""
        f = tmp_path / "sub" / "deep" / "file.txt"

        from thegent.utils.batch_ops import batch_write

        batch_write([(f, "nested")])
        assert f.read_text() == "nested"

    def test_write_empty_list(self) -> None:
        """Empty input is a no-op."""
        from thegent.utils.batch_ops import batch_write

        batch_write([])  # should not raise


@pytest.mark.requirement("FR-DX-001")
class TestBatchDelete:
    """Tests for batch_delete."""

    def test_delete_multiple_files(self, tmp_path: Path) -> None:
        """Delete multiple files."""
        f1 = tmp_path / "del1.txt"
        f2 = tmp_path / "del2.txt"
        f1.write_text("1")
        f2.write_text("2")

        from thegent.utils.batch_ops import batch_delete

        batch_delete([f1, f2])
        assert not f1.exists()
        assert not f2.exists()

    def test_delete_nonexistent_raises(self, tmp_path: Path) -> None:
        """Deleting a nonexistent file raises FileNotFoundError."""
        from thegent.utils.batch_ops import batch_delete

        with pytest.raises(FileNotFoundError):
            batch_delete([tmp_path / "ghost.txt"])

    def test_delete_empty_list(self) -> None:
        """Empty input is a no-op."""
        from thegent.utils.batch_ops import batch_delete

        batch_delete([])  # should not raise
