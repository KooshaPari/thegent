"""Unit tests for fanta first-class CLI entrypoint."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from thegent.fanta_main import app

runner = CliRunner()


def test_fanta_help_mentions_fanta_harness() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Antigma-backed interactive harness (fanta)." in result.output


def test_fanta_install_links_writes_symlinks(tmp_path: Path) -> None:
    shims_bin = tmp_path / "thegent-shims"
    shims_bin.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    shims_bin.chmod(0o755)

    with patch("thegent.anen_main.shutil.which", return_value=None):
        result = runner.invoke(app, ["install-links", "--bin-dir", str(tmp_path)])
    assert result.exit_code == 0

    fanta = tmp_path / "fanta"
    antigma = tmp_path / "antigma"
    assert fanta.is_symlink()
    assert antigma.is_symlink()
    assert fanta.resolve() == shims_bin.resolve()
    assert antigma.resolve() == shims_bin.resolve()
