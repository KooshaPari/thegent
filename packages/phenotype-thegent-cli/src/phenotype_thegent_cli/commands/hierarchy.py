"""CLI commands for milestone and sprint hierarchy management.

Milestones and sprints are stored as projects with type metadata
in the ProjectRegistry, providing a lightweight hierarchy for
organizing agent work.

WBS: wp-71005-hierarchy-cli
FR Traceability: FR-VER-002 (milestone and sprint management)

Commands:
    thegent plan milestone list/create/complete
    thegent plan sprint list/create/complete
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from phenotype_thegent_core.registry.project_registry import ProjectRecord, ProjectRegistry

console = Console()

app = typer.Typer(help="Hierarchy management: milestones and sprints.")
milestone_app = typer.Typer(help="Manage milestones (L4 hierarchy).")
sprint_app = typer.Typer(help="Manage sprints (L3 hierarchy).")
app.add_typer(milestone_app, name="milestone")
app.add_typer(sprint_app, name="sprint")


def _get_registry() -> ProjectRegistry:
    """Return the singleton ProjectRegistry instance."""
    return ProjectRegistry()


def _list_by_type(entity_type: str) -> list[ProjectRecord]:
    """Return all projects matching the given type metadata."""
    registry = _get_registry()
    return [p for p in registry.list_projects() if p.metadata.get("type") == entity_type]


def _find_by_name_and_type(name: str, entity_type: str) -> ProjectRecord | None:
    """Find a project by name and type metadata."""
    for p in _list_by_type(entity_type):
        if p.name == name:
            return p
    return None


# ---------------------------------------------------------------------------
# Milestone commands
# ---------------------------------------------------------------------------


@milestone_app.command("create")
def milestone_create(
    name: str = typer.Argument(..., help="Milestone name (e.g. m-reliability)"),
    label: Annotated[
        str | None,
        typer.Option("--label", "-l", help="Human-readable label for the milestone"),
    ] = None,
) -> None:
    """Create a new milestone."""
    registry = _get_registry()
    metadata = {"type": "milestone"}
    if label:
        metadata["label"] = label
    project = registry.register_project(name=name, path="milestone", metadata=metadata)
    console.print(f"[green]Milestone created:[/green] {project.name} (id={project.id})")


@milestone_app.command("list")
def milestone_list() -> None:
    """List all milestones."""
    milestones = _list_by_type("milestone")
    if not milestones:
        console.print("[yellow]No milestones found.[/yellow]")
        return

    table = Table(title="Milestones")
    table.add_column("Name", style="cyan")
    table.add_column("Label", style="green")
    table.add_column("Status", style="bold")
    table.add_column("ID", style="dim")

    for m in milestones:
        label = m.metadata.get("label", "-")
        status = m.metadata.get("status", "active")
        table.add_row(m.name, label, status, m.id)

    console.print(table)


@milestone_app.command("complete")
def milestone_complete(
    name: str = typer.Argument(..., help="Milestone name to mark as completed"),
) -> None:
    """Mark a milestone as completed."""
    found = _find_by_name_and_type(name, "milestone")
    if found is None:
        console.print(f"[red]Milestone '{name}' not found.[/red]")
        raise typer.Exit(1)

    # Update metadata to mark as completed
    registry = _get_registry()
    registry.update_project_metadata(found.id, {"status": "completed"})
    console.print(f"[green]Milestone '{name}' marked as completed.[/green]")


# ---------------------------------------------------------------------------
# Sprint commands
# ---------------------------------------------------------------------------


@sprint_app.command("create")
def sprint_create(
    name: str = typer.Argument(..., help="Sprint name (e.g. s-2026-W08)"),
    label: Annotated[
        str | None,
        typer.Option("--label", "-l", help="Human-readable label for the sprint"),
    ] = None,
) -> None:
    """Create a new sprint."""
    registry = _get_registry()
    metadata = {"type": "sprint"}
    if label:
        metadata["label"] = label
    project = registry.register_project(name=name, path="sprint", metadata=metadata)
    console.print(f"[green]Sprint created:[/green] {project.name} (id={project.id})")


@sprint_app.command("list")
def sprint_list() -> None:
    """List all sprints."""
    sprints = _list_by_type("sprint")
    if not sprints:
        console.print("[yellow]No sprints found.[/yellow]")
        return

    table = Table(title="Sprints")
    table.add_column("Name", style="cyan")
    table.add_column("Label", style="green")
    table.add_column("Status", style="bold")
    table.add_column("ID", style="dim")

    for s in sprints:
        label = s.metadata.get("label", "-")
        status = s.metadata.get("status", "active")
        table.add_row(s.name, label, status, s.id)

    console.print(table)


@sprint_app.command("complete")
def sprint_complete(
    name: str = typer.Argument(..., help="Sprint name to mark as completed"),
) -> None:
    """Mark a sprint as completed."""
    found = _find_by_name_and_type(name, "sprint")
    if found is None:
        console.print(f"[red]Sprint '{name}' not found.[/red]")
        raise typer.Exit(1)

    registry = _get_registry()
    registry.update_project_metadata(found.id, {"status": "completed"})
    console.print(f"[green]Sprint '{name}' marked as completed.[/green]")
