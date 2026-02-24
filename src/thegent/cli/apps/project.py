"""Project CLI app - project management commands."""

import typer
from typing import Any, Optional

from thegent.project.migrate import project_migrate as _project_migrate
from thegent.project.scaffold import scaffold_greenfield, scaffold_brownfield


# CLI app containers
setup_project_app = typer.Typer(help="Project management commands.")
install_app = typer.Typer(help="Install user/system assets and project runtime installation.")
scaffold_app = typer.Typer(help="Scaffold new project.")
update_app = typer.Typer(help="Update project.")


@install_app.command("project")
def install_project_cmd(
    mode: str = typer.Argument("agdd", help="brownfield, agdd, none"),
    project: str = typer.Argument(..., help="Project path"),
    template: str = typer.Option("auto", "--template", "-t", help="Template to use"),
    name: str = typer.Option("", "--name", "-n", help="Project name"),
    tenant: str = typer.Option("", "--tenant", help="Tenant ID"),
    json: bool = typer.Option(False, "--json", help="JSON output"),
    reconcile: bool = typer.Option(True, "--reconcile/--no-reconcile", help="Reconcile project"),
    register: bool = typer.Option(True, "--register/--no-register", help="Register project"),
    install_runtime: bool = typer.Option(True, "--install-runtime/--no-install-runtime", help="Install runtime"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run"),
) -> dict[str, Any]:
    """Install/brownfield project."""
    return _project_migrate(
        project_path=project,
        mode=mode,
    )


@scaffold_app.command("greenfield")
def scaffold_greenfield_cmd(
    destination: str = typer.Argument(..., help="Destination path"),
    profile: str = typer.Option("default", "--profile", help="Profile name"),
    name: str = typer.Option("", "--name", "-n", help="Project name"),
    description: str = typer.Option("", "--description", "-d", help="Description"),
    include_act: bool = typer.Option(True, "--include-act/--no-act", help="Include ACT tools"),
    include_qa_tools: bool = typer.Option(True, "--include-qa/--no-qa", help="Include QA tools"),
    include_pm_tools: bool = typer.Option(True, "--include-pm/--no-pm", help="Include PM tools"),
    language: str = typer.Option("python", "--language", "-l", help="Language"),
    register: bool = typer.Option(False, "--register", help="Register project"),
    install_runtime: bool = typer.Option(False, "--install-runtime", help="Install runtime"),
    tenant: str = typer.Option("", "--tenant", help="Tenant ID"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run"),
    json: bool = typer.Option(False, "--json", help="JSON output"),
) -> dict[str, Any]:
    """Scaffold new greenfield project."""
    return scaffold_greenfield(destination, template=language)


@scaffold_app.command("brownfield")
def scaffold_brownfield_cmd(
    project: str = typer.Argument(..., help="Project path"),
    mode: str = typer.Option("agdd", "--mode", help="Migration mode"),
    template: str = typer.Option("auto", "--template", "-t", help="Template"),
    name: str = typer.Option("", "--name", "-n", help="Project name"),
    tenant: str = typer.Option("", "--tenant", help="Tenant ID"),
    json: bool = typer.Option(False, "--json", help="JSON output"),
    register: bool = typer.Option(True, "--register/--no-register", help="Register project"),
    install_runtime: bool = typer.Option(True, "--install-runtime/--no-install-runtime", help="Install runtime"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run"),
    reconcile: bool = typer.Option(True, "--reconcile/--no-reconcile", help="Reconcile"),
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
