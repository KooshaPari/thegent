"""Unit tests for anen command wiring and shim-link installation."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.modules.pop("thegent", None)

from thegent.anen_main import GEMINI_FLASH_MODEL, app

runner = CliRunner()


def _mock_completed(returncode: int = 0) -> MagicMock:
    proc = MagicMock()
    proc.returncode = returncode
    return proc


@patch("thegent.anen_main._resolve_anen_cmd", return_value="anen")
@patch("thegent.anen_main.subprocess.run")
def test_default_anen_uses_flash_model(mock_run: MagicMock, _mock_resolve: MagicMock) -> None:
    mock_run.return_value = _mock_completed(0)

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    mock_run.assert_called_once_with(["anen", "--model", GEMINI_FLASH_MODEL], check=False)


@patch("thegent.anen_main._resolve_anen_cmd", return_value="anen")
@patch("thegent.anen_main.subprocess.run")
def test_anen_max_exec_sets_headless_model_flag(mock_run: MagicMock, _mock_resolve: MagicMock) -> None:
    mock_run.return_value = _mock_completed(0)

    result = runner.invoke(app, ["exec", "-m", "max", "hello world"])

    assert result.exit_code == 0
    mock_run.assert_called_once_with(["anen", "exec", "-m", "MiniMax-M2.5", "hello world"], check=False)


def test_install_links_writes_anen_wrappers(tmp_path: Path) -> None:
    shims_bin = tmp_path / "thegent-shims"
    shims_bin.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    shims_bin.chmod(0o755)

    with patch("thegent.anen_main.shutil.which", return_value=None):
        result = runner.invoke(app, ["install-links", "--bin-dir", str(tmp_path)])

    assert result.exit_code == 0

    antigma = tmp_path / "antigma"
    fanta = tmp_path / "fanta"
    assert antigma.is_symlink()
    assert fanta.is_symlink()
    assert antigma.resolve() == shims_bin.resolve()
    assert fanta.resolve() == shims_bin.resolve()


def test_resolve_anen_cmd_skips_thegent_wrapper(tmp_path: Path, monkeypatch) -> None:
    wrapper = tmp_path / "ante-wrapper"
    wrapper.write_text("#!/usr/bin/env sh\nexec thegent anen \"$@\"\n", encoding="utf-8")
    wrapper.chmod(0o755)

    native = tmp_path / "ante-native"
    native.write_text("#!/usr/bin/env sh\necho ok\n", encoding="utf-8")
    native.chmod(0o755)

    monkeypatch.delenv("THGENT_NATIVE_ANEN_BIN", raising=False)
    monkeypatch.delenv("THGENT_NATIVE_ANTE_BIN", raising=False)

    def _which(name: str) -> str:
        if name == "ante":
            return str(wrapper)
        return ""

    monkeypatch.setattr("shutil.which", _which)
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    monkeypatch.setattr(sys, "argv", [str(wrapper)])
    monkeypatch.setattr(os, "access", lambda *_: True)
    (tmp_path / ".ante" / "bin").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".ante" / "bin" / "ante").symlink_to(native)

    from thegent.anen_main import _resolve_anen_cmd

    assert Path(_resolve_anen_cmd()).resolve() == native.resolve()
