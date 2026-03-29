"""Thegent CLI run commands domain - facade with re-exports (WL-124)."""

# @trace WL-124
from __future__ import annotations

from pathlib import Path
from typing import Literal, cast

import typer
from typer.models import OptionInfo

from thegent.models.catalog import Route
from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    _format_context_usage_line,
    _format_grounding_sources_lines,
    _format_transcript_summary_line,
    _inject_skill_instructions,
    _normalize_output_format,
    console,
)


def run_cmd(
    agent: str | None,
    prompt: str,
    cd: Path | None = None,
    mode: str = "write",
    timeout: int = 90,
    full: bool = False,
    live: bool = False,
    model: str | None = None,
    provider: str | None = None,
    failover: bool = False,
    routing: str | None = None,
    include_contract: bool = False,
    run_id: str | None = None,
    lane: str = "standard",
    idempotency_token: str | None = None,
    confidence: float | None = None,
    arbitration: str | None = None,
    override_reason: str | None = None,
    contract_version: str | None = None,
    domain: str | None = None,
    speculative: bool = False,
    search: bool = True,
    debug: bool = False,
    task_id: str | None = None,
    shadow: bool = typer.Option(False, "--shadow", help="Run agent in an isolated shadow workspace (git worktree)"),
    lock: list[str] | None = typer.Option(None, "--lock", help="Lock specific resources/files (non-worktree)"),
    remote: str | None = typer.Option(None, "--remote", help="Remote host to offload execution to"),
    output_schema: str | None = typer.Option(
        None, "--output-schema", help="Path to JSON Schema file; validate agent output against it (WL-113)"
    ),
    image: list[str] | None = typer.Option(
        None, "--image", help="Image input path(s)/URL(s) for image-capable runs (WL-114)"
    ),
    audio: list[str] | None = typer.Option(
        None, "--audio", help="WL-116 transcript inputs (.txt/.md for current slice)"
    ),
    google_grounding: bool = typer.Option(
        False, "--google-grounding", help="Enable Gemini Google grounding flow (WL-119)"
    ),
    reasoning: str | None = typer.Option(
        None,
        "--reasoning",
        help="Reasoning effort level: minimal, low, medium, high, xhigh (WL-112)",
    ),
    skills: list[str] | None = typer.Option(
        None,
        "--skill",
        help="Activate skill instructions by name (repeatable) (WL-101).",
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Bypass the LLM response cache; always hit the backend (FR-CACHE-002).",
        is_flag=True,
    ),
) -> None:
    """Run an agent or droid with the given prompt. Model-first: agent=None, model set."""
    if isinstance(shadow, OptionInfo):
        shadow = False
    if isinstance(lock, OptionInfo):
        lock = None
    if isinstance(remote, OptionInfo):
        remote = None
    if isinstance(output_schema, OptionInfo):
        output_schema = None
    if isinstance(image, OptionInfo):
        image = None
    if isinstance(audio, OptionInfo):
        audio = None
    if isinstance(google_grounding, OptionInfo):
        google_grounding = False
    if isinstance(reasoning, OptionInfo):
        reasoning = None
    if isinstance(skills, OptionInfo):
        skills = None
    if isinstance(no_cache, OptionInfo):
        no_cache = False

    # Apply --no-cache: replace the module-level default ResponseCache with a
    # disabled instance so that CliproxyHTTPClient picks it up automatically.
    if no_cache:
        from thegent.cache.response_cache import configure_default_cache
        configure_default_cache(enabled=False)

    from thegent.cli.commands.impl import run_impl
    from thegent.models import ModelCatalog, resolve_route

    # Model-first: resolve agent via routing policy (WP-5003 cost_quality supported)
    effective_agent = agent
    if agent is None and model:
        settings = ThegentSettings()
        from thegent.models.catalog import normalize_route_policy

        policy = normalize_route_policy(routing or settings.default_routing)
        routes = ModelCatalog.routes_for(model)
        available = ", ".join(sorted({str(r.provider) for r in routes if getattr(r, "provider", None) is not None}))
        if not available:
            available = "none"

        resolved = None
        if provider:
            resolved = resolve_route(
                model,
                provider_hint=provider,
                policy=policy,
                quality_floor=getattr(settings, "cost_quality_min_weight", 0.1),
                lane="standard",
            )
        elif routes:
            resolved = routes[0]

        if resolved is None:
            if provider:
                console.print(
                    f"[red]Model '{model}' not available via provider '{provider}'. Available: {available}.[/red]"
                )
            else:
                console.print(f"[red]Model '{model}' has no available providers.[/red]")
            raise typer.Exit(1)
        if hasattr(resolved, "provider") and not isinstance(resolved, (list, tuple)):
            effective_agent = resolved.provider
        else:
            effective_agent = resolved

    # WP-5002: Session-start warning when session count high (memory optimization)
    settings = ThegentSettings()
    thresh = getattr(settings, "session_warn_threshold", 5)
    if isinstance(thresh, int) and thresh > 0:
        from thegent.cli.commands.impl import ps_impl

        sessions = ps_impl(all=True)
        running = sum(1 for s in sessions if (s.get("status") or "").lower() == "running")
        if running >= thresh:
            console.print(
                f"[yellow]Tip: {running} active session(s) detected. Each spawns LSP/MCP processes (~1–2 GB).[/yellow]"
            )
            console.print(
                "[dim]Run 'thegent mcp prune --force' to free memory, or 'thegent mcp spotlight-exclude' on macOS.[/dim]"
            )

    # WL-112: Validate --reasoning option
    _valid_reasoning = frozenset({"minimal", "low", "medium", "high", "xhigh"})
    if reasoning is not None and reasoning not in _valid_reasoning:
        console.print(
            f"[red]Invalid --reasoning value '{reasoning}'. Must be one of: {', '.join(sorted(_valid_reasoning))}[/red]"
        )
        raise typer.Exit(1)

    # WP-X2/X5/X6/X7: Unified execution via run_impl (FSM + Policy + Telemetry)
    effective_prompt = _inject_skill_instructions(prompt, skills)
    effective_agent_name: str | None
    if isinstance(effective_agent, Route):
        effective_agent_name = effective_agent.provider
    elif isinstance(effective_agent, str):
        effective_agent_name = effective_agent
    else:
        effective_agent_name = None
    res = run_impl(
        agent=effective_agent_name or agent,
        prompt=effective_prompt,
        cd=cd,
        mode=mode,
        timeout=timeout,
        full=full,
        live=live,
        model=model,
        provider=provider,
        run_id=run_id,
        owner=None,
        include_contract=include_contract,
        lane=lane,
        confidence=confidence,
        arbitration=arbitration,
        override_reason=override_reason,
        contract_version=contract_version,
        domain=domain,
        speculative=speculative,
        routing=routing,
        enable_search=search,
        debug=debug,
        task_id=task_id,
        shadow=shadow,
        lock=lock,
        remote=remote,
        output_schema=output_schema,
        image_paths=image,
        audio_files=audio,
        google_grounding=google_grounding,
        reasoning_effort=cast("Literal['minimal', 'low', 'medium', 'high', 'xhigh'] | None", reasoning),
    )

    # Telemetry: record run outcome
    output_formatter = _normalize_output_format(res.get("format", "text"))
    if output_formatter == "json":
        console.print_json(data=res)
    elif full:
        # Full output mode: print stdout and stderr separately
        output = res.get("output") or res.get("stdout", "")
        if output:
            console.print(output)
        if res.get("stderr"):
            console.print(f"[dim]{res['stderr']}[/dim]")
    elif output_formatter in ("structured", "markdown", "md"):
        if res.get("output"):
            console.print(res["output"])
        if res.get("transcript"):
            console.print("\n[dim]Transcript:[/dim]")
            console.print(res["transcript"])
    else:
        # Handle stdout/stderr keys for test compatibility
        output = res.get("output") or res.get("stdout", "")
        if output:
            console.print(output)
        # Handle timed_out warning
        if res.get("timed_out"):
            console.print("[yellow]Safety ceiling reached - run timed out[/yellow]")
        if res.get("usage") and full:
            usage_line = _format_context_usage_line(res["usage"])
            if usage_line:
                console.print(f"\n[dim]{usage_line}[/dim]")

        # Include audio transcript if present (WL-116)
        audio_metadata = res.get("audio_metadata")
        if audio_metadata:
            transcript_line = _format_transcript_summary_line(audio_metadata)
            if transcript_line:
                console.print(f"[dim]{transcript_line}[/dim]")

        # Include grounding sources if present (WL-119)
        grounding = res.get("grounding_sources")
        if grounding:
            grounding_lines = _format_grounding_sources_lines(grounding)
            for line in grounding_lines:
                console.print(f"[dim]{line}[/dim]")

    if res.get("exit_code") and res["exit_code"] != 0:
        if res.get("error"):
            console.print(f"[red]{res['error']}[/red]")
            if res.get("agents"):
                console.print(f"[dim]Available agents: {res['agents']}[/dim]")
        raise typer.Exit(res["exit_code"])


def bg_cmd(
    agent: str | None,
    prompt: str,
    cd: Path | None = None,
    name: str | None = typer.Option(None, "--name", help="Session name"),
    model: str | None = typer.Option(None, "--model", "-m", help="Explicit model"),
    provider: str | None = typer.Option(None, "--provider", "-p", help="Model provider"),
    timeout: int = typer.Option(90, "--timeout", "-t", help="Timeout in seconds"),
    lane: str = typer.Option("standard", "--lane", help="Routing lane"),
    confidence: float | None = typer.Option(None, "--confidence", help="Confidence threshold"),
    domain: str | None = typer.Option(None, "--domain", help="Domain context"),
    task_id: str | None = typer.Option(None, "--task-id", help="Link to task ID"),
    image: list[str] | None = typer.Option(None, "--image", help="Image input(s)"),
    audio: list[str] | None = typer.Option(None, "--audio", help="Audio input(s)"),
    skills: list[str] | None = typer.Option(None, "--skill", help="Activate skill(s)"),
) -> None:
    """Background run: spawn session and return immediately with session ID."""
    if isinstance(name, OptionInfo):
        name = None
    if isinstance(model, OptionInfo):
        model = None
    if isinstance(provider, OptionInfo):
        provider = None
    if isinstance(image, OptionInfo):
        image = None
    if isinstance(audio, OptionInfo):
        audio = None
    if isinstance(skills, OptionInfo):
        skills = None

    from thegent.cli.commands.impl import bg_impl

    effective_prompt = _inject_skill_instructions(prompt, skills)
    res = bg_impl(
        agent=agent,
        prompt=effective_prompt,
        cd=cd,
        model=model,
        provider=provider,
        timeout=timeout,
        lane=lane,
        confidence=confidence,
        domain=domain,
        task_id=task_id,
        image_paths=image,
    )

    if res.get("error"):
        console.print(f"[red]{res['error']}[/red]")
        raise typer.Exit(1)

    session_id = res.get("session_id")
    console.print(f"[bold green]Session:[/bold green] [cyan]{session_id}[/cyan]")
    if res.get("ready"):
        console.print("[dim]Status: awaiting input (ready for loop_send_cmd)[/dim]")

    if res.get("logs_path"):
        console.print(f"[dim]Logs: {res['logs_path']}[/dim]")


def retry_cmd(
    run_id: str,
) -> None:
    """Retry a failed run with the same parameters."""
    from thegent.cli.commands.impl import retry_impl

    res = retry_impl(run_id=run_id)

    if res.get("error"):
        console.print(f"[red]{res['error']}[/red]")
        raise typer.Exit(1)

    session_id = res.get("session_id")
    console.print(f"[bold green]Retry queued:[/bold green] [cyan]{session_id}[/cyan]")


# Re-export from submodules for backward compatibility
from thegent.cli.commands.run.run_cmds_loop import *  # noqa: F401, F403
from thegent.cli.commands.run.run_cmds_advanced import *  # noqa: F401, F403

__all__ = [
    "bg_cmd",
    "deep_research_cmd",
    "loop_cmd",
    "loop_send_cmd",
    "loop_stop_cmd",
    "replay_cmd",
    "retry_cmd",
    "run_cmd",
    "run_diff_cmd",
    "takeover_cmd",
    "terminal_route_cmd",
    "trace_replay_cmd",
]
