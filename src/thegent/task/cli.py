"""CLI commands for task management."""

import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from thegent.task.parser import TaskParseError, parse_task_file
from thegent.task.sync import WorkStreamSync
from thegent.task.validator import ValidationResult, validate_task_file

_log = logging.getLogger(__name__)
console = Console()
app = typer.Typer(name="task", help="Task management commands")


@app.command()
def validate(
    task_id: str | None = typer.Option(None, "--id", "-i", help="Task ID to validate"),
    task_file: Path | None = typer.Option(None, "--file", "-f", help="Task file path"),
    all: bool = typer.Option(False, "--all", "-a", help="Validate all tasks"),
    tasks_dir: Path = typer.Option(Path("tasks"), "--dir", "-d", help="Tasks directory"),
):
    """Validate task file(s)."""
    if all:
        # Validate all tasks in directory
        if not tasks_dir.exists():
            console.print(f"[red]Tasks directory not found: {tasks_dir}[/red]")
            raise typer.Exit(1)

        task_files = list(tasks_dir.glob("*.md"))
        if not task_files:
            console.print(f"[yellow]No task files found in {tasks_dir}[/yellow]")
            return

        console.print(f"[blue]Validating {len(task_files)} tasks...[/blue]")

        valid_count = 0
        invalid_count = 0

        for task_file_path in task_files:
            try:
                result = validate_task_file(task_file_path)
                if result.valid:
                    valid_count += 1
                    console.print(f"[green]✓[/green] {task_file_path.name}")
                else:
                    invalid_count += 1
                    console.print(f"[red]✗[/red] {task_file_path.name}")
                    for error in result.errors[:3]:  # Show first 3 errors
                        console.print(f"  [red]{error.field}:[/red] {error.message}")
            except Exception as e:  # noqa: PERF203 - intentional per-item error handling
                invalid_count += 1
                console.print(f"[red]✗[/red] {task_file_path.name}: {e}")

        console.print(f"\n[bold]Results:[/bold] {valid_count} valid, {invalid_count} invalid")

    elif task_file:
        # Validate specific file
        if not task_file.exists():
            console.print(f"[red]Task file not found: {task_file}[/red]")
            raise typer.Exit(1)

        result = validate_task_file(task_file)
        display_validation_result(task_file, result)

    elif task_id:
        # Find and validate by ID
        task_file_path = find_task_file(task_id, tasks_dir)
        if not task_file_path:
            console.print(f"[red]Task not found: {task_id}[/red]")
            raise typer.Exit(1)

        result = validate_task_file(task_file_path)
        display_validation_result(task_file_path, result)

    else:
        console.print("[red]Must specify --id, --file, or --all[/red]")
        raise typer.Exit(1)


@app.command()
def parse(
    task_file: Path = typer.Argument(..., help="Task file to parse"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output JSON file"),
):
    """Parse a task file and display or save result."""
    if not task_file.exists():
        console.print(f"[red]Task file not found: {task_file}[/red]")
        raise typer.Exit(1)

    try:
        task = parse_task_file(task_file)
        console.print(f"[green]✓[/green] Successfully parsed {task_file.name}")

        if output:
            import json

            output.write_text(json.dumps(task, indent=2), default=str).decode())
            console.print(f"[green]Saved to {output}[/green]")
        else:
            # Display task summary
            display_task_summary(task)

    except TaskParseError as e:
        console.print(f"[red]Parse error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        _log.exception("Unexpected error parsing task")
        raise typer.Exit(1)


@app.command(name="list")
def list_tasks(
    tasks_dir: Path = typer.Option(Path("tasks"), "--dir", "-d", help="Tasks directory"),
    priority: str | None = typer.Option(None, "--priority", "-p", help="Filter by priority"),
    subagent: str | None = typer.Option(None, "--subagent", "-s", help="Filter by subagent type"),
):
    """List tasks."""
    if not tasks_dir.exists():
        console.print(f"[yellow]Tasks directory not found: {tasks_dir}[/yellow]")
        return

    task_files = list(tasks_dir.glob("*.md"))
    if not task_files:
        console.print("[yellow]No task files found[/yellow]")
        return

    # Parse all tasks
    tasks = []
    for task_file in task_files:
        try:
            task = parse_task_file(task_file)
            tasks.append(task)
        except Exception:  # noqa: PERF203 - intentional per-item error handling
            continue

    # Apply filters
    if priority:
        tasks = [t for t in tasks if t.get("priority") == priority]
    if subagent:
        tasks = [t for t in tasks if t.get("subagent_type") == subagent]

    # Display table
    table = Table(title="Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Priority", style="yellow")
    table.add_column("Subagent", style="blue")
    table.add_column("Depends", style="dim")

    for task in tasks:
        priority_style = {"P1": "bold red", "P2": "yellow", "P3": "dim"}.get(task.get("priority", "P2"), "white")
        depends_str = ", ".join(task.get("depends", [])) or "-"

        table.add_row(
            task.get("id", "unknown"),
            task.get("title", "")[:50],
            f"[{priority_style}]{task.get('priority', 'P2')}[/]",
            task.get("subagent_type", "worker"),
            depends_str,
        )

    console.print(table)


def display_validation_result(file_path: Path, result: ValidationResult):
    """Display validation result."""
    if result.valid:
        console.print(f"[green]✓ Task is valid: {file_path.name}[/green]")
    else:
        console.print(f"[red]✗ Task validation failed: {file_path.name}[/red]")

        error_table = Table(title="Validation Errors")
        error_table.add_column("Field", style="cyan")
        error_table.add_column("Error", style="red")

        for error in result.errors:
            error_table.add_row(error.field or "root", error.message)

        console.print(error_table)


def display_task_summary(task: dict):
    """Display task summary."""
    content = f"""
[bold]ID:[/bold] {task.get("id", "unknown")}
[bold]Title:[/bold] {task.get("title", "")}
[bold]Priority:[/bold] {task.get("priority", "P2")}
[bold]Subagent:[/bold] {task.get("subagent_type", "worker")}
[bold]Dependencies:[/bold] {", ".join(task.get("depends", [])) or "None"}
"""
    panel = Panel(content, title=f"Task: {task.get('id', 'unknown')}", border_style="blue")
    console.print(panel)


def find_task_file(task_id: str, tasks_dir: Path) -> Path | None:
    """Find task file by ID."""
    task_file = tasks_dir / f"{task_id}.md"
    if task_file.exists():
        return task_file
    return None


@app.command()
def migrate(
    work_stream: Path = typer.Option(
        Path("docs/reference/WORK_STREAM.md"), "--work-stream", "-w", help="Path to WORK_STREAM.md"
    ),
    tasks_dir: Path = typer.Option(Path("tasks"), "--tasks-dir", "-d", help="Tasks directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Don't write files, just show what would be created"),
    legacy_file: Path | None = typer.Option(None, "--legacy-file", "-f", help="Migrate a single legacy task file"),
):
    """Migrate legacy task formats to YAML frontmatter format."""
    from thegent.task.migrate import migrate_legacy_task_to_yaml_frontmatter, migrate_work_stream_to_tasks

    if legacy_file:
        # Migrate single legacy file
        if not legacy_file.exists():
            console.print(f"[red]File not found: {legacy_file}[/red]")
            raise typer.Exit(1)

        content = legacy_file.read_text(encoding="utf-8")
        migrated_content = migrate_legacy_task_to_yaml_frontmatter(content)

        if dry_run:
            console.print("[yellow]Dry run - would create:[/yellow]")
            console.print(Panel(migrated_content, title=f"Migrated: {legacy_file.name}"))
        else:
            output_file = tasks_dir / f"{legacy_file.stem}.md"
            tasks_dir.mkdir(parents=True, exist_ok=True)
            output_file.write_text(migrated_content, encoding="utf-8")
            console.print(f"[green]Migrated:[/green] {legacy_file} -> {output_file}")
    else:
        # Migrate WORK_STREAM.md
        if not work_stream.exists():
            from thegent.errors import print_error

            print_error(f"WORK_STREAM.md not found: {work_stream}")
            raise typer.Exit(1)

        result = migrate_work_stream_to_tasks(work_stream, tasks_dir, dry_run=dry_run)

        if "error" in result:
            from thegent.errors import print_error

            print_error(result["error"])
            raise typer.Exit(1)

        console.print("[bold]Migration Results:[/bold]")
        console.print(f"  Migrated: {len(result['migrated'])}")
        console.print(f"  Skipped: {len(result['skipped'])}")
        console.print(f"  Errors: {len(result['errors'])}")

        if result["migrated"]:
            table = Table(title="Migrated Tasks")
            table.add_column("ID", style="cyan")
            table.add_column("Title", style="magenta")
            table.add_column("File", style="dim")

            for item in result["migrated"][:20]:  # Show first 20
                table.add_row(item["id"], item["title"][:50], item["file"])

            console.print(table)

            if len(result["migrated"]) > 20:
                console.print(f"[dim]... and {len(result['migrated']) - 20} more[/dim]")

        if result["errors"]:
            console.print("\n[red]Errors:[/red]")
            for error in result["errors"]:
                console.print(f"  {error['id']}: {error['error']}")

        if dry_run:
            console.print("\n[yellow]Dry run - no files were written. Use without --dry-run to migrate.[/yellow]")
        else:
            console.print(f"\n[green]Migration complete![/green] Task files written to {tasks_dir}")


@app.command()
def sync(
    work_stream: Path = typer.Option(
        Path("docs/reference/WORK_STREAM.md"), "--work-stream", "-w", help="Path to WORK_STREAM.md"
    ),
    tasks_dir: Path = typer.Option(Path("tasks"), "--tasks-dir", "-d", help="Tasks directory"),
    direction: str = typer.Option("both", "--direction", help="Sync direction: tasks-to-stream, stream-to-tasks, both"),
):
    """Sync task files with WORK_STREAM.md."""
    sync_manager = WorkStreamSync(work_stream, tasks_dir)

    if direction in ("tasks-to-stream", "both"):
        console.print("[blue]Syncing tasks to WORK_STREAM.md...[/blue]")
        result = sync_manager.update_work_stream_from_tasks()
        if "error" in result:
            from thegent.errors import print_error

            print_error(result["error"])
            raise typer.Exit(1)
        console.print(f"[green]✓[/green] Synced {result['tasks_synced']} tasks to BACKLOG")

    console.print("[green]Sync complete![/green]")


@app.command()
def claim(
    task_id: str = typer.Argument(..., help="Task ID to claim"),
    agent_id: str = typer.Option(None, "--agent", "-a", help="Agent ID (defaults to current user)"),
    work_stream: Path = typer.Option(
        Path("docs/reference/WORK_STREAM.md"), "--work-stream", "-w", help="Path to WORK_STREAM.md"
    ),
):
    """Claim a task (move from BACKLOG to CLAIMED in WORK_STREAM.md)."""
    import getpass

    if not agent_id:
        agent_id = getpass.getuser()

    sync_manager = WorkStreamSync(work_stream, Path("tasks"))
    result = sync_manager.claim_task(task_id, agent_id)

    if "error" in result:
        from thegent.errors import print_error

        print_error(result["error"])
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] Claimed task {task_id} as {agent_id}")


@app.command()
def complete(
    task_id: str = typer.Argument(..., help="Task ID to complete"),
    agent_id: str = typer.Option(None, "--agent", "-a", help="Agent ID (defaults to current user)"),
    work_stream: Path = typer.Option(
        Path("docs/reference/WORK_STREAM.md"), "--work-stream", "-w", help="Path to WORK_STREAM.md"
    ),
):
    """Complete a task (move from CLAIMED to COMPLETED in WORK_STREAM.md)."""
    import getpass

    if not agent_id:
        agent_id = getpass.getuser()

    sync_manager = WorkStreamSync(work_stream, Path("tasks"))
    result = sync_manager.complete_task(task_id, agent_id)

    if "error" in result:
        from thegent.errors import print_error

        print_error(result["error"])
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] Completed task {task_id} as {agent_id}")


@app.command()
def status(
    task_id: str = typer.Argument(..., help="Task ID to check"),
    work_stream: Path = typer.Option(
        Path("docs/reference/WORK_STREAM.md"), "--work-stream", "-w", help="Path to WORK_STREAM.md"
    ),
):
    """Get status of a task in WORK_STREAM.md."""
    sync_manager = WorkStreamSync(work_stream, Path("tasks"))
    status = sync_manager.get_task_status(task_id)

    if status is None:
        console.print(f"[yellow]Task {task_id} not found in WORK_STREAM.md[/yellow]")
    else:
        console.print(f"[blue]Task {task_id}:[/blue] {status}")
