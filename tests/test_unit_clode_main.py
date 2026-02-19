"""Unit tests for clode command wiring and wrapper installation."""

from pathlib import Path
from unittest.mock import patch

import pytest
import typer
from typer.testing import CliRunner

from thegent.clode_main import (
    _GLM_POLICY_COUNTER,
    _resolve_clode_token,
    _run_claude_interactive,
    _write_wrapper,
    app,
)

runner = CliRunner()


def test_resolve_clode_token_valid_policies_and_backends() -> None:
    _GLM_POLICY_COUNTER["glm"] = 0
    assert _resolve_clode_token("glm", "auto", "round_robin") == "nim"
    assert _resolve_clode_token("glm", "kilo", "cheapest") == "kilo"
    assert _resolve_clode_token("glm", "openrouter", "cheapest") == "openrouter"
    assert _resolve_clode_token("glm", "auto", "cheapest") == "nim"


def test_resolve_clode_token_round_robin_cycles() -> None:
    _GLM_POLICY_COUNTER["glm"] = 0
    assert _resolve_clode_token("glm", "auto", "round_robin") == "nim"
    assert _resolve_clode_token("glm", "auto", "round_robin") == "kilo"
    assert _resolve_clode_token("glm", "auto", "round_robin") == "zai"
    assert _resolve_clode_token("glm", "auto", "round_robin") == "minimax"
    assert _resolve_clode_token("glm", "auto", "round_robin") == "glm"


def test_resolve_clode_token_invalid_policy_exits() -> None:
    with pytest.raises(SystemExit):
        _resolve_clode_token("glm", "auto", "bad-policy")


def test_resolve_clode_token_unknown_prefer_falls_back_to_policy() -> None:
    assert _resolve_clode_token("glm", "rocket", "prefer_direct") == "glm:prefer_direct"


def test_install_links_bin_dir_missing_errors(tmp_path: Path) -> None:
    missing = tmp_path / "missing-dir"
    target = missing / "subdir"
    result = runner.invoke(app, ["install-links", "--bin-dir", str(target)])
    assert result.exit_code == 1


def test_install_links_writes_and_skips_without_force(tmp_path: Path) -> None:
    # First write should create all three wrappers.
    result = runner.invoke(app, ["install-links", "--bin-dir", str(tmp_path)])
    assert result.exit_code == 0
    expected = {
        "clode": '#!/usr/bin/env sh\nset -e\nexport THGENT_HARNESS="claude"\nexec thegent clode "$@"\n',
        "claudeglm": '#!/usr/bin/env sh\nset -e\nexport THGENT_HARNESS="claude"\nexec thegent clode glm "$@"\n',
        "claudemax": '#!/usr/bin/env sh\nset -e\nexport THGENT_HARNESS="claude"\nexec thegent clode max "$@"\n',
    }
    for name, expected_contents in expected.items():
        wrapper = tmp_path / name
        assert wrapper.exists()
        assert wrapper.read_text(encoding="utf-8") == expected_contents

    # Without --force, existing files should be preserved.
    prewrite = (tmp_path / "clode").read_text(encoding="utf-8")
    result = runner.invoke(app, ["install-links", "--bin-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "clode").read_text(encoding="utf-8") == prewrite


def test_install_links_force_rewrites_existing(tmp_path: Path) -> None:
    target = tmp_path / "clode"
    target.write_text("legacy", encoding="utf-8")
    target.chmod(0o644)
    (tmp_path / "claudeglm").write_text("legacy", encoding="utf-8")
    (tmp_path / "claudemax").write_text("legacy", encoding="utf-8")

    result = runner.invoke(app, ["install-links", "--bin-dir", str(tmp_path), "--force"])
    assert result.exit_code == 0
    assert (tmp_path / "clode").read_text(encoding="utf-8") != "legacy"
    assert (tmp_path / "claudeglm").read_text(encoding="utf-8") != "legacy"
    assert (tmp_path / "claudemax").read_text(encoding="utf-8") != "legacy"


def test_clode_max_and_glm_aliases_forward_expected_token() -> None:
    with patch("thegent.clode_main._run_claude_interactive") as run_interactive:
        result = runner.invoke(
            app,
            ["max"],
        )
        assert result.exit_code == 0
        run_interactive.assert_called_once_with("openrouter")

    with patch("thegent.clode_main._run_claude_interactive") as run_interactive:
        result = runner.invoke(
            app,
            ["glm", "--policy", "cheapest", "--prefer", "kilo"],
        )
        assert result.exit_code == 0
        run_interactive.assert_called_once_with("kilo")

    with patch("thegent.clode_main._run_claude_interactive") as run_interactive:
        result = runner.invoke(
            app,
            ["glm", "--prefer", "openrouter"],
        )
        assert result.exit_code == 0
        run_interactive.assert_called_once_with("openrouter")


def test_write_wrapper_functionality(tmp_path: Path) -> None:
    target = tmp_path / "shim"
    wrote = _write_wrapper(target, "thegent clode glm", force=False)
    assert wrote is True
    text = target.read_text(encoding="utf-8")
    assert text == '#!/usr/bin/env sh\nset -e\nexport THGENT_HARNESS="claude"\nexec thegent clode glm "$@"\n'
    assert (tmp_path / "shim").exists()

    # Existing file without force remains unchanged
    target.write_text("legacy", encoding="utf-8")
    assert _write_wrapper(target, "thegent clode max", force=False) is False
    assert target.read_text(encoding="utf-8") == "legacy"


def test_clode_provider_default_to_interactive() -> None:
    with patch("thegent.clode_main._run_claude_interactive") as run_interactive:
        result = runner.invoke(app, ["nim"])
        assert result.exit_code == 0
        run_interactive.assert_called_once_with("nim")


def test_clode_root_defaults_to_nim_interactive() -> None:
    with patch("thegent.clode_main._run_claude_interactive") as run_interactive:
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        run_interactive.assert_called_once_with("nim")


def test_clode_run_and_bg_delegate_to_claude_cmd() -> None:
    with patch("thegent.clode_main.run_cmd") as run_cmd:
        result = runner.invoke(app, ["nim", "run", "hello world"])
        assert result.exit_code == 0
        run_cmd.assert_called_once()
        _, kwargs = run_cmd.call_args
        assert kwargs["agent"] == "claude"
        assert kwargs["prompt"] == "hello world"
        assert kwargs["mode"] == "write"
        assert kwargs["timeout"] == 90

    with patch("thegent.clode_main.bg_cmd") as bg_cmd:
        result = runner.invoke(app, ["nim", "bg", "hello world", "--owner", "me"])
        assert result.exit_code == 0
        bg_cmd.assert_called_once()
        _, kwargs = bg_cmd.call_args
        assert kwargs["agent"] == "claude"
        assert kwargs["prompt"] == "hello world"
        assert kwargs["owner"] == "me"


def test_run_claude_interactive_exec_path_and_env_handshake() -> None:
    fake_env = {
        "ANTHROPIC_BASE_URL": "http://127.0.0.1:3847/v1",
        "ANTHROPIC_API_KEY": "openrouter",
    }
    with (
        patch("thegent.clode_main.shutil.which", return_value="/usr/bin/claude"),
        patch("thegent.clode_main._get_claude_env", return_value=fake_env),
        patch("thegent.clode_main.subprocess.run") as run_proc,
    ):
        _run_claude_interactive("openrouter")
        run_proc.assert_called_once()
        args, kwargs = run_proc.call_args
        assert args[0] == ["/usr/bin/claude"]
        assert kwargs["env"]["ANTHROPIC_API_KEY"] == "openrouter"
        assert kwargs["check"] is False


def test_run_claude_interactive_missing_binary_errors() -> None:
    with (
        patch("thegent.clode_main.shutil.which", return_value=None),
        patch("thegent.clode_main.console.print") as console_print,
    ):
        with pytest.raises(typer.Exit):
            _run_claude_interactive("nim")
        console_print.assert_called()
