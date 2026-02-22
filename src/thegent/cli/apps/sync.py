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
    op = cmd.sync_board(board_id=board_id, source=source, dry_run=dry_run)

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
