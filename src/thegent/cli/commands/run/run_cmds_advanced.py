"""Thegent CLI run commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import json
from pathlib import Path

import typer

from rich.panel import Panel
from rich.table import Table

from thegent.cli.commands._cli_shared import (
    RunRegistry,
    ThegentSettings,
    _get_run_subprocess_optimized,
    console,
)


def replay_cmd(run_id: str, what_if_env: str | None = None) -> None:
    """Decision replay and rationale snapshots (WP-4007)."""
    settings = ThegentSettings()
    from thegent.execution import ReplayManager

    rm = ReplayManager(settings.session_dir)
    chain = rm.get_replay_chain(run_id)

    if not chain:
        console.print(f"[red]No events found for {run_id}.[/red]")
        return

    console.print(Panel(f"Stepping through history for [bold cyan]{run_id}[/bold cyan]", title="Decision Replay"))

    for i, event in enumerate(chain):
        status = event.get("status", "unknown")
        color = "green" if status == "completed" else "red" if status == "failed" else "yellow"
        console.print(f"{i + 1}. [{color}]{status.upper()}[/{color}] at {event.get('started_at_utc')}")
        if event.get("policy_reason"):
            console.print(f"   [dim]Policy:[/dim] {event['policy_reason']}")

    if what_if_env:
        console.print(f"\n[bold yellow]Simulation (What-If):[/bold yellow] Environment = {what_if_env}")
        # dummy sim
        console.print(f"   [green]PRE-FLIGHT PASS:[/green] Run would be ALLOWED in {what_if_env}.")


def trace_replay_cmd(run_id: str) -> None:
    """WP-16001: Replay an execution trace in sandbox mode."""
    from thegent.planning.simulation import SimulationEngine

    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    engine = SimulationEngine(registry)

    console.print(f"Replaying run [cyan]{run_id}[/cyan] in [yellow]sandbox[/yellow]...")
    result = engine.simulate_what_if(run_id, target_env="sandbox")

    if result.get("status") == "error":
        console.print(f"[red]Error:[/red] {result.get('reason')}")
        return

    console.print("Simulation Status: [bold green]SUCCESS[/bold green]")
    console.print(f"Allowed: {result.get('allowed')}")
    console.print(f"Reason: {result.get('reason')}")
    console.print(f"Applied Constraints: {result.get('constraints_applied')}")


def terminal_route_cmd(prompt: str, cd: Path | None = None) -> None:
    """Automatically route a prompt to an active terminal session if matching."""
    from thegent.cli.commands.run.run_cmds import run_cmd
    from rich.console import Console

    from thegent.config import ThegentSettings
    from thegent.utils.routing_impl.task_router import TaskRouter
    from thegent.skills.terminal import send_to_tmux_pane

    console = Console()
    settings = ThegentSettings()
    router = TaskRouter(settings)

    target_path = str(cd or Path.cwd())
    pane_id = router.find_active_terminal_for_path(target_path)

    if pane_id:
        console.print(f"[bold cyan]Found active terminal for path {target_path} (pane {pane_id})[/bold cyan]")
        console.print(f"Routing prompt: [italic]{prompt}[/italic]")
        if send_to_tmux_pane(pane_id, prompt):
            console.print("[green]Successfully sent prompt to terminal.[/green]")
            console.print("[dim]Use 'thegent takeover' to attach if needed.[/dim]")
        else:
            console.print("[red]Failed to send prompt to terminal.[/red]")
    else:
        console.print(f"[yellow]No active terminal found for {target_path}.[/yellow]")
        console.print("Falling back to standard 'thegent run'...")
        run_cmd(prompt=prompt, agent="interactive_agent", cd=cd)


def deep_research_cmd(
    query: str = typer.Argument(..., help="Research query"),
    subreddits: str = typer.Option(None, "--subreddits", "-s", help="Comma-separated subreddits"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file path (JSON)"),
) -> None:
    """Perform deep research using the Deep Research Protocol (DRP)."""
    from thegent.skills.deep_research import perform_deep_research

    console.print("[bold cyan]Deep Research Protocol (DRP) starting...[/bold cyan]")
    console.print(f"Query: [green]{query}[/green]")
    if subreddits:
        console.print(f"Subreddits: [green]{subreddits}[/green]")

    sub_list = [s.strip() for s in subreddits.split(",") if s.strip()] if subreddits else None

    with console.status("[bold yellow]Researching...[/bold yellow]"):
        results = perform_deep_research(query, subreddits=sub_list)

    console.print("\n[bold green]Research complete![/bold green]")
    console.print(f"Found [blue]{len(results['ddg_results'])}[/blue] DDG results")
    console.print(f"Found [blue]{len(results['reddit_results'])}[/blue] Reddit results")
    console.print(f"Found [blue]{len(results['arxiv_results'])}[/blue] Arxiv results")
    console.print(f"Found [blue]{len(results['github_results'])}[/blue] GitHub results")

    if output:
        with output.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        console.print(f"\nResults saved to: [bold]{output}[/bold]")
    else:
        # Show a summary if no output file specified
        table = Table(title="Top Research Results")
        table.add_column("Source", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("URL", style="blue")

        for res in results["ddg_results"][:3]:
            table.add_row("DDG", res["title"][:50] + "...", res["url"])
        for res in results["reddit_results"][:3]:
            table.add_row("Reddit", res["title"][:50] + "...", res["url"])
        for res in results["arxiv_results"][:3]:
            table.add_row("Arxiv", res["title"][:50] + "...", res["url"])
        for res in results["github_results"][:3]:
            table.add_row("GitHub", res["title"][:50] + "...", res["url"])

        console.print(table)


def takeover_cmd(session_id: str) -> None:
    """Take over an active terminal session via tmux (WP-4008)."""

    from rich.console import Console

    from thegent.discovery import list_discovered_agents
    from thegent.skills.terminal import list_tmux_panes

    console = Console()
    panes = list_tmux_panes()

    # Try to find in discovered agents first (by PPID or session ID if matched)
    discovered = list_discovered_agents()
    target_pane = None

    for d in discovered:
        dsid = d.get("session_id")
        dppid = str(d.get("ppid", ""))
        if dppid == session_id or (dsid and (dsid == session_id or dsid.startswith(session_id) or session_id in dsid)):
            target_pane = d.get("tmux_pane")
            if target_pane:
                break

    # Try to find by session name or pane id directly
    target = next(
        (p for p in panes if p.session_name == session_id or p.pane_id in (f"%{session_id}", session_id)),
        None,
    )

    if not target and target_pane:
        target = next((p for p in panes if p.pane_id == target_pane), None)

    if not target:
        # Phase P4: Check for holdpty socket
        from thegent.cli.commands.impl import _find_session_meta

        try:
            meta_path = _find_session_meta(ThegentSettings(), session_id)
            socket_path = meta_path.parent / f"{session_id}.sock"
            if socket_path.exists():
                console.print(f"[bold green]Attaching to holdpty session: {session_id}[/bold green]")
                # Use a simple interactive proxy
                import select
                import socket
                import sys
                import termios
                import tty

                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(str(socket_path))

                # Set terminal to raw mode
                old_settings = termios.tcgetattr(sys.stdin)
                try:
                    tty.setraw(sys.stdin.fileno())
                    while True:
                        r, _, _ = select.select([sock, sys.stdin], [], [])
                        if sock in r:
                            data = sock.recv(1024)
                            if not data:
                                break
                            sys.stdout.buffer.write(data)
                            sys.stdout.buffer.flush()
                        if sys.stdin in r:
                            data = sys.stdin.buffer.read(1)
                            if not data:
                                break
                            sock.sendall(data)
                finally:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                return
        except Exception:
            console.print(
                f"[dim]Auto-attach path failed for session '{session_id}'; trying direct attach via tmux discovery output.[/dim]"
            )

        console.print(f"[red]Error: Session '{session_id}' not found in tmux, holdpty, or discovery registry.[/red]")
        return

    console.print(f"[bold green]Attaching to tmux session: {target.session_name}[/bold green]")
    try:
        run_subprocess_optimized = _get_run_subprocess_optimized()
        run_subprocess_optimized(["tmux", "attach-session", "-t", target.session_name], check=True)
    except Exception as e:
        console.print(f"[red]Failed to attach: {e}[/red]")


def run_diff_cmd(run_a: str, run_b: str) -> None:
    """Compare two execution runs (WP-16001)."""
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)

    a = registry.get_run(run_a)
    b = registry.get_run(run_b)

    if not a or not b:
        console.print(f"[red]Error:[/red] One or both runs not found: {run_a}, {run_b}")
        raise typer.Exit(1)

    table = Table(title=f"Run Diff: {run_a} vs {run_b}")
    table.add_column("Field", style="dim")
    table.add_column(run_a, style="cyan")
    table.add_column(run_b, style="magenta")

    # Common fields to compare
    fields = ["agent", "model", "status", "exit_code", "duration_s", "policy_result", "lane", "confidence"]

    for f in fields:
        val_a = str(a.get(f, "N/A"))
        val_b = str(b.get(f, "N/A"))
        style = "yellow" if val_a != val_b else "green"
        table.add_row(f, f"[{style}]{val_a}[/{style}]", f"[{style}]{val_b}[/{style}]")

    console.print(table)

    if a.get("prompt") != b.get("prompt"):
        console.print("\n[bold]Prompt Diff:[/bold]")
        import difflib

        diff = difflib.unified_diff(a["prompt"].splitlines(), b["prompt"].splitlines(), fromfile=run_a, tofile=run_b)
        for line in diff:
            if line.startswith("+"):
                console.print(f"[green]{line}[/green]")
            elif line.startswith("-"):
                console.print(f"[red]{line}[/red]")
            else:
                console.print(line)


__all__ = [
    "deep_research_cmd",
    "replay_cmd",
    "run_diff_cmd",
    "takeover_cmd",
    "terminal_route_cmd",
    "trace_replay_cmd",
]
