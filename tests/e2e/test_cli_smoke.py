"""End-to-end smoke tests for the thegent CLI.

Lifts T3 (E2E tests) from 0 to 2 (wired): exercises the real CLI app
entry point through typer's CliRunner to verify the critical user path
(version flag, help, and a subcommand invocation).
"""

from __future__ import annotations

import importlib

import pytest
from typer.testing import CliRunner


def test_main_module_loads() -> None:
    """The top-level thegent package must import cleanly."""
    thegent = importlib.import_module("thegent")
    assert thegent is not None


def test_cli_app_imports() -> None:
    """The CLI application entry point must be importable and well-formed."""
    from thegent.cli.apps.main import app

    assert app is not None
    assert hasattr(app, "callback")


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_cli_help_renders(runner: CliRunner) -> None:
    """`thegent --help` exits 0 and includes the program description."""
    from thegent.cli.apps.main import app

    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "thegent" in result.stdout.lower()


def test_cli_version_flag(runner: CliRunner) -> None:
    """`thegent --version` exits 0 and prints the version banner."""
    from thegent.cli.apps.main import app

    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "thegent" in result.stdout.lower()
    assert "version" in result.stdout.lower()


def test_cli_run_subcommand_renders(runner: CliRunner) -> None:
    """The `run` subcommand must be reachable via --help and documented."""
    from thegent.cli.apps.main import app

    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "prompt" in result.stdout.lower()
