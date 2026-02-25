"""Project CLI app - project management commands."""

import typer
from typing import Any

from thegent.project.migrate import project_migrate as _project_migrate
from thegent.project.scaffold import scaffold_greenfield

# CLI app containers
setup_project_app = typer.Typer(help="Project management commands.")
install_app = typer.Typer(help="Install project dependencies.")
scaffold_app = typer.Typer(help="Scaffold new project.")
update_app = typer.Typer(help="Update project.")


@install_app.command("project")
def install_project_cmd(
    mode: str = typer.Argument("agdd", help="brownfield, agdd, none"),
    project: str = typer.Argument(..., help="Project path"),
    template: str = typer.Option("auto", "--template", "-t", help="Template"),
    name: str = typer.Option("", "--name", "-n", help="Name"),
    tenant: str = typer.Option("", "--tenant", help="Tenant"),
    json: bool = typer.Option(False, "--json", help="JSON output"),
    reconcile: bool = typer.Option(True, "--reconcile/--no-reconcile"),
    register: bool = typer.Option(True, "--register/--no-register"),
    install_runtime: bool = typer.Option(True, "--install-runtime/--no-install-runtime"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> dict[str, Any]:
    """Install/brownfield project."""
    return _project_migrate(project_path=project, mode=mode)


@scaffold_app.command("greenfield")
def scaffold_greenfield_cmd(
    destination: str = typer.Argument(..., help="Destination"),
    profile: str = typer.Option("default", "--profile"),
    name: str = typer.Option("", "--name", "-n"),
    language: str = typer.Option("python", "--language", "-l"),
    tenant: str = typer.Option("", "--tenant"),
) -> dict[str, Any]:
    """Scaffold new project."""
    return _project_migrate(project_path=destination, mode=profile)


@scaffold_app.command("brownfield")
def scaffold_brownfield_cmd(
    project: str = typer.Argument(..., help="Project path"),
    mode: str = typer.Option("agdd", "--mode"),
    template: str = typer.Option("auto", "--template", "-t"),
    name: str = typer.Option("", "--name", "-n"),
    tenant: str = typer.Option("", "--tenant"),
    json: bool = typer.Option(False, "--json"),
) -> dict[str, Any]:
    """Scaffold brownfield project."""
    return _project_migrate(project_path=project, mode=mode)


# Module-level exports for test mocking
def project_migrate(**kwargs: Any) -> dict[str, Any]:
    """Entry point for project migration (used by CLI tests)."""
    return _project_migrate(
        project_path=kwargs.get("project", ""),
        mode=kwargs.get("mode", "agdd"),
    )


def project_scaffold(**kwargs: Any) -> dict[str, Any]:
    """Entry point for project scaffolding (used by CLI tests)."""
    return scaffold_greenfield(kwargs.get("destination", ""), template=kwargs.get("language", "python"))
