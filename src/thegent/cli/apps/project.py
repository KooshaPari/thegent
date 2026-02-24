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


# Callback for backward compatibility with old `install` command
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
    """Legacy install command - routes to thegent.install.run_install."""
    # If no subcommand, show help or handle legacy case
    if ctx.invoked_subcommand is None:
        # Try to import and call legacy install
        try:
            from thegent.install import run_install
            run_install(
                target=target,
                mode=mode,
                dry_run=dry_run,
                verbose=verbose,
                url=url,
                install_service=install_service,
            )
        except Exception:
            typer.echo("Use 'thegent install project' for project installation.")


@install_app.command("project")
def install_project(
    mode: str = typer.Argument("agdd", help="brownfield, agdd, none"),
    project: str = typer.Argument(..., help="Project path"),
    template: str = typer.Option("auto", "--template", "-t", help="Template to use"),
    name: str = typer.Option("", "--name", "-n", help="Project name"),
    tenant: str = typer.Option("", "--tenant", help="Tenant ID"),
    json: bool = typer.Option(False, "--json", help="JSON output"),
    # Legacy option for backward compatibility
    legacy_mode: str = typer.Option(None, "--mode", help="(ignored)"),
) -> dict[str, Any]:
    """Install/brownfield project migration."""
    effective_mode = legacy_mode or mode
    return project_migrate(project=project, mode=effective_mode, template=template, name=name, tenant=tenant)


@scaffold_app.command("greenfield")
def scaffold_greenfield_cmd(
    destination: str = typer.Argument(..., help="Destination path"),
    profile: str = typer.Option("default", "--profile", help="Profile name"),
    name: str = typer.Option("", "--name", "-n", help="Project name"),
    language: str = typer.Option("python", "--language", "-l", help="Language"),
    tenant: str = typer.Option("", "--tenant", help="Tenant ID"),
) -> dict[str, Any]:
    """Scaffold new greenfield project."""
    return project_scaffold(destination=destination, profile=profile, name=name, language=language, tenant=tenant)


@scaffold_app.command("brownfield")
def scaffold_brownfield_cmd(
    project: str = typer.Argument(..., help="Project path"),
    mode: str = typer.Option("agdd", "--mode", help="Migration mode"),
    template: str = typer.Option("auto", "--template", "-t", help="Template"),
    name: str = typer.Option("", "--name", "-n", help="Project name"),
    tenant: str = typer.Option("", "--tenant", help="Tenant ID"),
    json: bool = typer.Option(False, "--json", help="JSON output"),
) -> dict[str, Any]:
    """Scaffold brownfield project."""
    return project_scaffold(destination=project, profile=mode, name=name, language=template, tenant=tenant)


# Module-level aliases for test mocking
def project_migrate(**kwargs: Any) -> dict[str, Any]:
    """Entry point for project migration (used by CLI tests)."""
    return _project_migrate(
        project_path=kwargs.get("project", ""),
        mode=kwargs.get("mode", "agdd"),
    )


def project_scaffold(**kwargs: Any) -> dict[str, Any]:
    """Entry point for project scaffolding (used by CLI tests)."""
    return scaffold_greenfield(kwargs.get("destination", ""), template=kwargs.get("language", "python"))
