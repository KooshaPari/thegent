"""Skills management CLI commands."""

import shlex

import typer
from rich.console import Console
from rich.table import Table

from thegent_skills.skills.discovery import _get_thegent_root, discover_skills, load_skill, validate_skill

console = Console()
app = typer.Typer(help="Skills auto-discovery and management.")


@app.command("list", help="List all available skills.")
def skills_list(json_output: bool = typer.Option(False, "--json", help="Output skills as JSON")):
    """List all available skills with their metadata."""
    skills = sorted(discover_skills(), key=lambda skill: (skill.name.lower(), skill.name))
    payload = [
        {
            "name": skill.name,
            "version": skill.version,
            "entrypoint": skill.entrypoint,
            "description": skill.description,
            "path": str(skill.path),
        }
        for skill in skills
    ]

    if json_output:
        console.print_json(data=payload)
        return

    if not skills:
        console.print("[yellow]No skills found.[/yellow]")
        return

    table = Table(title="Available Skills")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Entrypoint", style="blue")
    table.add_column("Description")

    for skill in skills:
        table.add_row(
            skill.name,
            skill.version,
            skill.entrypoint,
            skill.description,
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(skills)} skill(s)[/dim]")


@app.command("show", help="Show detailed information about a skill.")
def skills_show(name: str = typer.Argument(..., help="Skill name")):
    """Show detailed information about a specific skill."""
    # First validate
    root = _get_thegent_root()
    skills_dir = root / "skills"
    skill_path = skills_dir / name

    validation = validate_skill(skill_path)

    # Then load
    skill = load_skill(name)

    if skill is None:
        console.print(f"[red]Skill not found: {name}[/red]")
        skills = discover_skills()
        console.print("\n[yellow]Available skills:[/yellow]")
        for s in skills:
            console.print(f"  - {s.name}")
        raise typer.Exit(1)

    # Print validation warnings/errors
    if validation.get("errors"):
        console.print("[red]Validation Errors:[/red]")
        for err in validation["errors"]:
            console.print(f"  [red]• {err}[/red]")

    if validation.get("warnings"):
        console.print("[yellow]Validation Warnings:[/yellow]")
        for warn in validation["warnings"]:
            console.print(f"  [yellow]• {warn}[/yellow]")

    # Print skill details
    console.print(f"\n[bold cyan]{skill['name']}[/bold cyan] (v{skill['version']})")
    console.print(f"[blue]Entrypoint:[/blue] {skill['entrypoint']}")
    console.print(f"\n[bold]Description:[/bold]\n{skill['description']}")

    # Print content preview
    content = skill.get("content", "")
    if content:
        console.print("\n[bold]Content Preview:[/bold]")
        preview = content[:500]
        if len(content) > 500:
            preview += "..."
        console.print(preview)

    console.print(f"\n[dim]Path: {skill['path']}[/dim]")


@app.command("validate", help="Validate a skill by name.")
def skills_validate(name: str = typer.Argument(..., help="Skill name")):
    """Validate a skill and show any errors or warnings."""
    root = _get_thegent_root()
    skills_dir = root / "skills"
    skill_path = skills_dir / name

    result = validate_skill(skill_path)

    if result["valid"]:
        console.print(f"[green]✓ Skill '{name}' is valid[/green]")
    else:
        console.print(f"[red]✗ Skill '{name}' is invalid[/red]")

    if result.get("errors"):
        console.print("\n[red]Errors:[/red]")
        for err in result["errors"]:
            console.print(f"  [red]• {err}[/red]")

    if result.get("warnings"):
        console.print("\n[yellow]Warnings:[/yellow]")
        for warn in result["warnings"]:
            console.print(f"  [yellow]• {warn}[/red]")

    if not result["valid"]:
        raise typer.Exit(1)


@app.command("select", help="Select a skill name and print the run command form.")
def skills_select(name: str = typer.Argument(..., help="Skill name")):
    """Validate a skill name for run-time selection via --skill."""
    cleaned_name = name.strip()
    if not cleaned_name:
        console.print("[red]Skill name must be non-empty.[/red]")
        raise typer.Exit(1)
    if any(ord(char) < 32 or ord(char) == 127 for char in cleaned_name):
        console.print("[red]Skill name must not contain control characters.[/red]")
        raise typer.Exit(1)
    skill = load_skill(cleaned_name)
    if skill is None:
        console.print(f"[red]Skill not found: {cleaned_name}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]Selected skill:[/green] {cleaned_name}")
    console.print(f'[dim]Use with:[/dim] thegent run agent "<prompt>" --skill {shlex.quote(cleaned_name)}')


if __name__ == "__main__":
    app()
