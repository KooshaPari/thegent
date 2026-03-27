"""Dotfiles CLI commands for thegent."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from thegent.dotfiles.manager import (
    TEMPLATES_DIR,
    get_profiles,
    install_profile,
    install_tool,
    list_tools,
)

app = typer.Typer(name="dotfiles", help="Manage dotfiles from thegent templates.")
console = Console()


@app.command("ls")
def cmd_ls(
    filter_prefix: Optional[str] = typer.Argument(None, help="Optional prefix filter (e.g. 'rust')"),
) -> None:
    """List all available tool configs in templates/shared/."""
    tools = list_tools()
    if filter_prefix:
        tools = [t for t in tools if t.startswith(filter_prefix)]

    table = Table("Tool", "Type", "Templates Root", show_header=True)
    for t in tools:
        path = TEMPLATES_DIR / t
        kind = "file" if path.is_file() else "dir"
        table.add_row(t, kind, str(TEMPLATES_DIR))
    console.print(table)
    console.print(f"\n[dim]{len(tools)} tool(s) available[/dim]")


@app.command("install")
def cmd_install(
    tool: Optional[str] = typer.Argument(None, help="Tool name (matches templates/shared/<tool>)"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Install a named profile"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be deployed without writing"),
    backup: bool = typer.Option(True, "--backup/--no-backup", help="Backup existing files to *.bak"),
) -> None:
    """Install dotfiles for a specific tool or a named profile."""
    if not profile and not tool:
        console.print("[red]Specify a tool name or --profile <name>[/red]")
        raise typer.Exit(1)

    if dry_run:
        console.print("[yellow]Dry run — no files will be written[/yellow]")

    if profile:
        try:
            results = install_profile(profile, dry_run=dry_run, backup=backup)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
    else:
        results = [install_tool(tool, dry_run=dry_run, backup=backup)]  # type: ignore[arg-type]

    any_error = False
    for r in results:
        status = r["status"]
        tool_name = r["tool"]
        files = r.get("files", [])
        if status in ("installed", "dry_run"):
            icon = "[green]✓[/green]"
            label = "would install" if dry_run else "installed"
            console.print(f"{icon} [bold]{tool_name}[/bold]: {label} ({len(files)} file(s))")
            for f in files:
                console.print(f"    [dim]{f}[/dim]")
        elif status == "not_found":
            console.print(f"[red]✗[/red] [bold]{tool_name}[/bold]: not found in templates/shared/")
            any_error = True
        elif status == "empty":
            console.print(f"[yellow]~[/yellow] [bold]{tool_name}[/bold]: no files to deploy (template dir is empty)")
        else:
            console.print(f"[red]✗[/red] [bold]{tool_name}[/bold]: unexpected status '{status}'")
            any_error = True

    if any_error:
        raise typer.Exit(1)


@app.command("profiles")
def cmd_profiles() -> None:
    """List available deployment profiles and their tools."""
    profiles = get_profiles()
    table = Table("Profile", "Tools", "Description", show_header=True)
    for name, cfg in profiles.items():
        tools = cfg.get("tools", [])
        desc = cfg.get("description", "")
        table.add_row(name, ", ".join(tools), desc)
    console.print(table)


@app.command("status")
def cmd_status(
    tool: Optional[str] = typer.Argument(None, help="Tool to check (omit for all)"),
) -> None:
    """Show which dotfiles are currently deployed at ~/."""
    tools = [tool] if tool else list_tools()
    table = Table("Tool", "File", "Deployed", show_header=True)
    for t in tools:
        tool_path = TEMPLATES_DIR / t
        if tool_path.is_file():
            dst = Path.home() / t
            table.add_row(t, str(dst), "[green]yes[/green]" if dst.exists() else "[dim]no[/dim]")
        elif tool_path.is_dir():
            for src in sorted(tool_path.rglob("*")):
                if src.is_file():
                    dst = Path.home() / src.relative_to(tool_path)
                    table.add_row(t, str(dst), "[green]yes[/green]" if dst.exists() else "[dim]no[/dim]")
    console.print(table)
