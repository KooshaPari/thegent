"""HookRegistrar — writes AgentRoleSpec entries into hook-config.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from thegent.infra.fast_yaml_parser import yaml_load, yaml_dump

if TYPE_CHECKING:
    from agent_roles.spec import AgentRoleSpec


class HookRegistrar:
    """Registers agent role specs into hook-config.yaml with idempotent updates."""

    def __init__(self, hook_config_path: Path) -> None:
        """Initialize HookRegistrar with path to hook-config.yaml.

        Args:
            hook_config_path: Path to hook-config.yaml file.
        """
        self._path = Path(hook_config_path)

    def register(self, spec: AgentRoleSpec) -> None:
        """Register an agent role spec into hook-config.yaml.

        Idempotent: registering the same spec multiple times creates only one entry.

        Args:
            spec: The AgentRoleSpec to register.

        Raises:
            FileNotFoundError: If hook-config.yaml does not exist.
            yaml.YAMLError: If YAML is invalid.
        """
        data = yaml_load(self._path) or {}
        hooks: list[dict] = data.get("hooks", [])

        # Remove existing entry for this name (idempotent)
        hooks = [h for h in hooks if h.get("name") != spec.name]

        # Add new entry
        hooks.append(
            {
                "name": spec.name,
                "event": spec.trigger,
                "script": f"hooks/role-{spec.name}.sh",
                "category": spec.category,
                "fr_traces": spec.fr_traces,
            }
        )

        data["hooks"] = hooks
        rendered = yaml_dump(data)
        self._path.write_text(rendered or "")
