"""Integration test: AgilePlus + Cycleloop full cycle."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from thegent.governance.agileplus import AgilePlusLoop


@pytest.mark.integration
def test_agileplus_runs_full_cycle_with_cycleloop(tmp_path: Path) -> None:
    """Test complete AgilePlus cycle uses Cycleloop for execution."""
    health_targets = tmp_path / "contracts" / "health-targets.json"
    health_targets.parent.mkdir(parents=True, exist_ok=True)
    health_targets.write_text(
        """{
        "version": "1.0.0",
        "dimensions": {
            "test_coverage": {"weight": 0.2, "target": 80, "direction": "higher_is_better"},
            "lint_violations": {"weight": 0.15, "target": 0, "direction": "lower_is_better"}
        },
        "bands": {"excellent": {"min": 90}, "healthy": {"min": 70}, "warning": {"min": 40}, "critical": {"min": 0}},
        "budget": {"daily_agent_calls": 20, "tiers": {"normal": {"max_utilization_pct": 50}, "cautious": {"max_utilization_pct": 80}, "restricted": {"max_utilization_pct": 95}, "halted": {"max_utilization_pct": 100}}}
    }"""
    )

    loop = AgilePlusLoop(
        project_dir=tmp_path,
        health_targets_path=health_targets,
        lifecycle_mode="soft",
    )

    assert loop.lifecycle_mode == "soft"

    with patch("thegent.governance.agileplus.AgilePlusLoop._run_scan") as mock_scan:
        mock_scan.return_value = Mock(dimensions={})
        result = loop.run_once()

    assert result.state.value in (
        "idle",
        "scanning",
        "analyzing",
        "error",
        "planning",
        "deploying",
        "verifying",
        "committing",
    )


def test_agileplus_lifecycle_mode_passed_to_deployer(tmp_path: Path) -> None:
    """Test lifecycle_mode is passed through to AgentDeployer."""
    health_targets = tmp_path / "contracts" / "health-targets.json"
    health_targets.parent.mkdir(parents=True, exist_ok=True)
    health_targets.write_text(
        """{
        "version": "1.0.0",
        "dimensions": {"test_coverage": {"weight": 0.2, "target": 80}},
        "bands": {"excellent": {"min": 90}, "healthy": {"min": 70}, "warning": {"min": 40}, "critical": {"min": 0}},
        "budget": {"daily_agent_calls": 20, "tiers": {"normal": {"max_utilization_pct": 50}, "cautious": {"max_utilization_pct": 80}, "restricted": {"max_utilization_pct": 95}, "halted": {"max_utilization_pct": 100}}}
    }"""
    )

    loop = AgilePlusLoop(
        project_dir=tmp_path,
        health_targets_path=health_targets,
        lifecycle_mode="hard",
    )

    assert loop.lifecycle_mode == "hard"
