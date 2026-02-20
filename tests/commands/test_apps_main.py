"""Unit tests for the modular CLI app entrypoints."""

from unittest.mock import patch

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


def test_install_compat_routes_to_run_install() -> None:
    """`thegent install` should remain available in the new app tree."""
    with patch("thegent.install.run_install") as mock_run_install:
        result = runner.invoke(
            app,
            ["install", "--target", "codex", "--mode", "smart", "--dry-run", "--verbose"],
        )

    assert result.exit_code == 0
    mock_run_install.assert_called_once_with(
        target="codex",
        mode="smart",
        dry_run=True,
        verbose=True,
        url=None,
        install_service=False,
    )
