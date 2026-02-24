"""Project CLI app - project management commands."""

import typer
from typing import Any, Optional

from thegent.project.migrate import project_migrate as _project_migrate
from thegent.project.scaffold import (
    scaffold_greenfield,
    scaffold_brownfield,
)

# CLI app containers
setup_project_app = typer.Typer(help="Project management commands.")
install_app = typer.Typer(help="Install user/system assets and project runtime installation.")
scaffold_app = typer.Typer(help="Scaffold new project.")
update_app = typer.Typer(help="Update project.")


@install_app.callback(invoke_without_command=True)
def install_callback(
    ctx: typer.Context,
    target: Optional[str] = typer.Option(None, "--target", help="Target to install"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Installation mode"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    url: Optional[str] = typer.Option(None, "--url", help="Install URL"),
    install_service: bool = typer.Option(False, "--install-service", help="Install as service"),
) -> None:
    """Legacy install command."""
    if ctx.invoked_subcommand is None:
        try:
            from thegent.install import run_install
            run_install(target=target, mode=mode, dry_run=dry_run, verbose=verbose, url=url, install_service=install_service)
        except Exception:
            typer.echo("Use 'thegent install project' for project installation.")


@install_app.command("project")
def install_project(
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
    legacy_mode: str = typer.Option(None, "--mode"),
) -> dict[str, Any]:
    """Install/brownfield project."""
    return project_migrate(project=project, mode=legacy_mode or mode, template=template, name=name, tenant=tenant)


@scaffold_app.command("greenfield")
def scaffold_greenfield_cmd(
    destination: str = typer.Argument(..., help="Destination"),
    profile: str = typer.Option("default", "--profile"),
    name: str = typer.Option("", "--name", "-n"),
    language: str = typer.Option("python", "--language", "-l"),
    tenant: str = typer.Option("", "--tenant"),
) -> dict[str, Any]:
    """Scaffold new project."""
    return project_scaffold(destination=destination, profile=profile, name=name, language=language, tenant=tenant)


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
    return project_migrate(project=project, mode=mode, template=template, name=name, tenant=tenant)


def project_migrate(**kwargs: Any) -> dict[str, Any]:
    """Entry point for tests."""
    return _project_migrate(project_path=kwargs.get("project", ""), mode=kwargs.get("mode", "agdd"))


def project_scaffold(**kwargs: Any) -> dict[str, Any]:
    """Entry point for tests."""
    return scaffold_greenfield(kwargs.get("destination", ""), template=kwargs.get("language", "python"))
