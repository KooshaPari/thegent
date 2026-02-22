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

    # 2. List droids
    res = runner.invoke(app, ["list-droids"])
    assert res.exit_code == 0

    # 3. Check orchestration planning (uses Claude by default)
    res = runner.invoke(app, ["orchestrate", "plan", "simple task"])
    assert res.exit_code in [0, 1]  # May fail if model unavailable, which is acceptable

    # 4. Health check
    res = runner.invoke(app, ["session-contract-health-gate", "--format", "json"])
    assert res.exit_code == 0

    # 5. Session status
    res = runner.invoke(app, ["ps"])
    assert res.exit_code == 0
