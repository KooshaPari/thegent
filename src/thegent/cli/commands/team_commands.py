"""Team command group extracted from cli.py (WL-124)."""

from __future__ import annotations

import orjson as json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from rich.console import Group
from rich.json import JSON
from rich.table import Table


def team_create_cmd(*, name: str, leader: str | None = None, teammates: str | None = None, console: Any) -> None:
    """WP-6008: Create a new multi-agent team."""
    from thegent.config import ThegentSettings
    from thegent.team.manager import TeamManager

    settings = ThegentSettings()
    mgr = TeamManager(settings.session_dir)
    teammate_list = [t.strip() for t in teammates.split(",")] if teammates else []
    team_id = mgr.create_team(name, leader or "claude", teammate_list)

    console.print(f"Team created: [bold green]{name}[/bold green] (ID: [cyan]{team_id}[/cyan])")
    console.print(f"Leader: [yellow]{leader or 'claude'}[/yellow]")
    if teammate_list:
        console.print(f"Teammates: {', '.join(teammate_list)}")


def team_task_add_cmd(*, team_id: str, title: str, description: str, console: Any) -> None:
    """WP-6008: Add a task to a team's backlog."""
    from thegent.config import ThegentSettings
    from thegent.team.manager import TeamManager

    settings = ThegentSettings()
    mgr = TeamManager(settings.session_dir)
    task_id = mgr.add_task(team_id, title, description)

    console.print(f"Task added to team [cyan]{team_id}[/cyan]: [bold]{title}[/bold] (ID: [green]{task_id}[/green])")


def team_task_list_cmd(*, team_id: str, console: Any) -> None:
    """WP-6008: List all tasks for a team."""
    from thegent.config import ThegentSettings
    from thegent.team.manager import TeamManager

    settings = ThegentSettings()
    mgr = TeamManager(settings.session_dir)
    tasks = mgr.list_tasks(team_id)

    if not tasks:
        console.print(f"No tasks found for team [cyan]{team_id}[/cyan].")
        return

    table = Table(title=f"Tasks for Team {team_id}")
    table.add_column("ID", style="green")
    table.add_column("Title", style="bold")
    table.add_column("Status", style="yellow")
    table.add_column("Assigned To", style="cyan")

    for t in tasks:
        table.add_row(t["id"], t["title"], t["status"], t["assigned_to"] or "Unassigned")

    console.print(table)


def _load_team_configs(teams_dir: Path) -> list[dict[str, Any]]:
    team_configs: list[dict[str, Any]] = []
    if not teams_dir.exists():
        return team_configs

    for path in sorted(teams_dir.iterdir()):
        if not path.is_dir():
            continue
        config_path = path / "config.json"
        if not config_path.exists():
            continue
        team_configs.append(json.loads(config_path.read_text(encoding="utf-8")))
    return team_configs


def _build_teammate_manager() -> Any:
    from thegent.config import ThegentSettings
    from thegent.governance.teammates import TeammateManager

    settings = ThegentSettings()
    return TeammateManager(settings.cache_dir / "teammates.json")


def _render_json(console: Any, payload: dict[str, Any]) -> None:
    console.print(JSON.from_data(payload, indent=2))


def team_list_cmd(*, format: str, console: Any) -> None:
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    manager = _build_teammate_manager()
    teams = _load_team_configs(settings.cache_dir / "teams")
    delegations = [asdict(item) for item in manager.get_delegations()]
    payload = {
        "teams": teams,
        "delegations": delegations,
    }

    if format == "json":
        _render_json(console, payload)
        return

    teams_table = Table(title="Active Teams")
    teams_table.add_column("Team ID", style="cyan")
    teams_table.add_column("Mode", style="yellow")
    teams_table.add_column("Teammates", style="green")
    teams_table.add_column("Created", style="magenta")
    if teams:
        for team in teams:
            teams_table.add_row(
                str(team.get("team_id", "")),
                str(team.get("mode", "")),
                str(team.get("teammates", "")),
                str(team.get("created_at", "")),
            )
    else:
        teams_table.add_row("-", "-", "-", "No persisted teams")

    delegations_table = Table(title="Delegations")
    delegations_table.add_column("ID", style="cyan")
    delegations_table.add_column("Teammate", style="yellow")
    delegations_table.add_column("Status", style="green")
    delegations_table.add_column("Parent Run", style="magenta")
    if delegations:
        for item in delegations:
            delegations_table.add_row(
                str(item.get("id", "")),
                str(item.get("teammate_id", "")),
                str(item.get("status", "")),
                str(item.get("parent_run_id", "")),
            )
    else:
        delegations_table.add_row("-", "-", "-", "No delegations")

    console.print(Group(teams_table, delegations_table))


def team_hierarchy_cmd(*, format: str, console: Any) -> None:
    manager = _build_teammate_manager()
    hierarchy = manager.hierarchy
    teams = [team.to_dict() for team in hierarchy.list_all_teams()]
    agents = [agent.to_dict() for agent in hierarchy.list_all_agents()]
    tree = hierarchy.get_hierarchy_tree()
    payload = {
        "tree": tree,
        "teams": teams,
        "agents": agents,
    }

    if format == "json":
        _render_json(console, payload)
        return

    summary = Table(title="Hierarchy Summary")
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value", style="green")
    summary.add_row("Teams", str(len(teams)))
    summary.add_row("Agents", str(len(agents)))
    summary.add_row("Root Present", "yes" if tree else "no")
    console.print(summary)
    console.print(JSON.from_data(tree if tree else {"tree": "empty"}, indent=2))


def team_crew_cmd(*, format: str, console: Any) -> None:
    manager = _build_teammate_manager()
    crews = [team.to_dict() for team in manager.hierarchy.list_all_teams()]
    payload = {"crews": crews}
    if format == "json":
        _render_json(console, payload)
        return

    table = Table(title="Agent Crews")
    table.add_column("Team ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Lead", style="yellow")
    table.add_column("Members", style="magenta")
    table.add_column("Mode", style="white")
    if crews:
        for crew in crews:
            table.add_row(
                str(crew.get("team_id", "")),
                str(crew.get("name", "")),
                str(crew.get("lead_id", "")),
                str(len(crew.get("members", []))),
                str(crew.get("coordination_mode", "")),
            )
    else:
        table.add_row("-", "No crews", "-", "0", "-")
    console.print(table)


__all__ = [
    "team_create_cmd",
    "team_crew_cmd",
    "team_hierarchy_cmd",
    "team_list_cmd",
    "team_task_add_cmd",
    "team_task_list_cmd",
]
