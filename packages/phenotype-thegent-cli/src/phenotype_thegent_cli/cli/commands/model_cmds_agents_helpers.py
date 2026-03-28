"""Helpers for model_cmds agent and droid presentation."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from rich.table import Table

_AGENT_BACKENDS: dict[str, str] = {
    "gemini": "cliproxy",
    "headless_agent": "cliproxy",
    "interactive_agent": "cliproxy",
    "copilot": "cliproxy",
    "antigravity": "cliproxy",
    "minimax": "cliproxy",
    "glm": "cliproxy",
    "kilo": "cliproxy",
    "kiro": "cliproxy",
    "nim": "cliproxy",
    "cliproxy": "cliproxy",
    "cursor": "cliproxy",
}


def render_agents_table(
    agents: list[str],
    *,
    resolve_agent: Callable[[str], str],
    console: Any,
) -> None:
    """Render available agents with backend labels."""
    table = Table(title="Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Backend", style="dim")

    from phenotype_thegent_agents.agents.registry import AGENT_LABELS

    for name in agents:
        display_name = AGENT_LABELS.get(name, name)
        canonical = resolve_agent(name)
        table.add_row(display_name, _AGENT_BACKENDS.get(canonical, "Direct"))

    console.print(table)


def render_droids_table(droids: list[str], *, console: Any) -> None:
    """Render available droids."""
    table = Table(title="Droids")
    table.add_column("Name", style="cyan")
    for name in sorted(droids):
        table.add_row(name)
    console.print(table)
