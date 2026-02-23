"""Top-level MCP command namespace.

This module exposes MCP lifecycle and migration commands directly under `thegent mcp`.
It mirrors the existing `thegent sys mcp` behavior while adding first-class subcommands
that are expected across tests/docs (install/up/down/prune/service/migrate etc.).
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from thegent.config import ThegentSettings
from thegent.mcp.hotreload import run_prod_hotreload
from thegent.mcp.manage import (
    migrate_to_unimount,
    mcp_down,
    mcp_restart,
    mcp_up,
    prune_periodic_install,
    prune_periodic_start,
    prune_periodic_status,
    prune_periodic_stop,
    prune_periodic_uninstall,
    remove_servers_from_client,
    service_install,
    service_uninstall,
    service_start,
    service_status,
    service_stop,
)
from thegent.orchestration.pruning.prune import mcp_prune

console = Console()
app = typer.Typer(help="Top-level MCP management and migration commands.")


def _parse_clients(raw: str | None) -> list[str]:
    if not raw:
        return ["cursor", "claude-code", "codex", "claude-desktop", "droid"]
    return [part.strip().lower() for part in raw.split(",") if part.strip()]


@app.command("install", help="Install thegent MCP entry into one or more clients.")
def mcp_install(
    target: str = typer.Argument("all", help="Client(s) to install: cursor|claude-code|codex|droid|claude-desktop|all"),
    url: str | None = typer.Option(None, "--url", help="MCP URL override (default: current settings URL)"),
    workspace: Path | None = typer.Option(None, "--workspace", help="Workspace for local client configs"),
) -> None:
    from thegent.mcp.manage import install_to_client

    requested = _parse_clients(None if target == "all" else target)
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    mcp_url = url or f"http://{settings.mcp_host}:{settings.mcp_port}/mcp"
    for client in requested:
        ok, msg = install_to_client(client, mcp_url, workspace=workspace)
        if not ok:
            console.print(f"[red]{msg}[/red]")
            raise typer.Exit(1)
        console.print(f"[green]{msg}[/green]")


@app.command("up", help="Start MCP + proxy services.")
def mcp_up_cmd() -> None:
    ok, msg = mcp_up()
    console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")
    raise typer.Exit(0 if ok else 1)


@app.command("down", help="Stop MCP + proxy services.")
def mcp_down_cmd() -> None:
    ok, msg = mcp_down()
    console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")
    raise typer.Exit(0 if ok else 1)


@app.command("restart", help="Restart MCP + proxy services.")
def mcp_restart_cmd() -> None:
    ok, msg = mcp_restart()
    console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")
    raise typer.Exit(0 if ok else 1)


@app.command("reload", help="Alias for restart (MCP + proxy services).")
def mcp_reload_cmd() -> None:
    ok, msg = mcp_restart()
    console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")
    raise typer.Exit(0 if ok else 1)


@app.command("hmr", help="Hot-reload MCP + proxy on source/config changes.")
def mcp_hmr_cmd(
    project_root: Path = typer.Option(
        Path.cwd(),
        "--project-root",
        help="Project root to watch (defaults to current working directory).",
    ),
    debounce_s: float = typer.Option(
        1.5,
        "--debounce",
        min=0.1,
        help="Minimum seconds between automatic restarts.",
    ),
) -> None:
    try:
        run_prod_hotreload(project_root=project_root, debounce_s=debounce_s)
    except Exception as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc


@app.command("status", help="Show MCP service status.")
def mcp_status() -> None:
    settings = ThegentSettings()
    ok, msg = service_status(settings)
    console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")
    console.print(f"URL: {'http://' + settings.mcp_host + ':' + str(settings.mcp_port) + '/mcp'}")
    raise typer.Exit(0 if ok else 1)


@app.command("service", help="Run MCP service lifecycle commands.")
def mcp_service(
    action: str = typer.Argument("install", help="Action: install|start|stop|status|uninstall"),
) -> None:
    normalized = action.strip().lower()
    if normalized == "install":
        ok, msg = service_install()
    elif normalized == "start":
        ok, msg = service_start()
    elif normalized == "stop":
        ok, msg = service_stop()
    elif normalized == "status":
        ok, msg = service_status(ThegentSettings())
    elif normalized == "uninstall":
        ok, msg = service_uninstall()
    else:
        console.print("[red]Action must be one of: install|start|stop|status|uninstall[/red]")
        raise typer.Exit(2)

    console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")
    raise typer.Exit(0 if ok else 1)


@app.command("fix", help="Remove old/broken MCP server entries (playwright).")
def mcp_fix(
    client: str | None = typer.Option(
        None,
        "--client",
        "--server",
        help="Comma-separated client list (default: all).",
    ),
) -> None:
    requested = _parse_clients(client)
    for target in requested:
        ok, msg = remove_servers_from_client(
            client=target,
            server_names=["playwright"],
            workspace=Path.cwd(),
        )
        if not ok:
            console.print(f"[red]{msg}[/red]")
            raise typer.Exit(1)
        console.print(f"[green]{msg}[/green]")


@app.command("migrate-unimount", help="Preserve existing MCP entries and align thegent/codex_apps URLs.")
def mcp_migrate_unimount(
    client: str = typer.Option(
        "all",
        "--client",
        help="Target client(s): cursor|claude-code|codex|droid|claude-desktop|all",
    ),
    url: str | None = typer.Option(None, "--url", help="Override MCP URL (defaults to ThegentSettings().mcp_url)."),
    workspace: Path | None = typer.Option(None, "--workspace", help="Override workspace for local config writes"),
) -> None:
    settings = ThegentSettings()
    requested = _parse_clients(None if client == "all" else client)
    mcp_url = url or f"http://{settings.mcp_host}:{settings.mcp_port}/mcp"
    for target in requested:
        ok, msg = migrate_to_unimount(client=target, mcp_url=mcp_url, workspace=workspace or Path.cwd())
        if not ok:
            console.print(f"[red]{msg}[/red]")
            raise typer.Exit(1)
        console.print(f"[green]{msg}[/green]")


@app.command("prune", help="Prune stale MCP/LSP resources.")
def mcp_prune_cmd(
    force: bool = typer.Option(False, "--force", "-f", help="Skip prompts"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show candidate processes only"),
    parent_pid: int | None = typer.Option(None, "--parent-pid", help="Prune children of this PID only"),
    shadow_age_hours: int = typer.Option(24, "--shadow-age-hours", help="Shadow expiry (hours)"),
    log_age_days: int = typer.Option(7, "--log-age-days", help="Session log expiry (days)"),
) -> None:
    mcp_prune(
        force=force,
        dry_run=dry_run,
        parent_pid=parent_pid,
        shadow_max_age_hours=shadow_age_hours,
        quality_log_max_age_days=log_age_days,
    )
    console.print("[green]prune completed[/green]")


@app.command("prune-periodic", help="Manage periodic prune daemon.")
def mcp_prune_periodic(
    action: str = typer.Argument("status", help="Action: install|start|stop|status|uninstall"),
) -> None:
    normalized = action.strip().lower()
    if normalized == "install":
        ok, msg = prune_periodic_install()
    elif normalized == "start":
        ok, msg = prune_periodic_start()
    elif normalized == "stop":
        ok, msg = prune_periodic_stop()
    elif normalized == "status":
        ok, msg = prune_periodic_status()
    elif normalized == "uninstall":
        ok, msg = prune_periodic_uninstall()
    else:
        console.print("[red]Action must be install|start|stop|status|uninstall[/red]")
        raise typer.Exit(2)

    console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")
    raise typer.Exit(0 if ok else 1)


@app.command("introspect", help="Inspect shared MCP daemon health.")
def mcp_introspect() -> None:
    from thegent.shared_mcp_manager import check_mcp_health

    ok, msg = check_mcp_health()
    console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")
    raise typer.Exit(0 if ok else 1)


@app.command("spotlight-exclude", help="Configure macOS spotlight exclusions for MCP runtime paths.")
def mcp_spotlight_exclude() -> None:
    console.print("[yellow]spotlight-exclude is planned and tracked in SWARM optimization docs.[/yellow]")
    console.print("[dim]Use [bold]thegent mcp fix[/bold] for current known MCP cleanup tasks.[/dim]")


@app.command("mcp-stdio", help="Start MCP over stdio transport (not yet implemented).")
def mcp_stdio() -> None:
    console.print("[yellow]thegent mcp-stdio is not implemented in this branch yet.[/yellow]")
    console.print("[dim]Use `thegent mcp up` while stdio support is being finalized.[/dim]")
