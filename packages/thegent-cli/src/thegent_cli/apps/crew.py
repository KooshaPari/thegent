"""Logical stream: top-level crew management commands."""

from __future__ import annotations

import typer

from thegent_cli.commands.cli_crew import (
    crew_add_agent_cmd,
    crew_add_task_cmd,
    crew_create_cmd,
    crew_execute_cmd,
    crew_list_cmd,
    crew_show_cmd,
    crew_status_cmd,
)

app = typer.Typer(name="crew", help="Manage execution crews and crew tasks.")


@app.command("create", help="Create a new crew.")
def create_cmd(
    name: str = typer.Option(..., "--name", help="Crew name"),
    description: str = typer.Option("", "--description", help="Crew description"),
    mode: str = typer.Option("sequential", "--mode", help="Execution mode: sequential, hierarchical, custom"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path (JSON)"),
) -> None:
    crew_create_cmd(name=name, description=description, execution_mode=mode, output=output)


@app.command("add-agent", help="Add an agent to a crew.")
def add_agent_cmd(
    crew_id: str = typer.Argument(..., help="Crew ID"),
    role: str = typer.Option(..., "--role", help="Agent role"),
    name: str = typer.Option(None, "--name", help="Agent name"),
    description: str = typer.Option("", "--description", help="Agent description"),
    capabilities: str = typer.Option("", "--capabilities", help="Comma-separated capabilities"),
    model: str = typer.Option(None, "--model", help="Model to use"),
) -> None:
    crew_add_agent_cmd(
        crew_id=crew_id,
        role=role,
        name=name,
        description=description,
        capabilities=capabilities,
        model=model,
    )


@app.command("add-task", help="Add a task to a crew.")
def add_task_cmd(
    crew_id: str = typer.Argument(..., help="Crew ID"),
    description: str = typer.Option(..., "--description", help="Task description"),
    dependencies: str = typer.Option("", "--dependencies", help="Comma-separated task IDs"),
    agent_id: str = typer.Option(None, "--agent-id", help="Assigned agent ID"),
) -> None:
    crew_add_task_cmd(crew_id=crew_id, description=description, dependencies=dependencies, agent_id=agent_id)


@app.command("execute", help="Execute a crew from a JSON file.")
def execute_cmd(
    crew_file: str = typer.Argument(..., help="Crew JSON file"),
    cwd: str = typer.Option(None, "--cwd", help="Working directory"),
    mode: str = typer.Option("write", "--mode", help="Execution mode: read-only, write, full"),
    timeout: int = typer.Option(300, "--timeout", help="Timeout in seconds"),
    model: str = typer.Option(None, "--model", help="Model override"),
) -> None:
    crew_execute_cmd(crew_file=crew_file, cwd=cwd, mode=mode, timeout=timeout, model=model)


@app.command("list", help="List crews.")
def list_cmd() -> None:
    crew_list_cmd()


@app.command("show", help="Show crew details.")
def show_cmd(crew_id: str = typer.Argument(..., help="Crew ID")) -> None:
    crew_show_cmd(crew_id=crew_id)


@app.command("status", help="Show crew execution status.")
def status_cmd(crew_id: str = typer.Option(None, "--crew-id", help="Crew ID")) -> None:
    crew_status_cmd(crew_id=crew_id)
