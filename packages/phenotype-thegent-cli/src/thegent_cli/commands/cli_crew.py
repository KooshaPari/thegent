"""CLI commands for crew management."""

import orjson as json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from thegent_agents.crew import Crew, CrewAgent, CrewExecutor, ExecutionMode, Task, TaskExecutor
from thegent_agents.crew.harness import create_agent_executor

console = Console()


def crew_create_cmd(
    name: str = typer.Option(..., "--name", help="Crew name"),
    description: str = typer.Option("", "--description", help="Crew description"),
    execution_mode: str = typer.Option("sequential", "--mode", help="Execution mode: sequential, hierarchical, custom"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path (JSON)"),
) -> None:
    """Create a new crew."""
    try:
        mode = ExecutionMode(execution_mode.lower())
    except ValueError:
        console.print(f"[red]Invalid execution mode: {execution_mode}[/red]")
        raise typer.Exit(1)

    crew = Crew(
        name=name,
        description=description,
        execution_mode=mode,
    )

    if output:
        output_path = Path(output)
        output_path.write_text(
            json.dumps(
                {
                    "id": crew.id,
                    "name": crew.name,
                    "description": crew.description,
                    "execution_mode": crew.execution_mode.value,
                    "agents": [],
                    "tasks": [],
                },
                indent=2,
            )
        ).decode()
        console.print(f"[green]✓[/green] Created crew: {crew.name} ({crew.id})")
        console.print(f"[dim]Saved to: {output_path}[/dim]")
    else:
        console.print(f"[green]✓[/green] Created crew: {crew.name} ({crew.id})")
        console.print(f"[dim]ID: {crew.id}[/dim]")


def crew_add_agent_cmd(
    crew_id: str = typer.Argument(..., help="Crew ID"),
    role: str = typer.Option(..., "--role", help="Agent role"),
    name: str = typer.Option(None, "--name", help="Agent name"),
    description: str = typer.Option("", "--description", help="Agent description"),
    capabilities: str = typer.Option("", "--capabilities", help="Comma-separated capabilities"),
    model: str = typer.Option(None, "--model", help="Model to use"),
) -> None:
    """Add agent to crew."""
    console.print(f"[yellow]Adding agent to crew {crew_id}...[/yellow]")
    console.print("[dim]Note: Crew persistence not yet implemented. This is a preview.[/dim]")

    agent = CrewAgent(
        role=role,
        name=name or role,
        description=description,
        capabilities=[c.strip() for c in capabilities.split(",") if c.strip()],
        model=model,
    )

    console.print(f"[green]✓[/green] Agent created: {agent.name} ({agent.id})")
    console.print(f"[dim]Role: {agent.role}[/dim]")


def crew_add_task_cmd(
    crew_id: str = typer.Argument(..., help="Crew ID"),
    description: str = typer.Option(..., "--description", help="Task description"),
    dependencies: str = typer.Option("", "--dependencies", help="Comma-separated task IDs"),
    agent_id: str = typer.Option(None, "--agent-id", help="Assigned agent ID"),
) -> None:
    """Add task to crew."""
    console.print(f"[yellow]Adding task to crew {crew_id}...[/yellow]")
    console.print("[dim]Note: Crew persistence not yet implemented. This is a preview.[/dim]")

    task = Task(
        description=description,
        agent_id=agent_id,
    )

    if dependencies:
        for dep_id in dependencies.split(","):
            task.add_dependency(dep_id.strip())

    console.print(f"[green]✓[/green] Task created: {task.id}")
    console.print(f"[dim]Description: {task.description[:50]}...[/dim]")
    if task.dependencies:
        console.print(f"[dim]Dependencies: {', '.join(task.dependencies)}[/dim]")


def crew_execute_cmd(
    crew_file: str = typer.Argument(..., help="Crew JSON file"),
    cwd: str = typer.Option(None, "--cwd", help="Working directory"),
    mode: str = typer.Option("write", "--mode", help="Execution mode: read-only, write, full"),
    timeout: int = typer.Option(300, "--timeout", help="Timeout in seconds"),
    model: str = typer.Option(None, "--model", help="Model override"),
) -> None:
    """Execute a crew from a JSON file."""
    console.print(f"[yellow]Executing crew from {crew_file}...[/yellow]")

    path = Path(crew_file)
    if not path.exists():
        from thegent_core.errors import print_error

        print_error(f"File not found: {crew_file}")
        raise typer.Exit(1)

    try:
        data = json.loads(path.read_text())

        # Reconstruct crew
        crew = Crew(
            name=data.get("name", "Unnamed Crew"),
            description=data.get("description", ""),
            execution_mode=ExecutionMode(data.get("execution_mode", "sequential")),
        )

        # Add agents
        for agent_data in data.get("agents", []):
            agent = CrewAgent(
                role=agent_data["role"],
                name=agent_data.get("name"),
                description=agent_data.get("description", ""),
                capabilities=agent_data.get("capabilities", []),
                model=agent_data.get("model"),
            )
            crew.add_agent(agent)

        # Add tasks
        for task_data in data.get("tasks", []):
            task = Task(
                description=task_data["description"],
                agent_id=task_data.get("agent_id"),
            )
            for dep_id in task_data.get("dependencies", []):
                task.add_dependency(dep_id)
            crew.add_task(task)

        # Create harness executor
        agent_exec = create_agent_executor(cwd=Path(cwd) if cwd else None, mode=mode, timeout=timeout, model=model)

        # Setup executor
        task_executor = TaskExecutor(agent_executor=agent_exec)
        crew_executor = CrewExecutor(crew, task_executor=task_executor)

        # Execute
        console.print("[green]Starting execution...[/green]")
        results = crew_executor.execute()

        # Show results
        table = Table(title=f"Execution Results: {crew.name}")
        table.add_column("Task ID", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Result/Error", style="white")

        for task_id, result in results.items():
            status = "[green]SUCCESS[/green]" if result.success else "[red]FAILED[/red]"
            output = result.result if result.success else result.error
            table.add_row(task_id, status, str(output)[:100] + "...")

        console.print(table)

        if crew.status == "completed":
            console.print("\n[bold green]✓ Crew execution completed successfully![/bold green]")
        else:
            console.print("\n[bold red]✗ Crew execution failed.[/bold red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error during execution: {e}[/red]")
        raise typer.Exit(1)


def crew_list_cmd() -> None:
    """List all crews."""
    console.print("[yellow]Listing crews...[/yellow]")
    console.print("[dim]Note: Crew persistence not yet implemented.[/dim]")

    table = Table(title="Crews")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Mode", style="yellow")
    table.add_column("Status", style="magenta")

    # Placeholder - would load from storage
    console.print("[dim]No crews found. Create one with 'thegent crew create'[/dim]")


def crew_show_cmd(crew_id: str = typer.Argument(..., help="Crew ID")) -> None:
    """Show crew details."""
    console.print(f"[yellow]Showing crew {crew_id}...[/yellow]")
    console.print("[red]Error: Crew persistence not yet implemented.[/red]")
    raise typer.Exit(1)


def crew_status_cmd(crew_id: str = typer.Option(None, "--crew-id", help="Crew ID")) -> None:
    """Show crew execution status."""
    console.print("[yellow]Crew status...[/yellow]")
    console.print("[dim]Note: Status tracking requires crew persistence.[/dim]")

    if crew_id:
        console.print(f"[dim]Crew ID: {crew_id}[/dim]")
    else:
        console.print("[dim]No crew ID specified. Use --crew-id[/dim]")
