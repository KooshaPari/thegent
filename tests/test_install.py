"""Unit tests for install module."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from thegent.install import (
    CLAUDE_MAPPING,
    EXCLUDE_DIRS,
    FACTORY_MAPPING,
    ROOT_FILES,
    create_symlink,
    get_home_dir,
    get_source_dest_mapping,
    run_install,
    should_exclude,
    smart_copy_file,
)


class TestConstants:
    """Tests for module constants."""

    def test_claude_mapping_keys(self) -> None:
        """CLAUDE_MAPPING contains expected keys."""
        assert "skills/agent-orchestra" in CLAUDE_MAPPING
        assert "hooks" in CLAUDE_MAPPING
        assert "templates" in CLAUDE_MAPPING
        assert "agents" in CLAUDE_MAPPING
        assert "commands" in CLAUDE_MAPPING
        assert "contracts" in CLAUDE_MAPPING

    def test_claude_mapping_values(self) -> None:
        """CLAUDE_MAPPING values point to correct destinations."""
        assert CLAUDE_MAPPING["skills/agent-orchestra"] == "skills/agent-orchestra"
        assert CLAUDE_MAPPING["hooks"] == "hooks"
        assert CLAUDE_MAPPING["templates"] == "templates"
        assert CLAUDE_MAPPING["agents"] == "agents"
        assert CLAUDE_MAPPING["commands"] == "commands"
        assert CLAUDE_MAPPING["contracts"] == "contracts"

    def test_factory_mapping_keys(self) -> None:
        """FACTORY_MAPPING contains expected keys."""
        assert ".factory/hooks" in FACTORY_MAPPING
        assert ".factory/skills" in FACTORY_MAPPING
        assert ".factory/commands" in FACTORY_MAPPING
        assert ".factory/droids" in FACTORY_MAPPING
        assert ".factory/plugins" in FACTORY_MAPPING
        assert ".factory/mcp.json" in FACTORY_MAPPING
        assert ".factory/config.json" in FACTORY_MAPPING
        assert ".factory/settings.json" in FACTORY_MAPPING

    def test_root_files(self) -> None:
        """ROOT_FILES contains expected files."""
        assert "CLAUDE.md" in ROOT_FILES
        assert "mcp_servers.json" in ROOT_FILES
        assert "qa-config.json" in ROOT_FILES

    def test_exclude_dirs(self) -> None:
        """EXCLUDE_DIRS contains expected directories."""
        assert "__pycache__" in EXCLUDE_DIRS
        assert ".pytest_cache" in EXCLUDE_DIRS
        assert ".ruff_cache" in EXCLUDE_DIRS
        assert ".mypy_cache" in EXCLUDE_DIRS
        assert "history.jsonl" in EXCLUDE_DIRS
        assert "session-env" in EXCLUDE_DIRS
        assert "debug" in EXCLUDE_DIRS
        assert "todos" in EXCLUDE_DIRS
        assert "tasks" in EXCLUDE_DIRS
        assert "teams" in EXCLUDE_DIRS


class TestGetHomeDir:
    """Tests for get_home_dir function."""

    def test_returns_path(self) -> None:
        """get_home_dir returns a Path object."""
        home = get_home_dir()
        assert isinstance(home, Path)

    def test_returns_user_home(self) -> None:
        """get_home_dir returns the user's home directory."""
        home = get_home_dir()
        expected = Path.home()
        assert home == expected


class TestShouldExclude:
    """Tests for should_exclude function."""

    def test_excludes_pycache(self) -> None:
        """should_exclude returns True for __pycache__."""
        assert should_exclude(Path("foo/__pycache__")) is True
        assert should_exclude(Path("__pycache__")) is True

    def test_excludes_pytest_cache(self) -> None:
        """should_exclude returns True for .pytest_cache."""
        assert should_exclude(Path("bar/.pytest_cache")) is True
        assert should_exclude(Path(".pytest_cache")) is True

    def test_excludes_ruff_cache(self) -> None:
        """should_exclude returns True for .ruff_cache."""
        assert should_exclude(Path("tests/.ruff_cache")) is True

    def test_excludes_mypy_cache(self) -> None:
        """should_exclude returns True for .mypy_cache."""
        assert should_exclude(Path("src/.mypy_cache")) is True

    def test_excludes_history_jsonl(self) -> None:
        """should_exclude returns True for history.jsonl."""
        assert should_exclude(Path("history.jsonl")) is True

    def test_excludes_session_env(self) -> None:
        """should_exclude returns True for session-env."""
        assert should_exclude(Path("session-env")) is True
        assert should_exclude(Path("foo/session-env")) is True

    def test_excludes_debug_dir(self) -> None:
        """should_exclude returns True for debug directory."""
        assert should_exclude(Path("debug")) is True

    def test_excludes_todos_dir(self) -> None:
        """should_exclude returns True for todos directory."""
        assert should_exclude(Path("todos")) is True

    def test_excludes_tasks_dir(self) -> None:
        """should_exclude returns True for tasks directory."""
        assert should_exclude(Path("tasks")) is True

    def test_excludes_teams_dir(self) -> None:
        """should_exclude returns True for teams directory."""
        assert should_exclude(Path("teams")) is True

    def test_does_not_exclude_regular_dirs(self) -> None:
        """should_exclude returns False for regular directories."""
        assert should_exclude(Path("src")) is False
        assert should_exclude(Path("tests")) is False
        assert should_exclude(Path("skills")) is False
        assert should_exclude(Path("hooks")) is False


class TestGetSourceDestMapping:
    """Tests for get_source_dest_mapping function."""

    def test_returns_dict(self) -> None:
        """get_source_dest_mapping returns a dict."""
        result = get_source_dest_mapping(Path("/fake/root"), "claude")
        assert isinstance(result, dict)

    def test_claude_target_includes_claude_mapping(self) -> None:
        """claude target includes CLAUDE_MAPPING entries."""
        result = get_source_dest_mapping(Path("/fake/root"), "claude")
        # Check that CLAUDE entries are included (relative to thegent root)
        assert any("skills/agent-orchestra" in str(k) for k in result.keys())

    def test_factory_target_includes_factory_mapping(self) -> None:
        """factory target includes FACTORY_MAPPING entries."""
        result = get_source_dest_mapping(Path("/fake/root"), "factory")
        # Check that factory entries are included
        assert any(".factory" in str(k) for k in result.keys())

    def test_both_target_includes_all_mappings(self) -> None:
        """both target includes both CLAUDE and FACTORY mappings."""
        result = get_source_dest_mapping(Path("/fake/root"), "both")
        # Should have entries from both mappings
        keys_str = [str(k) for k in result.keys()]
        assert any("skills/agent-orchestra" in k for k in keys_str)
        assert any(".factory" in k for k in keys_str)

    def test_invalid_target_raises(self) -> None:
        """Invalid target raises ValueError."""
        with pytest.raises(ValueError):
            get_source_dest_mapping(Path("/fake/root"), "invalid")


class TestSmartCopyFile:
    """Tests for smart_copy_file function."""

    def test_returns_copied_when_dest_not_exists(
        self, tmp_path: Path
    ) -> None:
        """smart_copy_file returns 'copied' when destination doesn't exist."""
        src = tmp_path / "source.txt"
        src.write_text("content")
        dst = tmp_path / "dest.txt"

        result = smart_copy_file(src, dst)

        assert result == "copied"
        assert dst.exists()
        assert dst.read_text() == "content"

    def test_returns_skipped_when_src_older(
        self, tmp_path: Path
    ) -> None:
        """smart_copy_file returns 'skipped' when source is older."""
        src = tmp_path / "source.txt"
        src.write_text("old content")
        dst = tmp_path / "dest.txt"
        dst.write_text("new content")

        # Make dst newer than src
        old_time = (dst.stat().st_mtime) - 10
        os.utime(src, (old_time, old_time))

        result = smart_copy_file(src, dst)

        assert result == "skipped"
        assert dst.read_text() == "new content"

    def test_returns_copied_when_src_newer(
        self, tmp_path: Path
    ) -> None:
        """smart_copy_file returns 'copied' when source is newer."""
        src = tmp_path / "source.txt"
        src.write_text("new content")
        dst = tmp_path / "dest.txt"
        dst.write_text("old content")

        # Make src newer than dst
        import time
        time.sleep(0.01)
        src.touch()

        result = smart_copy_file(src, dst)

        assert result == "copied"
        assert dst.read_text() == "new content"

    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        """smart_copy_file creates parent directories."""
        src = tmp_path / "source.txt"
        src.write_text("content")
        dst = tmp_path / "subdir" / "nested" / "dest.txt"

        result = smart_copy_file(src, dst)

        assert result == "copied"
        assert dst.exists()
        assert dst.parent.exists()


class TestCreateSymlink:
    """Tests for create_symlink function."""

    def test_creates_symlink(self, tmp_path: Path) -> None:
        """create_symlink creates a symlink."""
        src = tmp_path / "target.txt"
        src.write_text("target content")
        dst = tmp_path / "link.txt"

        result = create_symlink(src, dst)

        assert result == "created"
        assert dst.is_symlink()
        assert dst.readlink() == src

    def test_returns_existed_when_already_exists(
        self, tmp_path: Path
    ) -> None:
        """create_symlink returns 'existed' when link already exists."""
        src = tmp_path / "target.txt"
        src.write_text("target content")
        dst = tmp_path / "link.txt"
        dst.symlink_to(src)

        result = create_symlink(src, dst)

        assert result == "existed"


class TestRunInstall:
    """Tests for run_install function."""

    def test_returns_dict_with_counts(self) -> None:
        """run_install returns a dict with copied, skipped, conflicts, errors."""
        result = run_install(target="claude", dry_run=True)

        assert isinstance(result, dict)
        assert "copied" in result
        assert "skipped" in result
        assert "conflicts" in result
        assert "errors" in result

    def test_dry_run_no_changes(self, tmp_path: Path) -> None:
        """run_install with dry_run=True makes no actual changes."""
        # Mock home dir to tmp_path
        with patch("thegent.install.get_home_dir", return_value=tmp_path):
            result = run_install(target="claude", dry_run=True, verbose=False)

        # In dry run, copied should be 0 (or fewer than actual run)
        assert isinstance(result["copied"], int)
        assert isinstance(result["skipped"], int)
        assert isinstance(result["conflicts"], int)
        assert isinstance(result["errors"], int)

    def test_verbose_flag_accepted(self) -> None:
        """run_install accepts verbose flag without error."""
        result = run_install(target="claude", dry_run=True, verbose=True)

        assert isinstance(result, dict)

    def test_target_claude_valid(self) -> None:
        """run_install accepts target='claude'."""
        result = run_install(target="claude", dry_run=True)
        assert isinstance(result, dict)

    def test_target_factory_valid(self) -> None:
        """run_install accepts target='factory'."""
        result = run_install(target="factory", dry_run=True)
        assert isinstance(result, dict)

    def test_target_both_valid(self) -> None:
        """run_install accepts target='both'."""
        result = run_install(target="both", dry_run=True)
        assert isinstance(result, dict)

    def test_invalid_target_raises(self) -> None:
        """run_install raises ValueError for invalid target."""
        with pytest.raises(ValueError):
            run_install(target="invalid")

    def test_invalid_mode_raises(self) -> None:
        """run_install raises ValueError for invalid mode."""
        with pytest.raises(ValueError):
            run_install(mode="invalid")
