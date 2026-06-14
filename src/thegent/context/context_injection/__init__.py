"""Context rendering and tool context setup helpers."""

from pathlib import Path
from typing import Any


class ContextInjector:
    """Injector for context into operations."""

    def __init__(self, project_root: str | Path | None = None) -> None:
        self.project_root = Path(project_root) if project_root is not None else Path.cwd()
        self.context: dict[str, Any] = {}

    def inject(self, key: str, value: Any) -> None:
        """Inject context value."""
        self.context[key] = value

    def get(self, key: str) -> Any | None:
        """Get context value."""
        return self.context.get(key)

    def render_agent_md(self, agent: dict[str, Any], mesh: dict[str, Any]) -> str:
        """Render an agent context document from agent and mesh metadata."""
        resources = mesh.get("resources", [])
        resource_text = ", ".join(str(resource) for resource in resources) or "none"
        agents = mesh.get("agents", [])
        port_range = str(mesh.get("port_range", "unassigned"))

        return "\n".join(
            [
                "# AGENT IDENTITY",
                f"ID: {agent.get('id', 'unknown')}",
                f"Type: {agent.get('type', 'unknown')}",
                "",
                "# MESH STATUS",
                f"Status: {mesh.get('status', 'unknown')}",
                f"Active Agents: {len(agents)}",
                f"Shared Resources: {resource_text}",
                f"Use shared port range: {port_range}",
                "",
            ]
        )

    def setup_tool_context(self, agent_dir: str | Path, tool: str) -> Path:
        """Point a tool-specific context file at the canonical AGENT.md."""
        agent_path = Path(agent_dir)
        source = agent_path / "AGENT.md"
        if not source.exists():
            msg = f"Missing required context source file: {source}"
            raise FileNotFoundError(msg)

        target = agent_path / self._tool_context_filename(tool)
        if target.exists() or target.is_symlink():
            target.unlink()
        target.symlink_to(Path("AGENT.md"))
        return target

    @staticmethod
    def _tool_context_filename(tool: str) -> str:
        if tool.lower() == "claude":
            return "CLAUDE.md"
        return f"{tool.upper()}.md"


__all__ = ["ContextInjector"]
