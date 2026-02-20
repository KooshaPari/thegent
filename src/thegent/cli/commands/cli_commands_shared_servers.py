"""
CLI Commands for Shared Server Management
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from thegent.shared_mcp_manager import check_mcp_health, get_server_scope
from thegent.shared_server_integration import get_session_server_info

console = Console()
shared_app = typer.Typer(name="shared", help="Manage shared LSP/MCP servers")


@shared_app.command("status")
def shared_status(project_root: str = typer.Option(None, "--project", help="Project root path")):
    """Show status of shared servers."""
    proj_path = Path(project_root) if project_root else None

    info = get_session_server_info(project_root=proj_path)

    table = Table(title="Shared Server Status")
    table.add_column("Server", style="cyan")
    table.add_column("Scope", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Details", style="white")

    # MCP Status
    mcp_info = info["mcp"]
    mcp_health = mcp_info["health"]
    table.add_row(
        "MCP",
        mcp_info["scope"],
        "✅ Healthy" if mcp_health[0] else "❌ Unhealthy",
        mcp_info["url"] if mcp_health[0] else mcp_health[1],
    )

    # LSP Status
    lsp_info = info["lsp"]
    table.add_row("LSP", lsp_info["scope"], "✅ Configured", f"Lockfile: {lsp_info['lockfile']}")

    console.print(table)


@shared_app.command("health")
def shared_health(project_root: str = typer.Option(None, "--project", help="Project root path")):
    """Check health of shared servers."""
    proj_path = Path(project_root) if project_root else None

    is_healthy, message = check_mcp_health(project_root=proj_path)

    if is_healthy:
        console.print(f"✅ [green]{message}[/green]")
    else:
        console.print(f"❌ [red]{message}[/red]")


@shared_app.command("scope")
def shared_scope(project_root: str = typer.Option(None, "--project", help="Project root path")):
    """Show server scope (system-wide or project-scoped)."""
    proj_path = Path(project_root) if project_root else None

    scope_type, lockfile = get_server_scope(project_root=proj_path)

    console.print(f"Scope: [cyan]{scope_type}[/cyan]")
    console.print(f"Lockfile: [white]{lockfile}[/white]")

    if scope_type == "system":
        console.print("\n[green]✓[/green] Using system-wide shared server")
    else:
        console.print("\n[yellow]⚠[/yellow] Using project-scoped server")
        console.print(f"   Project: {proj_path}")
