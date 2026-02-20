"""Logical stream: Agent Execution and Lifecycle."""

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

console = Console()
app = typer.Typer(help="Execute agents, background sessions, and history.")


@app.command("agent", help="Run an agent task (Immediate, Background, or Loop).")
def run_agent(
    prompt: str = typer.Argument(..., help="Prompt for the agent"),
    agent: str | None = typer.Option(None, "--agent", "-a", help="Specific agent/droid name"),
    model: str | None = typer.Option(None, "--model", "-m", help="Specific LLM model to use"),
    bg: bool = typer.Option(False, "--bg", help="Run in background as a session"),
    loop: bool = typer.Option(False, "--loop", help="Run in a continuous Lifecycle loop"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory for the task"),
    timeout: int = typer.Option(90, "--timeout", help="Execution time budget in seconds"),
    full: bool = typer.Option(False, "--full", help="Show full agent output including stderr"),
    # Advanced / Governance Options
    run_id: str | None = typer.Option(None, "--run-id", help="Explicit run ID"),
    task_id: str | None = typer.Option(None, "--task-id", help="Associated Task ID (WP-16002)"),
    lane: str = typer.Option("standard", "--lane", help="Execution lane (standard|critical)"),
    routing: str | None = typer.Option(None, "--routing", "-R", help="Routing policy"),
    failover: bool = typer.Option(False, "--failover", help="Enable automatic failover"),
    contract_version: str | None = typer.Option(None, "--contract-version", help="Negotiate contract version"),
    domain: str | None = typer.Option(None, "--domain", help="Domain tag for policy evaluation"),
    speculative: bool = typer.Option(False, "--speculative", help="Enable speculative execution"),
    idempotency_token: str | None = typer.Option(None, "--idempotency-token", help="Token for replay detection"),
):
    from thegent.cli.commands.cli import bg_cmd, loop_cmd, run_cmd

    if loop:
        loop_cmd(prompt=prompt, todo_spec="Complete the task", agent=agent, cd=cd)
    elif bg:
        bg_cmd(
            agent=agent,
            prompt=prompt,
            cd=cd,
            mode="write",
            timeout=timeout,
            full=full,
            model=model,
            run_id=run_id,
            task_id=task_id,
            lane=lane,
            routing=routing,
            failover=failover,
            contract_version=contract_version,
            domain=domain,
            speculative=speculative,
            idempotency_token=idempotency_token,
        )
    else:
        run_cmd(
            agent=agent,
            prompt=prompt,
            cd=cd,
            model=model,
            timeout=timeout,
            full=full,
            run_id=run_id,
            task_id=task_id,
            lane=lane,
            routing=routing,
            failover=failover,
            contract_version=contract_version,
            domain=domain,
            speculative=speculative,
            idempotency_token=idempotency_token,
        )


@app.command("history", help="View execution run history.")
def run_history(
    limit: int = typer.Option(50, "--limit", "-l", help="Number of recent runs to show"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json|md)"),
):
    from thegent.cli.commands.cli import history_cmd

    history_cmd(limit=limit, format=format)


@app.command("logs", help="View telemetry and logs for specific runs.")
def run_logs(
    session_id: str | None = typer.Argument(None, help="Session ID to view logs for (defaults to latest)"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output in real-time"),
):
    from thegent.cli.commands.cli import logs_cmd

    logs_cmd(session_id=session_id, follow=follow)


@app.command("ps", help="List active background sessions.")
def run_ps(
    all_sessions: bool = typer.Option(False, "--all", "-a", help="Show all sessions, not just current owner"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Filter by owner tag"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json|md)"),
    include_contract: bool = typer.Option(False, "--include-contract", help="Include routing contract metadata"),
):
    from thegent.cli.commands.cli import ps_cmd

    ps_cmd(all_sessions=all_sessions, owner=owner, format=format, include_contract=include_contract)


@app.command("stop", help="Terminate a running session or loop.")
def run_stop(session_id: str | None = typer.Argument(None, help="Session ID to terminate")):
    from thegent.cli.commands.cli import loop_stop_cmd, stop_cmd

    try:
        loop_stop_cmd(session_id=session_id)
    except Exception:
        stop_cmd(session_id=session_id)
