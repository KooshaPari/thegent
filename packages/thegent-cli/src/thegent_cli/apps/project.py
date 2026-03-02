"""First-class project tenancy commands: sys setup project and install project.

This module defines the typer app objects and re-exports all command
implementations from project_commands.py for backward compatibility.

# @trace FR-TEN-001
"""

from __future__ import annotations

import typer
from rich.console import Console

console = Console()

# ---------------------------------------------------------------------------
# Sub-typer: thegent sys setup project <subcommand>
# ---------------------------------------------------------------------------

setup_project_app = typer.Typer(
    help="Register and manage projects with first-class tenant isolation.",
    no_args_is_help=True,
)

# ---------------------------------------------------------------------------
# Sub-typer: thegent install project
# ---------------------------------------------------------------------------

install_project_app = typer.Typer(
    help="Install Thegent runtime assets into a registered project directory.",
    no_args_is_help=True,
)


install_app = typer.Typer(
    help="Install user/system assets and project runtime assets.",
)
install_app.add_typer(install_project_app, name="project", help="Install Thegent runtime assets into a project.")

update_project_app = typer.Typer(
    help="Update Thegent runtime assets for registered or brownfield projects.",
    no_args_is_help=True,
)
update_app = typer.Typer(
    help="Update user/system assets and project runtime assets.",
)
update_app.add_typer(update_project_app, name="project", help="Update Thegent runtime assets in a project.")


scaffold_app = typer.Typer(
    help="Project scaffolding: greenfield bootstrap and brownfield migration.",
    no_args_is_help=True,
)

# Import all command implementations -- decorators register them on the app objects above.
from thegent_cli.apps.project_commands import (  # noqa: E402, F401
    install_callback,
    install_project_brownfield,
    install_project_brownfield_agdd,
    install_project_cmd,
    install_project_none,
    project_doctor,
    project_init,
    project_list,
    project_migrate,
    project_scaffold,
    project_scaffold_profiles,
    project_show,
    scaffold_brownfield,
    scaffold_brownfield_agdd,
    scaffold_brownfield_none,
    scaffold_greenfield,
    setup_project_brownfield,
    setup_project_brownfield_agdd,
    setup_project_brownfield_none,
    setup_project_greenfield,
    update_callback,
    update_project_brownfield,
    update_project_brownfield_agdd,
    update_project_cmd,
    update_project_none,
)
