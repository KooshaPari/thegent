"""Logical stream: Swarm Coordination and Teammates."""

import typer
from rich.console import Console

console = Console()
app = typer.Typer(help="Manage agent swarms, teammates, and hierarchy.")

# Teammates Sub-stream
teammates_app = typer.Typer(help="Manage specialized teammate agents and delegation (WP-16001)")
app.add_typer(teammates_app, name="teammates")


@teammates_app.command("list", help="List available agent personas (teammates).")
def teammates_list():
    from thegent_cli.commands.cli_teammates import list_teammates

    list_teammates()


@teammates_app.command("delegate", help="Delegate a prompt to a specific teammate.")
def teammates_delegate(
    teammate: str = typer.Argument(..., help="Teammate agent ID"),
    task: str = typer.Argument(..., help="Task description"),
    parent_run_id: str = typer.Option(None, "--parent-run", help="Parent run ID for tracking"),
):
    from thegent_cli.commands.cli_teammates import delegate_task

    delegate_task(teammate=teammate, task=task, parent_run_id=parent_run_id)


@teammates_app.command("status", help="Monitor the status of the teammate swarm.")
def teammates_status(
    run_id: str = typer.Option(None, "--run-id", help="Filter by parent run ID"),
):
    from thegent_cli.commands.cli_teammates import swarm_status

    swarm_status(run_id=run_id)


@teammates_app.command("show", help="Show detailed status and result for a specific delegation.")
def teammates_show(
    req_id: str = typer.Argument(..., help="Request ID to show"),
):
    from thegent_cli.commands.cli_teammates import show_delegation

    show_delegation(req_id=req_id)


# Legacy Team Commands (Swarm v1)
@app.command("create", help="Form a new agent swarm team.")
def team_create(
    name: str = typer.Argument(..., help="Team name"),
    agents: list[str] = typer.Argument(..., help="Agents to include in the swarm"),
):
    from thegent_cli.commands.cli import team_create_cmd

    team_create_cmd(name=name, teammates=",".join(agents) if agents else None)


@app.command("list", help="List active agent swarms.")
def team_list(format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)")):
    from thegent_cli.commands.team_commands import team_list_cmd

    if format not in {"rich", "json"}:
        raise typer.BadParameter("format must be one of: rich, json", param_hint="--format")
    team_list_cmd(format=format, console=console)


@app.command("hierarchy", help="Show current agent management hierarchy.")
def team_hierarchy(format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)")):
    from thegent_cli.commands.team_commands import team_hierarchy_cmd

    if format not in {"rich", "json"}:
        raise typer.BadParameter("format must be one of: rich, json", param_hint="--format")
    team_hierarchy_cmd(format=format, console=console)


@app.command("crew", help="List hierarchical agent crews.")
def team_crew(format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)")):
    from thegent_cli.commands.team_commands import team_crew_cmd

    if format not in {"rich", "json"}:
        raise typer.BadParameter("format must be one of: rich, json", param_hint="--format")
    team_crew_cmd(format=format, console=console)


# Shortcuts for common teammate ops at top level of team stream
@app.command("delegate", help="Delegate a prompt to a specific teammate (shortcut).")
def team_delegate(
    prompt: str = typer.Argument(..., help="Prompt to delegate"),
    teammate: str = typer.Option(..., "--teammate", "-t", help="Teammate name"),
):
    from thegent_cli.commands.cli_teammates import delegate_task

    delegate_task(teammate=teammate, task=prompt)


@app.command("status", help="Show teammate delegation status (shortcut).")
def team_status(
    run_id: str = typer.Option(None, "--run-id", help="Filter by parent run ID"),
):
    from thegent_cli.commands.cli_teammates import swarm_status

    swarm_status(run_id=run_id)
