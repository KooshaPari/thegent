"""Thegent CLI governance discovery and guardrails commands.

Extracted from governance_cmds.py as part of CLI refactoring (WL-124).
"""

This module handles guardrails enforcement and discovery of external agents
and governance-relevant code patterns.
"""

# @trace WL-124
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import orjson as json
import typer
from rich.console import Console
from rich.table import Table

from thegent.cli.commands._cli_shared import (
    _normalize_output_format,
    console,
)


def discovery_register_cmd(
    agent: str = typer.Option("?", "--agent", "-a", help="Agent name"),
    pid: int = typer.Option(0, "--pid", help="Process ID of the command"),
    ppid: int = typer.Option(0, "--ppid", help="Parent Process ID (agent session)"),
    cwd: str = typer.Option(".", "--cwd", help="Current working directory"),
    command: str | None = typer.Option(None, "--cmd", help="Command name being run"),
    args: str | None = typer.Option(None, "--args", help="Arguments preview"),
    session_id: str | None = typer.Option(None, "--session-id", help="Parsed session ID"),
    token_usage_json: str | None = typer.Option(None, "--token-usage", help="Token usage JSON"),
    mcp_errors: list[str] | None = typer.Option(None, "--mcp-error", help="MCP startup error(s)"),
) -> None:
    """Register or update a discovered external agent (WP-4008)."""
=======
    import json

>>>>>>> fix/ci-remove-macos
    from thegent.discovery import register_discovered_agent

    token_usage = None
    if token_usage_json:
        import contextlib

        with contextlib.suppress(Exception):
            token_usage = json.loads(token_usage_json)

    register_discovered_agent(
        pid=pid,
        ppid=ppid,
        agent=agent,
        cwd=cwd,
        command=command,
        args_preview=args,
        session_id=session_id,
        token_usage=token_usage,
        mcp_errors=mcp_errors,
    )


def discovery_parse_cmd(
    text: str = typer.Argument(None, help="Text to parse (defaults to stdin)"),
    register: bool = typer.Option(True, "--register/--no-register", help="Register discovered sessions"),
    ppid: int = typer.Option(0, "--ppid", help="Force PPID for all discovered sessions"),
) -> None:
    """Parse CLI output for session information and register them."""
    from thegent.discovery import register_discovered_agent
    from thegent.parser import parse_cli_output

    console_obj = Console()
    if text is None:
        if sys.stdin.isatty():
            console_obj.print("[yellow]Waiting for input on stdin (Ctrl+D to finish)...[/yellow]")
        text = sys.stdin.read()

    sessions = parse_cli_output(text)
    if not sessions:
        console_obj.print("[yellow]No sessions found in output.[/yellow]")
        return

    table = Table(title="Discovered Sessions")
    table.add_column("Agent")
    table.add_column("Session ID")
    table.add_column("Tokens (Total)")
    table.add_column("Errors")

    for s in sessions:
        tokens = str(s.token_usage.total) if s.token_usage else "-"
        errors = ", ".join(s.mcp_errors) if s.mcp_errors else "-"
        table.add_row(s.agent, s.session_id, tokens, errors)

        if register:
            target_ppid = ppid or os.getpid()
            register_discovered_agent(
                pid=0,
                ppid=target_ppid,
                agent=s.agent,
                cwd=str(Path.cwd()),
                session_id=s.session_id,
                token_usage=s.token_usage.model_dump() if s.token_usage else None,
                mcp_errors=s.mcp_errors,
            )

    console_obj.print(table)
    if register:
        console_obj.print(f"[green]Registered {len(sessions)} session(s).[/green]")


def discovery_scan_cmd(
    format: str | None = typer.Option(None, "--format", "-f", help="Output: json | rich (default)"),
) -> None:
    """Scan process tree for agent CLI sessions and auto-register them.

    Detects running cursor-agent, Claude Code, and Codex processes,
    extracts session IDs from --resume= when present, and registers them
    for introspection via thegent ps, terminal takeover, and inbox.
    """
    from thegent.discovery import list_discovered_agents, scan_agent_processes

    console_obj = Console()
    registered = scan_agent_processes()

    if not format or format == "rich":
        if registered:
            table = Table(title="Discovered Agent Sessions")
            table.add_column("PID", style="cyan")
            table.add_column("Agent", style="magenta")
            table.add_column("Session ID", style="green")
            table.add_column("CWD", style="dim")
            for r in registered:
                table.add_row(
                    str(r["pid"]),
                    r.get("agent", "?"),
                    r.get("session_id") or "—",
                    r.get("cwd", "?")[:50],
                )
            console_obj.print(table)
            console_obj.print(f"[green]Registered {len(registered)} agent session(s).[/green]")
        else:
            console_obj.print("[dim]No cursor-agent, claude-code, or codex processes found.[/dim]")
        existing = list_discovered_agents()
        if existing:
            console_obj.print(f"\n[dim]Total discovered agents: {len(existing)}[/dim]")
    elif format == "json":
        console_obj.print_json(data={"registered": registered, "count": len(registered)})


def guardrails_check_cmd(prompt: str, agent: str | None = None, model: str | None = None) -> None:
    """Check a prompt against active guardrails (FR-GOV-003..006)."""
    from thegent.governance.input_guardrails import InputGuardrails

    rails = InputGuardrails()
    results = rails.check(prompt, agent=agent, model=model)

    if not results:
        console.print("[green]Prompt passed all guardrails.[/green]")
        return

    console.print("[red]Prompt FAILED guardrail checks:[/red]")
    for res in results:
        console.print(f"- [bold]{res.rail_id}[/bold]: {res.violation}")
        if res.remediation:
            console.print(f"  [dim]Remediation: {res.remediation}[/dim]")


def guardrails_show_cmd() -> None:
    """Show active guardrail configuration (FR-GOV-007)."""
    from thegent.governance.input_guardrails import InputGuardrails

    rails = InputGuardrails()

    table = Table(title="Input Guardrails Configuration")
    table.add_column("Parameter")
    table.add_column("Value")

    table.add_row("Max Chars", str(rails.prompt_max_chars))
    table.add_row("Blocklist Patterns", str(len(rails.prompt_blocklist_patterns)))
    table.add_row("Agent Allowlist", ", ".join(rails.agent_allowlist) if rails.agent_allowlist else "None")
    table.add_row("Model Allowlist", ", ".join(rails.model_allowlist) if rails.model_allowlist else "None")
    table.add_row(
        "CWD Allowed Prefixes", ", ".join(rails.cwd_allowed_prefixes) if rails.cwd_allowed_prefixes else "None"
    )

    console.print(table)


__all__ = [
    "discovery_parse_cmd",
    "discovery_register_cmd",
    "discovery_scan_cmd",
    "guardrails_check_cmd",
    "guardrails_show_cmd",
]
