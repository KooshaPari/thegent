"""Agent roles CLI tests — TDD."""
# @trace FR-AR-006
from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner


def test_render_all_produces_md_files(tmp_path: Path) -> None:
    """Test that render-all command produces 20+ markdown files."""
    from agent_roles.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["render-all", "--agents-dir", str(tmp_path), "--no-register"])
    assert result.exit_code == 0, result.output
    md_files = list(tmp_path.glob("*.md"))
    assert len(md_files) >= 20


def test_list_command() -> None:
    """Test that list command shows all available roles."""
    from agent_roles.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "property_tester" in result.output


def test_render_single(tmp_path: Path) -> None:
    """Test that render command creates a single role markdown."""
    from agent_roles.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["render", "property_tester", "--agents-dir", str(tmp_path), "--no-register"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "property_tester.md").exists()


def test_render_nonexistent_role(tmp_path: Path) -> None:
    """Test that render fails with clear error for nonexistent role."""
    from agent_roles.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["render", "nonexistent_role", "--agents-dir", str(tmp_path), "--no-register"])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()
