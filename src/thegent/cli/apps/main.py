"""Thegent 3.0: Unified Agent Orchestration Entry Point.
Consolidates all legacy command sprawl into a clean, logical hierarchy.
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from thegent import __version__

console = Console()
app = typer.Typer(
    name="thegent",
    help="Unified Agent Orchestration OS - The Optimal System",
    no_args_is_help=True,
    add_completion=True,
)


def _version_callback(value: bool) -> None:
    if not value:
        return
    console.print(__version__)
    raise typer.Exit()

# Modular Stream Registrations
from thegent.cli.apps import (
    audit,
    bench,
    crew,
    domain,
    enterprise,
    govern,
    isolation,
    memory,
    orchestrate,
    plan,
    queue,
    registry,
    routing,
    rules,
    run,
    session,
    skills,
    mcp,
    sync,
    sys,
    team,
)
from thegent.cli.apps.project import install_app, scaffold_app, update_app
from thegent.cli.apps.project import setup_project_app
from thegent.mesh.main import app as mesh_app
from thegent.cli.commands import model_cmds
from thegent.cli.commands.cli_git import app as git_app


app.add_typer(run.app, name="run", help="Execution: Agent tasks, background runs, and history.")
app.add_typer(crew.app, name="crew", help="Crew: create, execute, inspect, and monitor crews.")
app.add_typer(bench.app, name="bench", help="Benchmark: run benchmark suites and persist result rows.")
app.add_typer(sync.app, name="sync", help="Synchronization: Rules, DAG, work-stream, and catalog.")
app.add_typer(skills.app, name="skill", help="Skills: Auto-discovery and management of agent skills.")
app.add_typer(audit.app, name="audit", help="Integrity: System health, security, and planning risk.")
app.add_typer(plan.app, name="plan", help="Roadmap: DAG tasks, work streams, and initiatives.")
app.add_typer(queue.app, name="queue", help="Queue: Unified prompt queue for deferred tasks (FR-HAX-001).")
app.add_typer(rules.app, name="rules", help="Rules: Cross-platform rules synchronization (FR-HAX-002).")
app.add_typer(team.app, name="team", help="Swarm: Coordination, teammates, and hierarchy.")
app.add_typer(domain.app, name="domain", help="Domain: mapping and tunnel advisor workflows (WL-124).")
app.add_typer(govern.app, name="govern", help="Governance: approval/rejection and escalation decisions.")
app.add_typer(sys.app, name="sys", help="System: Setup, MCP, LSP, and configuration.")
app.add_typer(
    setup_project_app,
    name="project",
    help="Project tenancy commands (alias for `thegent sys setup project`).",
)
app.add_typer(mcp.app, name="mcp", help="MCP: install, service, migration, and cleanup helpers.")
app.add_typer(isolation.app, name="isolation", help="Isolation: Multi-tenancy, L1/L2 nesting, and SHM.")
app.add_typer(mesh_app, name="mesh", help="Mesh: Local agent coordination, status, and discovery.")
app.add_typer(install_app, name="install", help="Install user/system assets and project runtime installation.")
app.add_typer(update_app, name="update", help="Update user/system assets and project runtime installation.")
app.add_typer(git_app, name="git", help="Coordinated git workflows for multi-agent development.")
app.add_typer(
    registry.app, name="registry", help="Registry: Agent capability index, recommendations, and health (WL-034)."
)
app.add_typer(
    routing.app, name="routing", help="Routing: LiteLLM, Pareto router, and model-first routing control (WL-012)."
)
app.add_typer(scaffold_app, name="scaffold", help="Project scaffolding and brownfield migration entrypoints.")
app.add_typer(
    enterprise.app, name="enterprise", help="Enterprise: compliance, GDPR, org hierarchy, key rotation (WL-051)."
)
app.add_typer(memory.app, name="memory", help="Memory: agent memory logs, synthesis, and gardening (WL-060).")
app.add_typer(session.app, name="session", help="Session: resume and inspect background sessions (WL-110).")
app.add_typer(
    orchestrate.app,
    name="orchestrate",
    help="Orchestrate: sub-agent goal decomposition and execution (WL-088).",
)


@app.command("setup", help="Run setup wizard and provider/install bootstrap.")
def setup_app_command(
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="NVIDIA NIM API key"),
    model: str | None = typer.Option(None, "--model", "-m", help="NVIDIA NIM model (default: z-ai/glm-5)"),
    openrouter_key: str | None = typer.Option(None, "--openrouter-key", help="OpenRouter API key"),
    kilo_key: str | None = typer.Option(None, "--kilo-key", help="Kilo.ai API key"),
    zai_key: str | None = typer.Option(None, "--zai-key", help="Z.AI (Zhipu) API key"),
    minimax_key: str | None = typer.Option(None, "--minimax-key", help="MiniMax API key"),
    wizard: bool = typer.Option(True, "--wizard/--no-wizard", help="Run interactive setup wizard"),
    links: bool = typer.Option(True, "--links/--no-links", help="Install claudeglm/claudemax shortcuts"),
    hooks: bool = typer.Option(
        False, "--hooks/--no-hooks", help="Install git hooks (pre-commit, pre-push) into .git/hooks"
    ),
    skills: bool = typer.Option(
        False, "--skills/--no-skills", help="Sync thegent-skills template to ~/.claude, ~/.cursor, project"
    ),
    harness: bool = typer.Option(False, "--harness/--no-harness", help="Install/update heliosShield harness"),
    full: bool = typer.Option(
        False,
        "--full",
        "-f",
        help="Full setup: install -t all, install-shims, lock-cleanup service, MCP service, and harness",
    ),
    agents: str | None = typer.Option(
        None,
        "--agents",
        "-a",
        help="Comma-separated agents to configure (e.g. claude,codex,cursor). Skips others in wizard.",
    ),
) -> None:
    """Legacy compatibility wrapper for setup flow."""
    model_cmds.setup_cmd(
        api_key=api_key or "",
        model=model or "",
        openrouter_key=openrouter_key or "",
        kilo_key=kilo_key or "",
        zai_key=zai_key or "",
        minimax_key=minimax_key or "",
        wizard=wizard,
        links=links,
        hooks=hooks,
        skills=skills,
        harness=harness,
        full=full,
        agents=agents or "",
    )


# Top-level Shortcuts
@app.command("do", help="Quick-run a prompt with the default agent.")
def quick_do(prompt: str = typer.Argument(..., help="Prompt to execute")):
    from thegent.cli.apps.run import run_agent

    run_agent(prompt=prompt)


@app.command("review", help="WL-107: run a read-only review and validate structured findings.")
def review_cmd(
    prompt: str = typer.Argument(..., help="Review request prompt"),
    agent: str | None = typer.Option(None, "--agent", help="Agent to run for review"),
    model: str | None = typer.Option(None, "--model", help="LLM model override"),
    format: str = typer.Option("rich", "--format", help="Output format: rich|json"),
) -> None:
    # @trace WL-107
    from thegent.cli.commands.cli import _format_context_usage_line
    from thegent.cli.commands.impl import review_impl

    output_format = format.strip().lower()
    if output_format not in {"rich", "json"}:
        console.print(f"[red]Unsupported --format '{format}'. Use 'rich' or 'json'.[/red]")
        raise typer.Exit(2)

    try:
        result = review_impl(prompt=prompt, agent=agent, model=model)
    except ValueError as exc:
        console.print(f"[red]Review output validation failed:[/red] {exc}")
        raise typer.Exit(2) from exc

    run_exit = result.get("exit_code", 1)
    if run_exit not in (0, 1):
        console.print(f"[red]Review run failed:[/red] {result.get('error', '')}")
        raise typer.Exit(run_exit)

    issues = result["issues"]
    context_usage = result.get("context_usage")
    if output_format == "json":
        payload: dict[str, object] = {
            "summary": result["summary"],
            "overall_rating": result["overall_rating"],
            "issues": issues,
        }
        if isinstance(context_usage, dict):
            payload["context_usage"] = context_usage
        console.print_json(data=payload)
    else:
        console.print(f"[bold]Summary:[/bold] {result['summary']}")
        console.print(f"[bold]Overall Rating:[/bold] {result['overall_rating']}")
        context_line = _format_context_usage_line(context_usage)
        if context_line:
            console.print(f"[dim]{context_line}[/dim]")
        if issues:
            for issue in issues:
                console.print(
                    f"- [{issue['severity']}] {issue['file']}:{issue['line']} - "
                    f"{issue['message']} (fix: {issue['suggestion']})"
                )
        else:
            console.print("[green]No issues found.[/green]")
    raise typer.Exit(1 if issues else 0)


@app.command("doctor", help="Run system doctor checks.")
def doctor_cmd(
    fix: bool = typer.Option(False, "--fix", "-f", help="Attempt to apply automatic fixes"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show planned fixes without applying them"),
) -> None:
    """Run thegent doctor from the unified top-level command surface."""
    from thegent.doctor import run_doctor

    success = run_doctor(fix=fix, dry_run=dry_run)
    raise typer.Exit(0 if success else 1)


@app.command("resume", help="Resume a session (shortcut for `thegent run resume`).")
def resume_top_level(
    session_id: str | None = typer.Argument(None, help="Session ID to resume (defaults to latest resumable)"),
    prompt: str | None = typer.Option(None, "--prompt", help="Optional follow-up prompt to queue after resume"),
    skill: list[str] | None = typer.Option(
        None,
        "--skill",
        help="Activate skill instructions by name (repeatable) (WL-101).",
    ),
) -> None:
    from thegent.cli.commands.cli import resume_cmd

    if skill:
        resume_cmd(session_id=session_id, prompt=prompt, skills=skill)
        return
    resume_cmd(session_id=session_id, prompt=prompt)


@app.command("fork", help="WL-106: Fork a session (shortcut for `thegent run fork`).")
def fork_top_level(
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
    from thegent.cli.apps.run import run_fork

    run_fork(session_id=session_id, from_turn=from_turn, new_session_id=new_session_id)


@app.command("rollback", help="WL-106: Roll back a session (shortcut for `thegent run rollback`).")
def rollback_top_level(
    session_id: str = typer.Argument(..., help="Session ID to roll back"),
    n_turns: int = typer.Option(..., "--n-turns", help="Number of latest turns to remove"),
) -> None:
    if n_turns < 1:
        raise typer.BadParameter("n-turns must be 1 or greater", param_hint="--n-turns")
    from thegent.cli.apps.run import run_rollback

    run_rollback(session_id=session_id, n_turns=n_turns)


@app.command("ps", help="List active background sessions (shortcut for `thegent run ps`).")
def quick_ps(
    all_sessions: bool = typer.Option(False, "--all", "-a", help="Show all sessions, not just current owner"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Filter by owner tag"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json|md)"),
    include_contract: bool = typer.Option(False, "--include-contract", help="Include routing contract metadata"),
):
    from thegent.cli.apps.run import run_ps

    run_ps(
        all_sessions=all_sessions,
        owner=owner,
        format=format,
        include_contract=include_contract,
    )


@app.command("reload", help="Quick alias for `thegent mcp reload`.")
def reload_top_level() -> None:
    from thegent.mcp.manage import mcp_restart

    ok, msg = mcp_restart()
    console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")
    raise typer.Exit(0 if ok else 1)


@app.command("hmr", help="Quick alias for `thegent mcp hmr` hot-reload loop.")
def hmr_top_level(
    project_root: Path = typer.Option(
        Path.cwd(),
        "--project-root",
        help="Project root to watch (defaults to current working directory).",
    ),
    debounce_s: float = typer.Option(
        1.5,
        "--debounce",
        min=0.1,
        help="Minimum seconds between automatic restarts.",
    ),
) -> None:
    from thegent.mcp.hotreload import run_prod_hotreload

    try:
        run_prod_hotreload(project_root=project_root, debounce_s=debounce_s)
    except Exception as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc


@app.command("list-agents", help="List available agents (OBSERVE operation).")
def list_agents_cmd_wrapper() -> None:
    from thegent.cli.commands.model_cmds import list_agents_cmd

    list_agents_cmd()


@app.command("list-droids", help="List available droids.")
def list_droids_cmd_wrapper(
    cd: str | None = typer.Option(None, "--cd", "-d", help="Project directory"),
) -> None:
    from pathlib import Path

    from thegent.cli.commands.model_cmds import list_droids_cmd

    resolved_cd = Path(cd) if cd else None
    list_droids_cmd(cd=resolved_cd)


@app.command("session-contract-health-gate", help="Evaluate session contract health gate.")
def session_health_gate_wrapper(
    all_sessions: bool = typer.Option(False, "--all", "-a", help="Include all sessions (not just current owner)"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Owner tag filter"),
    strict: bool = typer.Option(False, "--strict", help="Strict health check mode"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich|json|md"),
    min_healthy_ratio: float = typer.Option(1.0, "--min-healthy-ratio", help="Minimum healthy ratio threshold"),
    policy_profile: str | None = typer.Option(None, "--policy-profile", help="Health policy profile"),
    no_worse_than_baseline: bool = typer.Option(False, "--no-worse-than-baseline", help="Check for regression"),
    regression_tolerance: float = typer.Option(0.0, "--regression-tolerance", help="Tolerance for regression"),
    output: str | None = typer.Option(None, "--output", help="Export to file"),
    export_format: str | None = typer.Option(None, "--export-format", help="Export format override"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing export file"),
) -> None:
    """Evaluate session contract health gate."""
    from pathlib import Path

    from thegent.cli.commands.session_cmds import session_contract_health_gate_cmd

    output_path = Path(output) if output else None
    session_contract_health_gate_cmd(
        all_sessions=all_sessions,
        owner=owner,
        strict=strict,
        format=format,
        min_healthy_ratio=min_healthy_ratio,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        output=output_path,
        export_format=export_format,
        overwrite=overwrite,
    )


@app.command("session-contract-health-report", help="Generate session contract health report.")
def session_health_report_wrapper(
    all_sessions: bool = typer.Option(False, "--all", "-a", help="Include all sessions (not just current owner)"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Owner tag filter"),
    strict: bool = typer.Option(False, "--strict", help="Strict health check mode"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich|json|md"),
    policy_profile: str | None = typer.Option(None, "--policy-profile", help="Health policy profile"),
    no_worse_than_baseline: bool = typer.Option(False, "--no-worse-than-baseline", help="Check for regression"),
    regression_tolerance: float = typer.Option(0.0, "--regression-tolerance", help="Tolerance for regression"),
    output: str | None = typer.Option(None, "--output", help="Export to file"),
    export_format: str | None = typer.Option(None, "--export-format", help="Export format override"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing export file"),
) -> None:
    """Generate session contract health report."""
    from pathlib import Path

    from thegent.cli.commands.session_cmds import session_contract_health_report_cmd

    output_path = Path(output) if output else None
    session_contract_health_report_cmd(
        all_sessions=all_sessions,
        owner=owner,
        strict=strict,
        format=format,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        output=output_path,
        export_format=export_format,
        overwrite=overwrite,
    )


@app.command("session-contract-health-trend", help="Session contract health trend analysis.")
def session_health_trend_wrapper(
    payload_type: str = typer.Option(
        "session_contract_health_report",
        "--payload-type",
        help="Payload type to trend (session_contract_health_report, session_contract_health_gate)",
    ),
    all_sessions: bool = typer.Option(False, "--all", "-a", help="Include all sessions (not just current owner)"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Owner tag filter"),
    strict: bool = typer.Option(False, "--strict", help="Strict health check mode"),
    policy_profile: str | None = typer.Option(None, "--policy-profile", help="Health policy profile"),
    min_healthy_ratio: float = typer.Option(1.0, "--min-healthy-ratio", help="Minimum healthy ratio threshold"),
    top_blocked: int = typer.Option(25, "--top-blocked", help="Top N blocked rows to include"),
    limit: int = typer.Option(20, "--limit", help="Maximum snapshots to analyze"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich|json|md"),
    output: str | None = typer.Option(None, "--output", help="Export to file"),
    export_format: str | None = typer.Option(None, "--export-format", help="Export format override"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing export file"),
) -> None:
    """Analyze session contract health trends."""
    from pathlib import Path

    from thegent.cli.commands.session_cmds import session_contract_health_trend_cmd

    output_path = Path(output) if output else None
    session_contract_health_trend_cmd(
        payload_type=payload_type,
        all_sessions=all_sessions,
        owner=owner,
        strict=strict,
        policy_profile=policy_profile,
        min_healthy_ratio=min_healthy_ratio,
        top_blocked=top_blocked,
        limit=limit,
        format=format,
        output=output_path,
        export_format=export_format,
        overwrite=overwrite,
    )


@app.command("domain-map", hidden=True)
def domain_map_compat(
    domain_name: str = typer.Argument(..., help="Domain or subdomain to expose."),
    target: str = typer.Option("http://localhost:3847", "--target", "-t"),
    mode: str = typer.Option("advisor", "--mode"),
    registrar: str = typer.Option("porkbun", "--registrar"),
    dns_provider: str = typer.Option("cloudflare", "--dns-provider"),
    tunnel_name: str = typer.Option("thegent", "--tunnel-name"),
    format: str = typer.Option("rich", "--format", "-F"),
) -> None:
    """Compatibility shim for legacy `thegent domain-map` usage."""
    from thegent.cli.commands.domain_map import domain_map_cmd

    domain_map_cmd(
        domain=domain_name,
        target=target,
        mode=mode,
        registrar=registrar,
        dns_provider=dns_provider,
        tunnel_name=tunnel_name,
        format=format,
    )


@app.command("help", help="Show inline examples for a command.")
def help_cmd(
    command: str = typer.Argument(..., help="Command to show examples for"),
) -> None:
    """Show inline usage examples for COMMAND.

    # @trace WL-040 WP-4004

    Example::

        thegent help run
        thegent help plan
        thegent help doctor
    """
    from thegent.cli.help_examples import show_help_examples

    show_help_examples(command)


@app.command("agent-server", help="Run thegent JSON-RPC agent server over stdio.")
def agent_server_cmd() -> None:
    from thegent.protocols.jsonrpc_agent_server import serve_stdio

    raise typer.Exit(serve_stdio())


@app.callback(invoke_without_command=True)
def main_welcome(
    ctx: typer.Context,
    _version: bool = typer.Option(
        False,
        "--version",
        help="Show thegent version and exit.",
        is_eager=True,
        callback=_version_callback,
    ),
):
    if ctx.invoked_subcommand is None:
        console.print(
            Panel(
                "[bold cyan]Thegent 3.0 (Optimal)[/bold cyan]\n"
                "[dim]The Optimized Agent Orchestration System[/dim]\n\n"
                "Key Streams:\n"
                "  [green]thegent run[/green]       Execute agent tasks\n"
                "  [green]thegent sync[/green]      Synchronize system state\n"
                "  [green]thegent audit[/green]     Check system health/risk\n"
                "  [green]thegent plan[/green]      Manage the roadmap\n"
                "\n"
                "Team Discovery:\n"
                "  [green]thegent team teammates list[/green] Discover teammate personas\n"
                "\n"
                "Support Commands:\n"
                "  [green]thegent setup[/green]       Run setup wizard\n"
                "  [green]thegent doctor[/green]      Run system doctor checks\n",
                title="thegent",
                border_style="blue",
            )
        )


if __name__ == "__main__":
    app()
