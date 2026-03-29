"""Accessibility smoke checks for CLI help surfaces."""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()
pytestmark = pytest.mark.a11y


def test_top_level_help_has_usage_and_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    text = result.stdout.lower()
    assert "usage" in text
    assert "commands" in text or "command" in text


def test_help_output_has_no_ansi_escape_noise() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "\x1b[" not in result.stdout
