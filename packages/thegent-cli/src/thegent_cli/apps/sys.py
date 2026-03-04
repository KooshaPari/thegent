"""Logical stream: System and Lifecycle Operations."""

from __future__ import annotations

import orjson as json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from thegent_cli.apps.project import setup_project_app
from thegent_core.config import ThegentSettings

console = Console()
app = typer.Typer(help="System configuration, MCP servers, and daemon ops.")


# ---------------------------------------------------------------------------
# thegent sys setup project <subcommand>
# setup_app groups interactive setup (invoke_without_command) + project tenancy.
# ---------------------------------------------------------------------------

setup_app = typer.Typer(help="System setup and project tenancy.")
setup_app.add_typer(setup_project_app, name="project", help="Register and manage project tenants.")
app.add_typer(setup_app, name="setup", help="Interactive setup and project tenancy.")


@setup_app.callback(invoke_without_command=True)
def setup_app_callback(ctx: typer.Context) -> None:
    """Interactive system setup when no subcommand is given."""
    if ctx.invoked_subcommand is None:
        from thegent_cli.commands.cli import setup_cmd

        setup_cmd()


@app.command("mcp", help="Manage Model Context Protocol (MCP) servers.")
def sys_mcp(
    action: str = typer.Argument(..., help="Action (list|add|remove|prune|fix|migrate|migrate-unimount)"),
    server: str | None = typer.Option(None, "--server", "-s", help="Server name"),
    command: str | None = typer.Option(None, "--command", "-c", help="Command to run the server"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip interactive prompts for prune"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show prune actions without deleting"),
    parent_pid: int | None = typer.Option(None, "--parent-pid", help="Only prune children of this PID"),
    shadow_age_hours: int = typer.Option(24, "--shadow-age-hours", help="Prune .shadow-* older than N hours"),
    log_age_days: int = typer.Option(7, "--log-age-days", help="Prune .quality/logs older than N days"),
):
    from thegent_mcp.mcp.manage import (
        _get_mcp_url,
        install_to_client,
        migrate_to_unimount,
        remove_servers_from_client,
        FAILING_MCP_SERVERS,
        service_status,
    )
    from thegent_execution.orchestration.pruning.prune import mcp_prune

    settings = ThegentSettings()
    normalized = action.strip().lower()
    requested_clients = [part.strip().lower() for part in (server or "").split(",") if part.strip()]
    clients = requested_clients if requested_clients else ["cursor", "claude-code", "codex", "claude-desktop", "droid"]

    if normalized == "prune":
        mcp_prune(
            force=force,
            dry_run=dry_run,
            parent_pid=parent_pid,
            shadow_max_age_hours=shadow_age_hours,
            quality_log_max_age_days=log_age_days,
        )
        return

    if normalized == "list":
        ok, msg = service_status(settings)
        scope = getattr(settings, "mcp_scope", "project")
        console.print(f"MCP service: {'running' if ok else 'not-running'}")
        console.print(f"Scope: {scope}")
        console.print(f"Status: {msg}")
        console.print(f"URL: {_get_mcp_url(settings)}")
        return

    if normalized == "fix":
        if "all" in clients:
            clients = ["cursor", "claude-code", "codex", "claude-desktop", "droid"]
        for client in clients:
            ok, msg = remove_servers_from_client(
                client=client, server_names=sorted(FAILING_MCP_SERVERS), workspace=Path.cwd()
            )
            if not ok:
                console.print(f"[red]{msg}[/red]")
                raise typer.Exit(1)
            console.print(f"[green]{msg}[/green]")
        return

    if normalized in {"migrate", "migrate-unimount"}:
        for client in clients:
            ok, msg = migrate_to_unimount(client=client, mcp_url=_get_mcp_url(settings), workspace=Path.cwd())
            if not ok:
                console.print(f"[red]{msg}[/red]")
                raise typer.Exit(1)
            console.print(f"[green]{msg}[/green]")
        return

    if normalized == "add":
        if not server:
            raise typer.BadParameter("--server is required for action=add (e.g. codex|cursor|claude-code|droid)")
        url = command or _get_mcp_url(settings)
        ok, msg = install_to_client(client=server, url=url, workspace=Path.cwd())
        if not ok:
            console.print(f"[red]{msg}[/red]")
            raise typer.Exit(1)
        console.print(f"[green]{msg}[/green]")
        return

    if normalized == "remove":
        if not server:
            raise typer.BadParameter("--server is required for action=remove (target client)")
        target = command or "thegent"
        names = [n.strip() for n in target.split(",") if n.strip()]
        ok, msg = remove_servers_from_client(client=server, server_names=names, workspace=Path.cwd())
        if not ok:
            console.print(f"[red]{msg}[/red]")
            raise typer.Exit(1)
        console.print(f"[green]{msg}[/green]")
        return

    raise typer.BadParameter(f"Unknown action '{action}'. Expected: list|add|remove|prune|fix|migrate|migrate-unimount")


@app.command("lsp", help="Manage Language Server Protocol (LSP) processes.")
def sys_lsp(
    action: str = typer.Argument(..., help="Action (list|restart|prune)"),
    language: str | None = typer.Option(None, "--lang", "-l", help="Language identifier"),
):
    console.print("[yellow]LSP management is not yet implemented.[/yellow]")
    console.print("Use 'thegent lsp' command instead.")


@app.command("cp", help="Manage the Thegent control-plane daemon.")
def sys_cp(
    action: str = typer.Argument(..., help="Action (status|start|stop|restart)"),
):
    console.print("[yellow]Control plane management is not yet implemented.[/yellow]")
    console.print("Use 'thegent ps' to see running processes.")


@app.command("session", help="Manage agent background sessions and artifacts.")
def sys_session(
    action: str = typer.Argument(..., help="Action (list|prune|archive)"),
    session_id: str | None = typer.Option(None, "--id", "-i", help="Specific session ID"),
):
    from thegent_cli.commands.cli import session_cmd

    session_cmd(session_id=session_id, action=action)


@app.command("config", help="View or modify system configuration.")
def sys_config(
    action: str = typer.Argument("view", help="Action (view|set|unset)"),
    key: str | None = typer.Option(None, "--key", "-k", help="Configuration key"),
    value: str | None = typer.Option(None, "--value", "-v", help="Configuration value"),
):
    console.print("[yellow]Config management is not yet implemented.[/yellow]")
    console.print("Use 'thegent config' command instead.")


@app.command("terminal", help="Manage managed terminal sessions.")
def sys_terminal(
    action: str = typer.Argument("list", help="Action (list|open|prune)"),
    name: str | None = typer.Option(None, "--name", "-n", help="Terminal session name"),
):
    console.print("[yellow]Terminal management is not yet implemented.[/yellow]")


@app.command("shadow", help="Manage git shadow worktrees for agent isolation.")
def sys_shadow(
    action: str = typer.Argument("status", help="Action (status|cleanup|stats)"),
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
):
    """Manage git shadow worktrees.

    Shadows use git worktrees (NOT file copying) for efficient isolation.
    - Active worktrees share .git objects (no disk duplication)
    - Orphaned directories are cleaned up on demand

    Actions:
        status  - Show current shadow worktree status
        cleanup - Remove orphaned shadow directories
        stats   - Detailed statistics about shadows
    """
    from thegent_execution.orchestration.shadow import cleanup_shadows, get_shadow_stats

    repo_path = Path(path).resolve()

    if action == "status":
        stats = get_shadow_stats(repo_path)

        table = Table(title="Shadow Worktree Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Active Worktrees", str(stats["active_worktrees"]))
        table.add_row("Orphaned Dirs", str(stats["orphaned_dirs"]))
        table.add_row("Disk Usage", f"{stats['disk_usage_bytes'] / 1024 / 1024:.2f} MB")

        console.print(table)

        if stats["orphaned_dirs"] > 0:
            console.print(f"\n[yellow]Warning: {stats['orphaned_dirs']} orphaned directories found.[/yellow]")
            console.print("[yellow]   Run 'thegent sys shadow cleanup' to remove them.[/yellow]")

    elif action == "cleanup":
        result = cleanup_shadows(repo_path)
        console.print(f"[green]{result['message']}[/green]")

    elif action == "stats":
        stats = get_shadow_stats(repo_path)
        console.print(json.dumps(stats, indent=2).decode().decode())

    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        console.print("Valid actions: status, cleanup, stats")
        raise typer.Exit(1)
