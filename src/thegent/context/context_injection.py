"""Phase 14: Context Injection implementation.
Includes AGENT.md template system, tool-specific context symlinks, and dynamic updates.
"""

import logging
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)


class ContextInjector:
    """Manages injection of context into agents."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def render_agent_md(self, agent_info: dict[str, Any], mesh_state: dict[str, Any]) -> str:
        """Render AGENT.md from template with current mesh state."""
        resources = mesh_state.get("resources", [])
        if not isinstance(resources, list):
            resources = [str(resources)]
        shared_resources = ", ".join(resources) if resources else "none"

        template = """# AGENT IDENTITY
ID: {id}
Type: {type}

# MESH STATE
Status: {status}
Active Agents: {agent_count}
Shared Resources: {shared_resources}

# COORDINATION RULES
1. Always claim file leases before writing.
2. Signal intent for long-running operations.
3. Use shared port range: {port_range}
"""
        return template.format(
            id=agent_info.get("id"),
            type=agent_info.get("type"),
            status=mesh_state.get("status"),
            agent_count=len(mesh_state.get("agents", [])),
            shared_resources=shared_resources,
            port_range=mesh_state.get("port_range", "N/A"),
        )

    def setup_tool_context(self, agent_dir: Path, agent_type: str) -> None:
        """Set up tool-specific context files (symlinks)."""
        rules_map = {
            "claude": ("CLAUDE.md", "AGENT.md"),
            "cursor": (".cursorrules", "AGENT.md"),
            "cline": (".clinerules", "AGENT.md"),
            "aider": (".aider.conf.yml", "AGENT.md"),
        }

        if agent_type in rules_map:
            target_name, source_name = rules_map[agent_type]
            source_path = agent_dir / source_name
            target_path = agent_dir / target_name

            if not source_path.exists():
                raise FileNotFoundError(f"Missing required context source file: {source_path}")

            if target_path.exists() or target_path.is_symlink():
                if target_path.is_symlink() and target_path.readlink() == Path(source_name):
                    return
                target_path.unlink()

            target_path.symlink_to(source_name)
            logger.info(f"Created context symlink for {agent_type}: {target_name} -> {source_name}")

    def update_context(self, agent_id: str, agent_dir: Path, mesh_state: dict[str, Any]) -> None:
        """Dynamically update AGENT.md when mesh state changes."""
        agent_md = agent_dir / "AGENT.md"
        # We need agent_info, would normally fetch from registry
        agent_info = {"id": agent_id, "type": "unknown"}
        content = self.render_agent_md(agent_info, mesh_state)
        agent_md.write_text(content)
        logger.info(f"Updated context for agent {agent_id}")
