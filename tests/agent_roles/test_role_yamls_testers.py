"""Tests for tester role YAML spec files.

@trace FR-AR-003
"""

from pathlib import Path

import pytest

LIBRARY_DIR = Path(__file__).parent.parent.parent / "src" / "agent_roles" / "library"


@pytest.mark.parametrize(
    "yaml_file",
    [
        "testers/property_tester.yaml",
        "testers/mutation_tester.yaml",
        "testers/bdd_tester.yaml",
        "testers/contract_tester.yaml",
        "testers/security_fuzzer.yaml",
    ],
)
def test_tester_yaml_valid(yaml_file: str) -> None:
    """Verify tester YAML files are valid and have required fields."""
    from agent_roles.spec import AgentRoleSpec

    path = LIBRARY_DIR / yaml_file
    assert path.exists(), f"Missing: {path}"
    spec = AgentRoleSpec.from_yaml(path)
    assert spec.category == "testers"
    assert len(spec.capabilities) >= 2
    assert len(spec.fr_traces) >= 1
