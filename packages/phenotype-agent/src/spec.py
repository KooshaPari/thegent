"""AgentRoleSpec Pydantic model — canonical definition of an agent role."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from thegent.infra.fast_yaml_parser import yaml_load
from pydantic import BaseModel

Category = Literal["testers", "content", "infrastructure", "core"]


class AgentRoleSpec(BaseModel):
    """Specification for an agent role with metadata and capabilities."""

    name: str
    display_name: str
    category: Category
    trigger: str
    description: str
    capabilities: list[str]
    constraints: list[str]
    tools_allowed: list[str]
    output_format: str
    fr_traces: list[str]

    @classmethod
    def from_yaml(cls, path: Path) -> AgentRoleSpec:
        """Load AgentRoleSpec from a YAML file.

        Args:
            path: Path to YAML file

        Returns:
            Parsed AgentRoleSpec instance

        Raises:
            FileNotFoundError: If YAML file does not exist
            yaml.YAMLError: If YAML is invalid
            ValueError: If required fields are missing or invalid
        """
        data = yaml_load(Path(path).read_text())
        return cls(**data)
