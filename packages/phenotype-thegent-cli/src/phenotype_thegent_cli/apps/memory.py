"""Memory management CLI commands.

# @trace WL-060
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from pathlib import Path
from typing import Literal, cast

import typer
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer(help="Memory: agent memory logs, synthesis, and gardening.")
snapshot_app = typer.Typer(help="Snapshot tools for session memory.")
dump_app = typer.Typer(help="Dump index and lookup tools.")
app.add_typer(snapshot_app, name="snapshot")
app.add_typer(dump_app, name="dump")


def _supports_param(fn: Callable[..., object], param: str) -> bool:
    return param in inspect.signature(fn).parameters


def _dynamic_cmd(fn: Callable[..., object]) -> Callable[..., None]:
    return cast("Callable[..., None]", fn)


@app.command("garden", help="Run the Gardener Agent: detect and update stale docs.")
def memory_garden(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Detect stale docs and synthesise updates without writing files.",
    ),
    max_age_days: int = typer.Option(
        7,
        "--max-age-days",
        help="Age threshold in days for stale doc detection.",
    ),
    project_root: str = typer.Option(
        ".",
        "--project-root",
        help="Project root directory (defaults to cwd).",
    ),
) -> None:
    """Run a full Gardener Agent cycle.

    Reads memory logs, conversation dumps, and governance events;
    detects stale documentation; synthesises rule-based updates; and
    writes patches back to the relevant docs (unless --dry-run).

    # @trace WL-060
    """
    from phenotype_thegent_agents.gardener import GardenerAgent

    root = Path(project_root).resolve()
    agent = GardenerAgent(dry_run=dry_run, project_root=root)

    console.print(
        f"[bold cyan]Gardener Agent[/bold cyan] — "
        f"project_root=[dim]{root}[/dim]  "
        f"dry_run=[dim]{dry_run}[/dim]  "
        f"max_age_days=[dim]{max_age_days}[/dim]"
    )

    result = agent.run(max_age_days=max_age_days)

    table = Table(title="Garden Cycle Result")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Docs checked", str(result.docs_checked))
    table.add_row("Docs updated", str(result.docs_updated))
    table.add_row("Dry run", str(result.dry_run))
    console.print(table)

    if result.items_found:
        console.print("\n[bold]Items found:[/bold]")
        for item in result.items_found:
            console.print(f"  [yellow]{item}[/yellow]")
    else:
        console.print("\n[green]No stale documentation detected.[/green]")


@snapshot_app.command("list", help="List snapshots with optional filters.")
def memory_snapshot_list(
    project: Path | None = typer.Option(None, "--project", help="Project root (defaults to cwd)."),
    limit: int = typer.Option(50, "--limit", help="Max snapshots to return."),
    trigger: str | None = typer.Option(None, "--trigger", help="Filter by trigger."),
    tag: str | None = typer.Option(None, "--tag", help="Filter by tag."),
    since: str | None = typer.Option(None, "--since", help="Only snapshots captured at/after ISO time."),
    format: str | None = typer.Option(None, "--format", "-F", help="Output format (rich|json)."),
) -> None:
    from phenotype_thegent_cli.commands.team_cmds import snapshot_list_cmd

    snapshot_list_cmd(project=project, limit=limit, trigger=trigger, tag=tag, since=since, format=format)


@snapshot_app.command("index", help="Show snapshot index summary.")
def memory_snapshot_index(
    project: Path | None = typer.Option(None, "--project", help="Project root (defaults to cwd)."),
    limit: int = typer.Option(200, "--limit", help="Max snapshots included in index."),
    format: str | None = typer.Option(None, "--format", "-F", help="Output format (rich|json)."),
) -> None:
    from phenotype_thegent_cli.commands.team_cmds import snapshot_index_cmd

    snapshot_index_cmd(project=project, limit=limit, format=format)


@snapshot_app.command("export", help="Export one snapshot to markdown.")
def memory_snapshot_export(
    snapshot_path: Path = typer.Argument(..., help="Path to snapshot JSON file."),
    project: Path | None = typer.Option(None, "--project", help="Project root (defaults to cwd)."),
    out_path: Path | None = typer.Option(None, "--out", help="Output markdown path."),
    format: str | None = typer.Option(None, "--format", "-F", help="Output format (rich|json)."),
) -> None:
    from phenotype_thegent_cli.commands.team_cmds import snapshot_export_cmd

    cmd = _dynamic_cmd(snapshot_export_cmd)
    # Keep compatibility with older team command signatures that may not accept format yet.
    if _supports_param(snapshot_export_cmd, "format"):
        cmd(snapshot_path=snapshot_path, project=project, out_path=out_path, format=format)
        return
    cmd(snapshot_path=snapshot_path, project=project, out_path=out_path)


@snapshot_app.command("prune", help="Delete old snapshots beyond keep limit.")
def memory_snapshot_prune(
    project: Path | None = typer.Option(None, "--project", help="Project root (defaults to cwd)."),
    max_keep: int = typer.Option(500, "--max-keep", help="Number of newest snapshots to keep."),
    format: str | None = typer.Option(None, "--format", "-F", help="Output format (rich|json)."),
) -> None:
    from phenotype_thegent_cli.commands.team_cmds import snapshot_prune_cmd

    snapshot_prune_cmd(project=project, max_keep=max_keep, format=format)


@snapshot_app.command("meta", help="Show snapshot trigger/tag metadata.")
def memory_snapshot_meta(
    project: Path | None = typer.Option(None, "--project", help="Project root (defaults to cwd)."),
    limit: int = typer.Option(500, "--limit", help="Max snapshots to inspect."),
    format: str | None = typer.Option(None, "--format", "-F", help="Output format (rich|json)."),
) -> None:
    from phenotype_thegent_cli.commands.team_cmds import snapshot_meta_cmd

    snapshot_meta_cmd(project=project, limit=limit, format=format)


@snapshot_app.command("daily-index", help="Show per-day snapshot index.")
def memory_snapshot_daily_index(
    project: Path | None = typer.Option(None, "--project", help="Project root (defaults to cwd)."),
    limit: int = typer.Option(1000, "--limit", help="Max snapshots to aggregate."),
    trigger: str | None = typer.Option(None, "--trigger", help="Filter by trigger."),
    tag: str | None = typer.Option(None, "--tag", help="Filter by tag."),
    since: str | None = typer.Option(None, "--since", help="Only snapshots captured at/after ISO time."),
    format: str | None = typer.Option(None, "--format", "-F", help="Output format (rich|json)."),
) -> None:
    from phenotype_thegent_cli.commands.team_cmds import snapshot_daily_index_cmd

    cmd = _dynamic_cmd(snapshot_daily_index_cmd)
    # Keep compatibility with older team command signatures that may not accept filters yet.
    has_trigger = _supports_param(snapshot_daily_index_cmd, "trigger")
    has_tag = _supports_param(snapshot_daily_index_cmd, "tag")
    has_since = _supports_param(snapshot_daily_index_cmd, "since")
    if has_trigger and has_tag and has_since:
        cmd(project=project, limit=limit, trigger=trigger, tag=tag, since=since, format=format)
        return
    if has_trigger and has_tag:
        cmd(project=project, limit=limit, trigger=trigger, tag=tag, format=format)
        return
    if has_trigger and has_since:
        cmd(project=project, limit=limit, trigger=trigger, since=since, format=format)
        return
    if has_tag and has_since:
        cmd(project=project, limit=limit, tag=tag, since=since, format=format)
        return
    if has_trigger:
        cmd(project=project, limit=limit, trigger=trigger, format=format)
        return
    if has_tag:
        cmd(project=project, limit=limit, tag=tag, format=format)
        return
    if has_since:
        cmd(project=project, limit=limit, since=since, format=format)
        return
    cmd(project=project, limit=limit, format=format)


@snapshot_app.command("daily-export", help="Export per-day snapshot index files.")
def memory_snapshot_daily_export(
    project: Path | None = typer.Option(None, "--project", help="Project root (defaults to cwd)."),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Directory for exported index files."),
    limit: int = typer.Option(1000, "--limit", help="Max snapshots to aggregate."),
    trigger: str | None = typer.Option(None, "--trigger", help="Filter by trigger."),
    tag: str | None = typer.Option(None, "--tag", help="Filter by tag."),
    since: str | None = typer.Option(None, "--since", help="Only snapshots captured at/after ISO time."),
    format: str | None = typer.Option(None, "--format", "-F", help="Output format (rich|json)."),
) -> None:
    from phenotype_thegent_cli.commands.team_cmds import snapshot_daily_export_cmd

    cmd = _dynamic_cmd(snapshot_daily_export_cmd)
    # Keep compatibility with older team command signatures that may not accept filters yet.
    has_trigger = _supports_param(snapshot_daily_export_cmd, "trigger")
    has_tag = _supports_param(snapshot_daily_export_cmd, "tag")
    has_since = _supports_param(snapshot_daily_export_cmd, "since")
    if has_trigger and has_tag and has_since:
        cmd(project=project, out_dir=out_dir, limit=limit, trigger=trigger, tag=tag, since=since, format=format)
        return
    if has_trigger and has_tag:
        cmd(project=project, out_dir=out_dir, limit=limit, trigger=trigger, tag=tag, format=format)
        return
    if has_trigger and has_since:
        cmd(project=project, out_dir=out_dir, limit=limit, trigger=trigger, since=since, format=format)
        return
    if has_tag and has_since:
        cmd(project=project, out_dir=out_dir, limit=limit, tag=tag, since=since, format=format)
        return
    if has_trigger:
        cmd(project=project, out_dir=out_dir, limit=limit, trigger=trigger, format=format)
        return
    if has_tag:
        cmd(project=project, out_dir=out_dir, limit=limit, tag=tag, format=format)
        return
    if has_since:
        cmd(project=project, out_dir=out_dir, limit=limit, since=since, format=format)
        return
    cmd(project=project, out_dir=out_dir, limit=limit, format=format)


@snapshot_app.command("daily-totals", help="Show per-day snapshot totals.")
def memory_snapshot_daily_totals(
    project: Path | None = typer.Option(None, "--project", help="Project root (defaults to cwd)."),
    limit: int = typer.Option(1000, "--limit", help="Max snapshots to aggregate."),
    trigger: str | None = typer.Option(None, "--trigger", help="Filter by trigger."),
    tag: str | None = typer.Option(None, "--tag", help="Filter by tag."),
    since: str | None = typer.Option(None, "--since", help="Only snapshots captured at/after ISO time."),
    format: Literal["rich", "json"] | None = typer.Option(
        None,
        "--format",
        "-F",
        help="Output format (rich|json).",
    ),
) -> None:
    from phenotype_thegent_cli.commands.team_cmds import snapshot_daily_totals_cmd

    cmd = _dynamic_cmd(snapshot_daily_totals_cmd)
    # Keep compatibility with older team command signatures that may not accept filters yet.
    has_trigger = _supports_param(snapshot_daily_totals_cmd, "trigger")
    has_tag = _supports_param(snapshot_daily_totals_cmd, "tag")
    has_since = _supports_param(snapshot_daily_totals_cmd, "since")
    if has_trigger and has_tag and has_since:
        cmd(project=project, limit=limit, trigger=trigger, tag=tag, since=since, format=format)
        return
    if has_trigger and has_tag:
        cmd(project=project, limit=limit, trigger=trigger, tag=tag, format=format)
        return
    if has_trigger and has_since:
        cmd(project=project, limit=limit, trigger=trigger, since=since, format=format)
        return
    if has_tag and has_since:
        cmd(project=project, limit=limit, tag=tag, since=since, format=format)
        return
    if has_trigger:
        cmd(project=project, limit=limit, trigger=trigger, format=format)
        return
    if has_tag:
        cmd(project=project, limit=limit, tag=tag, format=format)
        return
    if has_since:
        cmd(project=project, limit=limit, since=since, format=format)
        return
    cmd(project=project, limit=limit, format=format)


@dump_app.command("index", help="Generate dump index outputs.")
def memory_dump_index(
    project: Path | None = typer.Option(None, "--project", help="Project root (defaults to cwd)."),
    format: str | None = typer.Option(None, "--format", "-F", help="Output format (rich|json)."),
) -> None:
    from phenotype_thegent_cli.commands.team_cmds import dump_index_cmd

    dump_index_cmd(project=project, format=format)


@dump_app.command("latest", help="Show latest dump path.")
def memory_dump_latest(
    project: Path | None = typer.Option(None, "--project", help="Project root (defaults to cwd)."),
    category: str | None = typer.Option(None, "--category", help="Optional dump category filter."),
    json_only: bool = typer.Option(False, "--json-only", help="Only consider JSON dump files."),
    format: str | None = typer.Option(None, "--format", "-F", help="Output format (rich|json)."),
) -> None:
    from phenotype_thegent_cli.commands.team_cmds import dump_latest_cmd

    dump_latest_cmd(project=project, category=category, json_only=json_only, format=format)


@dump_app.command("categories", help="List dump categories.")
def memory_dump_categories(
    project: Path | None = typer.Option(None, "--project", help="Project root (defaults to cwd)."),
    format: Literal["rich", "json"] | None = typer.Option(
        None,
        "--format",
        "-F",
        help="Output format (rich|json).",
    ),
) -> None:
    from phenotype_thegent_cli.commands.team_cmds import dump_categories_cmd

    dump_categories_cmd(project=project, format=format)
