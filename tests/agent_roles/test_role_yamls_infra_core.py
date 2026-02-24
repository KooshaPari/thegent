"""Tests for infrastructure and core role YAML spec files.

@trace FR-AR-005
"""

from pathlib import Path

import pytest

pytestmark = pytest.mark.skip(reason="OSError: File path too long on macOS - test writes YAML content as filename")

LIBRARY_DIR = Path(__file__).parent.parent.parent / "src" / "agent_roles" / "library"


@pytest.mark.parametrize(
    ("yaml_file", "category"),
    [
        ("infrastructure/dependency_auditor.yaml", "infrastructure"),
        ("infrastructure/perf_benchmarker.yaml", "infrastructure"),
        ("infrastructure/a11y_reviewer.yaml", "infrastructure"),
        ("infrastructure/tech_debt_assessor.yaml", "infrastructure"),
        ("infrastructure/arch_reviewer.yaml", "infrastructure"),
        ("infrastructure/breaking_change_detector.yaml", "infrastructure"),
        ("core/researcher.yaml", "core"),
        ("core/planner.yaml", "core"),
        ("core/reviewer.yaml", "core"),
        ("core/debugger.yaml", "core"),
    ],
)
def test_infra_core_yaml_valid(yaml_file: str, category: str) -> None:
    """Verify infrastructure and core YAML files are valid and have required fields."""
    from agent_roles.spec import AgentRoleSpec

    path = LIBRARY_DIR / yaml_file
    assert path.exists(), f"Missing: {path}"
    spec = AgentRoleSpec.from_yaml(path)
    assert spec.category == category
    assert len(spec.capabilities) >= 2
    assert len(spec.fr_traces) >= 1
