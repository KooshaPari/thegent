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
    assert "dex|clode" in codex_script
    assert 'exec thegent "$HARNESS" "$@"' in codex_script

    assert roid.read_text(encoding="utf-8") == (
        '#!/usr/bin/env sh\nset -e\nexport THGENT_HARNESS="droid"\nexec thegent roid "$@"\n'
    )
    assert dex.read_text(encoding="utf-8") == (
        '#!/usr/bin/env sh\nset -e\nexport THGENT_HARNESS="codex"\nexec thegent dex "$@"\n'
    )
    assert clode.read_text(encoding="utf-8") == (
        '#!/usr/bin/env sh\nset -e\nexport THGENT_HARNESS="claude"\nexec thegent clode "$@"\n'
    )


def test_main_registers_roid_typer() -> None:
    result = runner.invoke(app, ["roid", "--help"])
    assert result.exit_code == 0
    assert "Factory Droid-backed interactive harness" in result.output
