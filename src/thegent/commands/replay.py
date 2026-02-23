"""CLI command: thegent replay [list | run | diff]

Sub-commands for the SimulationReplayEngine:
  list  — list available session files.
  run   — replay a session, printing events to stdout.
  diff  — compare two sessions and print a structured diff.
"""

from __future__ import annotations

import orjson as json
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(help="Replay agent sessions for debugging and regression testing.")


def _get_engine(sessions_root: Path | None = None):
    from thegent.simulation.replay import SimulationReplayEngine

    return SimulationReplayEngine(sessions_root=sessions_root)


def _find_session_file(engine, session_id: str) -> Path | None:
    """Return the first .json meta file whose stem starts with session_id."""
    for path in engine.list_sessions():
        if path.stem == session_id or path.stem.startswith(session_id):
            return path
    return None


@app.command("list")
def replay_list(
    sessions_root: Annotated[
        Path | None,
        typer.Option("--sessions-root", "-s", help="Override sessions root directory."),
    ] = None,
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Emit results as JSON."),
    ] = False,
) -> None:
    """List all available session files.

    Example::

        thegent replay list
        thegent replay list --json
        thegent replay list --sessions-root /custom/path
    """
    from rich.console import Console
    from rich.table import Table

    engine = _get_engine(sessions_root)
    sessions = engine.list_sessions()

    if output_json:
        typer.echo(json.dumps([str(p).decode() for p in sessions], indent=2))
        return

    if not sessions:
        typer.echo("No session files found.")
        return

    console = Console()
    table = Table(title="Available Sessions", show_lines=True)
    table.add_column("Session File", style="cyan")
    table.add_column("Size", style="dim")
    for path in sessions:
        size = f"{path.stat().st_size:,} B"
        table.add_row(str(path), size)
    console.print(table)


@app.command("run")
def replay_run(
    session_id: Annotated[str, typer.Argument(help="Session ID or path to .json file.")],
    speed: Annotated[
        float,
        typer.Option("--speed", help="Playback speed multiplier. 0 = no sleep."),
    ] = 0.0,
    sessions_root: Annotated[
        Path | None,
        typer.Option("--sessions-root", "-s", help="Override sessions root directory."),
    ] = None,
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Emit each event as a JSON line."),
    ] = False,
    from_event: Annotated[
        int,
        typer.Option("--from", help="Start replay from this event index (0-based)."),
    ] = 0,
) -> None:
    """Replay a session, printing each event to stdout.

    SESSION_ID may be a bare session ID (matched by prefix), a path to the
    .json meta file, or a partial session stem.

    Example::

        thegent replay run 20260219T231757Z-copilot-p21250-1f588a47
        thegent replay run ./path/to/session.json --json
        thegent replay run <id> --from 5 --speed 0
    """
    from rich.console import Console

    engine = _get_engine(sessions_root)

    # Try as a direct path first, then search by ID
    candidate = Path(session_id)
    session_file: Path | None
    if candidate.exists() and candidate.suffix == ".json":
        session_file = candidate
    else:
        session_file = _find_session_file(engine, session_id)

    if session_file is None:
        typer.echo(f"Session not found: {session_id}", err=True)
        raise typer.Exit(1)

    try:
        session = engine.load_session(session_file)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(f"Error loading session: {exc}", err=True)
        raise typer.Exit(1) from exc

    console = Console()

    if from_event > 0:
        try:
            event_iter = engine.replay_from_event(session, from_event)
        except IndexError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(1) from exc
    else:
        event_iter = engine.replay(session, speed=speed)

    for event in event_iter:
        if output_json:
            typer.echo(
                json.dumps(
                    {
                        "timestamp": event.timestamp,
                        "event_type": event.event_type,
                        "data": event.data,
                    }
                )).decode()
        else:
            console.print(f"[dim]{event.timestamp:.3f}[/dim] [bold cyan]{event.event_type}[/bold cyan]: {event.data}")


@app.command("diff")
def replay_diff(
    session_a: Annotated[str, typer.Argument(help="First session ID or path.")],
    session_b: Annotated[str, typer.Argument(help="Second session ID or path.")],
    sessions_root: Annotated[
        Path | None,
        typer.Option("--sessions-root", "-s", help="Override sessions root directory."),
    ] = None,
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Emit diff as JSON."),
    ] = False,
) -> None:
    """Compare two sessions and print a structured diff.

    Example::

        thegent replay diff <session_a_id> <session_b_id>
        thegent replay diff <id_a> <id_b> --json
    """
    from rich.console import Console

    engine = _get_engine(sessions_root)

    def _resolve(sid: str) -> Path:
        candidate = Path(sid)
        if candidate.exists() and candidate.suffix == ".json":
            return candidate
        found = _find_session_file(engine, sid)
        if found is None:
            typer.echo(f"Session not found: {sid}", err=True)
            raise typer.Exit(1)
        return found

    file_a = _resolve(session_a)
    file_b = _resolve(session_b)

    try:
        sess_a = engine.load_session(file_a)
        sess_b = engine.load_session(file_b)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(f"Error loading session: {exc}", err=True)
        raise typer.Exit(1) from exc

    diff = engine.compare_sessions(sess_a, sess_b)

    if output_json:
        typer.echo(json.dumps(diff, indent=2), default=str).decode())
        return

    console = Console()
    console.print(f"[bold]Diff[/bold]: {sess_a.session_id}  vs  {sess_b.session_id}")

    if (
        not diff["metadata_diff"]
        and not diff["events_changed"]
        and not diff["events_added"]
        and not diff["events_removed"]
    ):
        console.print("[green]Sessions are identical.[/green]")
        return

    if diff["metadata_diff"]:
        console.print("\n[bold yellow]Metadata changes:[/bold yellow]")
        for key, val in diff["metadata_diff"].items():
            console.print(f"  {key}: [red]{val['a']}[/red] -> [green]{val['b']}[/green]")

    if diff["events_changed"]:
        console.print(f"\n[bold yellow]Events changed:[/bold yellow] {len(diff['events_changed'])}")

    if diff["events_added"]:
        console.print(f"\n[bold green]Events added:[/bold green] {len(diff['events_added'])}")

    if diff["events_removed"]:
        console.print(f"\n[bold red]Events removed:[/bold red] {len(diff['events_removed'])}")

    tc = diff["tool_calls_diff"]
    if tc["added"] or tc["removed"] or tc["changed"]:
        console.print(
            f"\n[bold]Tool calls[/bold]: "
            f"+{len(tc['added'])} added, "
            f"-{len(tc['removed'])} removed, "
            f"~{len(tc['changed'])} changed"
        )
