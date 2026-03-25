"""Installation wizard functions for thegent.

Interactive installation and configuration wizard.
Extracted from install.py for maintainability.
"""

from __future__ import annotations

import logging
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm, Prompt


logger = logging.getLogger(__name__)
console = Console()


def _get_thegent_root() -> Path:
    """Get the thegent repository root."""
    # Find the repository root
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    return Path.cwd()


def run_wizard(url: str | None = None) -> None:
    """Run the interactive installation wizard.

    Args:
        url: Optional project URL to install
    """
    console.print("\n[bold cyan]thegent Installation Wizard[/bold cyan]\n")

    # Step 1: Check system dependencies
    console.print("[bold]Step 1: System Dependencies[/bold]")
    from thegent.install_system import install_system_dependencies, verify_mise_installation

    if not verify_mise_installation(console):
        install_system_dependencies(console)

    # Step 2: Setup hooks
    console.print("\n[bold]Step 2: Git Hooks[/bold]")
    if Confirm.ask("Setup git hooks?", default=True):
        from thegent.install_hooks import setup_hooks

        setup_hooks(verbose=True)

    # Step 3: Setup skills
    console.print("\n[bold]Step 3: Skills[/bold]")
    if Confirm.ask("Install factory skills?", default=True):
        from thegent.install_hooks import setup_skills

        root = _get_thegent_root()
        setup_skills(root / "skills", verbose=True)

    # Step 4: MCP configuration
    console.print("\n[bold]Step 4: MCP Configuration[/bold]")
    if Confirm.ask("Configure MCP servers?", default=False):
        _configure_mcp_wizard()

    # Step 5: Project setup
    if url:
        console.print("\n[bold]Step 5: Project Setup[/bold]")
        console.print(f"Installing project: {url}")
        run_install_project(url)
    else:
        console.print("\n[bold]Step 5: Project Setup[/bold]")
        if Confirm.ask("Install a project?", default=False):
            project_url = Prompt.ask("Project URL or path")
            run_install_project(project_url)

    console.print("\n[green]✓ Installation complete![/green]")


def run_install_project(
    project_path: str,
    bundle: str = "default",
    mode: str = "smart",
    dry_run: bool = False,
) -> bool:
    """Install thegent into a project.

    Args:
        project_path: Path or URL to project
        bundle: Bundle to install
        mode: Installation mode (smart, force, editable)
        dry_run: If True, don't make changes

    Returns:
        True if successful
    """
    from thegent.install_bundles import resolve_bundles
    from thegent.install_manager import InstallManager
    from thegent.install_models import InstallMode

    console.print(f"\n[cyan]Installing thegent into: {project_path}[/cyan]")

    # Resolve project path
    path = Path(project_path).expanduser().resolve()
    if not path.exists():
        console.print(f"[red]Project path not found: {path}[/red]")
        return False

    # Create manager
    manager = InstallManager(dry_run=dry_run, verbose=True)

    # Map mode string to enum
    mode_map = {
        "smart": InstallMode.SMART,
        "force": InstallMode.FORCE,
        "editable": InstallMode.EDITABLE,
        "interactive": InstallMode.INTERACTIVE,
    }
    install_mode = mode_map.get(mode.lower(), InstallMode.SMART)

    thegent_root = _get_thegent_root()
    resolved_items = resolve_bundles(
        bundle_names=[bundle],
        bundle_manifest=None,
        thegent_root=thegent_root,
        home=path,
        cwd=path,
        fallback_mode=install_mode,
    )

    for source, target, item_mode in resolved_items:
        result = manager.install_file(source, target, item_mode)
        if result.name == "ERROR":
            console.print(f"[red]Failed: {target}[/red]")

    manager.save_manifest()

    console.print(f"[green]✓ Installed {len(resolved_items)} files[/green]")
    return True


def run_install_system(
    console: Console | None = None,
    dry_run: bool = False,
) -> tuple[bool, str]:
    """Install system dependencies.

    Args:
        console: Rich console for output
        dry_run: If True, don't make changes

    Returns:
        Tuple of (success, message)
    """
    from thegent.install_system import install_system_dependencies

    return install_system_dependencies(console, dry_run)


def run_install(
    target: str = "all",
    bundle: str = "default",
    mode: str = "smart",
    dry_run: bool = False,
    url: str | None = None,
) -> bool:
    """Run full installation.

    Args:
        target: What to install (all, system, project, hooks)
        bundle: Bundle to install
        mode: Installation mode
        dry_run: If True, don't make changes
        url: Optional project URL

    Returns:
        True if successful
    """
    console = Console()

    targets = target.split(",") if "," in target else [target]

    success = True

    if "all" in targets or "system" in targets:
        console.print("\n[bold]Installing system dependencies...[/bold]")
        ok, msg = run_install_system(console, dry_run)
        if ok:
            console.print(f"[green]✓ {msg}[/green]")
        else:
            console.print(f"[red]✗ {msg}[/red]")
            success = False

    if "all" in targets or "hooks" in targets:
        console.print("\n[bold]Setting up hooks...[/bold]")
        from thegent.install_hooks import setup_hooks

        result = setup_hooks(dry_run=dry_run, verbose=True)
        console.print(f"[green]✓ Hooks: {result}[/green]")

    if "all" in targets or "project" in targets:
        if url:
            console.print("\n[bold]Installing project...[/bold]")
            ok = run_install_project(url, bundle, mode, dry_run)
            if not ok:
                success = False
        else:
            console.print("[yellow]No project URL specified, skipping project install[/yellow]")

    return success


def _configure_mcp_wizard() -> None:
    """Run MCP configuration wizard."""
    console.print("\n[cyan]MCP Server Configuration[/cyan]")

    from thegent.mcp.manage import service_install

    servers = [("thegent", "thegent MCP service")]

    for server_name, description in servers:
        if Confirm.ask(f"Configure {server_name} ({description})?", default=False):
            try:
                ok, message = service_install()
                if ok:
                    console.print(f"[green]✓ {server_name} configured[/green]")
                else:
                    console.print(f"[red]✗ Failed to configure {server_name}: {message}[/red]")
            except Exception as e:
                console.print(f"[red]✗ Failed to configure {server_name}: {e}[/red]")


__all__ = [
    "run_wizard",
    "run_install_project",
    "run_install_system",
    "run_install",
]
