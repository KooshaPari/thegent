"""System configuration management - Nix-like declarative system setup.

Usage:
    thegent system install --bundle dev
    thegent system install --target shells.zsh
    thegent system install --all
    thegent system verify
    thegent system status
"""

import typer
from rich.console import Console

system_app = typer.Typer(help="System configuration management (Nix-like)")
console = Console()


@system_app.callback(invoke_without_command=True)
def system_callback(ctx: typer.Context) -> None:
    """System configuration management."""


@system_app.command("install")
def system_install(
    target: str = typer.Option(
        "auto",
        "--target",
        "-t",
        help="Target: shells.zsh, tools.git, harnesses.claude-code, or comma-separated list. Use 'all' for everything, 'auto' for detected.",
    ),
    bundle: str = typer.Option(
        None,
        "--bundle",
        "-b",
        help="Install a bundle: core, dev, terminal, productivity, all",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be installed"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Install system configurations."""
    from thegent.cli.system import cmd_install
    import argparse

    args = argparse.Namespace(
        manifest=None,
        all=target == "all",
        bundle=bundle,
        target=target if target not in ("all", "auto") else None,
        auto=target == "auto",
        dry_run=dry_run,
        verbose=verbose,
    )

    exit(cmd_install(args))


@system_app.command("verify")
def system_verify(
    target: str = typer.Option(
        "auto",
        "--target",
        "-t",
        help="Target to verify, or 'all', or 'auto' for detected",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Verify installed configurations."""
    from thegent.cli.system import cmd_verify
    import argparse

    args = argparse.Namespace(
        manifest=None,
        all=target == "all",
        target=target if target not in ("all", "auto") else None,
        verbose=verbose,
    )

    exit(cmd_verify(args))


@system_app.command("status")
def system_status() -> None:
    """Show installation status."""
    from thegent.cli.system import cmd_status
    import argparse

    args = argparse.Namespace(manifest=None)
    exit(cmd_status(args))
