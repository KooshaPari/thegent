"""Unit tests for roid command wiring and shim-link installation."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.modules.pop("thegent", None)

from thegent.roid_main import GEMINI_FLASH_MODEL, app

runner = CliRunner()


def _mock_completed(returncode: int = 0) -> MagicMock:
    proc = MagicMock()
    proc.returncode = returncode
    return proc


@patch("thegent.roid_main._resolve_droid_cmd", return_value="droid")
@patch("thegent.roid_main.subprocess.run")
def test_default_roid_uses_flash_model(mock_run: MagicMock, _mock_resolve: MagicMock) -> None:
    mock_run.return_value = _mock_completed(0)

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    mock_run.assert_called_once_with(["droid", "--model", GEMINI_FLASH_MODEL], check=False)


@patch("thegent.roid_main._resolve_droid_cmd", return_value="droid")
@patch("thegent.roid_main.subprocess.run")
def test_roid_flash_uses_flash_model(mock_run: MagicMock, _mock_resolve: MagicMock) -> None:
    mock_run.return_value = _mock_completed(0)

    result = runner.invoke(app, ["flash"])

    assert result.exit_code == 0
    mock_run.assert_called_once_with(["droid", "--model", GEMINI_FLASH_MODEL], check=False)


@patch("thegent.roid_main._resolve_droid_cmd", return_value="droid")
@patch("thegent.roid_main.subprocess.run")
def test_roid_mini_uses_gpt5_mini(mock_run: MagicMock, _mock_resolve: MagicMock) -> None:
    mock_run.return_value = _mock_completed(0)

    result = runner.invoke(app, ["mini"])

    assert result.exit_code == 0
    mock_run.assert_called_once_with(["droid", "--model", "gpt-5-mini"], check=False)


def test_install_links_writes_roid_wrappers(tmp_path: Path) -> None:
    shims_bin = tmp_path / "thegent-shims"
    shims_bin.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    shims_bin.chmod(0o755)

    with patch("thegent.roid_main.shutil.which", return_value=None):
        result = runner.invoke(app, ["install-links", "--bin-dir", str(tmp_path)])

    assert result.exit_code == 0

    roid = tmp_path / "roid"
    assert roid.is_symlink()
    assert roid.resolve() == shims_bin.resolve()
