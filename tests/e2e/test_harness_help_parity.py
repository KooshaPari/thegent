"""E2E harness help parity checks for dex/roid/fanta surfaces."""

from __future__ import annotations

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner
from thegent.dex_main import app as dex_app
from thegent.fanta_main import app as fanta_app
from thegent.roid_main import app as roid_app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_dex_max_help_exposes_resume_and_continue_flags() -> None:
    result = runner.invoke(dex_app, ["max", "--help"])
    assert result.exit_code == 0
    assert "--resume" in result.stdout
    assert "--continue" in result.stdout


@pytest.mark.e2e
def test_roid_help_exits_zero() -> None:
    result = runner.invoke(roid_app, ["--help"])
    assert result.exit_code == 0
    assert "Factory Droid-backed interactive harness" in result.stdout


@pytest.mark.e2e
def test_fanta_help_exits_zero() -> None:
    result = runner.invoke(fanta_app, ["--help"])
    assert result.exit_code == 0
    assert "Antigma-backed interactive harness" in result.stdout
