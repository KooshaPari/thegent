"""Wave 79 CLI surface tests for update aliases and Pareto panel."""

from __future__ import annotations

from typer.testing import CliRunner

from thegent.cli.apps.project import update_app
from thegent.cli.apps.routing import app as routing_app

runner = CliRunner()


def test_update_help_exits_zero() -> None:
    result = runner.invoke(update_app, ["--help"])
    assert result.exit_code == 0
    assert "Update user/system assets" in result.output


def test_update_project_help_exits_zero() -> None:
    result = runner.invoke(update_app, ["project", "--help"])
    assert result.exit_code == 0
    assert "Update Thegent runtime assets" in result.output


def test_update_project_brownfield_variants_help_exit_zero() -> None:
    for subcmd in ("brownfield", "ag-dd", "none"):
        result = runner.invoke(update_app, ["project", subcmd, "--help"])
        assert result.exit_code == 0
        assert subcmd in result.output


def test_routing_pareto_panel_help_exits_zero() -> None:
    result = runner.invoke(routing_app, ["pareto-panel", "--help"])
    assert result.exit_code == 0
    assert "pareto-panel" in result.output
