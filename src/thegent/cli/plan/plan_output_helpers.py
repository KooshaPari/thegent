"""Rendering helpers for plan/DAG CLI commands."""

from __future__ import annotations

import orjson as json
import sys
from typing import Any

from rich.table import Table


def resolve_output_format(requested: str | None, settings: Any, *, default: str = "rich") -> str:
    """Normalize command output format using CLI settings fallback."""
    return (requested or settings.output_format or default).lower()


def render_dag_list(tasks: list[dict[str, str]], fmt: str, *, console: Any) -> None:
    """Render `dag list` output for json/md/rich formats."""
    if not tasks:
        if fmt == "json":
            sys.stdout.write(json.dumps({"tasks": []}).decode() + "\n")
        else:
            console.print("[dim]No tasks in DAG.[/dim]")
        return
    if fmt == "json":
        sys.stdout.write(json.dumps({"tasks": tasks}).decode() + "\n")
        return
    if fmt == "md":
        console.print("## DAG Session\n")
        console.print("| id | agent | prompt | depends_on | status |")
        console.print("|----|-------|--------|------------|--------|")
        for t in tasks:
            console.print(
                f"| {t.get('id', '—')} | {t.get('agent', '—')} | {t.get('prompt', '—')} | {t.get('depends_on', '—')} | {t.get('status', '—')} |"
            )
        return

    tbl = Table(title="DAG Tasks")
    tbl.add_column("id")
    tbl.add_column("agent")
    tbl.add_column("prompt")
    tbl.add_column("depends_on")
    tbl.add_column("status")
    for t in tasks:
        tbl.add_row(
            t.get("id", "—"),
            t.get("agent", "—"),
            t.get("prompt", "—"),
            t.get("depends_on", "—"),
            t.get("status", "—"),
        )
    console.print(tbl)


def render_dag_status(rows: list[dict[str, str]], fmt: str, *, console: Any) -> None:
    """Render `dag status` output for json/md/rich formats."""
    if fmt == "json":
        sys.stdout.write(json.dumps({"tasks": rows}).decode() + "\n")
        return
    if not rows:
        console.print("[dim]No tasks with session_id.[/dim]")
        return
    if fmt == "md":
        console.print("| id | status | session_id | session_status |")
        console.print("|----|--------|------------|----------------|")
        for r in rows:
            console.print(f"| {r['id']} | {r['status']} | {r['session_id']} | {r['session_status']} |")
        return

    tbl = Table(title="DAG Status (tasks with session_id)")
    tbl.add_column("id")
    tbl.add_column("status")
    tbl.add_column("session_id")
    tbl.add_column("session_status")
    for r in rows:
        tbl.add_row(r["id"], r["status"], r["session_id"], r["session_status"])
    console.print(tbl)


def render_dag_ready(ready_ids: list[str], tasks: list[dict[str, str]], fmt: str, *, console: Any) -> None:
    """Render `dag ready` output for ids/json/md/rich formats."""
    if not ready_ids:
        console.print("[dim]No ready tasks.[/dim]")
        return
    if fmt == "ids":
        console.print("\n".join(ready_ids))
        return
    if fmt == "json":
        sys.stdout.write(json.dumps({"ready_task_ids": ready_ids}).decode() + "\n")
        return
    if fmt == "md":
        console.print("| id | agent | prompt |")
        console.print("|----|-------|--------|")
        for t in tasks:
            tid = t.get("id", "")
            prompt = t.get("prompt", "")
            prompt_preview = (prompt[:60] + "...") if len(prompt) > 60 else prompt
            console.print(f"| {tid} | {t.get('agent', '—')} | {prompt_preview} |")
        return

    tbl = Table(title="Ready DAG Tasks")
    tbl.add_column("id")
    tbl.add_column("agent")
    tbl.add_column("prompt")
    for t in tasks:
        tid = t.get("id", "")
        prompt = t.get("prompt", "")
        preview = (prompt[:60] + "...") if len(prompt) > 60 else (prompt or "—")
        tbl.add_row(tid, t.get("agent", "—"), preview)
    console.print(tbl)


def render_plan_next_items(items: list[dict[str, str]], *, console: Any) -> None:
    """Render `plan do-next` items in rich table format."""
    table = Table(title="Next work items")
    table.add_column("ID", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Source", style="dim")
    table.add_column("Prompt", style="green")
    for n in items:
        description = n.get("description", "") or ""
        prompt = n.get("prompt_suggestion", "") or ""
        table.add_row(
            n.get("id", ""),
            description[:60] + ("..." if len(description) > 60 else ""),
            n.get("source", ""),
            prompt[:50] + ("..." if len(prompt) > 50 else ""),
        )
    console.print(table)
    console.print('[dim]Use: thegent run "<prompt_suggestion>" or thegent_do_next + thegent_run[/dim]')
