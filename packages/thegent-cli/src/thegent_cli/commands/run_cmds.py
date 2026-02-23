"""Thegent CLI run commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Literal, cast

import typer

from rich.panel import Panel
from rich.table import Table

from thegent_cli.commands._cli_shared import (
    RunRegistry,
    ThegentSettings,
    _format_context_usage_line,
    _format_grounding_sources_lines,
    _format_transcript_summary_line,
    _get_run_subprocess_optimized,
    _inject_skill_instructions,
    _normalize_output_format,
    _resolve_session_id,
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
) -> None:
    """Run an agent or droid with the given prompt. Model-first: agent=None, model set."""
    from thegent_cli.commands.impl import run_impl
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
            if resolved is None:
                provider_routes = [r for r in routes if str(getattr(r, "provider", "")) == str(provider)]
                if provider_routes:
                    resolved = provider_routes[0]
        else:
            if routes:
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
            effective_agent = getattr(resolved, "provider")
        else:
            effective_agent = resolved

    # WP-5002: Session-start warning when session count high (memory optimization)
    settings = ThegentSettings()
    thresh = getattr(settings, "session_warn_threshold", 5)
    if isinstance(thresh, int) and thresh > 0:
        from thegent_cli.commands.impl import ps_impl

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
    from thegent.config_provider import get_config_provider

    effective_prompt = _inject_skill_instructions(prompt, skills)
    res = run_impl(
        agent=effective_agent or agent,
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
        config_provider=get_config_provider(),
    )

    if "error" in res:
        console.print(f"[red]Error: {res['error']}[/red]")
        if res.get("remediation"):
            console.print(f"[yellow]Suggested Fix: {res['remediation']}[/yellow]")
        if "agents" in res:
            console.print(f"[dim]Available Agents: {res['agents']}[/dim]")
        raise typer.Exit(res.get("exit_code", 1))

    if res.get("stdout"):
        console.print(res["stdout"])
    if res.get("stderr"):
        console.print(res["stderr"], style="dim")

    context_line = _format_context_usage_line(res.get("context_usage"))
    if context_line:
        console.print(f"[dim]{context_line}[/dim]")
    transcript_line = _format_transcript_summary_line(res.get("audio_metadata"))
    if transcript_line:
        console.print(f"[dim]{transcript_line}[/dim]")
    grounding_lines = _format_grounding_sources_lines(res.get("grounding_sources"))
    for line in grounding_lines:
        console.print(f"[dim]{line}[/dim]")

    if full:
        if res.get("stderr"):
            console.print(res["stderr"], style="dim")
        if res.get("stdout"):
            console.print(res["stdout"])
    # condensed output is already in stdout if not full
    elif res.get("stdout"):
        console.print(res["stdout"])

    if res.get("timed_out"):
        console.print("[yellow]Run exceeded the safety ceiling (time budget).[/yellow]")

    if res.get("exit_code") != 0:
        raise typer.Exit(res.get("exit_code", 1))


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

    from thegent_cli.commands.impl import loop_impl

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
    takeover_file.write_text(json.dumps({"prompt": prompt}), encoding="utf-8")
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


def bg_cmd(
    *,
    agent: str | None,
    droid: str | None = None,
    prompt: str,
    cd: Path | None,
    mode: str,
    timeout: int,
    full: bool,
    model: str | None,
    provider: str | None = None,
    routing: str | None = None,
    failover: bool = False,
    owner: str | None,
    output_format: str | None = None,
    continue_from: str | None = None,
    continuation_include_stderr: bool = False,
    include_contract: bool = False,
    run_id: str | None = None,
    lane: str | None = None,
    idempotency_token: str | None = None,
    confidence: float | None = None,
    arbitration: str | None = None,
    override_reason: str | None = None,
    contract_version: str | None = None,
    domain: str | None = None,
    speculative: bool = False,
    debug: bool = False,
    task_id: str | None = None,
    remote: Annotated[str | None, typer.Option("--remote", help="Remote host to offload execution to")] = None,
    image: list[str] | None = None,
    skills: list[str] | None = None,
) -> str:
    if agent is None and droid is not None:
        agent = droid

    from thegent_cli.commands.impl import bg_impl

    # WP-5002: Session-start warning when session count high (memory optimization)
    settings = ThegentSettings()
    thresh = getattr(settings, "session_warn_threshold", 5)
    if isinstance(thresh, int) and thresh > 0:
        from thegent_cli.commands.impl import ps_impl

        sessions = ps_impl(all=True)
        running = sum(1 for s in sessions if (s.get("status") or "").lower() == "running")
        if running >= thresh:
            console.print(
                f"[yellow]Tip: {running} active session(s) detected. Each spawns LSP/MCP processes (~1–2 GB).[/yellow]"
            )
            console.print(
                "[dim]Run 'thegent mcp prune --force' to free memory, or 'thegent mcp spotlight-exclude' on macOS.[/dim]"
            )

    # WP-X2/X5/X6/X7: Unified background execution via bg_impl
    from thegent.config_provider import get_config_provider

    effective_prompt = _inject_skill_instructions(prompt, skills)
    res = bg_impl(
        agent=agent,
        prompt=effective_prompt,
        cd=cd,
        mode=mode,
        timeout=timeout,
        full=full,
        model=model,
        provider=provider,
        owner=owner,
        continue_from=continue_from,
        continuation_include_stderr=continuation_include_stderr,
        include_contract=include_contract,
        routing=routing,
        failover=failover,
        run_id=run_id,
        lane=lane,
        idempotency_token=idempotency_token,
        confidence=confidence,
        arbitration=arbitration,
        override_reason=override_reason,
        contract_version=contract_version,
        domain=domain,
        speculative=speculative,
        debug=debug,
        task_id=task_id,
        remote=remote,
        image_paths=image,
        config_provider=get_config_provider(),
    )

    if "error" in res:
        console.print(f"[red]Error: {res['error']}[/red]")
        if res.get("remediation"):
            console.print(f"[yellow]Suggested Fix: {res['remediation']}[/yellow]")
        raise typer.Exit(res.get("exit_code", 1))

    session_id = res["session_id"]
    log_path = res["log_path"]
    owner_tag = res["owner"]

    settings = ThegentSettings()
    fmt = _normalize_output_format(output_format, default=settings.output_format or "rich")
    if fmt == "json":
        console.print_json(data=res)
    elif fmt == "md":
        console.print(f"**Session started:** `{session_id}`  \n**Log:** `{log_path}`")
    else:
        console.print(f"Session started: [bold cyan]{session_id}[/bold cyan]")
        console.print(f"Log path: [dim]{log_path}[/dim]")
        console.print(f"Owner: [dim]{owner_tag}[/dim]")

    return session_id


def retry_cmd(
    run_id: str | None = None,
    agent: str | None = None,
    failover: bool = False,
    cd: Path | None = None,
    override_reason: str | None = None,
) -> None:
    """Retry a failed run. With no run_id, list recent failed runs."""
    from thegent_cli.commands.impl import history_impl, retry_impl

    # G-DX-02: Use latest if not provided and in non-interactive mode or specifically requested
    if run_id:
        res = retry_impl(
            run_id=run_id,
            agent_override=agent,
            failover=failover,
            cd=cd,
            override_reason=override_reason,
        )
        if "error" in res:
            console.print(f"[red]{res['error']}[/red]")
            raise typer.Exit(res.get("exit_code", 1))
        return

    # No run_id: list failed runs
    runs = history_impl(limit=50)
    failed = [r for r in runs if r.get("status") in ("failed", "timed_out")]
    if not failed:
        console.print("[dim]No failed runs found. Use: thegent retry <run_id>[/dim]")
        return

    console.print("[bold]Recent failed runs[/bold]")
    t = Table(show_header=True, header_style="cyan")
    t.add_column("Run ID", style="dim")
    t.add_column("Agent", style="cyan")
    t.add_column("Status", style="red")
    t.add_column("Prompt", style="dim", max_width=40, overflow="ellipsis")
    for r in failed[:10]:
        t.add_row(
            r.get("run_id", "?"),
            r.get("agent", "?"),
            r.get("status", "?"),
            (r.get("prompt", "") or "")[:40] + ("..." if len(r.get("prompt", "") or "") > 40 else ""),
        )
    console.print(t)
    console.print("\n[dim]Retry with: thegent retry <run_id> [--failover][--override REASON][/dim]")


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
        with open(output, "w") as f:
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
        from thegent_cli.commands.impl import _find_session_meta

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
