"""CLI commands for the cross-project persona registry.

Exposes:
  thegent registry register [project_dir]
  thegent registry search <capability>
  thegent registry list

FR Traceability: FR-AGT-020
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Cross-project persona registry (FR-AGT-020)")
console = Console()


def _load_registry(registry_file: Path | None = None):
    """Return a loaded CrossProjectRegistry instance."""
    from phenotype_thegent_core.registry.cross_project import CrossProjectRegistry

    reg = CrossProjectRegistry(registry_file=registry_file)
    reg.load()
    return reg


@app.command("register")
def registry_register(
    project_dir: Path = typer.Argument(
        None,
        help="Root of the project to register (defaults to current directory)",
    ),
) -> None:
    """Discover and register personas from PROJECT_DIR/agents/."""
    if project_dir is None:
        project_dir = Path.cwd()
    project_dir = project_dir.resolve()

    if not project_dir.is_dir():
        from phenotype_thegent_core.errors import print_error

        print_error(f"{project_dir} is not a directory.")
        raise typer.Exit(1)

    reg = _load_registry()
    records = reg.register_project(project_dir)

    if not records:
        console.print(f"[yellow]No persona files found in {project_dir / 'agents'}.[/yellow]")
        return

    table = Table(title=f"Registered personas from {project_dir}")
    table.add_column("Name", style="cyan")
    table.add_column("Capabilities", style="green")
    table.add_column("File", style="dim")

    for r in records:
        caps = ", ".join(r.capabilities) if r.capabilities else "-"
        table.add_row(r.name, caps, str(r.persona_file.relative_to(project_dir)))

    console.print(table)
    console.print(f"[green]Registered {len(records)} persona(s).[/green]")


@app.command("search")
def registry_search(
    capability: str = typer.Argument(..., help="Capability keyword to search for"),
) -> None:
    """Search for personas that advertise CAPABILITY."""
    reg = _load_registry()
    results = reg.search(capability)

    if not results:
        console.print(f"[yellow]No personas found for capability: {capability!r}.[/yellow]")
        return

    table = Table(title=f"Personas matching '{capability}'")
    table.add_column("Name", style="cyan")
    table.add_column("Project", style="blue")
    table.add_column("Capabilities", style="green")
    table.add_column("Last Seen", style="dim")

    for r in results:
        caps = ", ".join(r.capabilities)
        table.add_row(r.name, str(r.project_root), caps, r.last_seen.strftime("%Y-%m-%d %H:%M"))

    console.print(table)


@app.command("list")
def registry_list(
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)"),
) -> None:
    """List all personas in the cross-project registry.

    # @trace WL-040 WP-4002
    """
    import json
    import sys

    reg = _load_registry()
    records = reg.get_all()

    if not records:
        if format == "json":
            sys.stdout.write(json.dumps([]).decode() + "\n")
        else:
            console.print("[yellow]Registry is empty. Run 'thegent registry register <dir>' first.[/yellow]")
        return

    if format == "json":
        data = [
            {
                "name": r.name,
                "project": str(r.project_root),
                "capabilities": list(r.capabilities) if r.capabilities else [],
                "last_seen": r.last_seen.strftime("%Y-%m-%d %H:%M"),
            }
            for r in sorted(records, key=lambda x: (str(x.project_root), x.name))
        ]
        sys.stdout.write(json.dumps(data).decode() + "\n")
        return

    table = Table(title="Cross-Project Persona Registry")
    table.add_column("Name", style="cyan")
    table.add_column("Project", style="blue")
    table.add_column("Capabilities", style="green")
    table.add_column("Last Seen", style="dim")

    for r in sorted(records, key=lambda x: (str(x.project_root), x.name)):
        caps = ", ".join(r.capabilities) if r.capabilities else "-"
        table.add_row(r.name, str(r.project_root), caps, r.last_seen.strftime("%Y-%m-%d %H:%M"))

    console.print(table)
    console.print(f"[dim]{len(records)} persona(s) total.[/dim]")
