"""Thegent CLI run commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import orjson as json
from pathlib import Path

from thegent.cli.commands._cli_shared import _resolve_session_id, console

def loop_cmd(
    prompt: str,
    todo_spec: str,
    agent: str | None = None,
    checker: str = "antigravity",
    loop_mode: str = "soft",
    cd: Path | None = None,
) -> None:
    """Run a Lifecycle loop with Checker oversight."""
    from rich.console import Console

    from thegent.cli.commands.impl import loop_impl

    local_console = Console()
    local_console.print(f"[bold cyan]Starting Lifecycle loop ({loop_mode})...[/bold cyan]")

    def on_worker_output(text: str) -> None:
        local_console.print(text, end="")

    def on_progress(iteration: int, total: int, message: str) -> None:
        local_console.print(f"[dim][Iteration {iteration}/{total}] {message}[/dim]")

    res = loop_impl(
        agent=agent or "cursor",
        prompt=prompt,
        todo_spec=todo_spec,
        checker=checker,
        mode=loop_mode,
        cd=cd,
        on_worker_output=on_worker_output,
        on_progress=on_progress,
    )

    local_console.print(f"\n[bold green]Loop finished after {res['iterations']} iterations.[/bold green]")

def loop_send_cmd(session_id: str | None = None, prompt: str = "") -> None:
    """Send a prompt to a running Lifecycle loop (human or agent takeover)."""
    sid = _resolve_session_id(session_id)
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    session_dir = settings.session_dir / sid
    session_dir.mkdir(parents=True, exist_ok=True)
    takeover_file = session_dir / "takeover.json"
    takeover_file.write_text(json.dumps({"prompt": prompt}).decode(), encoding="utf-8")
    console.print(f"[green]Takeover input sent to loop session {sid}.[/green]")
    console.print("[dim]The loop will use this as the next prompt on its next iteration.[/dim]")

def loop_stop_cmd(session_id: str | None = None) -> None:
    """Send STOP signal to a running Lifecycle loop."""
    sid = _resolve_session_id(session_id)
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    session_dir = settings.session_dir / sid
    session_dir.mkdir(parents=True, exist_ok=True)
    stop_file = session_dir / "STOP"
    stop_file.write_text("STOP")
    console.print(f"[green]Stop signal sent to loop session {sid}.[/green]")
__all__ = [
    "loop_cmd",
    "loop_send_cmd",
    "loop_stop_cmd",
]
