"""
E2E test for: thegent sync research

Agent Journey: Agent executes thegent sync research command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestResearchDeep:
    """E2E tests for thegent sync research command."""

    def test_research_deep_exits_zero(self) -> None:
        """thegent sync research exits with code 0."""
        result = runner.invoke(app, ["research", "deep"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_research_deep_produces_output(self) -> None:
        """thegent sync research produces expected output."""
        result = runner.invoke(app, ["research", "deep"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_research_deep_help_exits_zero(self) -> None:
        """thegent sync research --help exits with code 0."""
        result = runner.invoke(app, ["research", "deep", "--help"])
        assert result.exit_code == 0
