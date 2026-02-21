"""Team command group extracted from cli.py (WL-124)."""

from __future__ import annotations

from typing import Any

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


__all__ = ["team_create_cmd", "team_task_add_cmd", "team_task_list_cmd"]
