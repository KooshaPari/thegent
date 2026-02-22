"""Logical stream: System State Synchronization.

# @trace WL-037
"""

import asyncio
from pathlib import Path

import typer
from rich.console import Console

from . import models

console = Console()
app = typer.Typer(help="Synchronize rules, DAG, and model catalog.")
gh_project_app = typer.Typer(help="GitHub Project v2 sync helpers (optional; disabled by default).")

app.add_typer(models.app, name="models", help="Manage custom models and providers.")
app.add_typer(gh_project_app, name="gh-project", help="Bidirectional sync with GitHub Projects v2.")


@app.command("all", help="Synchronize all system components.")
def sync_all(
    components: list[str] | None = typer.Option(None, "--component", "-c", help="Specific components to sync"),
    force: bool = typer.Option(False, "--force", "-f", help="Force synchronization"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Simulate synchronization"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)"),
):
    from thegent.cli.commands.cli_sync import sync_cmd_impl

    asyncio.run(sync_cmd_impl(components=components, force=force, dry_run=dry_run, format=format))


@app.command(
    "work-stream",
    help=(
        "Pull latest WORK_STREAM.md, merge local changes, and push back. "
        "Appends new items; preserves CLAIMED/COMPLETED status. (WL-037)"
    ),
)
def sync_work_stream_full(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Report changes without writing."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
):
    """``thegent sync work-stream`` — full work stream integration.

    # @trace WL-037
    """
    from thegent.commands.sync import SyncCommand, SyncOperationStatus

    root = (project or Path.cwd()).resolve()
    cmd = SyncCommand(project_root=root)
    op = cmd.sync_work_stream(dry_run=dry_run)

    if op.status == SyncOperationStatus.FAILED:
        console.print(f"[red]work-stream sync failed: {op.message}[/red]")
        for err in op.errors:
            console.print(f"[red]  {err}[/red]")
        raise typer.Exit(1)

    if dry_run:
        console.print(f"[yellow]Dry-run: {op.message}[/yellow]")
    else:
        console.print(f"[green]{op.message}[/green]")
        for change in op.changes[:10]:
            console.print(f"  [dim]{change}[/dim]")


@app.command(
    "rules",
    help=(
        "Alias for ``thegent rules sync``. Syncs canonical .thegent/rules/ to all platform-specific locations. (WL-037)"
    ),
)
def sync_rules(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Report what would be written without writing."),
    platform: str | None = typer.Option(None, "--platform", help="Platform: cursor|claude|codex|all (default: all)."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
):
    """``thegent sync rules`` — delegate to RulesSyncManager.

    # @trace WL-037
    """
    from thegent.commands.sync import SyncCommand, SyncOperationStatus

    root = (project or Path.cwd()).resolve()
    cmd = SyncCommand(project_root=root)
    op = cmd.sync_rules(dry_run=dry_run)

    if op.status == SyncOperationStatus.FAILED:
        console.print(f"[red]rules sync failed: {op.message}[/red]")
        for err in op.errors:
            console.print(f"[red]  {err}[/red]")
        raise typer.Exit(1)

    if dry_run:
        console.print(f"[yellow]Dry-run: {op.message}[/yellow]")
    else:
        console.print(f"[green]{op.message}[/green]")
        for change in op.changes[:20]:
            console.print(f"  [dim]{change}[/dim]")


@app.command(
    "research",
    help=(
        "Run ``plan incorporate`` then update WORK_STREAM.md BACKLOG "
        "from new fragments in docs/research/ and docs/plans/. (WL-037)"
    ),
)
def sync_research(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Report changes without writing."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
):
    """``thegent sync research`` — incorporate research fragments into WORK_STREAM.md.

    # @trace WL-037
    """
    from thegent.commands.sync import SyncCommand, SyncOperationStatus

    root = (project or Path.cwd()).resolve()
    cmd = SyncCommand(project_root=root)
    op = cmd.sync_research(dry_run=dry_run)

    if op.status == SyncOperationStatus.FAILED:
        console.print(f"[red]research sync failed: {op.message}[/red]")
        for err in op.errors:
            console.print(f"[red]  {err}[/red]")
        raise typer.Exit(1)

    if dry_run:
        console.print(f"[yellow]Dry-run: {op.message}[/yellow]")
    else:
        console.print(f"[green]{op.message}[/green]")
        details = op.details
        if details:
            console.print(
                f"  [dim]incorporate_merged={details.get('incorporate_merged', 0)}, "
                f"research_incorporated={details.get('research_incorporated', 0)}[/dim]"
            )


@app.command("dag", help="Synchronize DAG state from session meta files.")
def sync_dag(force: bool = typer.Option(False, "--force", "-f")):
    from thegent.cli.commands.cli_sync import sync_cmd_impl

    asyncio.run(sync_cmd_impl(components=["dag"], force=force))


@app.command("work", help="Incorporate new work items into WORK_STREAM.md (legacy alias; prefer work-stream).")
def sync_work(force: bool = typer.Option(False, "--force", "-f")):
    from thegent.cli.commands.cli_sync import sync_cmd_impl

    asyncio.run(sync_cmd_impl(components=["work-stream"], force=force))


@app.command("catalog", help="Update the model catalog by scraping providers.")
def sync_catalog(force: bool = typer.Option(False, "--force", "-f")):
    from thegent.cli.commands.cli_sync import sync_cmd_impl

    asyncio.run(sync_cmd_impl(components=["catalog"], force=force))


@app.command("update", help="Update system components and dependencies.")
def sync_update(
    components: list[str] | None = typer.Option(None, "--component", "-c", help="Specific components to update"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Simulate update"),
    force: bool = typer.Option(False, "--force", "-f", help="Force update"),
):
    from thegent.cli.commands.cli_sync import update_cmd_impl

    asyncio.run(update_cmd_impl(components=components, dry_run=dry_run, force=force))


@app.command("status", help="Show sync status and drift report. (FR-SYNC-039)")
def sync_status(
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
    output_format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)."),
):
    """``thegent sync status`` — report drift and sync state.

    # @trace FR-SYNC-039
    """
    from thegent.commands.sync import SyncCommand, SyncOperationStatus

    root = (project or Path.cwd()).resolve()
    cmd = SyncCommand(project_root=root)
    op = cmd.status()

    if output_format == "json":
        import json

        console.print(json.dumps({"ok": op.ok, "message": op.message, "changes": op.changes}))
        return

    if op.status == SyncOperationStatus.FAILED:
        console.print(f"[red]sync status failed: {op.message}[/red]")
        raise typer.Exit(1)

    color = "green" if op.ok else "yellow"
    console.print(f"[{color}]{op.message}[/{color}]")
    for change in op.changes[:20]:
        console.print(f"  [dim]{change}[/dim]")


@app.command("push", help="Push local config to remote sync target. (FR-SYNC-039)")
def sync_push(
    target: str | None = typer.Option(None, "--target", "-t", help="Remote target URL or identifier."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
):
    """``thegent sync push`` — push local state to remote.

    # @trace FR-SYNC-039
    """
    from thegent.commands.sync import SyncCommand, SyncOperationStatus

    root = (project or Path.cwd()).resolve()
    cmd = SyncCommand(project_root=root)
    op = cmd.push(target=target)

    if op.status == SyncOperationStatus.FAILED:
        console.print(f"[red]push failed: {op.message}[/red]")
        raise typer.Exit(1)

    console.print(f"[green]{op.message}[/green]")
    for change in op.changes[:20]:
        console.print(f"  [dim]{change}[/dim]")


@app.command("pull", help="Pull remote config to local. (FR-SYNC-040)")
def sync_pull(
    source: str | None = typer.Option(None, "--source", "-s", help="Remote source URL or identifier."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
):
    """``thegent sync pull`` — pull remote state to local.

    # @trace FR-SYNC-040
    """
    from thegent.commands.sync import SyncCommand, SyncOperationStatus

    root = (project or Path.cwd()).resolve()
    cmd = SyncCommand(project_root=root)
    op = cmd.pull(source=source)

    if op.status == SyncOperationStatus.FAILED:
        console.print(f"[red]pull failed: {op.message}[/red]")
        raise typer.Exit(1)

    console.print(f"[green]{op.message}[/green]")
    for change in op.changes[:20]:
        console.print(f"  [dim]{change}[/dim]")


@app.command("reset", help="Reset local sync state to clean baseline. (FR-SYNC-040)")
def sync_reset(
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirm reset without interactive prompt."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
):
    """``thegent sync reset`` — reset local sync state.

    # @trace FR-SYNC-040
    """
    from thegent.commands.sync import SyncCommand, SyncOperationStatus

    if not yes:
        console.print("[yellow]Pass --yes to confirm reset.[/yellow]")
        raise typer.Exit(1)

    root = (project or Path.cwd()).resolve()
    cmd = SyncCommand(project_root=root)
    op = cmd.reset()

    if op.status == SyncOperationStatus.FAILED:
        console.print(f"[red]reset failed: {op.message}[/red]")
        raise typer.Exit(1)

    console.print(f"[green]{op.message}[/green]")


@gh_project_app.command("status", help="Show GitHub Project sync readiness from THGENT_GH_PROJECT_* settings.")
def gh_project_status(
    output_format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)."),
) -> None:
    from thegent.config import ThegentSettings
    from thegent.integrations.gh_project_sync import config_from_settings, status

    result = status(config_from_settings(ThegentSettings()))
    if output_format == "json":
        import json

        console.print(json.dumps({"ok": result.ok, "message": result.message, "details": result.details, "errors": result.errors}))
        return

    color = "green" if result.ok else "red"
    console.print(f"[{color}]{result.message}[/{color}]")
    for key, value in result.details.items():
        console.print(f"  [dim]{key}={value}[/dim]")
    for err in result.errors:
        console.print(f"[red]  {err}[/red]")
    if not result.ok:
        raise typer.Exit(1)


@gh_project_app.command("sync", help="Run pull/push/both synchronization planning against GitHub Project and local WORK_STREAM.")
def gh_project_sync(
    direction: str = typer.Option("both", "--direction", "-d", help="Sync direction: pull|push|both."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Dry-run by default; use --apply to execute."),
    output_format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)."),
) -> None:
    from thegent.config import ThegentSettings
    from thegent.integrations.gh_project_sync import config_from_settings, sync_bidirectional

    normalized_direction = direction.strip().lower()
    if normalized_direction not in {"pull", "push", "both"}:
        console.print(f"[red]Invalid --direction: {direction}. Use pull|push|both.[/red]")
        raise typer.Exit(2)

    result = sync_bidirectional(
        config_from_settings(ThegentSettings()),
        direction=normalized_direction,  # type: ignore[arg-type]
        project_root=(project or Path.cwd()).resolve(),
        dry_run=dry_run,
    )
    if output_format == "json":
        import json

        console.print(json.dumps({"ok": result.ok, "message": result.message, "details": result.details, "errors": result.errors}))
        if not result.ok:
            raise typer.Exit(1)
        return

    color = "green" if result.ok else "red"
    console.print(f"[{color}]{result.message}[/{color}]")
    for key, value in result.details.items():
        console.print(f"  [dim]{key}={value}[/dim]")
    for err in result.errors:
        console.print(f"[red]  {err}[/red]")
    if not result.ok:
        raise typer.Exit(1)


@gh_project_app.command("export", help="Export GitHub Project items to CSV.")
def gh_project_export(
    output: Path = typer.Option(..., "--output", "-o", help="CSV output path."),
    limit: int = typer.Option(500, "--limit", "-L", min=1, max=5000, help="Maximum items to fetch."),
) -> None:
    from thegent.config import ThegentSettings
    from thegent.integrations.gh_project_sync import config_from_settings, export_csv

    result = export_csv(config_from_settings(ThegentSettings()), output=output, limit=limit)
    color = "green" if result.ok else "red"
    console.print(f"[{color}]{result.message}[/{color}]")
    for key, value in result.details.items():
        console.print(f"  [dim]{key}={value}[/dim]")
    for err in result.errors:
        console.print(f"[red]  {err}[/red]")
    if not result.ok:
        raise typer.Exit(1)


@gh_project_app.command("import", help="Import CSV rows into GitHub Project items (URL or draft issue title).")
def gh_project_import(  # noqa: A001 - typer command name should stay `import`
    input_path: Path = typer.Option(..., "--input", "-i", help="CSV input path."),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Dry-run by default; use --apply to execute."),
) -> None:
    from thegent.config import ThegentSettings
    from thegent.integrations.gh_project_sync import config_from_settings, import_csv_items

    result = import_csv_items(config_from_settings(ThegentSettings()), input_path=input_path, dry_run=dry_run)
    color = "green" if result.ok else "red"
    console.print(f"[{color}]{result.message}[/{color}]")
    for key, value in result.details.items():
        console.print(f"  [dim]{key}={value}[/dim]")
    for err in result.errors:
        console.print(f"[red]  {err}[/red]")
    if not result.ok:
        raise typer.Exit(1)


@app.command("autopilot", help="Run automatic bidirectional sync for WORK_STREAM.md <-> GitHub Projects <-> Linear.")
def sync_autopilot(
    once: bool = typer.Option(False, "--once", help="Run one cycle and exit."),
    interval_sec: int | None = typer.Option(None, "--interval", "-i", min=10, help="Polling interval in seconds."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
    allow_disabled: bool = typer.Option(
        False,
        "--allow-disabled",
        help="Exit successfully when autosync is disabled (useful for background service composition).",
    ),
) -> None:
    from thegent.config import ThegentSettings
    from thegent.integrations.workstream_autosync import run_autosync_loop

    settings = ThegentSettings()
    if not settings.workstream_autosync_enabled:
        if allow_disabled:
            console.print("[yellow]workstream autosync disabled; exiting (allow-disabled).[/yellow]")
            return
        console.print(
            "[red]workstream autosync disabled. Set THGENT_WORKSTREAM_AUTOSYNC_ENABLED=1 to enable.[/red]"
        )
        raise typer.Exit(1)

    effective_interval = interval_sec or settings.workstream_autosync_interval_sec
    root = (project or Path.cwd()).resolve()
    mode = "single-run" if once else f"daemon ({effective_interval}s interval)"
    console.print(f"[green]Starting workstream autosync: {mode}[/green]")
    run_autosync_loop(
        settings=settings,
        project_root=root,
        once=once,
        interval_sec=effective_interval,
    )
