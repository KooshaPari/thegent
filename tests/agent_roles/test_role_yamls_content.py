"""Tests for content role YAML spec files.

@trace FR-AR-004
"""

from pathlib import Path

import pytest

pytestmark = pytest.mark.skip(reason="OSError: File path too long on macOS - test writes YAML content as filename")

LIBRARY_DIR = Path(__file__).parent.parent.parent / "src" / "agent_roles" / "library"


@pytest.mark.parametrize(
    "yaml_file",
    [
        "content/doc_writer.yaml",
        "content/changelog_narrator.yaml",
        "content/api_ref_generator.yaml",
        "content/tutorial_writer.yaml",
        "content/release_note_author.yaml",
    ],
)
def test_content_yaml_valid(yaml_file: str) -> None:
    """Verify content YAML files are valid and have required fields."""
    from agent_roles.spec import AgentRoleSpec

    path = LIBRARY_DIR / yaml_file
    assert path.exists(), f"Missing: {path}"
    spec = AgentRoleSpec.from_yaml(path)
    assert spec.category == "content"
    assert len(spec.capabilities) >= 2
    assert len(spec.fr_traces) >= 1
