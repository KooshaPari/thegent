"""Accessibility smoke checks for CLI help surfaces."""

import pytest
from typer.testing import CliRunner

from thegent.main import app

# For a11y smoke checks we want to verify the *plain-text* contract of
# the help surface, so force Click/Typer to emit ANSI-free output.
# Click 8.x reads NO_COLOR / FORCE_COLOR / TERM via the per-invocation
# env passed to CliRunner (TERM=dumb + FORCE_COLOR=0 disables color
# even on Click versions that ignore NO_COLOR alone).
runner = CliRunner(env={"NO_COLOR": "1", "TERM": "dumb", "FORCE_COLOR": "0"})
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
