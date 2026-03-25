"""CLI commands for the shadow audit log.

Provides ``thegent audit log`` and ``thegent audit diff`` subcommands
for inspecting the immutable audit trail of agent git operations.

WBS: wp-71004-audit-cli
FR Traceability: FR-VER-005 (audit log and diff CLI)

Commands:
    thegent audit log  [--project NAME] [--limit N]
    thegent audit diff <sha1> <sha2> [--project NAME]
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from thegent_audit.audit.shadow_audit_git import ShadowAuditGit
from thegent_core.registry.project_registry import ProjectRecord, ProjectRegistry

console = Console()

app = typer.Typer(help="Shadow audit log: view git operation history.")


def _get_registry() -> ProjectRegistry:
    """Return the singleton ProjectRegistry instance."""
    return ProjectRegistry()


def _get_shadow() -> ShadowAuditGit:
    """Return the singleton ShadowAuditGit instance."""
    return ShadowAuditGit()


def _find_project_by_name(name: str) -> ProjectRecord | None:
    """Find a project by name in the registry."""
    registry = _get_registry()
    for p in registry.list_projects():
        if p.name == name:
            return p
    return None


@app.command("log")
def audit_log(
    project: Annotated[
        str,
        typer.Option("--project", "-p", help="Project name to show audit log for"),
    ],
    limit: Annotated[
        int | None,
        typer.Option("--limit", "-n", help="Maximum number of entries to show"),
    ] = None,
) -> None:
    """Show audit log entries for a project."""
    found = _find_project_by_name(project)
    if found is None:
        console.print(f"[red]Project '{project}' not found.[/red]")
        raise typer.Exit(1)

    shadow = _get_shadow()
    entries = shadow.get_audit_log(found.id, limit=limit)

    if not entries:
        console.print(f"[yellow]No audit entries for project '{project}'.[/yellow]")
        return

    table = Table(title=f"Audit Log: {project}")
    table.add_column("SHA", style="cyan", max_width=12)
    table.add_column("Message", style="white")
    table.add_column("Created", style="dim")

    for entry in entries:
        table.add_row(entry.sha[:12], entry.message, entry.created_at)

    console.print(table)
    console.print(f"[dim]{len(entries)} entries shown.[/dim]")


@app.command("diff")
def audit_diff(
    sha1: str = typer.Argument(..., help="First SHA to compare"),
    sha2: str = typer.Argument(..., help="Second SHA to compare"),
    project: Annotated[
        str,
        typer.Option("--project", "-p", help="Project name"),
    ] = "",
) -> None:
    """Show diff between two audit entries."""
    if not project:
        console.print("[red]--project is required.[/red]")
        raise typer.Exit(1)

    found = _find_project_by_name(project)
    if found is None:
        console.print(f"[red]Project '{project}' not found.[/red]")
        raise typer.Exit(1)

    shadow = _get_shadow()
    entries = shadow.get_audit_log(found.id)

    entry1 = next((e for e in entries if e.sha == sha1), None)
    entry2 = next((e for e in entries if e.sha == sha2), None)

    if entry1 is None or entry2 is None:
        missing = []
        if entry1 is None:
            missing.append(sha1)
        if entry2 is None:
            missing.append(sha2)
        console.print(f"[red]SHA(s) not found: {', '.join(missing)}[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]Entry 1:[/bold] {entry1.sha} - {entry1.message}")
    console.print(f"[dim]{entry1.created_at}[/dim]")
    console.print(entry1.diff or "[dim](no diff)[/dim]")
    console.print()
    console.print(f"[bold]Entry 2:[/bold] {entry2.sha} - {entry2.message}")
    console.print(f"[dim]{entry2.created_at}[/dim]")
    console.print(entry2.diff or "[dim](no diff)[/dim]")
