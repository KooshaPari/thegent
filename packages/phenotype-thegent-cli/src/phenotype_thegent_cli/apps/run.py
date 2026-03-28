"""Logical stream: Agent Execution and Lifecycle."""

from pathlib import Path
from typing import TypeVar, cast

import typer
from rich.console import Console
from typer.models import ArgumentInfo, OptionInfo

console = Console()
app = typer.Typer(help="Execute agents, background sessions, and history.")

_T = TypeVar("_T")


def _unwrap_typer_default(value: _T) -> _T:
    """Return concrete default value when command function is called directly in Python."""
    if isinstance(value, (OptionInfo | ArgumentInfo)):
        return cast("_T", value.default)
    return value


def _auto_select_agent(prompt: str) -> str | None:
    """Auto-select the best agent for a prompt using the capability index (WL-034).

    Returns the top-ranked agent name, or None if no agents are indexed or
    no match is found.
    """
    try:
        from phenotype_thegent_agents.capability_index import CapabilityIndex

        recommendations = CapabilityIndex.get().recommend(prompt, top_n=1)
        if recommendations:
            return recommendations[0].name
        return None
    except Exception:
        return None


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
    no_auto_agent: bool = typer.Option(
        False,
        "--no-auto-agent",
        help="Disable automatic agent selection from capability index (WL-034)",
    ),
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
    # Remote compute options
    remote: str | None = typer.Option(
        None,
        "--remote",
        "-r",
        help="Execute on remote node (hostname or 'auto' for round-robin)",
    ),
    remote_sync: bool = typer.Option(
        False,
        "--remote-sync",
        help="Sync workspace to remote before execution (requires --remote)",
    ),
    output_schema: str | None = typer.Option(
        None,
        "--output-schema",
        help="Path to JSON Schema file; validate agent output against it (WL-113)",
    ),
    image: list[str] | None = typer.Option(
        None,
        "--image",
        help="Image input path(s)/URL(s) for image-capable runs (WL-114).",
    ),
    audio: list[str] | None = typer.Option(
        None,
        "--audio",
        help="Transcript input path(s) for WL-116 audio pipeline (currently accepts .txt/.md/.srt transcript files).",
    ),
    google_grounding: bool = typer.Option(
        False,
        "--google-grounding",
        help="Enable Gemini Google grounding flow (WL-119).",
    ),
    skill: list[str] | None = typer.Option(
        None,
        "--skill",
        help="Activate skill instructions by name (repeatable) (WL-101).",
    ),
) -> None:
    """Run an agent task against a prompt.

    When no --agent is specified, the capability index is consulted to pick the
    best-matching agent for the prompt (WL-034). Use --no-auto-agent to skip this.
    """
    from phenotype_thegent_cli.commands.cli import bg_cmd, loop_cmd, run_cmd

    prompt = str(_unwrap_typer_default(prompt))
    agent = _unwrap_typer_default(agent)
    model = _unwrap_typer_default(model)
    bg = bool(_unwrap_typer_default(bg))
    loop = bool(_unwrap_typer_default(loop))
    cd = _unwrap_typer_default(cd)
    timeout = int(_unwrap_typer_default(timeout))
    full = bool(_unwrap_typer_default(full))
    no_auto_agent = bool(_unwrap_typer_default(no_auto_agent))
    run_id = _unwrap_typer_default(run_id)
    task_id = _unwrap_typer_default(task_id)
    lane = str(_unwrap_typer_default(lane))
    routing = _unwrap_typer_default(routing)
    failover = bool(_unwrap_typer_default(failover))
    contract_version = _unwrap_typer_default(contract_version)
    domain = _unwrap_typer_default(domain)
    speculative = bool(_unwrap_typer_default(speculative))
    idempotency_token = _unwrap_typer_default(idempotency_token)
    remote = _unwrap_typer_default(remote)
    remote_sync = bool(_unwrap_typer_default(remote_sync))
    output_schema = _unwrap_typer_default(output_schema)
    image = _unwrap_typer_default(image)
    audio = _unwrap_typer_default(audio)
    google_grounding = bool(_unwrap_typer_default(google_grounding))
    skill = _unwrap_typer_default(skill)

    effective_agent = agent if isinstance(agent, str) else None

    # WL-034: Auto-select agent from capability index when --agent not specified
    if effective_agent is None and not no_auto_agent:
        selected = _auto_select_agent(prompt)
        if selected is not None:
            from phenotype_thegent_agents.capability_index import CapabilityIndex

            recs = CapabilityIndex.get().recommend(prompt, top_n=1)
            score = recs[0].score if recs else 0.0
            console.print(f"[dim]Using agent: {selected} (score: {score:.4f})[/dim]")
            effective_agent = selected

    # Handle remote execution
    if isinstance(remote, str) and remote:
        from phenotype_thegent_core.compute.remote_runner import RemoteRunner

        runner = RemoteRunner(
            node=remote if remote != "auto" else None,
            sync_workspace=remote_sync,
        )
        result = runner.run_agent_task(
            prompt=prompt,
            agent=effective_agent,
            timeout_s=timeout,
            cd=str(cd) if isinstance(cd, Path) else None,
        )
        console.print(f"[dim]Remote execution on {result.node} completed with exit code {result.exit_code}[/dim]")
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[red]{result.stderr}[/red]")
        return

    if loop:
        loop_cmd(prompt=prompt, todo_spec="Complete the task", agent=effective_agent, cd=cd)
    elif bg:
        bg_cmd(
            agent=effective_agent,
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
            owner=None,
            image=image,
            skills=skill,
        )
    else:
        run_cmd(
            agent=effective_agent,
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
            output_schema=output_schema,
            image=image,
            audio=audio,
            google_grounding=google_grounding,
            skills=skill,
        )


@app.command("free", help="Run a task with the free-tier agent, auto-selecting from capability index (WL-034).")
def run_free(
    prompt: str = typer.Argument(..., help="Prompt for the agent"),
    model: str | None = typer.Option(None, "--model", "-m", help="Specific LLM model to use"),
    bg: bool = typer.Option(False, "--bg", help="Run in background as a session"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory for the task"),
    timeout: int = typer.Option(300, "--timeout", help="Execution time budget in seconds"),
    full: bool = typer.Option(False, "--full", help="Show full agent output including stderr"),
    no_auto_agent: bool = typer.Option(
        False,
        "--no-auto-agent",
        help="Disable automatic agent selection; use default free-tier agent (copilot)",
    ),
    run_id: str | None = typer.Option(None, "--run-id", help="Explicit run ID"),
    task_id: str | None = typer.Option(None, "--task-id", help="Associated Task ID (WP-16002)"),
) -> None:
    """Run a task with free-tier agent.

    When no --no-auto-agent flag is set, the capability index is consulted to
    pick the best-matching agent (WL-034). Falls back to 'copilot' (gpt-5-mini)
    when no indexed agent matches.
    """
    from phenotype_thegent_cli.commands.cli import bg_cmd, run_cmd

    effective_agent: str | None = None
    effective_model: str | None = model

    if not no_auto_agent:
        selected = _auto_select_agent(prompt)
        if selected is not None:
            from phenotype_thegent_agents.capability_index import CapabilityIndex

            recs = CapabilityIndex.get().recommend(prompt, top_n=1)
            score = recs[0].score if recs else 0.0
            console.print(f"[dim]Using agent: {selected} (score: {score:.4f})[/dim]")
            effective_agent = selected
        else:
            # No capability match: fall through to default free-tier
            effective_agent = "copilot"
            effective_model = effective_model or "gpt-5-mini"
    else:
        effective_agent = "copilot"
        effective_model = effective_model or "gpt-5-mini"

    if bg:
        bg_cmd(
            agent=effective_agent,
            prompt=prompt,
            cd=cd,
            mode="write",
            timeout=timeout,
            full=full,
            model=effective_model,
            run_id=run_id,
            task_id=task_id,
            owner=None,
        )
    else:
        run_cmd(
            agent=effective_agent,
            prompt=prompt,
            cd=cd,
            model=effective_model,
            timeout=timeout,
            full=full,
            run_id=run_id,
            task_id=task_id,
        )


@app.command("history", help="View execution run history.")
def run_history(
    limit: int = typer.Option(50, "--limit", "-l", help="Number of recent runs to show"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json|md)"),
) -> None:
    from phenotype_thegent_cli.commands.cli import history_cmd

    history_cmd(limit=limit, format=format)


@app.command("logs", help="View telemetry and logs for specific runs.")
def run_logs(
    session_id: str | None = typer.Argument(None, help="Session ID to view logs for (defaults to latest)"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output in real-time"),
) -> None:
    from phenotype_thegent_cli.commands.cli import logs_cmd

    logs_cmd(session_id=session_id, follow=follow)


@app.command("ps", help="List active background sessions.")
def run_ps(
    all_sessions: bool = typer.Option(False, "--all", "-a", help="Show all sessions, not just current owner"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Filter by owner tag"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json|md)"),
    include_contract: bool = typer.Option(False, "--include-contract", help="Include routing contract metadata"),
) -> None:
    from phenotype_thegent_cli.commands.cli import ps_cmd

    ps_cmd(all_sessions=all_sessions, owner=owner, format=format, include_contract=include_contract)


@app.command("stop", help="Terminate a running session or loop.")
def run_stop(session_id: str | None = typer.Argument(None, help="Session ID to terminate")) -> None:
    from phenotype_thegent_cli.commands.cli import loop_stop_cmd, stop_cmd

    try:
        loop_stop_cmd(session_id=session_id)
    except Exception:
        stop_cmd(session_id=session_id)


@app.command("resume", help="Resume a session using the stable state contract (WL-110).")
def run_resume(
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


@app.command("fork", help="WL-106: Fork a session at a 1-based turn index (stub wiring).")
def run_fork(
    session_id: str = typer.Argument(..., help="Source session ID to fork"),
    from_turn: int | None = typer.Option(
        None,
        "--from-turn",
        help="1-based turn cutoff to copy into the fork (defaults to full history)",
    ),
    new_session_id: str | None = typer.Option(None, "--new-session-id", help="Optional explicit ID for forked session"),
) -> None:
    if from_turn is not None and from_turn < 1:
        raise typer.BadParameter("from_turn must be 1 or greater", param_hint="--from-turn")
    from phenotype_thegent_cli.commands.cli import session_fork_cmd

    session_fork_cmd(session_id=session_id, from_turn=from_turn, new_session_id=new_session_id)


@app.command("rollback", help="WL-106: Roll back a session by N turns (stub wiring).")
def run_rollback(
    session_id: str = typer.Argument(..., help="Session ID to roll back"),
    n_turns: int = typer.Option(..., "--n-turns", help="Number of latest turns to remove"),
) -> None:
    if n_turns < 1:
        raise typer.BadParameter("n-turns must be 1 or greater", param_hint="--n-turns")
    from phenotype_thegent_cli.commands.cli import session_rollback_cmd

    session_rollback_cmd(session_id=session_id, n_turns=n_turns)


# ---------------------------------------------------------------------------
# Harness Terminal Management (integrated under agent run)
# ---------------------------------------------------------------------------


@app.command("attach", help="Attach to a running agent harness terminal session.")
def run_attach(
    harness: str = typer.Argument(..., help="Harness type (cursor, codex, claude, ante, droid)"),
    session_id: str = typer.Argument(..., help="Session ID to attach to"),
    host_id: str | None = typer.Option(None, "--host", help="Remote host ID"),
) -> None:
    """Attach to a running harness terminal session."""
    from phenotype_thegent_cli.commands.impl import harness_interact_impl

    result = harness_interact_impl(
        harness=harness,
        action="attach_terminal",
        host_id=host_id,
        session_id=session_id,
    )

    if result.get("success"):
        console.print(f"[green]Attached to session:[/green] {session_id}")
    else:
        console.print(f"[red]Error:[/red] {result.get('error', result.get('stderr', 'Unknown'))}")


@app.command("send", help="Send a message/prompt to a harness.")
def run_send(
    harness: str = typer.Argument(..., help="Harness type (cursor, codex, claude, ante, droid)"),
    prompt: str = typer.Argument(..., help="Prompt to send to the harness"),
    host_id: str | None = typer.Option(None, "--host", help="Remote host ID"),
) -> None:
    """Send a prompt to a harness."""
    from phenotype_thegent_cli.commands.impl import harness_interact_impl

    result = harness_interact_impl(
        harness=harness,
        action="send_message",
        host_id=host_id,
        prompt=prompt,
    )

    if result.get("success"):
        console.print(f"[green]Sent to {harness}:[/green] {result.get('stdout', '')}")
    else:
        console.print(f"[red]Error:[/red] {result.get('error', result.get('stderr', 'Unknown'))}")
