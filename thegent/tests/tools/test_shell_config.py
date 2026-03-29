"""Tests for shell_config.py — ShellConfigFile and ShellConfigAuditor.

@trace FR-TOOLS-001
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from thegent.tools.shell_config import (
    ShellConfigAuditor,
    ShellConfigFile,
    _is_shell_config,
    _resolve_source,
)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def _write(tmp_path: Path, name: str, content: str) -> Path:
    """Write a shell file to tmp_path and return its Path."""
    p = tmp_path / name
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


# ──────────────────────────────────────────────────────────────────────────────
# _is_shell_config
# ──────────────────────────────────────────────────────────────────────────────


def test_is_shell_config_zsh_extension():
    assert _is_shell_config(Path("foo.zsh")) is True


def test_is_shell_config_sh_extension():
    assert _is_shell_config(Path("bar.sh")) is True


def test_is_shell_config_zshrc_name():
    assert _is_shell_config(Path(".zshrc")) is True


def test_is_shell_config_zshenv_name():
    assert _is_shell_config(Path(".zshenv")) is True


def test_is_shell_config_python_file():
    assert _is_shell_config(Path("script.py")) is False


def test_is_shell_config_text_file():
    assert _is_shell_config(Path("README.txt")) is False


# ──────────────────────────────────────────────────────────────────────────────
# _resolve_source
# ──────────────────────────────────────────────────────────────────────────────


def test_resolve_source_absolute():
    result = _resolve_source("/etc/zshrc", Path("/home/user"))
    assert result == Path("/etc/zshrc")


def test_resolve_source_relative():
    result = _resolve_source("./other.zsh", Path("/home/user/shell"))
    assert result == Path("/home/user/shell/other.zsh")


def test_resolve_source_dynamic_returns_none():
    result = _resolve_source("$ZDOTDIR/plugins.zsh", Path("/home/user"))
    assert result is None


def test_resolve_source_backtick_returns_none():
    result = _resolve_source("`brew --prefix`/share/zsh", Path("/home/user"))
    assert result is None


# ──────────────────────────────────────────────────────────────────────────────
# ShellConfigFile.parse — function detection
# ──────────────────────────────────────────────────────────────────────────────


def test_parse_function_keyword_syntax(tmp_path: Path):
    p = _write(
        tmp_path,
        "a.zsh",
        """\
        function my_func() {
            echo hello
        }
        """,
    )
    cfg = ShellConfigFile.parse(p)
    assert "my_func" in cfg.functions


def test_parse_function_posix_syntax(tmp_path: Path):
    p = _write(
        tmp_path,
        "b.zsh",
        """\
        my_func() {
            echo hello
        }
        """,
    )
    cfg = ShellConfigFile.parse(p)
    assert "my_func" in cfg.functions


def test_parse_multiple_functions(tmp_path: Path):
    p = _write(
        tmp_path,
        "multi.zsh",
        """\
        foo() { echo foo; }
        bar() { echo bar; }
        function baz() { echo baz; }
        """,
    )
    cfg = ShellConfigFile.parse(p)
    assert set(cfg.functions) == {"foo", "bar", "baz"}


def test_parse_no_functions(tmp_path: Path):
    p = _write(tmp_path, "empty.zsh", "export FOO=1\n")
    cfg = ShellConfigFile.parse(p)
    assert cfg.functions == []


# ──────────────────────────────────────────────────────────────────────────────
# ShellConfigFile.parse — alias detection
# ──────────────────────────────────────────────────────────────────────────────


def test_parse_alias_simple(tmp_path: Path):
    p = _write(tmp_path, "aliases.zsh", "alias ll='ls -lah'\n")
    cfg = ShellConfigFile.parse(p)
    assert "ll" in cfg.aliases


def test_parse_alias_multiple(tmp_path: Path):
    p = _write(
        tmp_path,
        "many_aliases.zsh",
        """\
        alias g='git'
        alias gst='git status'
        alias ll='ls -lah'
        """,
    )
    cfg = ShellConfigFile.parse(p)
    assert set(cfg.aliases) == {"g", "gst", "ll"}


# ──────────────────────────────────────────────────────────────────────────────
# ShellConfigFile.parse — source detection
# ──────────────────────────────────────────────────────────────────────────────


def test_parse_source_dot(tmp_path: Path):
    p = _write(tmp_path, "loader.zsh", ". ./other.zsh\n")
    cfg = ShellConfigFile.parse(p)
    assert len(cfg.raw_sources) == 1
    assert cfg.raw_sources[0] == "./other.zsh"


def test_parse_source_keyword(tmp_path: Path):
    p = _write(tmp_path, "loader2.zsh", 'source "$HOME/.zshrc.local"\n')
    cfg = ShellConfigFile.parse(p)
    assert any(".zshrc.local" in s for s in cfg.raw_sources)


def test_parse_path_populated(tmp_path: Path):
    p = _write(tmp_path, "x.zsh", "export X=1\n")
    cfg = ShellConfigFile.parse(p)
    assert cfg.path == p.resolve()


# ──────────────────────────────────────────────────────────────────────────────
# ShellConfigAuditor.audit
# ──────────────────────────────────────────────────────────────────────────────


def test_audit_finds_zsh_files(tmp_path: Path):
    _write(tmp_path, "one.zsh", "foo() { echo 1; }\n")
    _write(tmp_path, "two.sh", "bar() { echo 2; }\n")
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path])
    names = {c.path.name for c in configs}
    assert "one.zsh" in names
    assert "two.sh" in names


def test_audit_ignores_non_shell_files(tmp_path: Path):
    _write(tmp_path, "notes.txt", "some text\n")
    _write(tmp_path, "script.py", "print('hi')\n")
    _write(tmp_path, "keep.zsh", "export A=1\n")
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path])
    names = {c.path.name for c in configs}
    assert "notes.txt" not in names
    assert "script.py" not in names
    assert "keep.zsh" in names


def test_audit_empty_directory(tmp_path: Path):
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path])
    assert configs == []


def test_audit_nonexistent_directory(tmp_path: Path):
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path / "does_not_exist"])
    assert configs == []


def test_audit_no_duplicates_in_list(tmp_path: Path):
    _write(tmp_path, "a.zsh", "export A=1\n")
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path, tmp_path])  # same dir twice
    paths = [c.path for c in configs]
    assert len(paths) == len(set(paths))


# ──────────────────────────────────────────────────────────────────────────────
# ShellConfigAuditor.find_duplicates
# ──────────────────────────────────────────────────────────────────────────────


def test_find_duplicates_detects_same_function(tmp_path: Path):
    _write(tmp_path, "a.zsh", "shared_func() { echo a; }\n")
    _write(tmp_path, "b.zsh", "shared_func() { echo b; }\n")
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path])
    dupes = auditor.find_duplicates(configs)
    assert "shared_func" in dupes
    assert len(dupes["shared_func"]) == 2


def test_find_duplicates_unique_functions_not_reported(tmp_path: Path):
    _write(tmp_path, "a.zsh", "only_in_a() { echo a; }\n")
    _write(tmp_path, "b.zsh", "only_in_b() { echo b; }\n")
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path])
    dupes = auditor.find_duplicates(configs)
    assert dupes == {}


def test_find_duplicates_three_way_clash(tmp_path: Path):
    for letter in ("a", "b", "c"):
        _write(tmp_path, f"{letter}.zsh", "triple() { echo; }\n")
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path])
    dupes = auditor.find_duplicates(configs)
    assert "triple" in dupes
    assert len(dupes["triple"]) == 3


# ──────────────────────────────────────────────────────────────────────────────
# ShellConfigAuditor.generate_consolidated
# ──────────────────────────────────────────────────────────────────────────────


def test_generate_consolidated_includes_shebang(tmp_path: Path):
    _write(tmp_path, "x.zsh", "export X=1\n")
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path])
    merged = auditor.generate_consolidated(configs)
    assert merged.startswith("#!/usr/bin/env zsh")


def test_generate_consolidated_includes_all_content(tmp_path: Path):
    _write(tmp_path, "a.zsh", "export ALPHA=1\n")
    _write(tmp_path, "b.zsh", "export BETA=2\n")
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path])
    merged = auditor.generate_consolidated(configs)
    assert "ALPHA=1" in merged
    assert "BETA=2" in merged


def test_generate_consolidated_warns_on_duplicates(tmp_path: Path):
    _write(tmp_path, "a.zsh", "dup() { echo a; }\n")
    _write(tmp_path, "b.zsh", "dup() { echo b; }\n")
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path])
    merged = auditor.generate_consolidated(configs)
    assert "WARNING" in merged
    assert "dup" in merged


def test_generate_consolidated_empty_list():
    auditor = ShellConfigAuditor()
    merged = auditor.generate_consolidated([])
    assert "No shell configuration files found" in merged


def test_generate_consolidated_origin_comment(tmp_path: Path):
    p = _write(tmp_path, "origin_test.zsh", "export Z=1\n")
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path])
    merged = auditor.generate_consolidated(configs)
    assert str(p.resolve()) in merged


# ──────────────────────────────────────────────────────────────────────────────
# ShellConfigAuditor.check_sourcing_order
# ──────────────────────────────────────────────────────────────────────────────


def test_check_sourcing_order_missing_source_reported(tmp_path: Path):
    _write(tmp_path, "loader.zsh", "source /nonexistent/path.zsh\n")
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path])
    issues = auditor.check_sourcing_order(configs)
    # Should flag that /nonexistent/path.zsh is not in discovered set
    assert any("not in the discovered set" in i for i in issues)


def test_check_sourcing_order_no_issues_for_unresolvable_dynamic_sources(tmp_path: Path):
    # $ZDOTDIR cannot be resolved statically → _resolve_source returns None
    # → the source is not added to cfg.sources → no "not in discovered set" issue
    _write(tmp_path, "dynamic.zsh", "source $ZDOTDIR/plugins.zsh\n")
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path])
    issues = auditor.check_sourcing_order(configs)
    # No "not in the discovered set" issues from unresolvable dynamic sources
    missing_issues = [i for i in issues if "not in the discovered set" in i]
    assert missing_issues == []


def test_check_sourcing_order_empty_file_reported(tmp_path: Path):
    _write(tmp_path, "empty.zsh", "")
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path])
    issues = auditor.check_sourcing_order(configs)
    assert any("empty.zsh" in i for i in issues)


def test_sourcing_graph_populated(tmp_path: Path):
    _write(tmp_path, "main.zsh", "source ./sub.zsh\n")
    _write(tmp_path, "sub.zsh", "export SUB=1\n")
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path])
    graph = auditor.sourcing_graph(configs)
    assert "main.zsh" in graph


def test_sourcing_graph_no_sources_excluded(tmp_path: Path):
    _write(tmp_path, "nosource.zsh", "export A=1\n")
    auditor = ShellConfigAuditor()
    configs = auditor.audit([tmp_path])
    graph = auditor.sourcing_graph(configs)
    assert "nosource.zsh" not in graph


# ──────────────────────────────────────────────────────────────────────────────
# Integration: audit actual shell/ directory
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def repo_shell_configs() -> list[ShellConfigFile]:
    """Parse the real shell/ directory for integration tests."""
    repo_root = Path(__file__).parent.parent.parent
    shell_dir = repo_root / "shell"
    if not shell_dir.is_dir():
        pytest.skip("shell/ directory not found")
    auditor = ShellConfigAuditor()
    return auditor.audit([shell_dir])


def test_real_shell_dir_finds_files(repo_shell_configs: list[ShellConfigFile]):
    assert len(repo_shell_configs) >= 1


def test_real_shell_dir_has_functions(repo_shell_configs: list[ShellConfigFile]):
    all_funcs = [fn for cfg in repo_shell_configs for fn in cfg.functions]
    assert len(all_funcs) > 0


def test_real_shell_dir_consolidated_is_string(repo_shell_configs: list[ShellConfigFile]):
    auditor = ShellConfigAuditor()
    merged = auditor.generate_consolidated(repo_shell_configs)
    assert isinstance(merged, str)
    assert len(merged) > 0
