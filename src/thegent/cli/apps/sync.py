"""Logical stream: System State Synchronization.

# @trace WL-037
"""

import asyncio
import importlib.util
import orjson as json
import os
from dataclasses import is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import typer
from rich.console import Console

from . import models

console = Console()
app = typer.Typer(help="Synchronize rules, DAG, and model catalog.")
gh_project_app = typer.Typer(help="GitHub Project v2 sync helpers (optional; disabled by default).")

_BOOTSTRAP_SYNC_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "bootstrap_sync_workflow_project.py"


def _serialize_model_data(value: Any) -> dict[str, Any]:
    """Return a plain mapping for pydantic v2/v1 models and dataclass contracts."""
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump(mode="python")
        if isinstance(dumped, dict):
            return dumped
        raise TypeError("model_dump() must return a mapping")

    legacy_dict = getattr(value, "dict", None)
    if callable(legacy_dict):
        dumped = legacy_dict()
        if isinstance(dumped, dict):
            return dumped
        raise TypeError("dict() must return a mapping")

    if not isinstance(value, type) and is_dataclass(value):
        field_names = getattr(value, "__dataclass_fields__", {})
        if isinstance(field_names, dict):
            return {str(name): getattr(value, name) for name in field_names}

    if isinstance(value, dict):
        return value
    raise TypeError(f"Unsupported model payload type: {type(value)!r}")


def _load_bootstrap_sync_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "thegent_bootstrap_sync_workflow_project",
        _BOOTSTRAP_SYNC_SCRIPT,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load bootstrap script: {_BOOTSTRAP_SYNC_SCRIPT}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


@app.command("bootstrap-gh", help="Bootstrap sync-system GitHub project + issues idempotently.")
def sync_bootstrap_github(
    owner: str = typer.Option(..., "--owner", help="GitHub owner or org (e.g. KooshaPari)"),
    repo: str = typer.Option(..., "--repo", help="Repository slug (e.g. KooshaPari/thegent)"),
    project_title: str = typer.Option(
        "thegent Sync System Deep Integration",
        "--project-title",
        help="Project title to create or reuse",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Print commands without executing them"),
):
    """Run `scripts/bootstrap_sync_workflow_project.py` via an in-process module load."""
    module = _load_bootstrap_sync_module()
    bootstrap_sync = getattr(module, "bootstrap_sync_workflow_project", None)
    if not callable(bootstrap_sync):
        raise RuntimeError("bootstrap_sync_workflow_project() missing from bootstrap module")
    summary = bootstrap_sync(
        owner=owner,
        repo=repo,
        project_title=project_title,
        dry_run=dry_run,
    )

    console.print(f"[green]Prepared {summary['prepared_count']} sync workflow issues[/green]")
    if summary.get("project_number"):
        console.print(f"[green]Project number: {summary['project_number']}[/green]")


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

        console.print(json.dumps({"ok": op.ok, "message": op.message, "changes": op.changes}).decode().decode())
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
    source: str | None = typer.Option(
        "github", "--source", "-s", help="Board source: github|linear (default: github)."
    ),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Report changes without writing."),
    shadow_mode: bool = typer.Option(
        False,
        "--shadow-mode",
        help="Compute outbound board mutations without performing remote writes.",
    ),
    wl_start: int | None = typer.Option(
        None,
        "--wl-start",
        help="Inclusive lower WL numeric bound (for example, 184 for WL-184).",
    ),
    wl_end: int | None = typer.Option(
        None,
        "--wl-end",
        help="Inclusive upper WL numeric bound (for example, 188 for WL-188).",
    ),
    write_batch_size: int = typer.Option(
        50,
        "--write-batch-size",
        help="Maximum number of items per external write batch.",
    ),
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
    op = cmd.sync_board(
        board_id=board_id,
        source=source or "github",
        dry_run=dry_run,
        shadow_mode=shadow_mode,
        wl_start=wl_start,
        wl_end=wl_end,
        write_batch_size=write_batch_size,
    )

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


@app.command("board-migrate", help="Migrate legacy board IDs to canonical WL-* IDs. (WL-247)")
def sync_board_migrate(
    legacy_ids: list[str] = typer.Argument(..., help="Legacy board IDs to migrate (repeatable)."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Report migration mapping without applying."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
):
    from thegent.commands.sync import SyncCommand, SyncOperationStatus

    root = (project or Path.cwd()).resolve()
    cmd = SyncCommand(project_root=root)
    op = cmd.migrate_legacy_board_ids(legacy_ids=legacy_ids, dry_run=dry_run)
    if op.status == SyncOperationStatus.FAILED:
        console.print(f"[red]{op.message}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]{op.message}[/green]")
    for change in op.changes:
        console.print(f"  [dim]{change}[/dim]")


@app.command("remote-orphans", help="Detect remote tracker items not present locally. (WL-248)")
def sync_remote_orphans(
    remote_ids: list[str] = typer.Argument(..., help="Remote item IDs to compare against local WORK_STREAM."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
):
    from thegent.commands.sync import SyncCommand, SyncOperationStatus

    root = (project or Path.cwd()).resolve()
    cmd = SyncCommand(project_root=root)
    op = cmd.detect_remote_orphans(remote_ids=remote_ids)
    color = "red" if op.status == SyncOperationStatus.FAILED else "green"
    console.print(f"[{color}]{op.message}[/{color}]")
    for change in op.changes:
        console.print(f"  [dim]{change}[/dim]")
    raise typer.Exit(1 if op.status == SyncOperationStatus.FAILED else 0)


@app.command("local-orphans", help="Detect local WORK_STREAM items lacking remote mappings. (WL-249)")
def sync_local_orphans(
    mapping_cache: Path = typer.Option(
        Path("docs/reference/connector_mapping_cache.json"),
        "--mapping-cache",
        help="Connector mapping cache path (default: docs/reference/connector_mapping_cache.json).",
    ),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
):
    from thegent.commands.sync import SyncCommand, SyncOperationStatus

    root = (project or Path.cwd()).resolve()
    cmd = SyncCommand(project_root=root)
    mapping_cache_path = mapping_cache if mapping_cache.is_absolute() else root / mapping_cache
    op = cmd.detect_local_orphans(mapping_cache_path=mapping_cache_path)
    color = "red" if op.status == SyncOperationStatus.FAILED else "green"
    console.print(f"[{color}]{op.message}[/{color}]")
    for change in op.changes:
        console.print(f"  [dim]{change}[/dim]")
    raise typer.Exit(1 if op.status == SyncOperationStatus.FAILED else 0)


@app.command("conflicts", help="List unresolved sync conflicts with recommended actions. (WL-204)")
def sync_conflicts(
    queue_file: Path = typer.Option(
        Path("docs/reference/sync_conflicts.json"),
        "--queue-file",
        help="Path to machine-readable conflict queue JSON.",
    ),
):
    from thegent.sync.conflicts import render_conflict_surface
    from thegent.sync.queue import ConflictQueueStore

    queue = ConflictQueueStore(queue_file)
    lines = render_conflict_surface(queue.pending())
    if not lines:
        console.print("[green]No unresolved conflicts.[/green]")
        return
    for line in lines:
        console.print(line)


@app.command("freeze", help="Freeze outbound sync writes for maintenance windows. (WL-206)")
def sync_freeze(
    reason: str = typer.Option(..., "--reason", help="Reason for freezing sync writes."),
    actor: str = typer.Option("operator", "--actor", help="Actor performing the freeze."),
    state_file: Path = typer.Option(
        Path("docs/reference/sync_freeze_state.json"),
        "--state-file",
        help="Path to freeze state file.",
    ),
):
    from thegent.sync.controller import SyncController

    controller = SyncController(state_file)
    state = controller.freeze(reason=reason, actor=actor)
    console.print(f"[yellow]Sync writes frozen[/yellow] actor={state.actor} reason={state.reason} at={state.frozen_at}")


@app.command("unfreeze", help="Unfreeze outbound sync writes. (WL-206)")
def sync_unfreeze(
    actor: str = typer.Option("operator", "--actor", help="Actor performing the unfreeze."),
    state_file: Path = typer.Option(
        Path("docs/reference/sync_freeze_state.json"),
        "--state-file",
        help="Path to freeze state file.",
    ),
):
    from thegent.sync.controller import SyncController

    controller = SyncController(state_file)
    controller.unfreeze(actor=actor)
    console.print(f"[green]Sync writes unfrozen[/green] actor={actor}")


@app.command("health", help="Render connector health scoreboard lines. (WL-209)")
def sync_health(
    entry: list[str] = typer.Option(
        [],
        "--entry",
        help="Connector entry as 'name,success_rate,drift_count'; repeat per connector.",
    ),
):
    from thegent.sync.health import ConnectorHealth, render_health_scoreboard

    rows: list[ConnectorHealth] = []
    for raw in entry:
        parts = [part.strip() for part in raw.split(",")]
        if len(parts) != 3:
            raise typer.BadParameter("entry must use 'name,success_rate,drift_count'")
        name, success_rate, drift_count = parts
        rows.append(ConnectorHealth(connector=name, success_rate=float(success_rate), drift_count=int(drift_count)))

    if not rows:
        console.print("[yellow]No connector entries provided.[/yellow]")
        raise typer.Exit(1)

    for line in render_health_scoreboard(rows):
        console.print(line)


@app.command("ga-readiness", help="Evaluate autosync GA readiness criteria. (WL-240)")
def sync_ga_readiness(
    format: str = typer.Option("json", "--format", "-F", help="Output format (json|rich)."),
):
    from thegent.sync.ga_readiness import evaluate_ga_readiness

    checks = {
        "criteria_doc_exists": Path("docs/reference/AUTOSYNC_GA_READINESS_CRITERIA.md").exists(),
        "status_artifact_exists": Path("docs/reference/autosync_status.json").exists(),
        "autosync_enabled": os.environ.get("THGENT_WORKSTREAM_AUTOSYNC_ENABLED", "").strip().lower()
        in {"1", "true", "yes", "on"},
    }
    result = evaluate_ga_readiness(checks)
    payload = {"ready": result.ready, "passed": result.passed, "failed": result.failed}
    if format == "json":
        console.print(json.dumps(payload, sort_keys=True).decode().decode())
    elif format == "rich":
        status = "[green]ready[/green]" if result.ready else "[red]not-ready[/red]"
        console.print(f"Autosync GA readiness: {status}")
        if result.failed:
            console.print(f"Missing checks: {', '.join(result.failed)}")
    else:
        raise typer.BadParameter("format must be json or rich", param_hint="--format")
    if not result.ready:
        raise typer.Exit(1)


@app.command("audit", help="Audit sync policies and print current configuration. (WL-261)")
def sync_audit(
    format: str = typer.Option("json", "--format", "-F", help="Output format (json|table)."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
    policy_path: Path | None = typer.Option(None, "--policy-path", help="Override .thegent/sync-policy.yaml path."),
):
    """``thegent sync audit`` — validate runtime behavior against sync-policy contract.

    Prints current sync policies (enabled connectors, quota budgets, policy modes)
    as JSON or formatted table.

    # @trace WL-261
    """
    from thegent.integrations.sync_auditor import SyncAuditor

    auditor = SyncAuditor()
    root = (project or Path.cwd()).resolve()
    try:
        contract = auditor.load_policy_contract(project_root=root, explicit_path=policy_path)
    except Exception as exc:
        console.print(f"[red]sync audit failed: {exc}[/red]")
        raise typer.Exit(1) from exc

    if format == "json":
        payload = auditor.audit_as_dict()
        payload["schema_version"] = contract.schema_version
        payload["conflict_precedence"] = contract.conflict_precedence
        payload["strict_mode"] = contract.strict_mode
        payload["tenancy"] = _serialize_model_data(contract.tenancy) if contract.tenancy is not None else None
        console.print(json.dumps(payload, indent=2).decode().decode())
    elif format == "table":
        audit_result = auditor.audit_as_dict()
        tenancy = contract.tenancy
        console.print("[bold]Sync Policy Audit[/bold]")
        console.print(f"Timestamp: {audit_result['timestamp']}")
        console.print(f"Status: {audit_result['audit_status']}")
        console.print(f"Schema Version: {contract.schema_version}")
        console.print(f"Conflict Precedence: {contract.conflict_precedence}")
        console.print(f"Strict Mode: {contract.strict_mode}")
        console.print(f"Enabled Connectors: {audit_result['enabled_connectors']}")
        console.print(f"Quota Budgets: {audit_result['quota_budgets']}")
        console.print(f"Policy Modes: {audit_result['policy_modes']}")
        if tenancy is None:
            console.print("Tenancy Mode: n/a")
        else:
            console.print(
                f"Tenancy Mode: {tenancy.mode} (projects={len(tenancy.projects)}, "
                f"default_tenant={tenancy.default_tenant})"
            )
    else:
        console.print(f"[red]Unknown format: {format}[/red]")
        raise typer.Exit(1)


@app.command(
    "dead-letter-queue",
    help="Inspect dead-letter replay queue candidates without mutating state. (WL-331)",
)
def sync_dead_letter_queue(
    source: str | None = typer.Option(None, "--source", "-s", help="Filter connector source (github|linear)."),
    board_id: str | None = typer.Option(None, "--board", "-b", help="Filter board ID."),
    limit: int = typer.Option(
        50,
        "--limit",
        "-l",
        min=1,
        max=1000,
        help="Maximum due replay candidates to render.",
    ),
    output_format: str = typer.Option("table", "--format", "-F", help="Output format (table|json)."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
):
    """``thegent sync dead-letter-queue`` — inspect replay queue candidates.

    Read-only command that reports pending queue records and due replay candidates.

    # @trace WL-331
    """
    from thegent.commands.sync import SyncCommand

    root = (project or Path.cwd()).resolve()
    try:
        cmd = SyncCommand(project_root=root)
        queue = cmd._dead_letter_queue()
        pending_records = queue.pending(source=source, board_id=board_id)
        due_records = queue.candidates_for_replay(now=datetime.now(UTC), source=source, board_id=board_id)
    except Exception as exc:
        console.print(f"[red]dead-letter queue inspection failed: {exc}[/red]")
        raise typer.Exit(1) from exc

    selected_records = due_records[:limit]
    payload = {
        "operation": "dead-letter-queue",
        "queue_path": str(queue.queue_path),
        "filters": {"source": source, "board_id": board_id, "limit": limit},
        "counts": {
            "pending_total": len(pending_records),
            "due_total": len(due_records),
            "selected": len(selected_records),
        },
        "candidates": [
            {
                "entry_id": record.entry_id,
                "source": record.source,
                "board_id": record.board_id,
                "item_id": record.item.get("id"),
                "status": record.status,
                "attempts": record.attempts,
                "max_attempts": record.max_attempts,
                "next_attempt_at": record.next_attempt_at,
                "last_attempt_at": record.last_attempt_at,
                "error": record.error,
            }
            for record in selected_records
        ],
    }

    if output_format == "json":
        typer.echo(json.dumps(payload, indent=2))
        return

    if output_format != "table":
        console.print(f"[red]Unknown format: {output_format}[/red]")
        raise typer.Exit(1)

    console.print(
        "[bold]Dead-letter queue[/bold] "
        f"pending={payload['counts']['pending_total']} "
        f"due={payload['counts']['due_total']} "
        f"selected={payload['counts']['selected']}"
    )
    if not selected_records:
        console.print("[yellow]No due replay candidates.[/yellow]")
        return

    for record in selected_records:
        item_id = record.item.get("id", "<unknown>")
        console.print(
            f"{record.entry_id} source={record.source} board={record.board_id} "
            f"item={item_id} attempts={record.attempts}/{record.max_attempts}"
        )


@app.command(
    "dead-letter-replay",
    help="Replay failed remote write operations from sync dead-letter queue. (WL-214)",
)
def sync_dead_letter_replay(
    source: str | None = typer.Option(None, "--source", "-s", help="Filter connector source (github|linear)."),
    board_id: str | None = typer.Option(None, "--board", "-b", help="Filter board ID."),
    limit: int = typer.Option(50, "--limit", "-l", min=1, max=1000, help="Maximum dead-letter records to replay."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview replay candidates without mutating queue."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root (default: cwd)."),
):
    """``thegent sync dead-letter-replay`` — replay pending remote-write dead letters.

    # @trace WL-214
    """
    from thegent.commands.sync import SyncCommand, SyncOperationStatus

    root = (project or Path.cwd()).resolve()
    cmd = SyncCommand(project_root=root)
    op = cmd.replay_dead_letters(source=source, board_id=board_id, limit=limit, dry_run=dry_run)

    if op.status == SyncOperationStatus.FAILED:
        console.print(f"[red]dead-letter replay failed: {op.message}[/red]")
        for err in op.errors[:10]:
            console.print(f"[red]  {err}[/red]")
        raise typer.Exit(1)

    prefix = "[yellow]Dry-run:[/yellow]" if dry_run else "[green]"
    suffix = "" if dry_run else "[/green]"
    console.print(f"{prefix} {op.message}{suffix}")
    for change in op.changes[:20]:
        console.print(f"  [dim]{change}[/dim]")


@app.command("rollback", help="Manage work stream snapshots and rollback. (WL-185)")
def sync_rollback(
    list_snapshots: bool = typer.Option(False, "--list", "-l", help="List available snapshots."),
    snapshot_id: str | None = typer.Option(None, "--snapshot", "-s", help="Snapshot ID to restore."),
    latest: bool = typer.Option(False, "--latest", help="Restore the most recent snapshot."),
    create_snapshot: bool = typer.Option(
        False, "--create", help="Create a rollback snapshot from current WORK_STREAM."
    ),
    cycle_id: str = typer.Option("", "--cycle-id", help="Optional cycle identifier to stamp on created snapshot."),
    work_stream: Path | None = typer.Option(
        None, "--work-stream", "-w", help="Path to WORK_STREAM.md (default: docs/reference/WORK_STREAM.md)."
    ),
):
    """``thegent sync rollback`` — manage work stream snapshots.

    Use --list to show available snapshots, --create to create one, or
    --snapshot/--latest to restore.

    # @trace WL-185
    """
    from thegent.integrations.reflection_rollback import ReflectionRollbackManager

    ws_path = (work_stream or Path("docs/reference/WORK_STREAM.md")).resolve()
    manager = ReflectionRollbackManager()

    if list_snapshots:
        snapshots = manager.list_snapshots()
        if not snapshots:
            console.print("[yellow]No snapshots available[/yellow]")
            return

        console.print("[bold]Available snapshots:[/bold]")
        for snap in snapshots[:10]:  # Show 10 most recent
            console.print(f"  {snap.snapshot_id:8} {snap.timestamp:26} {snap.cycle_id}")
        return

    if create_snapshot:
        snapshot = manager.take_snapshot(ws_path, cycle_id=cycle_id)
        console.print(f"[green]Created snapshot {snapshot.snapshot_id}[/green]")
        return

    if latest:
        snapshots = manager.list_snapshots()
        if not snapshots:
            console.print("[red]No snapshots available to restore[/red]")
            raise typer.Exit(1)
        snapshot_id = snapshots[0].snapshot_id

    if snapshot_id:
        try:
            manager.rollback_to(snapshot_id, ws_path)
            console.print(f"[green]Restored snapshot {snapshot_id}[/green]")
        except FileNotFoundError:
            console.print(f"[red]Snapshot not found: {snapshot_id}[/red]")
            raise typer.Exit(1)
        return

    console.print("[yellow]Use --list, --create, --snapshot ID, or --latest[/yellow]")


@app.command(
    "autopilot",
    help=(
        "Run automatic workstream reflection background cycle. "
        "Continuously syncs WORK_STREAM.md with GitHub Projects and Linear. (WL-160)"
    ),
)
def sync_autopilot(
    subcommand: str = typer.Argument(
        "",
        help="Optional autopilot subcommand. Use `doctor` to run diagnostics.",
    ),
    once: bool = typer.Option(False, "--once", "-1", help="Run single cycle and exit (for testing)."),
    interval: int = typer.Option(
        300,
        "--interval",
        "-i",
        help="Cycle interval in seconds (default: 300).",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Report actions without executing."),
    area: list[str] | None = typer.Option(
        None,
        "--area",
        help="Limit sync scope to one or more area values (repeat flag).",
    ),
    status: list[str] | None = typer.Option(
        None,
        "--status",
        help="Limit sync scope to one or more statuses (repeat flag).",
    ),
    priority: list[str] | None = typer.Option(
        None,
        "--priority",
        help="Limit sync scope to one or more priorities (repeat flag).",
    ),
    wl_range: list[str] | None = typer.Option(
        None,
        "--wl-range",
        help="Limit sync scope to WL ranges in WL-N..WL-M form (repeat flag).",
    ),
    remote_missing_item_policy: str | None = typer.Option(
        None,
        "--remote-missing-item-policy",
        help="Policy for local WL IDs missing in remote reads: ignore|archive|delete.",
    ),
    output_format: str = typer.Option(
        "rich",
        "--format",
        "-F",
        help="Output format (rich|json).",
    ),
    bootstrap_required: list[str] = typer.Option(
        [],
        "--bootstrap-required",
        help="Required mapping field names that must exist before apply (repeatable).",
    ),
    bootstrap_map: list[str] = typer.Option(
        [],
        "--bootstrap-map",
        help="Bootstrap mapping in <field_name>=<field_id> format (repeatable).",
    ),
    bootstrap_connector: str = typer.Option(
        "",
        "--bootstrap-connector",
        help="Connector used for bootstrap mapping cache checks (default from env/config).",
    ),
    simulation_mode: bool = typer.Option(
        False,
        "--simulation-mode",
        help="Run autopilot cycle without connector mutations or reads.",
    ),
    offline: bool = typer.Option(
        False,
        "--offline",
        help="Alias for --simulation-mode; run with no connector I/O.",
    ),
    snapshot_retention_count: int | None = typer.Option(
        None,
        "--snapshot-retention-count",
        help="Override snapshot retention count for this run.",
    ),
    artifact_encryption: bool = typer.Option(
        False,
        "--artifact-encryption",
        help="Enable artifact encryption for this run.",
    ),
    artifact_encryption_key: str = typer.Option(
        "",
        "--artifact-encryption-key",
        help="Artifact encryption key for this run.",
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

    from thegent.integrations.workstream_autosync import (
        RemoteMissingItemPolicy,
        WorkstreamAutosyncRunner,
        load_autosync_config_from_env,
    )
    from thegent.integrations.connector_mapping_cache import ConnectorMappingCache

    if subcommand and subcommand != "doctor":
        raise typer.BadParameter(f"Unknown autopilot subcommand: {subcommand}")

    # Load config from environment
    config = load_autosync_config_from_env()

    if subcommand == "doctor":
        _run_autopilot_doctor(config=config, output_format=output_format)
        return

    if interval < 10 or interval > 3600:
        raise typer.BadParameter("interval must be between 10 and 3600 seconds", param_hint="--interval")

    # Override config with CLI options
    if interval != 300:
        config.cycle_interval_seconds = interval
    if dry_run:
        config.dry_run = True
    if simulation_mode or offline:
        config.simulation_mode = True
    if snapshot_retention_count is not None:
        if snapshot_retention_count < 1:
            raise typer.BadParameter(
                "snapshot-retention-count must be >= 1",
                param_hint="--snapshot-retention-count",
            )
        config.snapshot_retention_count = snapshot_retention_count
    if artifact_encryption:
        config.artifact_encryption_enabled = True
    if artifact_encryption_key:
        config.artifact_encryption_enabled = True
        config.artifact_encryption_key = artifact_encryption_key
    if area:
        config.scope_areas = list(area)
    if status:
        config.scope_statuses = [value.upper() for value in status]
    if priority:
        config.scope_priorities = [value.upper() for value in priority]
    if wl_range:
        config.scope_wl_ranges = [value.upper() for value in wl_range]
    if remote_missing_item_policy is not None:
        try:
            config.remote_missing_item_policy = RemoteMissingItemPolicy(remote_missing_item_policy.strip().lower())
        except ValueError as exc:
            raise typer.BadParameter(
                "remote-missing-item-policy must be one of: ignore, archive, delete",
                param_hint="--remote-missing-item-policy",
            ) from exc

    effective_required_fields = list(bootstrap_required) or list(config.bootstrap_required_fields)
    if effective_required_fields:
        mapping_cache = ConnectorMappingCache(cache_file=config.bootstrap_mapping_cache_path)
        effective_connector = bootstrap_connector.strip() or config.bootstrap_connector
        parsed_bootstrap: dict[str, str] = {}
        for raw in bootstrap_map:
            if "=" not in raw:
                raise typer.BadParameter(
                    "bootstrap-map must use <field_name>=<field_id> format",
                    param_hint="--bootstrap-map",
                )
            field_name, field_id = raw.split("=", 1)
            parsed_bootstrap[field_name.strip()] = field_id.strip()

        if mapping_cache.bootstrap_required(effective_connector, effective_required_fields):
            missing = [
                field_name
                for field_name in effective_required_fields
                if mapping_cache.get(effective_connector, field_name) is None and field_name not in parsed_bootstrap
            ]
            if missing:
                raise typer.BadParameter(
                    "missing required bootstrap mappings for: " + ", ".join(missing),
                    param_hint="--bootstrap-map",
                )
            mapping_cache.bootstrap(effective_connector, parsed_bootstrap)
            console.print(
                f"[green]Bootstrap mappings saved[/green] connector={effective_connector} "
                f"fields={','.join(sorted(parsed_bootstrap.keys()))}"
            )

    # Validate configuration
    if not config.is_valid():
        console.print(
            "[yellow]Autopilot not enabled. Set THGENT_WORKSTREAM_AUTOSYNC_ENABLED=true "
            "and configure at least one platform:[/yellow]"
        )
        console.print("  GitHub: THGENT_GITHUB_ENABLED=true THGENT_GITHUB_OWNER=... THGENT_GITHUB_PROJECT_NUMBER=...")
        console.print("  Linear:  THGENT_LINEAR_ENABLED=true THGENT_LINEAR_API_KEY=... THGENT_LINEAR_TEAM_KEY=...")
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
        cycle_status = runner.get_status()

        if output_format == "json":
            console.print(json.dumps(cycle_status, indent=2, default=str).decode().decode())
        else:
            console.print("[green]Autopilot cycle complete[/green]")
            if cycle_status["last_operation"]:
                op = cycle_status["last_operation"]
                console.print(f"  Operation: {op['operation_id']}")
                console.print(f"  Platform: {op['platform']}")
                console.print(f"  Processed: {op['items_processed']} items")
                console.print(f"  Successful: {op['items_successful']} items")
                if op["errors"]:
                    console.print("  [red]Errors:[/red]")
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


def _run_autopilot_doctor(*, config: Any, output_format: str) -> None:
    import json
    import os

    from thegent.integrations.connector_mapping_cache import ConnectorMappingCache

    checks: list[dict[str, Any]] = []

    autosync_enabled = bool(getattr(config, "enabled", False))
    checks.append(
        {
            "check": "autosync_enabled",
            "status": "pass" if autosync_enabled else "fail",
            "message": "THGENT_WORKSTREAM_AUTOSYNC_ENABLED must be true for autopilot.",
        }
    )

    github_enabled = bool(getattr(config, "github_enabled", False))
    github_owner = str(getattr(config, "github_owner", "") or "").strip()
    github_project_number = int(getattr(config, "github_project_number", 0) or 0)
    github_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or ""
    if github_enabled:
        github_ok = bool(github_owner and github_project_number > 0 and github_token.strip())
        checks.append(
            {
                "check": "github_credentials",
                "status": "pass" if github_ok else "fail",
                "message": "GitHub requires owner, project number, and GITHUB_TOKEN/GH_TOKEN.",
                "details": {
                    "owner_set": bool(github_owner),
                    "project_number_set": github_project_number > 0,
                    "token_set": bool(github_token.strip()),
                },
            }
        )
    else:
        checks.append(
            {
                "check": "github_credentials",
                "status": "skip",
                "message": "GitHub connector is disabled.",
            }
        )

    linear_enabled = bool(getattr(config, "linear_enabled", False))
    linear_api_key = str(getattr(config, "linear_api_key", "") or "").strip()
    linear_team_key = str(getattr(config, "linear_team_key", "") or "").strip()
    if linear_enabled:
        linear_ok = bool(linear_api_key and linear_team_key)
        checks.append(
            {
                "check": "linear_credentials",
                "status": "pass" if linear_ok else "fail",
                "message": "Linear requires THGENT_LINEAR_API_KEY and THGENT_LINEAR_TEAM_KEY.",
                "details": {
                    "api_key_set": bool(linear_api_key),
                    "team_key_set": bool(linear_team_key),
                },
            }
        )
    else:
        checks.append(
            {
                "check": "linear_credentials",
                "status": "skip",
                "message": "Linear connector is disabled.",
            }
        )

    required_fields = [
        str(field).strip() for field in list(getattr(config, "bootstrap_required_fields", [])) if str(field).strip()
    ]
    mapping_connector = str(getattr(config, "bootstrap_connector", "github") or "github").strip() or "github"
    mapping_cache_path = getattr(config, "bootstrap_mapping_cache_path", None)
    if required_fields:
        mapping_cache = ConnectorMappingCache(cache_file=mapping_cache_path)
        field_states: dict[str, str] = {}
        missing_fields: list[str] = []
        for field_name in required_fields:
            status = mapping_cache.get_with_status(mapping_connector, field_name)
            state = str(status.get("status", "missing"))
            field_states[field_name] = state
            if state != "fresh":
                missing_fields.append(field_name)

        checks.append(
            {
                "check": "field_mappings",
                "status": "pass" if not missing_fields else "fail",
                "message": "Required connector field mappings must be cached and fresh.",
                "details": {
                    "connector": mapping_connector,
                    "missing_or_stale_fields": missing_fields,
                    "field_states": field_states,
                },
            }
        )
    else:
        checks.append(
            {
                "check": "field_mappings",
                "status": "skip",
                "message": "No bootstrap required fields configured.",
            }
        )

    failed_checks = [check["check"] for check in checks if check.get("status") == "fail"]
    payload = {
        "ok": len(failed_checks) == 0,
        "failed_checks": failed_checks,
        "checks": checks,
    }

    if output_format == "json":
        typer.echo(json.dumps(payload, indent=2, sort_keys=True).decode().decode())
        return

    color = "green" if payload["ok"] else "red"
    console.print(f"[{color}]Autopilot doctor {'passed' if payload['ok'] else 'failed'}[/{color}]")
    for check in checks:
        status = check["status"]
        symbol = {"pass": "[green]PASS[/green]", "fail": "[red]FAIL[/red]", "skip": "[yellow]SKIP[/yellow]"}.get(
            status,
            status.upper(),
        )
        console.print(f"{symbol} {check['check']} - {check['message']}")


def _normalize_autosync_runner(raw_runner: Any) -> dict[str, Any]:
    runner = raw_runner if isinstance(raw_runner, dict) else {}
    blockers = runner.get("open_blockers")
    blocker_list = [str(item) for item in blockers] if isinstance(blockers, list) else []
    try:
        failure_queue_size = int(runner.get("failure_queue_size", 0))
    except (TypeError, ValueError):
        failure_queue_size = 0

    return {
        "enabled": bool(runner.get("enabled", False)),
        "is_running": bool(runner.get("is_running", False)),
        "last_sync_time": runner.get("last_sync_time") if isinstance(runner.get("last_sync_time"), str) else None,
        "github_enabled": bool(runner.get("github_enabled", False)),
        "linear_enabled": bool(runner.get("linear_enabled", False)),
        "last_operation": runner.get("last_operation") if isinstance(runner.get("last_operation"), dict) else None,
        "open_blockers": blocker_list,
        "failure_queue_size": max(0, failure_queue_size),
    }


def _normalize_no_op_summary(raw_no_op_summary: Any) -> dict[str, Any] | None:
    if not isinstance(raw_no_op_summary, dict):
        return None

    skipped_connectors = raw_no_op_summary.get("skipped_connectors", 0)
    try:
        skipped_connectors = int(skipped_connectors)
    except (TypeError, ValueError):
        skipped_connectors = 0

    return {
        "no_op": bool(raw_no_op_summary.get("no_op")),
        "reason": str(raw_no_op_summary.get("reason", "")),
        "skipped_connectors": skipped_connectors,
    }


def _normalize_autosync_status(raw_status: Any, *, read_error: str | None = None) -> dict[str, Any]:
    status = raw_status if isinstance(raw_status, dict) else {}
    runner = _normalize_autosync_runner(status.get("runner"))
    open_blockers = status.get("open_blockers")
    blocker_list = [str(item) for item in open_blockers] if isinstance(open_blockers, list) else runner["open_blockers"]

    try:
        total_cycles = int(status.get("total_cycles", 0))
    except (TypeError, ValueError):
        total_cycles = 0

    try:
        failure_queue_size = int(status.get("failure_queue_size", runner["failure_queue_size"]))
    except (TypeError, ValueError):
        failure_queue_size = runner["failure_queue_size"]

    last_error = status.get("last_error")
    if last_error is not None and not isinstance(last_error, str):
        last_error = str(last_error)
    if read_error:
        last_error = read_error

    health = status.get("health")
    if isinstance(health, str):
        health = health.lower().strip()
    if health not in {"ok", "degraded", "down"}:
        health = "degraded" if last_error else "ok"

    return {
        "last_cycle_at": status.get("last_cycle_at") if isinstance(status.get("last_cycle_at"), str) else None,
        "total_cycles": max(0, total_cycles),
        "last_error": last_error,
        "health": health,
        "runner": runner,
        "open_blockers": blocker_list,
        "failure_queue_size": max(0, failure_queue_size),
        "correlation_id": str(status.get("correlation_id")) if status.get("correlation_id") is not None else None,
        "no_op_summary": _normalize_no_op_summary(status.get("no_op_summary")),
        "checkpoint": status.get("checkpoint"),
        "incident_snapshot": status.get("incident_snapshot"),
    }


@app.command(
    "autopilot-status",
    help="Query autopilot health, lag, and last-cycle summary.",
)
def sync_autopilot_status(
    format: str = typer.Option(
        "rich",
        "--format",
        "-F",
        help="Output format (rich|json).",
    ),
):
    """``thegent sync autopilot-status`` — query autopilot status.

    Reads from autosync_status.json if it exists and displays health summary.

    # @trace WL-171
    """
    import json
    import os
    from datetime import datetime

    from rich.table import Table

    status_file = Path(os.getenv("THGENT_AUTOSYNC_STATUS_PATH", "docs/reference/autosync_status.json"))

    raw_status: dict[str, Any] = {}
    read_error: str | None = None
    if status_file.exists():
        try:
            with open(status_file, encoding="utf-8") as f:
                parsed = json.load(f)
                if isinstance(parsed, dict):
                    raw_status = parsed
                else:
                    read_error = f"Status file {status_file} must be a JSON object."
        except (OSError, json.JSONDecodeError) as exc:
            read_error = f"Failed to parse {status_file}: {exc}"

    status = _normalize_autosync_status(raw_status, read_error=read_error)

    # Output in requested format
    if format == "json":
        typer.echo(json.dumps(status, indent=2, default=str).decode().decode())
    else:
        # Create rich table
        table = Table(title="Autopilot Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")

        # Format last_cycle_at
        last_cycle = status.get("last_cycle_at")
        if last_cycle:
            try:
                dt = datetime.fromisoformat(last_cycle)
                last_cycle_str = dt.isoformat()
            except (ValueError, TypeError):
                last_cycle_str = str(last_cycle) if last_cycle else "Never"
        else:
            last_cycle_str = "Never"

        table.add_row("Last Cycle", last_cycle_str)
        table.add_row("Total Cycles", str(status.get("total_cycles", 0)))

        # Health status with color
        health = status.get("health", "ok")
        health_color = "green" if health == "ok" else "yellow" if health == "degraded" else "red"
        table.add_row("Health", f"[{health_color}]{health}[/{health_color}]")

        last_error = status.get("last_error")
        if last_error:
            table.add_row("Last Error", f"[red]{last_error}[/red]")
        else:
            table.add_row("Last Error", "[green]None[/green]")

        correlation_id = status.get("correlation_id")
        if correlation_id:
            table.add_row("Run ID", str(correlation_id))

        no_op_summary = status.get("no_op_summary")
        if isinstance(no_op_summary, dict):
            table.add_row(
                "No-Op",
                "[yellow]true[/yellow]" if bool(no_op_summary.get("no_op")) else "[green]false[/green]",
            )
            reason = str(no_op_summary.get("reason", "")).strip()
            if reason:
                table.add_row("No-Op Reason", reason)
            table.add_row("No-Op Connectors Skipped", str(no_op_summary.get("skipped_connectors", 0)))

        console.print(table)
