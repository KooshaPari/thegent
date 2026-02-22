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

app.add_typer(models.app, name="models", help="Manage custom models and providers.")


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


@app.command("board", help="Synchronize GitHub Projects/Linear board state. (WL-159)")
def sync_board(
    board_id: str | None = typer.Option(None, "--board", "-b", help="Board ID (GitHub project number or Linear key)."),
    source: str | None = typer.Option("github", "--source", "-s", help="Board source: github|linear (default: github)."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Report changes without writing."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
):
    """``thegent sync board`` — synchronize cross-repo board state.

    Operationalize repeatable board update/import flow using native tooling.
    Syncs local WORK_STREAM.md status with GitHub Projects or Linear issues.

    # @trace WL-159
    """
    from thegent.commands.sync import SyncCommand, SyncOperationStatus

    root = (project or Path.cwd()).resolve()
    cmd = SyncCommand(project_root=root)
    op = cmd.sync_board(board_id=board_id, source=source or "github", dry_run=dry_run)

    if op.status == SyncOperationStatus.FAILED:
        console.print(f"[red]board sync failed: {op.message}[/red]")
        for err in op.errors:
            console.print(f"[red]  {err}[/red]")
        raise typer.Exit(1)

    if dry_run:
        console.print(f"[yellow]Dry-run: {op.message}[/yellow]")
    else:
        console.print(f"[green]{op.message}[/green]")

    for change in op.changes[:20]:
        console.print(f"  [dim]{change}[/dim]")


@app.command("audit", help="Audit sync policies and print current configuration. (WL-261)")
def sync_audit(
    format: str = typer.Option("json", "--format", "-F", help="Output format (json|table)."),
):
    """``thegent sync audit`` — validate runtime behavior against sync-policy contract.

    Prints current sync policies (enabled connectors, quota budgets, policy modes)
    as JSON or formatted table.

    # @trace WL-261
    """
    from thegent.integrations.sync_auditor import SyncAuditor

    auditor = SyncAuditor()

    # Read from config (stub for now; in production would load from config file)
    # This is a minimal implementation; actual config loading would be added
    auditor.set_enabled_connectors([])
    auditor.set_quota_budgets({})
    auditor.set_policy_modes({})

    if format == "json":
        console.print(auditor.audit_as_json())
    elif format == "table":
        audit_result = auditor.audit_as_dict()
        console.print("[bold]Sync Policy Audit[/bold]")
        console.print(f"Timestamp: {audit_result['timestamp']}")
        console.print(f"Status: {audit_result['audit_status']}")
        console.print(f"Enabled Connectors: {audit_result['enabled_connectors']}")
        console.print(f"Quota Budgets: {audit_result['quota_budgets']}")
        console.print(f"Policy Modes: {audit_result['policy_modes']}")
    else:
        console.print(f"[red]Unknown format: {format}[/red]")
        raise typer.Exit(1)


@app.command(
    "autopilot",
    help=(
        "Run automatic workstream reflection background cycle. "
        "Continuously syncs WORK_STREAM.md with GitHub Projects and Linear. (WL-160)"
    ),
)
def sync_autopilot(
    once: bool = typer.Option(
        False, "--once", "-1", help="Run single cycle and exit (for testing)."
    ),
    interval: int = typer.Option(
        300,
        "--interval",
        "-i",
        help="Cycle interval in seconds (default: 300).",
        ge=10,
        le=3600,
    ),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Report actions without executing."),
    output_format: str = typer.Option(
        "rich",
        "--format",
        "-F",
        help="Output format (rich|json).",
    ),
):
    """``thegent sync autopilot`` — run automatic workstream reflection.

    Continuously reflects local WORK_STREAM.md status to GitHub Projects and Linear,
    and pulls remote status updates back to local markdown. Enable by setting:
        - THGENT_WORKSTREAM_AUTOSYNC_ENABLED=true
        - THGENT_GITHUB_ENABLED=true + THGENT_GITHUB_OWNER + THGENT_GITHUB_PROJECT_NUMBER
        - OR THGENT_LINEAR_ENABLED=true + THGENT_LINEAR_API_KEY + THGENT_LINEAR_TEAM_KEY

    # @trace WL-160
    """
    import json
    import os

    from thegent.integrations.workstream_autosync import (
        WorkstreamAutosyncRunner,
        load_autosync_config_from_env,
    )

    # Load config from environment
    config = load_autosync_config_from_env()

    # Override config with CLI options
    if interval != 300:
        config.cycle_interval_seconds = interval
    if dry_run:
        config.dry_run = True

    # Validate configuration
    if not config.is_valid():
        console.print(
            "[yellow]Autopilot not enabled. Set THGENT_WORKSTREAM_AUTOSYNC_ENABLED=true "
            "and configure at least one platform:[/yellow]"
        )
        console.print(
            "  GitHub: THGENT_GITHUB_ENABLED=true THGENT_GITHUB_OWNER=... "
            "THGENT_GITHUB_PROJECT_NUMBER=..."
        )
        console.print(
            "  Linear:  THGENT_LINEAR_ENABLED=true THGENT_LINEAR_API_KEY=... "
            "THGENT_LINEAR_TEAM_KEY=..."
        )
        raise typer.Exit(0)

    console.print(
        f"[green]Workstream autopilot starting[/green] "
        f"(interval={interval}s, github={config.should_sync_github()}, "
        f"linear={config.should_sync_linear()}, dry_run={dry_run})"
    )

    # Run the cycle
    runner = WorkstreamAutosyncRunner(config)

    if once:
        # Single cycle mode (useful for testing)
        asyncio.run(runner._perform_sync_cycle())
        status = runner.get_status()

        if output_format == "json":
            console.print(json.dumps(status, indent=2, default=str))
        else:
            console.print("[green]Autopilot cycle complete[/green]")
            if status["last_operation"]:
                op = status["last_operation"]
                console.print(f"  Operation: {op['operation_id']}")
                console.print(f"  Platform: {op['platform']}")
                console.print(f"  Processed: {op['items_processed']} items")
                console.print(f"  Successful: {op['items_successful']} items")
                if op["errors"]:
                    console.print(f"  [red]Errors:[/red]")
                    for err in op["errors"][:3]:
                        console.print(f"    {err}")
    else:
        # Continuous cycle mode
        async def run_autopilot():
            await runner.start()
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                console.print("[yellow]Received interrupt, shutting down...[/yellow]")
            finally:
                await runner.stop()

        try:
            asyncio.run(run_autopilot())
        except KeyboardInterrupt:
            console.print("[yellow]Autopilot stopped[/yellow]")
