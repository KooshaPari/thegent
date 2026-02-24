"""DAG CLI run, sync, recover, checkpoint commands (WL-120).

Advanced DAG operations: execution, synchronization, recovery, checkpointing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from rich.console import Console
from rich.table import Table

from thegent.config import ThegentSettings
from thegent.cli.commands.dag_impl import (
    _atomic_write,
    _check_dag_cycles,
    _dag_path,
    _dag_update_task,
    _ensure_dag_file,
    _parse_dag_full,
    _parse_depends_on,
    _serialize_dag,
    _session_status_for,
    _validate_agent,
    dag_ready_impl,
    dag_recover_impl,
    dag_run_impl,
    dag_sync_impl,
)
from thegent.cli.commands._cli_shared import _resolve_checkpoint_id
from thegent.cli.services.run_session_helpers import (
    default_owner_tag as _default_owner_tag,
    resolve_cwd as _resolve_cwd,
)
import orjson as json

console = Console()

TERMINAL_STATUSES = frozenset({"done", "cancelled", "skipped"})


    if res.get("changed"):
        console.print("[green]Synced DAG status with sessions.[/green]")
        console.print("[dim]Auto-checkpoint created.[/dim]")
        run_next = res.get("run_next", {})
        if run_next and run_next.get("spawned"):
            for item in run_next["spawned"]:
                console.print(f"[green]{item['task_id']}[/green] -> {item['session_id']}")
    else:
        console.print("[dim]No status changes detected.[/dim]")


def dag_checkpoint_cmd(cd: Path | None = None, reason: str = "Manual checkpoint") -> None:
    """Create a point-in-time checkpoint of the DAG state."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG not found: {dag_path}[/red]")
        raise typer.Exit(1)

    settings = ThegentSettings()
    from thegent.execution import CheckpointRegistry

    registry = CheckpointRegistry(settings.session_dir)

    content = dag_path.read_text(encoding="utf-8")
    owner = _default_owner_tag(cwd)

    ckpt = registry.create_checkpoint(reason=reason, dag_content=content, owner=owner)
    console.print(f"[green]Checkpoint created:[/green] {ckpt.checkpoint_id} ({reason})")


def dag_rollback_cmd(checkpoint_id: str | None = None, cd: Path | None = None) -> None:
    """Rollback DAG state to a specific checkpoint."""
    cid = _resolve_checkpoint_id(checkpoint_id)
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"

    settings = ThegentSettings()
    from thegent.execution import CheckpointRegistry

    registry = CheckpointRegistry(settings.session_dir)

    ckpt = registry.get_checkpoint(cid)
    if not ckpt:
        console.print(f"[red]Checkpoint not found: {cid}[/red]")
        raise typer.Exit(1)

    content = ckpt.get("dag_content")
    if content is None:
        console.print("[red]Checkpoint has no content.[/red]")
        raise typer.Exit(1)

    _atomic_write(dag_path, content, backup=True)
    console.print(f"[green]DAG rolled back to checkpoint:[/green] {cid}")
    console.print(f"[dim]Reason: {ckpt.get('reason')}[/dim]")


def dag_checkpoints_cmd(limit: int = 20) -> None:
    """List recent DAG checkpoints."""
    settings = ThegentSettings()
    from thegent.execution import CheckpointRegistry

    registry = CheckpointRegistry(settings.session_dir)

    ckpts = registry.list_checkpoints(limit=limit)
    if not ckpts:
        console.print("[dim]No checkpoints found.[/dim]")
        return

    table = Table(title=f"DAG Checkpoints (last {limit})")
    table.add_column("Checkpoint ID", style="cyan")
    table.add_column("Created (UTC)", style="magenta")
    table.add_column("Owner", style="green")
    table.add_column("Reason", style="white")

    for c in ckpts:
        cid = c.get("checkpoint_id", "?")
        created = c.get("created_at_utc", "").split("T")[-1][:8]
        owner = c.get("owner", "?")
        reason_str = c.get("reason", "")
        table.add_row(cid, created, owner, reason_str)

    console.print(table)


def dag_recover_cmd(cd: Path | None = None, action: str = "retry-failed") -> None:
    """Perform recovery playbook actions on the DAG."""
    res = dag_recover_impl(cd=cd, action=action)
    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
        raise typer.Exit(1)
    if res.get("changed"):
        msg = {
            "retry-failed": "[green]Reset all failed tasks to pending.[/green]",
            "clear-stuck": "[green]Reset all running tasks to pending.[/green]",
            "reset-retries": "[green]Reset all retry counters.[/green]",
            "fallback": "[green]Swapped failed tasks to fallback agents.[/green]",
        }.get(action, "[green]Recovery applied.[/green]")
        console.print(msg)
    else:
        console.print("[dim]No changes needed.[/dim]")


def dag_probe_cmd(cd: Path | None = None, baseline_id: str | None = None) -> None:
    """Compare current DAG state with a baseline checkpoint to detect regressions."""
    cwd, dag_path = _dag_path(cd)
    if cwd is None or dag_path is None or not dag_path.exists():
        console.print(f"[red]DAG not found: {dag_path}[/red]")
        raise typer.Exit(1)
    assert dag_path is not None

    settings = ThegentSettings()
    from thegent.execution import CheckpointRegistry

    registry = CheckpointRegistry(settings.session_dir)

    if not baseline_id:
        ckpts = registry.list_checkpoints(limit=1)
        if not ckpts:
            console.print("[yellow]No baseline checkpoint found. Use --baseline-id.[/yellow]")
            return
        baseline_id = ckpts[0]["checkpoint_id"]

    ckpt = registry.get_checkpoint(baseline_id or "")
    if not ckpt:
        console.print(f"[red]Baseline checkpoint not found: {baseline_id}[/red]")
        raise typer.Exit(1)

    baseline_content = ckpt["dag_content"]
    current_content = dag_path.read_text(encoding="utf-8")

    if baseline_content == current_content:
        console.print(f"[green]No drift detected against baseline {baseline_id}.[/green]")
    else:
        console.print(f"[yellow]Drift detected against baseline {baseline_id}:[/yellow]")
        import difflib

        diff = difflib.unified_diff(
            baseline_content.splitlines(keepends=True),
            current_content.splitlines(keepends=True),
            fromfile=f"baseline:{baseline_id}",
            tofile="current",
        )
        console.print("".join(diff))


__all__ = [
    "TERMINAL_STATUSES",
    "dag_update_cmd",
    "dag_cancel_cmd",
    "dag_status_cmd",
    "dag_ready_cmd",
    "dag_reconcile_cmd",
    "dag_run_cmd",
    "dag_sync_cmd",
    "dag_checkpoint_cmd",
    "dag_rollback_cmd",
    "dag_checkpoints_cmd",
    "dag_recover_cmd",
    "dag_probe_cmd",
]


__all__ = [
    "dag_reconcile_cmd",
    "dag_run_cmd",
    "dag_sync_cmd",
    "dag_checkpoint_cmd",
    "dag_rollback_cmd",
    "dag_checkpoints_cmd",
    "dag_recover_cmd",
    "dag_probe_cmd",
]


__all__ = [
    "dag_sync_cmd",
    "dag_checkpoint_cmd",
    "dag_rollback_cmd",
    "dag_checkpoints_cmd",
    "dag_recover_cmd",
    "dag_probe_cmd",
]
