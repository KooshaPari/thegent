"""Logical stream: Session management — resume and list (WL-110)."""

from __future__ import annotations

import orjson as json

import typer
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer(help="Session: resume and inspect background sessions (WL-110).")


@app.command("resume", help="Resume a session using the stable state contract (WL-110).")
def session_resume(
    session_id: str | None = typer.Argument(None, help="Session ID to resume (defaults to latest resumable)"),
    prompt: str | None = typer.Option(None, "--prompt", help="Optional follow-up prompt to queue after resume"),
    skill: list[str] | None = typer.Option(
        None,
        "--skill",
        help="Activate skill instructions by name (repeatable) (WL-101).",
    ),
) -> None:
    from phenotype_thegent_cli.commands.cli import resume_cmd

    resume_cmd(session_id=session_id, prompt=prompt, skills=skill)


@app.command("list", help="List all sessions with status (WL-110).")
def session_list(
    all_sessions: bool = typer.Option(False, "--all", "-a", help="Show all sessions, not just current owner"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Filter by owner tag"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format: rich|json"),
    limit: int = typer.Option(50, "--limit", "-n", help="Maximum sessions to return"),
) -> None:
    from phenotype_thegent_cli.commands.impl import session_list_impl

    output_format = format.strip().lower()
    if output_format not in {"rich", "json"}:
        console.print(f"[red]Unsupported --format '{format}'. Use 'rich' or 'json'.[/red]")
        raise typer.Exit(2)

    sessions = session_list_impl(all_sessions=all_sessions, owner=owner, limit=limit)

    if output_format == "json":
        console.print_json(json.dumps(sessions).decode().decode())
        return

    if not sessions:
        console.print("[dim]No sessions found.[/dim]")
        return

    table = Table(title="Sessions", show_lines=False)
    table.add_column("Session ID", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Agent", style="yellow")
    table.add_column("Model", style="blue")
    table.add_column("Updated", style="dim")

    for s in sessions:
        table.add_row(
            s.get("session_id") or s.get("id") or "?",
            s.get("status", "unknown"),
            s.get("agent") or "?",
            s.get("model") or "?",
            s.get("updated_at_utc") or s.get("started_at_utc") or "?",
        )

    console.print(table)
