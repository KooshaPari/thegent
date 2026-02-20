"""Unit tests for dex command wiring and shim-link installation."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from thegent.dex_main import (
    _DEX_BYPASS_FLAG,
    _MODEL_ALIAS,
    _resolve_provider_for_model,
    app,
)

runner = CliRunner()


def test_model_alias_mapping() -> None:
    """Model aliases map to canonical IDs."""
    assert _MODEL_ALIAS["composer"] == "composer-1.5"
    assert _MODEL_ALIAS["max"] == "minimax-m2.5"
    assert _MODEL_ALIAS["glm"] == "glm-5"
    assert _MODEL_ALIAS["haiku"] == "claude-haiku-4.5"
    assert _MODEL_ALIAS["opus"] == "claude-opus-4.6"
    assert _MODEL_ALIAS["sonnet"] == "claude-sonnet-4.5"
    assert _MODEL_ALIAS["step"] == "step-3.5-flash"
    assert _MODEL_ALIAS["mini"] == "gpt-5-mini"


def test_resolve_provider_composer_uses_cursor() -> None:
    """Composer 1.5 routes to cursor."""
    assert _resolve_provider_for_model("composer") == "cursor"


def test_resolve_provider_glm_round_robins() -> None:
    """GLM-5 round-robins across nim, kilo, minimax, glm."""
    providers_seen = set()
    for _ in range(8):
        p = _resolve_provider_for_model("glm")
        providers_seen.add(p)
    assert providers_seen.issubset({"nim", "kilo", "minimax", "glm"})


def test_resolve_provider_haiku_uses_claude_set() -> None:
    """Claude Haiku round-robins across claude, antigravity."""
    providers_seen = set()
    for _ in range(4):
        p = _resolve_provider_for_model("haiku")
        providers_seen.add(p)
    assert providers_seen.issubset({"claude", "antigravity"})


def test_resolve_provider_step_uses_nim() -> None:
    """Step 3.5 routes to nim."""
    assert _resolve_provider_for_model("step") == "nim"


def test_resolve_provider_mini_uses_copilot() -> None:
    """GPT-5-mini routes to copilot."""
    assert _resolve_provider_for_model("mini") == "copilot"


def test_resolve_provider_max_round_robins() -> None:
    """M2.5 (max) round-robins across nim, kilo, minimax."""
    providers_seen = set()
    for _ in range(8):
        p = _resolve_provider_for_model("max")
        providers_seen.add(p)
    assert "nim" in providers_seen or "kilo" in providers_seen or "minimax" in providers_seen


def test_dex_uses_bypass_flag() -> None:
    """Dex uses --dangerously-bypass-approvals-and-sandbox, not --dangerously-skip-permissions."""
    assert _DEX_BYPASS_FLAG == "--dangerously-bypass-approvals-and-sandbox"
    assert "skip-permissions" not in _DEX_BYPASS_FLAG


def test_install_links_bin_dir_missing_errors(tmp_path: Path) -> None:
    missing = tmp_path / "missing-dir"
    target = missing / "subdir"
    result = runner.invoke(app, ["install-links", "--bin-dir", str(target)])
    assert result.exit_code == 1


def test_install_links_writes_model_shims(tmp_path: Path) -> None:
    """Install creates dex -> thegent-shims symlink."""
    shims_bin = tmp_path / "thegent-shims"
    shims_bin.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    shims_bin.chmod(0o755)

    with patch("thegent.dex_main.shutil.which", return_value=None):
        result = runner.invoke(app, ["install-links", "--bin-dir", str(tmp_path)])
    assert result.exit_code == 0
    wrapper = tmp_path / "dex"
    assert wrapper.is_symlink(), "dex should be a symlink"
    assert wrapper.resolve() == shims_bin.resolve()


def test_dex_composer_uses_composer_model() -> None:
    """dex composer uses composer-1.5 (Cursor), not max."""
    with patch("thegent.dex_main._run_codex_interactive") as run_interactive:
        result = runner.invoke(app, ["composer"])
        assert result.exit_code == 0
        run_interactive.assert_called_once_with(
            "composer",
            extra_args=[],
            dangerously_bypass=True,
        )


def test_dex_max_forwards_bypass_flag() -> None:
    with patch("thegent.dex_main._run_codex_interactive") as run_interactive:
        result = runner.invoke(app, ["max"])
        assert result.exit_code == 0
        run_interactive.assert_called_once_with(
            "max",
            extra_args=[],
            dangerously_bypass=True,
        )


def test_dex_glm_uses_glm_model() -> None:
    with patch("thegent.dex_main._run_codex_interactive") as run_interactive:
        result = runner.invoke(app, ["glm"])
        assert result.exit_code == 0
        run_interactive.assert_called_once_with(
            "glm",
            extra_args=[],
            dangerously_bypass=True,
        )


def test_dex_haiku_uses_haiku_model() -> None:
    with patch("thegent.dex_main._run_codex_interactive") as run_interactive:
        result = runner.invoke(app, ["haiku"])
        assert result.exit_code == 0
        run_interactive.assert_called_once_with(
            "haiku",
            extra_args=[],
            dangerously_bypass=True,
        )


def test_dex_opus_uses_opus_model() -> None:
    with patch("thegent.dex_main._run_codex_interactive") as run_interactive:
        result = runner.invoke(app, ["opus"])
        assert result.exit_code == 0
        run_interactive.assert_called_once_with(
            "opus",
            extra_args=[],
            dangerously_bypass=True,
        )


def test_dex_sonnet_uses_sonnet_model() -> None:
    with patch("thegent.dex_main._run_codex_interactive") as run_interactive:
        result = runner.invoke(app, ["sonnet"])
        assert result.exit_code == 0
        run_interactive.assert_called_once_with(
            "sonnet",
            extra_args=[],
            dangerously_bypass=True,
        )


def test_dex_ultra_uses_ultra_model() -> None:
    """dex ultra uses Llama Nemotron Ultra via NIM."""
    with patch("thegent.dex_main._run_codex_interactive") as run_interactive:
        result = runner.invoke(app, ["ultra"])
        assert result.exit_code == 0
        run_interactive.assert_called_once_with(
            "ultra",
            extra_args=[],
            dangerously_bypass=True,
        )


def test_dex_run_accepts_mini_model() -> None:
    """dex run mini <prompt> uses gpt-5-mini via copilot."""
    with patch("thegent.dex_main._run_model_cmd") as run_cmd:
        result = runner.invoke(app, ["run", "mini", "hello"])
        assert result.exit_code == 0
        run_cmd.assert_called_once()
        assert run_cmd.call_args[0][0] == "mini"


def test_dex_run_rejects_unknown_model() -> None:
    result = runner.invoke(app, ["run", "unknown", "prompt"])
    assert result.exit_code == 1
    assert "Unknown model" in result.output
