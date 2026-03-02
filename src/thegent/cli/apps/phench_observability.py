"""Phench diagnostics and observability commands."""

from __future__ import annotations

from typing import Any, Callable

import typer
from rich.console import Console
from rich.prompt import IntPrompt

console = Console()

TargetResolver = Callable[[], list[str]]
TargetTimelineLoader = Callable[..., dict[str, Any]]
TargetStatusLoader = Callable[[str], Any]
RunAction = Callable[..., int]
AuditAction = Callable[[str], dict[str, Any]]


def _ensure_timeline_target(
    *,
    list_targets_fn: TargetResolver,
) -> str:
    targets = list_targets_fn()
    if not targets:
        raise typer.BadParameter(
            "No targets found under Phenotype/projects. Initialize one with `phench target init`."
        )
    if len(targets) == 1:
        return targets[0]
    console.print("Select target:")
    for idx, value in enumerate(targets, start=1):
        console.print(f"{idx}. {value}")
    target_index = IntPrompt.ask("Target number", default=1)
    if target_index < 1 or target_index > len(targets):
        raise typer.BadParameter("Target selection out of range.")
    return targets[target_index - 1]


def register_observability_commands(
    app: typer.Typer,
    *,
    list_targets_fn: TargetResolver,
    target_timeline_fn: TargetTimelineLoader,
    target_status_fn: TargetStatusLoader,
    run_target_fn: RunAction,
    audit_shared_modules_fn: AuditAction,
) -> None:
    @app.command("tui", help="Interactive selector: target -> timeline -> run.")
    def tui_cmd() -> None:
        selected_target = _ensure_timeline_target(list_targets_fn=list_targets_fn)
        timeline = target_timeline_fn(selected_target, limit=20)
        repo_id = timeline.get("repo_id", "")
        label = f" ({repo_id})" if repo_id else ""
        console.print(f"Timeline for [bold]{selected_target}[/bold]{label}:")
        for line in timeline.get("recent", []):
            console.print(f"  {line}")
        exit_code = run_target_fn(selected_target)
        raise typer.Exit(exit_code)

    @app.command("status", help="Show lock/runtime/env status for a target.")
    def status_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
        state = target_status_fn(name)
        import orjson as json

        console.print_json(json.dumps(state).decode())

    @app.command("audit-shared", help="Audit shared Python modules across repos in a target lock.")
    def audit_shared_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
        state = audit_shared_modules_fn(name)
        import orjson as json

        console.print_json(json.dumps(state).decode())
