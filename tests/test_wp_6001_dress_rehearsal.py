"""WP-6001: End-to-End Dress Rehearsal test suite."""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
def test_dress_rehearsal_flow():
    """Verify core orchestration flow from run to benchmark."""
    # 1. List agents
    res = runner.invoke(app, ["list-agents"])
    assert res.exit_code == 0

    # 2. Resolve route
    # Note: 'resolve-model-route' was not found, using 'inspect' which provides similar info
    res = runner.invoke(app, ["orchestrate", "inspect", "claude-haiku-4.5"])
    assert res.exit_code == 0

    # 3. Check cockpit
    res = runner.invoke(app, ["observe", "cockpit"])
    assert res.exit_code == 0

    # 4. Check benchmark
    res = runner.invoke(app, ["observe", "benchmark"])
    assert res.exit_code == 0

    # 5. Check policy
    res = runner.invoke(app, ["policy", "show"])
    assert res.exit_code == 0
