"""Unit tests for install-shims parity and roid registration in main CLI."""

from __future__ import annotations

from typing import TYPE_CHECKING

from typer.testing import CliRunner

from thegent.main import _install_agent_accelerators, app

if TYPE_CHECKING:
    from pathlib import Path

runner = CliRunner()


def test_install_agent_accelerators_writes_roid_and_codex_shims(tmp_path: Path) -> None:
    _install_agent_accelerators(tmp_path, force=True)

    codex = tmp_path / "codex"
    roid = tmp_path / "roid"
    dex = tmp_path / "dex"
    clode = tmp_path / "clode"

    assert codex.exists()
    assert roid.exists()
    assert dex.exists()
    assert clode.exists()

    codex_script = codex.read_text(encoding="utf-8")
    # Allow either bash routing or Rust shim
    assert ("dex|clode" in codex_script or "Rust shim" in codex_script)
    
    # Check other shims exist and have reasonable content
    for shim, harness, cmd in [
        (roid, "droid", "roid"),
        (dex, "codex", "dex"),
        (clode, "claude", "clode"),
    ]:
        content = shim.read_text(encoding="utf-8")
        if "Rust shim" in content:
            assert f'exec' in content
            assert harness in content or cmd in content
        else:
            assert f'export THGENT_HARNESS="{harness}"' in content
            assert f'exec thegent {cmd} "$@"' in content


def test_main_registers_roid_typer() -> None:
    result = runner.invoke(app, ["roid", "--help"])
    assert result.exit_code == 0
    assert "Factory Droid-backed interactive harness" in result.output
