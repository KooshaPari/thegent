"""Unit tests for the modular CLI app entrypoints."""

import orjson as json
from pathlib import Path
from unittest.mock import ANY, patch

from typer.testing import CliRunner

from thegent.cli.apps.main import app

runner = CliRunner()


def test_top_level_ps_shortcut_routes_to_run_ps() -> None:
    """`thegent ps` should route through the run stream implementation."""
    with patch("thegent.cli.apps.run.run_ps") as mock_run_ps:
        result = runner.invoke(
            app,
            ["ps", "--all", "--owner", "alice", "--format", "json", "--include-contract"],
        )

    assert result.exit_code == 0
    mock_run_ps.assert_called_once_with(
        all_sessions=True,
        owner="alice",
        format="json",
        include_contract=True,
    )


def test_top_level_do_shortcut_routes_to_run_agent() -> None:
    """`thegent do` should route through the run stream implementation."""
    with patch("thegent.cli.apps.run.run_agent") as mock_run_agent:
        result = runner.invoke(app, ["do", "hello"])

    assert result.exit_code == 0
    mock_run_agent.assert_called_once_with(prompt="hello")


def test_git_help_works() -> None:
    """`thegent git --help` should work."""
    result = runner.invoke(app, ["git", "--help"])
    assert result.exit_code == 0
    assert "COMMAND" in result.output
