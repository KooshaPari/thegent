"""Thegent CLI entry point (subcommand-only)."""

import builtins
from pathlib import Path

builtins.Path = Path

import json
import os
import platform
import sys
import warnings
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from thegent.commands.sync import SyncCommand, SyncResult

# G-DX-01: Silencing noisy non-fatal warnings for better operator experience.
# Must be before any other imports that might trigger Pydantic plugin loading.
warnings.filterwarnings("ignore", message=".*is not JSON serializable; excluding default from JSON schema.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="uvicorn")
warnings.filterwarnings("ignore", message=".*ImportError while loading the `logfire-plugin` Pydantic plugin.*")

from pathlib import Path

import typer
from rich.console import Console

from thegent.config import ThegentSettings

console = Console()

from thegent.cli import (
    archive_cmd,
    audit_verify_cmd,
    benchmark_cmd,
    bg_cmd,
    cliproxy_login_cmd,
    closure_pack_cmd,
    cockpit_cmd,
    compliance_report_cmd,
    config_check_cmd,
    contracts_conformance_cmd,
    contracts_registry_cmd,
    cost_status_cmd,
    dag_add_cmd,
    dag_cancel_cmd,
    dag_checkpoint_cmd,
    dag_checkpoints_cmd,
    dag_list_cmd,
    dag_probe_cmd,
    dag_ready_cmd,
    dag_reconcile_cmd,
    dag_recover_cmd,
    dag_remove_cmd,
    dag_rollback_cmd,
    dag_run_cmd,
    dag_status_cmd,
    dag_sync_cmd,
    dag_update_cmd,
    dag_validate_cmd,
    data_protection_cmd,
    deep_research_cmd,
    discovery_parse_cmd,
    discovery_register_cmd,
    discovery_scan_cmd,
    drift_cmd,
    escalate_add_cmd,
    escalate_approve_cmd,
    escalate_list_cmd,
    escalate_resolve_cmd,
    explorer_cmd,
    feedback_cmd,
    forensics_snapshot_cmd,
    govern_configure_cmd,
    govern_go_cycle_cmd,
    govern_go_health_cmd,
    govern_go_status_cmd,
    govern_go_watch_cmd,
    handoff_list_cmd,
    handoff_show_cmd,
    history_cmd,
    inspect_cmd,
    interruption_list_cmd,
    interruption_snooze_cmd,
    list_agents_cmd,
    list_droids_cmd,
    list_models_cmd,
    load_status_cmd,
    logs_cmd,
    loop_cmd,
    loop_send_cmd,
    loop_stop_cmd,
    migration_cmd,
    modes_cmd,
    operations_cmd,
    pause_cmd,
    plan_analyze_cmd,
    plan_claim_cmd,
    plan_complete_cmd,
    plan_do_next_cmd,
    plan_get_next_cmd,
    plan_incorporate_cmd,
    plan_loop_cmd,
    plan_progress_cmd,
    plan_wait_next_cmd,
    policy_show_cmd,
    project_list_cmd,
    project_register_cmd,
    ps_cmd,
    purge_cmd,
    resolve_model_route_cmd,
    resume_cmd,
    retry_cmd,
    rules_sync_cmd,
    run_cmd,
    session_contract_health_gate_cmd,
    session_contract_health_report_cmd,
    session_contract_health_trend_cmd,
    session_contracts_cmd,
    setup_cmd,
    sitback_dashboard_cmd,
    status_cmd,
    stop_cmd,
    summary_cmd,
    sweep_cmd,
    takeover_cmd,
    team_create_cmd,
    team_task_add_cmd,
    team_task_list_cmd,
    terminal_route_cmd,
    usage_cmd,
    wait_cmd,
    workstream_dashboard_cmd,
    workstream_query_cmd,
    workstream_stats_cmd,
)
from thegent.cli_custom import context_history_cmd, memory_cmd, scratchpad_cmd


def init_cmd(
    url: str = typer.Option(None, "--url", "-u", help="MCP server URL (default: http://127.0.0.1:3847/mcp)"),
    cli: bool = typer.Option(
        False, "--cli", help="Non-interactive, agent-friendly setup (smart mode, all detected targets)"
    ),
) -> None:
    """Initialize thegent: configure MCP clients and background services."""
    from rich.console import Console

    from thegent.install import run_install, run_wizard

    if cli:
        console = Console()
        console.print("[bold cyan]thegent init --cli[/bold cyan] (non-interactive)")
        run_install(
            target="all",
            mode="smart",
            install_service=True,
            verbose=True,
            url=url,
        )
        console.print("\n[bold green]Init complete.[/bold green]")
        return

    # Default to interactive wizard
    run_wizard(url=url)


app = typer.Typer(
    name="thegent",
    help="Unified agent orchestration CLI for Factory skills and droids",
    no_args_is_help=False,
    add_completion=True,
    epilog="Getting started: thegent run 'Hello' free | thegent doctor | thegent setup | thegent plan do-next\nShell completion: thegent --install-completion zsh",
)


@app.callback(invoke_without_command=True)
def _main_callback(ctx: typer.Context) -> None:
    """When no subcommand given, show quick start panel."""
    if ctx.invoked_subcommand is not None:
        return
    from rich.panel import Panel

    console.print(
        Panel(
            "[bold]Getting started[/bold]\n\n"
            '[cyan]thegent run[/cyan] "<prompt>" free    Run a task\n'
            "[cyan]thegent doctor[/cyan]                 Verify environment\n"
            "[cyan]thegent setup[/cyan]                  Configure providers\n"
            "[cyan]thegent plan do-next[/cyan]           Next work item\n\n"
            "[dim]Full help: thegent --help[/dim]",
            title="thegent",
            border_style="blue",
        )
    )
    raise typer.Exit(0)


app.command("init")(init_cmd)
app.command("setup")(setup_cmd)
app.command("summary")(summary_cmd)
app.command("nim-setup", hidden=True)(setup_cmd)


@app.command("doctor")
def doctor_cmd(
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix detected issues"),
) -> None:
    """Verify environment health and fix performance bottlenecks."""
    from thegent.doctor import run_doctor

    success = run_doctor(fix=fix)
    raise typer.Exit(0 if success else 1)


@app.command("upgrade")
def upgrade_cmd(
    check_only: bool = typer.Option(False, "--check", "-c", help="Only check, don't print upgrade instructions"),
) -> None:
    """Check for newer thegent version and print upgrade instructions."""
    import importlib.metadata

    try:
        current = importlib.metadata.version("thegent")
    except importlib.metadata.PackageNotFoundError:
        console.print("[yellow]thegent not installed via pip. Check for updates manually.[/yellow]")
        raise typer.Exit(0)

    try:
        import httpx

        resp = httpx.get("https://pypi.org/pypi/thegent/json", timeout=5.0)
        if resp.status_code != 200:
            raise typer.Exit(0)
        data = resp.json()
        latest = data.get("info", {}).get("version", current)
    except Exception:
        console.print("[dim]Could not check for updates (network error)[/dim]")
        raise typer.Exit(0)

    try:
        from packaging.version import Version

        newer = Version(latest) > Version(current)
    except ImportError:
        newer = latest != current

    if newer:
        console.print(f"[green]A new version is available: {latest} (you have {current})[/green]")
        if not check_only:
            console.print("[dim]Upgrade: pip install -U thegent  or  uv tool install thegent[/dim]")
    elif check_only:
        console.print(f"[green]You have the latest version: {current}[/green]")


orchestrate_app = typer.Typer(help="Agent execution and session management")
govern_app = typer.Typer(help="Governance, policy, and compliance")
federation_app = typer.Typer(help="Manage multi-org policy federation (WP-13001)")
govern_app.add_typer(federation_app, name="federation")

learning_app = typer.Typer(help="Manage autonomous learning and model promotion (WP-14002)")
govern_app.add_typer(learning_app, name="learning")

trust_app = typer.Typer(help="Trust boundary and environment transition controls (WP-3007)")
govern_app.add_typer(trust_app, name="trust")

signatures_app = typer.Typer(help="Signed action artifacts (MAIF) management (WP-3002)")
govern_app.add_typer(signatures_app, name="signatures")

compliance_app = typer.Typer(help="Enterprise compliance and audit reports (WP-15004)")
govern_app.add_typer(compliance_app, name="compliance")

guardrails_app = typer.Typer(help="Input guardrails and prompt validation (FR-GOV-003..007)")
govern_app.add_typer(guardrails_app, name="guardrails")

finance_app = typer.Typer(help="Financial safety and cost governance (WP-5XXX)")
govern_app.add_typer(finance_app, name="finance")

research_app = typer.Typer(help="Deep research and discovery commands")
app.add_typer(research_app, name="research")

from thegent.secrets.cli import app as secrets_app
app.add_typer(secrets_app, name="secrets")


@research_app.command("deep")
def deep_research(
    query: str = typer.Argument(..., help="Research query"),
    subreddits: str = typer.Option(None, "--subreddits", "-s", help="Comma-separated subreddits"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file path (JSON)"),
) -> None:
    """Perform deep research using the Deep Research Protocol (DRP)."""
    deep_research_cmd(query=query, subreddits=subreddits, output=output)


team_app = typer.Typer(help="Manage multi-agent teams (WP-6008)")
orchestrate_app.add_typer(team_app, name="team")


@team_app.command("create")
def team_create(
    name: str = typer.Argument(..., help="Team name"),
    leader: str = typer.Option("claude", "--leader", "-l", help="Team leader agent"),
    teammates: str = typer.Option("cursor,codex", "--teammates", "-t", help="Comma-separated list of teammates"),
) -> None:
    """Create a new multi-agent team."""
    team_create_cmd(name=name, leader=leader, teammates=teammates)


@team_app.command("add-task")
def team_task_add(
    team_id: str = typer.Argument(..., help="Team ID"),
    title: str = typer.Argument(..., help="Task title"),
    description: str = typer.Option("", "--desc", "-d", help="Task description"),
) -> None:
    """Add a task to a team's backlog."""
    team_task_add_cmd(team_id=team_id, title=title, description=description)


@team_app.command("list-tasks")
def team_task_list(
    team_id: str = typer.Argument(..., help="Team ID"),
) -> None:
    """List all tasks for a team."""
    team_task_list_cmd(team_id=team_id)


project_app = typer.Typer(help="Manage cross-project discovery (WP-11XXX)")
app.add_typer(project_app, name="project")


@project_app.command("register")
def project_register(
    path: Path = typer.Argument(..., help="Project path"),
    name: str | None = typer.Option(None, "--name", "-n", help="Project name"),
) -> None:
    """Register a project in the global registry."""
    project_register_cmd(path=path, name=name)


@project_app.command("list")
def project_list() -> None:
    """List all registered projects."""
    project_list_cmd()


forensics_app = typer.Typer(help="Forensic auditing and snapshotting (WP-12XXX)")
app.add_typer(forensics_app, name="forensics")

from thegent.commands.audit import app as _audit_app
from thegent.commands.idea_seeds import app as _seeds_app
from thegent.commands.registry import app as _registry_app
from thegent.commands.replay import app as _replay_app
from thegent.commands.tools import app as _tools_app

app.add_typer(_audit_app, name="audit")
app.add_typer(_registry_app, name="registry")
app.add_typer(_replay_app, name="replay")
app.add_typer(_seeds_app, name="seeds")
app.add_typer(_tools_app, name="tools")

# ---------------------------------------------------------------------------
# thegent lint -- oxlint-backed linting accelerator
# ---------------------------------------------------------------------------

lint_app = typer.Typer(help="Lint JS/TS/Python files via oxlint (fast) or ESLint/ruff.")
app.add_typer(lint_app, name="lint")


@lint_app.callback(invoke_without_command=True)
def _lint_callback(ctx: typer.Context) -> None:
    """When called with no subcommand, run the default 'run' subcommand."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(lint_run)


@lint_app.command("run")
def lint_run(
    paths: list[Path] = typer.Argument(default=None, help="Files or directories to lint (default: .)"),
    fast: bool = typer.Option(True, "--fast/--no-fast", help="Use oxlint fast-path when available"),
    oxlint_config: Path = typer.Option(None, "--oxlint-config", help="Path to oxlintrc.json"),
    eslint_config: Path = typer.Option(None, "--eslint-config", help="Path to ESLint config"),
    output_json: bool = typer.Option(False, "--json", help="Output results as JSON"),
) -> None:
    """Lint JS/TS files via oxlint (50-100x faster) or fall back to ESLint.

    Examples::

        thegent lint run src/
        thegent lint run --no-fast src/
        thegent lint run --json src/ web/
    """
    from thegent.tools.linting_accelerator import LintingAccelerator

    linter = LintingAccelerator()
    effective_paths = paths or [Path()]

    try:
        results = linter.lint(
            effective_paths,
            fast=fast,
            oxlint_config=oxlint_config,
            eslint_config=eslint_config,
        )
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}", highlight=False)
        raise typer.Exit(1)

    if output_json:
        import json as _json

        console.print(
            _json.dumps(
                [
                    {
                        "file": r.file,
                        "line": r.line,
                        "column": r.column,
                        "severity": r.severity,
                        "rule": r.rule,
                        "message": r.message,
                        "source": r.source,
                    }
                    for r in results
                ],
                indent=2,
            )
        )
    elif not results:
        console.print("[green]No lint issues found.[/green]")
    else:
        for r in results:
            colour = "red" if r.severity == "error" else "yellow"
            console.print(f"[{colour}]{r}[/{colour}]", highlight=False)
        console.print(f"\n[bold]{len(results)} issue(s) found.[/bold]")

    if any(r.severity == "error" for r in results):
        raise typer.Exit(1)


@lint_app.command("check")
def lint_check(
    paths: list[Path] = typer.Argument(default=None, help="Files or directories to lint (default: .)"),
    fast: bool = typer.Option(True, "--fast/--no-fast", help="Use oxlint fast-path when available"),
) -> None:
    """Check availability of lint backends without linting.

    Examples::

        thegent lint check
    """
    from thegent.tools.linting_accelerator import LintingAccelerator

    linter = LintingAccelerator()
    oxlint_ok = linter.is_oxlint_available()
    eslint_ok = linter.is_eslint_available()
    ruff_ok = linter.is_ruff_available()

    console.print(f"oxlint  : {'[green]available[/green]' if oxlint_ok else '[dim]not found[/dim]'}")
    console.print(f"eslint  : {'[green]available[/green]' if eslint_ok else '[dim]not found[/dim]'}")
    console.print(f"ruff    : {'[green]available[/green]' if ruff_ok else '[dim]not found[/dim]'}")

    if fast:
        active = "oxlint" if oxlint_ok else ("eslint" if eslint_ok else "none")
    else:
        active = "eslint" if eslint_ok else "none"
    console.print(f"\nActive backend (fast={fast}): [bold]{active}[/bold]")


@forensics_app.command("snapshot")
def forensics_snapshot(
    run_id: str | None = typer.Option(None, "--run-id", "-r", help="Run ID"),
    phase: str | None = typer.Option(None, "--phase", "-p", help="Snapshot phase: pre | post"),
) -> None:
    """Capture a forensic snapshot of the current environment."""
    forensics_snapshot_cmd(run_id=run_id, phase=phase)


@finance_app.command("dashboard")
def finance_dashboard() -> None:
    """Show financial safety dashboard (WP-Y1)."""
    try:
        from thegent.cli_impl import financial_dashboard_impl
    except ImportError:
        typer.echo("financial_dashboard_impl not available", err=True)
        raise typer.Exit(1)

    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    financial_dashboard_impl(settings)


@govern_app.command("configure")
def govern_configure(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing health-targets.json"),
) -> None:
    """Bootstrap governance: create contracts/health-targets.json if missing."""
    govern_configure_cmd(cd=cd, force=force)


@orchestrate_app.command("run-diff")
def run_diff(
    run_a: str = typer.Argument(..., help="ID of first run"),
    run_b: str = typer.Argument(..., help="ID of second run"),
) -> None:
    """Compare two execution runs (trace comparison)."""
    from thegent.cli import run_diff_cmd

    run_diff_cmd(run_a, run_b)


@orchestrate_app.command("trace-replay")
def trace_replay(
    run_id: str = typer.Argument(..., help="ID of run to replay"),
) -> None:
    """Replay an execution trace in simulation mode (WP-16001)."""
    from thegent.cli import trace_replay_cmd

    trace_replay_cmd(run_id)


teammates_app = typer.Typer(help="Manage specialized teammate agents and delegation (WP-16001)")
inbox_app = typer.Typer(help="Unified agent inbox and event stream (WP-12006)")
orchestrate_app.add_typer(teammates_app, name="teammates")

deferral_app = typer.Typer(help="Manage deferred non-critical tasks (WP-5004)")
orchestrate_app.add_typer(deferral_app, name="deferral")


@deferral_app.command("list")
def deferral_list() -> None:
    """List all currently deferred tasks."""
    from thegent.cli import deferral_list_cmd

    deferral_list_cmd()


workstream_app = typer.Typer(help="Workstream management and auto-launch system")
app.add_typer(workstream_app, name="workstream")


@workstream_app.command("query")
def workstream_query(
    query: str = typer.Argument(..., help="SQL query to execute"),
) -> None:
    """Execute SQL query on workstream database."""
    from thegent.cli import workstream_query_cmd

    workstream_query_cmd(query=query)


@workstream_app.command("stats")
def workstream_stats() -> None:
    """Get workstream statistics."""
    from thegent.cli import workstream_stats_cmd

    workstream_stats_cmd()


@workstream_app.command("dashboard")
def workstream_dashboard() -> None:
    """Launch workstream dashboard TUI."""
    from thegent.cli import workstream_dashboard_cmd

    workstream_dashboard_cmd()


@deferral_app.command("resume")
def deferral_resume(
    run_id: str = typer.Argument(..., help="ID of run to resume"),
) -> None:
    """Manually resume a deferred task."""
    from thegent.cli import deferral_resume_cmd

    deferral_resume_cmd(run_id)


# ========== Hierarchy Commands ==========

hierarchy_app = typer.Typer(help="Agent hierarchy and relationship management")
orchestrate_app.add_typer(hierarchy_app, name="hierarchy")


@hierarchy_app.command("show")
def hierarchy_show(
    agent_id: str = typer.Option(None, "--agent-id", help="Show hierarchy for specific agent"),
    team_id: str = typer.Option(None, "--team-id", help="Show hierarchy for specific team"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text, json, tree"),
) -> None:
    """Show agent hierarchy."""
    try:
        from thegent.cli import hierarchy_show_cmd
    except ImportError:
        typer.echo("hierarchy_show_cmd not available", err=True)
        raise typer.Exit(1)

    hierarchy_show_cmd(agent_id=agent_id, team_id=team_id, format=format)


@hierarchy_app.command("tree")
def hierarchy_tree(
    root_id: str = typer.Option(None, "--root", help="Root agent run_id"),
) -> None:
    """Show hierarchy tree structure."""
    try:
        from thegent.cli import hierarchy_tree_cmd
    except ImportError:
        typer.echo("hierarchy_tree_cmd not available", err=True)
        raise typer.Exit(1)

    hierarchy_tree_cmd(root_id=root_id)


@hierarchy_app.command("relationships")
def hierarchy_relationships(
    agent_id: str = typer.Option(None, "--agent-id", help="Filter by agent run_id"),
) -> None:
    """Show agent relationships."""
    from thegent.cli import hierarchy_relationships_cmd

    hierarchy_relationships_cmd(agent_id=agent_id)


# ========== Team Management Commands ==========

teams_app = typer.Typer(help="Team management and coordination")
orchestrate_app.add_typer(teams_app, name="teams")


@teams_app.command("create")
def teams_create(
    team_id: str = typer.Argument(..., help="Team identifier"),
    name: str = typer.Option(..., "--name", help="Team name"),
    description: str = typer.Option("", "--description", help="Team description"),
    team_type: str = typer.Option("functional", "--type", help="Team type: functional, project, ad_hoc"),
    coordination_mode: str = typer.Option(
        "hierarchical", "--coordination", help="Coordination mode: hierarchical, collaborative, swarm"
    ),
    lead_id: str = typer.Option(..., "--lead", help="Team lead agent run_id"),
) -> None:
    """Create a new team."""
    try:
        from thegent.cli import teams_create_cmd
    except ImportError:
        typer.echo("teams_create_cmd not available", err=True)
        raise typer.Exit(1)

    teams_create_cmd(
        team_id=team_id,
        name=name,
        description=description,
        team_type=team_type,
        coordination_mode=coordination_mode,
        lead_id=lead_id,
    )


@teams_app.command("list")
def teams_list() -> None:
    """List all teams."""
    try:
        from thegent.cli import teams_list_cmd
    except ImportError:
        typer.echo("teams_list_cmd not available", err=True)
        raise typer.Exit(1)

    teams_list_cmd()


@teams_app.command("show")
def teams_show(team_id: str = typer.Argument(..., help="Team identifier")) -> None:
    """Show team details."""
    from thegent.cli import teams_show_cmd

    teams_show_cmd(team_id=team_id)


@teams_app.command("add-member")
def teams_add_member(
    team_id: str = typer.Argument(..., help="Team identifier"),
    agent_run_id: str = typer.Argument(..., help="Agent run_id to add"),
) -> None:
    """Add member to team."""
    from thegent.cli import teams_add_member_cmd

    teams_add_member_cmd(team_id=team_id, agent_run_id=agent_run_id)


@teams_app.command("remove-member")
def teams_remove_member(
    team_id: str = typer.Argument(..., help="Team identifier"),
    agent_run_id: str = typer.Argument(..., help="Agent run_id to remove"),
) -> None:
    """Remove member from team."""
    from thegent.cli import teams_remove_member_cmd

    teams_remove_member_cmd(team_id=team_id, agent_run_id=agent_run_id)


# ========== Crew Management Commands ==========

crew_app = typer.Typer(help="Agent Crew orchestration (impl-agent-crew-maximal-mvp)")
orchestrate_app.add_typer(crew_app, name="crew")


@crew_app.command("create")
def crew_create(
    name: str = typer.Option(..., "--name", help="Crew name"),
    description: str = typer.Option("", "--description", help="Crew description"),
    execution_mode: str = typer.Option("sequential", "--mode", help="Execution mode: sequential, hierarchical, custom"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path (JSON)"),
) -> None:
    """Create a new crew."""
    from thegent.cli_crew import crew_create_cmd

    crew_create_cmd(name=name, description=description, execution_mode=execution_mode, output=output)


@crew_app.command("add-agent")
def crew_add_agent(
    crew_id: str = typer.Argument(..., help="Crew ID"),
    role: str = typer.Option(..., "--role", help="Agent role"),
    name: str = typer.Option(None, "--name", help="Agent name"),
    description: str = typer.Option("", "--description", help="Agent description"),
    capabilities: str = typer.Option("", "--capabilities", help="Comma-separated capabilities"),
    model: str = typer.Option(None, "--model", help="Model to use"),
) -> None:
    """Add agent to crew."""
    from thegent.cli_crew import crew_add_agent_cmd

    crew_add_agent_cmd(
        crew_id=crew_id,
        role=role,
        name=name,
        description=description,
        capabilities=capabilities,
        model=model,
    )


@crew_app.command("add-task")
def crew_add_task(
    crew_id: str = typer.Argument(..., help="Crew ID"),
    description: str = typer.Option(..., "--description", help="Task description"),
    dependencies: str = typer.Option("", "--dependencies", help="Comma-separated task IDs"),
    agent_id: str = typer.Option(None, "--agent-id", help="Assigned agent ID"),
) -> None:
    """Add task to crew."""
    from thegent.cli_crew import crew_add_task_cmd

    crew_add_task_cmd(
        crew_id=crew_id,
        description=description,
        dependencies=dependencies,
        agent_id=agent_id,
    )


@crew_app.command("execute")
def crew_execute(
    crew_id: str = typer.Argument(..., help="Crew ID"),
    cwd: str = typer.Option(None, "--cwd", help="Working directory"),
    mode: str = typer.Option("write", "--mode", help="Execution mode: read-only, write, full"),
    timeout: int = typer.Option(300, "--timeout", help="Timeout in seconds"),
    model: str = typer.Option(None, "--model", help="Model override"),
) -> None:
    """Execute a crew."""
    from thegent.cli_crew import crew_execute_cmd

    crew_execute_cmd(crew_file=crew_id, cwd=cwd, mode=mode, timeout=timeout, model=model)


@crew_app.command("list")
def crew_list() -> None:
    """List all crews."""
    from thegent.cli_crew import crew_list_cmd

    crew_list_cmd()


@crew_app.command("show")
def crew_show(crew_id: str = typer.Argument(..., help="Crew ID")) -> None:
    """Show crew details."""
    from thegent.cli_crew import crew_show_cmd

    crew_show_cmd(crew_id=crew_id)


@crew_app.command("status")
def crew_status(crew_id: str = typer.Option(None, "--crew-id", help="Crew ID")) -> None:
    """Show crew execution status."""
    from thegent.cli_crew import crew_status_cmd

    crew_status_cmd(crew_id=crew_id)


@compliance_app.command("export")
def compliance_export(framework: str, output: str = "compliance_bundle.json"):
    """Export evidence bundle for SOC2, ISO27001, or EU-AI-ACT."""
    from pathlib import Path

    from thegent.config import ThegentSettings
    from thegent.governance.compliance import ComplianceExporter

    settings = ThegentSettings()
    exporter = ComplianceExporter(settings.session_dir)
    target = Path(output)
    bundle = exporter.export_bundle(framework, target)

    typer.echo(f"Successfully exported {framework} evidence to {target}")
    typer.echo(f"Mapped Controls: {len(bundle['controls'])}")


@compliance_app.command("siem-test")
def compliance_siem_test(
    message: str = typer.Argument("Test SIEM egress event", help="Test message"),
    severity: str = typer.Option("low", "--severity", "-s", help="Event severity"),
) -> None:
    """Test SIEM event egress (WP-15001)."""
    from thegent.cli import compliance_siem_test_cmd

    compliance_siem_test_cmd(message=message, severity=severity)


@compliance_app.command("plugin-check")
def compliance_plugin_check(
    plugin_id: str = typer.Argument(..., help="Plugin ID to verify"),
    signature: str = typer.Argument(..., help="Signature to verify"),
) -> None:
    """Verify a plugin contract (WP-15003)."""
    from thegent.cli import compliance_plugin_check_cmd

    compliance_plugin_check_cmd(plugin_id=plugin_id, signature=signature)


@compliance_app.command("redact")
def compliance_redact(
    text: str = typer.Argument(..., help="Text to redact"),
) -> None:
    """Test PII/Secret redaction (WP-15005)."""
    from thegent.cli import compliance_redact_cmd

    compliance_redact_cmd(text=text)


@compliance_app.command("ledger-verify")
def ledger_verify():
    """Verify the integrity of the immutable incident ledger (WP-15002)."""
    from thegent.config import ThegentSettings
    from thegent.governance.ledger import IncidentLedger

    settings = ThegentSettings()
    ledger_path = settings.session_dir / "incident_ledger.jsonl"
    ledger = IncidentLedger(ledger_path)

    if ledger.verify_integrity():
        typer.echo("Ledger integrity VERIFIED. Hash chain is intact.")
    else:
        typer.echo("Ledger integrity FAILED! Hash chain breach detected.")


@trust_app.command("status")
def govern_trust_status(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich"),
) -> None:
    """Show last environment and trust boundary status (WP-3007)."""
    from thegent.cli import trust_status_cmd

    trust_status_cmd(format=format)


@signatures_app.command("list")
def govern_signatures_list(
    limit: int = typer.Option(50, "--limit", "-n", help="Max artifacts to show"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich"),
) -> None:
    """List signed MAIF artifacts (WP-3002)."""
    from thegent.cli import signatures_list_cmd

    signatures_list_cmd(limit=limit, format=format)


@signatures_app.command("verify")
def govern_signatures_verify(
    run_id: str = typer.Argument(..., help="Run ID to verify"),
) -> None:
    """Verify a signed MAIF artifact (WP-3002)."""
    from thegent.cli import signatures_verify_cmd

    signatures_verify_cmd(run_id=run_id)


@learning_app.command("list")
def learning_list():
    """List all candidate models in the learning registry."""
    import importlib

    from thegent.config import ThegentSettings

    LearningRegistry = importlib.import_module("thegent.planning.learning").LearningRegistry

    settings = ThegentSettings()
    registry_path = settings.session_dir / "learning_registry.json"
    mgr = LearningRegistry(registry_path)
    models = mgr.list_models()

    if not models:
        typer.echo("No learning models registered.")
        return

    for m in models:
        typer.echo(f"Model: {m.id} | Status: {m.status.upper()} | Success Rate: {m.metrics.success_rate:.1%}")


@learning_app.command("promote")
def learning_promote(model_id: str, approver: str):
    """Promote a candidate model to 'promoted' status (WP-14003)."""
    import importlib

    from thegent.config import ThegentSettings

    LearningRegistry = importlib.import_module("thegent.planning.learning").LearningRegistry

    settings = ThegentSettings()
    registry_path = settings.session_dir / "learning_registry.json"
    mgr = LearningRegistry(registry_path)

    if mgr.finalize_promotion(model_id, approver):
        typer.echo(f"Model {model_id} successfully promoted by {approver}.")
    else:
        typer.echo(f"Failed to promote model {model_id}. Ensure it is in 'candidate' status.")


@learning_app.command("rollback")
def learning_rollback(model_id: str):
    """Rollback a promoted or candidate model (WP-14003)."""
    import importlib
    import logging

    from thegent.config import ThegentSettings

    _log = logging.getLogger(__name__)

    LearningRegistry = importlib.import_module("thegent.planning.learning").LearningRegistry

    settings = ThegentSettings()
    registry_path = settings.session_dir / "learning_registry.json"
    mgr = LearningRegistry(registry_path)

    model = next((m for m in mgr.list_models() if m.id == model_id), None)
    if not model:
        typer.echo(f"Model {model_id} not found.")
        return

    model.status = "rejected"
    save_fn = getattr(mgr, "save", None)
    if callable(save_fn):
        save_fn()
    else:
        _log.warning("LearningRegistry.save() not available; skipping persisted save")
    typer.echo(f"Model {model_id} has been rolled back and rejected.")


@federation_app.command("list")
def federation_list():
    """List all federated namespaces (WP-13005)."""
    from thegent.config import ThegentSettings
    from thegent.governance.federation import FederatedPolicyManager

    settings = ThegentSettings()
    mgr = FederatedPolicyManager(settings.session_dir / "policies")
    health = mgr.get_federation_health()

    typer.echo(f"Federation Health: {health['status']}")
    typer.echo(f"Active Namespaces: {health['namespace_count']}")
    for ns in health["namespaces"]:
        typer.echo(f"  - {ns}")


@federation_app.command("status")
def federation_status():
    """Show detailed federation health and drift status (WP-13005)."""
    from thegent.config import ThegentSettings
    from thegent.governance.federation import FederatedPolicyManager

    settings = ThegentSettings()
    mgr = FederatedPolicyManager(settings.session_dir / "policies")
    health = mgr.get_federation_health()

    typer.echo(json.dumps(health, indent=2))


recover_app = typer.Typer(help="State recovery and self-healing")
observe_app = typer.Typer(help="Observability, telemetry, and performance")
plan_app = typer.Typer(help="Task planning and DAG management")
discovery_app = typer.Typer(help="Discovery of external agents (WP-4008)")
config_app = typer.Typer(help="Configuration: show, set, check and concurrency (multi-tenant aware)")
session_app = typer.Typer(help="Session management: list, show, logs, send, attach (WP-9000)")

discovery_app.command("register")(discovery_register_cmd)
discovery_app.command("parse")(discovery_parse_cmd)
discovery_app.command("scan")(discovery_scan_cmd)

@config_app.command("check")
def config_check(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Validate config; fail-fast on misconfig (DX-010, ROB-013)."""
    config_check_cmd(format=format)

@config_app.command("concurrency")
def config_concurrency(
    show: bool = typer.Option(False, "--show", help="Show current concurrency status"),
    set_limit: int | None = typer.Option(None, "--set", help="Set concurrency limit (1-200)"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """View or set concurrency limit."""
    from thegent.cli import concurrency_set_cmd, concurrency_show_cmd
    if set_limit is not None:
        concurrency_set_cmd(set_limit)
    else:
        concurrency_show_cmd(format=format)

@config_app.command("show")
def config_show(
    tenant_id: str | None = typer.Option(None, "--tenant", "-T", help="Tenant ID"),
    session_id: str | None = typer.Option(None, "--session", "-S", help="Session ID"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich | json"),
) -> None:
    """Show resolved configuration for the current context."""
    from thegent.config_provider import get_config_provider

    p = get_config_provider()
    resolved = p.resolve(tenant_id=tenant_id, session_id=session_id)

    if format == "json":
        import json
        typer.echo(json.dumps(resolved, indent=2))
    else:
        from rich.table import Table
        table = Table(title=f"Resolved Configuration (Tenant: {tenant_id or 'default'})")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        for k, v in sorted(resolved.items()):
            table.add_row(k, str(v))
        console.print(table)

@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Config key to set"),
    value: str = typer.Argument(..., help="Config value to set"),
) -> None:
    """Set a configuration value."""
    from thegent.cli import config_set_cmd
    config_set_cmd(key, value)

session_app.command("list")(ps_cmd)
session_app.command("show")(status_cmd)
session_app.command("logs")(logs_cmd)
session_app.command("send")(loop_send_cmd)
session_app.command("stop")(loop_stop_cmd)
session_app.command("attach")(takeover_cmd)

from thegent.agents.unified_registry_cli import app as registry_app
from thegent.cli_swarm import app as swarm_app
from thegent.cli_teammates import app as teammates_app
from thegent.clode_main import app as clode_app

app.add_typer(registry_app, name="registry")
app.add_typer(swarm_app, name="swarm")
app.add_typer(teammates_app, name="teammates")
orchestrate_app.add_typer(teammates_app, name="teammates")
from thegent.clode_main import sitback_cmd
from thegent.roid_main import app as roid_app
from thegent.terminal_cli import app as terminal_app

dex_app: typer.Typer | None = None
try:
    from thegent.dex_main import app as _dex_app
    dex_app = _dex_app
except Exception:
    dex_app = None

app.command("sitback")(sitback_cmd)
app.add_typer(clode_app, name="clode")
app.add_typer(roid_app, name="roid")
if dex_app is not None:
    app.add_typer(dex_app, name="dex")
app.add_typer(orchestrate_app, name="orchestrate")
app.add_typer(govern_app, name="govern")
app.add_typer(session_app, name="session")

# AgilePlus governance commands (go command group)
go_app = typer.Typer(help="AgilePlus governance commands: cycle, watch, status, health")


@go_app.command("health")
def go_health(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich"),
) -> None:
    """Show current health score (composite 0-100, band, per-dimension breakdown)."""
    govern_go_health_cmd(cd=cd, format=format)


@go_app.command("status")
def go_status(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Show current governance status (state, cycle_id, shutdown_requested)."""
    govern_go_status_cmd(cd=cd)


@go_app.command("cycle")
def go_cycle(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    force: bool = typer.Option(False, "--force", help="Run even if health >= threshold"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich"),
) -> None:
    """Run a single governance cycle."""
    govern_go_cycle_cmd(cd=cd, force=force, format=format)


@go_app.command("watch")
def go_watch(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    interval: int = typer.Option(300, "--interval", help="Seconds between cycles"),
    max_cycles: int | None = typer.Option(None, "--max-cycles", help="Maximum cycles to run"),
) -> None:
    """Run continuous governance mode."""
    govern_go_watch_cmd(cd=cd, interval=interval, max_cycles=max_cycles)


app.add_typer(go_app, name="go")
app.add_typer(recover_app, name="recover")
app.add_typer(observe_app, name="observe")
app.add_typer(plan_app, name="plan")
app.add_typer(discovery_app, name="discovery")
app.add_typer(config_app, name="config")

orchestrate_app.add_typer(discovery_app, name="discovery")
app.add_typer(terminal_app, name="terminal")


@orchestrate_app.command("loop")
def loop(
    prompt: str = typer.Argument(..., help="Initial task prompt"),
    todo_spec: str = typer.Argument(..., help="Todo spec/task list for the checker"),
    agent: str | None = typer.Option(None, "--agent", "-a", help="Worker agent name"),
    checker: str = typer.Option("antigravity", "--checker", help="Checker agent name"),
    mode: str = typer.Option("soft", "--mode", help="Loop mode: soft | hard"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Run a Lifecycle loop with Checker oversight."""
    loop_cmd(
        prompt=prompt,
        todo_spec=todo_spec,
        agent=agent,
        checker=checker,
        loop_mode=mode,
        cd=cd,
    )


@orchestrate_app.command("loop-send")
def loop_send(
    session_id: str | None = typer.Argument(None, help="Loop session ID (auto-detected if missing)"),
    prompt: str = typer.Argument(..., help="Next prompt to inject (takeover)"),
) -> None:
    """Send prompt to a running loop. Human or agent can use this to inject the next instruction."""
    loop_send_cmd(session_id=session_id, prompt=prompt)


@orchestrate_app.command("loop-stop")
def loop_stop(
    session_id: str | None = typer.Argument(None, help="Loop session ID to stop (auto-detected if missing)"),
) -> None:
    """Send STOP signal to a running Lifecycle loop."""
    loop_stop_cmd(session_id=session_id)


@app.command("run")
@orchestrate_app.command("run")
def run(
    prompt: str = typer.Argument(None, help="Task prompt (omit when using --retry --run-id)"),
    agent: str | None = typer.Argument(None, help="Provider (optional when -M/--model given)"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    retry_run: bool = typer.Option(
        False, "--retry", help="Retry failed run by --run-id (looks up prompt from registry)"
    ),
    mode: str = typer.Option("write", "--mode", "-m", help="Mode: read-only, write, full"),
    timeout: int | None = typer.Option(
        None, "--timeout", "-t", help="Timeout in seconds (default: 10m; use 1800 for 30m)"
    ),
    full: bool = typer.Option(False, "--full", "-f", help="Show full raw output (default: stream-json, parsed)"),
    live: bool = typer.Option(False, "--live", help="Stream output live to terminal"),
    model: str | None = typer.Option(
        None, "--model", "-M", help="Model override, 'auto' for Pareto+classifier, or model-first when agent omitted"
    ),
    provider: str | None = typer.Option(None, "--provider", "-P", help="Provider override for model-first routing"),
    failover: bool = typer.Option(False, "--failover", help="On failure, try next route (model-first only)"),
    routing: str | None = typer.Option(
        None, "--routing", "-R", help="Routing policy: prefer_direct | prefer_proxy (default from config)"
    ),
    include_contract: bool = typer.Option(
        False, "--include-contract", help="Print resolved model route contract metadata in output"
    ),
    run_id: str | None = typer.Option(None, "--run-id", help="Explicit run ID for registry correlation"),
    lane: str = typer.Option("standard", "--lane", help="Execution lane: standard, critical, recovery"),
    idempotency_token: str | None = typer.Option(
        None, "--idempotency-token", help="Deterministic token to prevent duplicate runs"
    ),
    confidence: float | None = typer.Option(None, "--confidence", help="Task confidence score (0.0-1.0)"),
    arbitration: str | None = typer.Option(
        None, "--arbitration", help="Arbitration role: leader | follower | consensus"
    ),
    override: str | None = typer.Option(None, "--override", help="Policy override reason code"),
    contract_version: str | None = typer.Option(
        None, "--contract-version", help="Contract schema version (default: current)"
    ),
    domain: str | None = typer.Option(None, "--domain", help="Domain tag for tiered retention (WP-3006)"),
    speculative: bool = typer.Option(False, "--speculative", help="Enable speculative execution mode (WP-5001)"),
    search: bool = typer.Option(True, "--search/--no-search", help="Enable web search for codex agents (default: on)"),
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug mode (THGENT_DEBUG=1, proxy -debug for model/provider/latency tags)"
    ),
    task_id: str | None = typer.Option(None, "--task-id", help="Associate run with a specific task ID"),
    tenant: str | None = typer.Option(None, "--tenant", "-T", help="Tenant ID for config resolution"),
) -> None:
    """Run a foreground agent invocation. Use -M <model> without agent for model-first routing.

    Examples:
      thegent run "Fix bug in auth.py" free
      thegent run "Implement feature" -M gemini-3-flash
      thegent run "Review code" --mode read-only
    """
    if retry_run and run_id:
        retry_cmd(run_id=run_id, agent=agent, failover=failover, cd=cd, override_reason=override)
        return
    if not prompt:
        typer.echo("Error: prompt required (or use --retry --run-id <run_id>)")
        raise typer.Exit(1)
    settings = ThegentSettings()
    effective_timeout = timeout if timeout is not None else settings.default_timeout
    run_cmd(
        prompt=prompt,
        agent=agent,
        cd=cd,
        mode=mode,
        timeout=effective_timeout,
        full=full,
        live=live,
        model=model,
        provider=provider,
        failover=failover,
        routing=routing,
        include_contract=include_contract,
        run_id=run_id,
        lane=lane,
        idempotency_token=idempotency_token,
        confidence=confidence,
        arbitration=arbitration,
        override_reason=override,
        contract_version=contract_version,
        domain=domain,
        speculative=speculative,
        search=search,
        debug=debug,
        task_id=task_id,
        tenant=tenant,
    )


import contextlib

from thegent.orchestration.tasks import TaskRole


def _run_role_cmd(
    role: TaskRole,
    prompt: str,
    cd: Path | None = None,
    mode: str = "write",
    timeout: int | None = None,
    bg: bool = False,
    model: str | None = None,
    agent: str | None = None,
    owner: str | None = None,
    live: bool = True,
    full: bool = False,
) -> None:
    """Run a task with a specific role-based system prompt."""
    settings = ThegentSettings()
    # If agent or model is explicitly provided, we use those.
    # Otherwise, we use the virtual 'role' agent which defaults to gemini-3-flash.
    effective_agent = agent or role.value
    effective_timeout = timeout or settings.default_timeout

    if bg:
        bg_cmd(
            prompt=prompt,
            agent=effective_agent,
            cd=cd,
            mode=mode,
            timeout=effective_timeout,
            full=full,
            model=model,
            owner=owner,
        )
    else:
        run_cmd(
            prompt=prompt,
            agent=effective_agent,
            cd=cd,
            mode=mode,
            timeout=effective_timeout,
            full=full,
            live=live,
            model=model,
        )


@app.command("summarize")
def summarize(
    prompt: str = typer.Argument(..., help="Content or task to summarize"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    bg: bool = typer.Option(False, "--bg", "-b", help="Run in background"),
    model: str | None = typer.Option(None, "--model", "-M", help="Model override"),
    timeout: int | None = typer.Option(None, "--timeout", "-t", help="Timeout override"),
) -> None:
    """Summarize content with brevity and key takeaways."""
    _run_role_cmd(TaskRole.SUMMARIZE, prompt, cd=cd, bg=bg, model=model, timeout=timeout)


@app.command("research")
def research(
    prompt: str = typer.Argument(..., help="Research topic or task"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    bg: bool = typer.Option(False, "--bg", "-b", help="Run in background"),
    model: str | None = typer.Option(None, "--model", "-M", help="Model override"),
    timeout: int | None = typer.Option(None, "--timeout", "-t", help="Timeout override"),
) -> None:
    """Deep dive research and comprehensive information gathering."""
    _run_role_cmd(TaskRole.RESEARCH, prompt, cd=cd, bg=bg, model=model, timeout=timeout)


@app.command("review")
def review(
    prompt: str = typer.Argument(..., help="Content or code to review"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    bg: bool = typer.Option(False, "--bg", "-b", help="Run in background"),
    model: str | None = typer.Option(None, "--model", "-M", help="Model override"),
    timeout: int | None = typer.Option(None, "--timeout", "-t", help="Timeout override"),
) -> None:
    """Critical analysis and quality checks for code or documentation."""
    _run_role_cmd(TaskRole.REVIEW, prompt, cd=cd, bg=bg, model=model, timeout=timeout)


@app.command("explain")
def explain(
    prompt: str = typer.Argument(..., help="Concept or task to explain"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    bg: bool = typer.Option(False, "--bg", "-b", help="Run in background"),
    model: str | None = typer.Option(None, "--model", "-M", help="Model override"),
    timeout: int | None = typer.Option(None, "--timeout", "-t", help="Timeout override"),
) -> None:
    """Clarification and educational explanation of complex concepts."""
    _run_role_cmd(TaskRole.EXPLAIN, prompt, cd=cd, bg=bg, model=model, timeout=timeout)


@app.command("fix")
def fix(
    prompt: str = typer.Argument(..., help="Bug description or task to fix"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    bg: bool = typer.Option(False, "--bg", "-b", help="Run in background"),
    model: str | None = typer.Option(None, "--model", "-M", help="Model override"),
    timeout: int | None = typer.Option(None, "--timeout", "-t", help="Timeout override"),
) -> None:
    """Bug identification and resolution."""
    _run_role_cmd(TaskRole.FIX, prompt, cd=cd, bg=bg, model=model, timeout=timeout)


@app.command("code")
def code(
    prompt: str = typer.Argument(..., help="Feature implementation or coding task"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    bg: bool = typer.Option(False, "--bg", "-b", help="Run in background"),
    model: str | None = typer.Option(None, "--model", "-M", help="Model override"),
    timeout: int | None = typer.Option(None, "--timeout", "-t", help="Timeout override"),
) -> None:
    """Feature implementation and coding tasks."""
    _run_role_cmd(TaskRole.CODE, prompt, cd=cd, bg=bg, model=model, timeout=timeout)


@app.command("free")
def free(
    prompt: str = typer.Argument(None, help="Task prompt (omit when using --do-next)"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    mode: str = typer.Option("write", "--mode", "-m", help="Mode: read-only, write, full"),
    timeout: int = typer.Option(
        None,
        "--timeout",
        "-t",
        help="Timeout in seconds (default from THGENT_DEFAULT_TIMEOUT_FREE, else 300)",
    ),
    do_next: bool = typer.Option(False, "--do-next", "-n", help="Find next work item from plan do-next and run it"),
    repeat: int = typer.Option(
        1, "--repeat", "-r", help="With --do-next: run up to N work packages in sequence (stop on first failure)"
    ),
    live: bool = typer.Option(True, "--live/--no-live", "-l", help="Stream output live (default: on)"),
    bg: bool = typer.Option(False, "--bg", "-b", help="Run in background (async)"),
    diff: bool = typer.Option(False, "--diff", "-D", help="Suppress live stream; show diff/summary at end"),
) -> None:
    """Base free tier: Copilot gpt-5-mini. Alias for thegent run \"<prompt>\" free."""
    if repeat > 1 and not do_next:
        typer.echo("--repeat requires --do-next")
        raise typer.Exit(1)
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    effective_timeout = timeout if timeout is not None else settings.default_timeout_free
    effective_live = live and not diff

    for attempt in range(max(1, repeat)):
        if do_next:
            from thegent.cli_impl import do_next_impl

            result = do_next_impl(cd=Path(cd) if cd else None, limit=1)
            if "error" in result:
                typer.echo(f"Error: {result['error']}")
                raise typer.Exit(1)
            items = result.get("next_items", [])
            if not items:
                if attempt == 0:
                    typer.echo("No next work items found. Use: thegent plan do-next")
                    raise typer.Exit(1)
                typer.echo(f"[do-next] No more items after {attempt} work package(s).")
                break
            prompt = items[0].get("prompt_suggestion", "")
            if not prompt:
                typer.echo("No prompt_suggestion in first work item.")
                raise typer.Exit(1)
            typer.echo(
                f"[do-next {attempt + 1}/{repeat}] {items[0].get('id', '?')}: {(prompt[:60] + '...') if len(prompt) > 60 else prompt}"
            )
        if not prompt:
            typer.echo("Error: prompt required (or use --do-next)")
            raise typer.Exit(1)

        if bg:
            bg_cmd(
                prompt=prompt,
                agent="copilot",
                cd=cd,
                mode=mode,
                model="gpt-5-mini",
                timeout=effective_timeout,
                full=False,
                owner=None,
            )
        else:
            run_cmd(
                prompt=prompt,
                agent="copilot",
                cd=cd,
                mode=mode,
                model="gpt-5-mini",
                live=effective_live,
                timeout=effective_timeout,
            )

        if do_next and repeat > 1 and attempt < repeat - 1:
            prompt = ""


@app.command("route")
@orchestrate_app.command("route")
def terminal_route(
    prompt: str = typer.Argument(..., help="Task prompt to route"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Route task to an active terminal session if available."""
    terminal_route_cmd(prompt=prompt, cd=cd)


@app.command("bg")
@orchestrate_app.command("bg")
def bg(
    prompt: str = typer.Argument(..., help="Task prompt"),
    agent: str | None = typer.Argument(None, help="Provider (optional when -M/--model given)"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    mode: str = typer.Option("write", "--mode", "-m", help="Mode: read-only, write, full"),
    timeout: int | None = typer.Option(
        None, "--timeout", "-t", help="Timeout in seconds (default: 10m; use 1800 for 30m)"
    ),
    full: bool = typer.Option(False, "--full", help="Use full raw output mode"),
    owner: str | None = typer.Option(None, "--owner", help="Session owner tag (default: <user>:<cwd-name>)"),
    model: str | None = typer.Option(None, "--model", "-M", help="Model override or model-first"),
    provider: str | None = typer.Option(None, "--provider", "-P", help="Provider override for model-first routing"),
    routing: str | None = typer.Option(
        None, "--routing", "-R", help="Routing policy: prefer_direct | prefer_proxy (default from config)"
    ),
    failover: bool = typer.Option(False, "--failover", help="On failure, try next route (model-first only)"),
    format: str | None = typer.Option(
        None,
        "--format",
        help="Output format: json | rich (default) | md (agent-friendly)",
    ),
    include_contract: bool = typer.Option(
        False, "--include-contract", help="Include resolved route contract metadata in output"
    ),
    continuation: str | None = typer.Option(
        None, "--continuation", "-C", help="Prior session id(s) to continue from (comma-separated)"
    ),
    continuation_stderr: bool = typer.Option(
        False, "--continuation-stderr", help="Include stderr from prior session(s)"
    ),
    run_id: str | None = typer.Option(None, "--run-id", help="Explicit run ID for registry correlation"),
    lane: str = typer.Option("standard", "--lane", help="Execution lane: standard, critical, recovery"),
    idempotency_token: str | None = typer.Option(
        None, "--idempotency-token", help="Deterministic token to prevent duplicate runs"
    ),
    confidence: float | None = typer.Option(None, "--confidence", help="Task confidence score (0.0-1.0)"),
    arbitration: str | None = typer.Option(
        None, "--arbitration", help="Arbitration role: leader | follower | consensus"
    ),
    override: str | None = typer.Option(None, "--override", help="Policy override reason code"),
    contract_version: str | None = typer.Option(
        None, "--contract-version", help="Contract schema version (default: current)"
    ),
    domain: str | None = typer.Option(None, "--domain", help="Domain tag for tiered retention (WP-3006)"),
    speculative: bool = typer.Option(False, "--speculative", help="Enable speculative execution mode (WP-5001)"),
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug mode (THGENT_DEBUG=1 for model/provider/latency tags)"
    ),
    task_id: str | None = typer.Option(None, "--task-id", help="Associate run with a specific task ID"),
    tenant: str | None = typer.Option(None, "--tenant", "-T", help="Tenant ID for config resolution"),
) -> None:
    """Start a background run and register a session."""
    settings = ThegentSettings()
    effective_timeout = timeout if timeout is not None else settings.default_timeout
    bg_cmd(
        prompt=prompt,
        agent=agent,
        cd=cd,
        mode=mode,
        timeout=effective_timeout,
        full=full,
        model=model,
        provider=provider,
        routing=routing,
        failover=failover,
        owner=owner,
        output_format=format,
        include_contract=include_contract,
        continue_from=continuation,
        continuation_include_stderr=continuation_stderr,
        run_id=run_id,
        lane=lane,
        idempotency_token=idempotency_token,
        confidence=confidence,
        arbitration=arbitration,
        override_reason=override,
        contract_version=contract_version,
        domain=domain,
        speculative=speculative,
        debug=debug,
        task_id=task_id,
        tenant=tenant,
    )


history_app = typer.Typer(
    help="Execution history and audit commands",
    invoke_without_command=True,
    no_args_is_help=False,
)


@history_app.callback(invoke_without_command=True)
def history_root(
    ctx: typer.Context,
    limit: int = typer.Option(50, "--limit", "-l", help="Number of runs to show"),
    format: str | None = typer.Option(
        None,
        "--format",
        help="Output format: json | rich (default) | md",
    ),
) -> None:
    """Default `history` behavior: list runs when no subcommand is provided."""
    if ctx.invoked_subcommand is None:
        history_cmd(limit=limit, format=format)


@history_app.command("list")
@observe_app.command("history")
def history_list(
    limit: int = typer.Option(50, "--limit", "-l", help="Number of runs to show"),
    format: str | None = typer.Option(
        None,
        "--format",
        help="Output format: json | rich (default) | md",
    ),
) -> None:
    """List execution run history (sync and background)."""
    history_cmd(limit=limit, format=format)


@history_app.command("events")
def history_events(
    limit: int = typer.Option(100, "--limit", "-l", help="Number of events to show"),
    run_id: str | None = typer.Option(None, "--run-id", help="Filter events by Run ID"),
    format: str | None = typer.Option(
        None,
        "--format",
        help="Output format: json | rich (default) | md",
    ),
) -> None:
    """List raw telemetry events."""
    from thegent.cli import events_cmd

    events_cmd(run_id=run_id, limit=limit, format=format)


@history_app.command("verify")
@govern_app.command("verify")
def history_audit_verify(
    format: str | None = typer.Option(None, "--format", help="Output format: json | rich"),
) -> None:
    """Verify the integrity of the execution run registry."""
    audit_verify_cmd(format=format)


app.add_typer(history_app, name="history")


isolation_app = typer.Typer(help="Manage agent isolation and multi-tenancy.")
app.add_typer(isolation_app, name="isolation")

@isolation_app.command("check")
def isolation_check(
    mode: str = typer.Option("sub-user", "--mode", help="Isolation mode to check")
) -> None:
    """Check the status of the isolation system."""
    from thegent.cli_impl import isolation_check_impl
    isolation_check_impl(mode=mode)

@isolation_app.command("share-run")
def isolation_share_run(
    command: list[str] = typer.Argument(..., help="Command to run shared"),
    tenant_id: str = typer.Option("default", "--tenant", help="Tenant ID"),
    role: str | None = typer.Option(None, "--role", help="L1 Role (e.g. frontend_lead)"),
) -> None:
    """Run a command shared across tenants using CLI-Share debouncing."""
    from pathlib import Path

    from thegent.isolation.sub_user_provider import SubUserIsolationProvider

    provider = SubUserIsolationProvider(enable_l1_nesting=bool(role))
    context = provider.allocate_tenant(tenant_id, role=role)

    result = provider.execute_in_context(context, command, share=True)

    if result.get("cached"):
        pass

    raise typer.Exit(code=result["returncode"])


# Inbox commands (unified events)
inbox_app = typer.Typer(help="Unified event inbox: list, wait")


@inbox_app.callback(invoke_without_command=True)
def inbox_root(
    ctx: typer.Context,
    owner: str | None = typer.Option(None, "--owner", "-o", help="Filter by owner"),
    agent: str | None = typer.Option(None, "--agent", "-a", help="Filter by agent"),
    event_type: str | None = typer.Option(
        None,
        "--event",
        "-e",
        help="Filter by event: start|finish|feedback|pause|resume|escalation",
    ),
    status: str | None = typer.Option(
        None,
        "--status",
        "-s",
        help="Filter by status: running|completed|failed",
    ),
    sources: str | None = typer.Option(
        "registry,escalation",
        "--sources",
        help="Comma-separated: registry,escalation",
    ),
    limit: int = typer.Option(50, "--limit", "-l", help="Max events to show"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output: json | rich (default)"),
) -> None:
    """Default: list recent inbox events. Use 'inbox wait' to block until new event."""
    if ctx.invoked_subcommand is None:
        from thegent.cli import inbox_list_cmd

        inbox_list_cmd(
            owner=owner,
            agent=agent,
            event_type=event_type,
            status=status,
            sources=sources,
            limit=limit,
            format=format,
        )


@inbox_app.command("list")
@observe_app.command("inbox")
def inbox_list(
    owner: str | None = typer.Option(None, "--owner", "-o", help="Filter by owner"),
    agent: str | None = typer.Option(None, "--agent", "-a", help="Filter by agent"),
    event_type: str | None = typer.Option(
        None,
        "--event",
        "-e",
        help="Filter by event: start|finish|feedback|pause|resume|escalation",
    ),
    status: str | None = typer.Option(
        None,
        "--status",
        "-s",
        help="Filter by status: running|completed|failed",
    ),
    sources: str | None = typer.Option(
        "registry,escalation",
        "--sources",
        help="Comma-separated: registry,escalation",
    ),
    limit: int = typer.Option(50, "--limit", "-l", help="Max events to show"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output: json | rich (default)"),
) -> None:
    """List unified inbox events with optional filters."""
    from thegent.cli import inbox_list_cmd

    inbox_list_cmd(
        owner=owner,
        agent=agent,
        event_type=event_type,
        status=status,
        sources=sources,
        limit=limit,
        format=format,
    )


@inbox_app.command("wait")
def inbox_wait(
    owner: str | None = typer.Option(None, "--owner", "-o", help="Filter by owner"),
    agent: str | None = typer.Option(None, "--agent", "-a", help="Filter by agent"),
    event_type: str | None = typer.Option(
        None,
        "--event",
        "-e",
        help="Filter by event: start|finish|feedback|pause|resume|escalation",
    ),
    status: str | None = typer.Option(
        None,
        "--status",
        "-s",
        help="Filter by status: running|completed|failed",
    ),
    sources: str | None = typer.Option(
        "registry,escalation",
        "--sources",
        help="Comma-separated: registry,escalation",
    ),
    poll: float = typer.Option(2.0, "--poll", "-p", help="Poll interval in seconds"),
    timeout: float = typer.Option(0.0, "--timeout", "-t", help="Max wait seconds (0=unbounded)"),
    notify: bool = typer.Option(True, "--notify/--no-notify", help="Ring bell on new event"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output: json | rich (default)"),
) -> None:
    """Wait for next inbox event matching filters. Blocks until new event or timeout."""
    from thegent.cli import inbox_wait_cmd

    inbox_wait_cmd(
        owner=owner,
        agent=agent,
        event_type=event_type,
        status=status,
        sources=sources,
        poll=poll,
        timeout=timeout,
        notify=notify,
        format=format,
    )


app.add_typer(inbox_app, name="inbox")

queue_app = typer.Typer(help="Manage the deferred prompt queue ($defer).")
app.add_typer(queue_app, name="queue")


@queue_app.command("list")
def queue_list(
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch live"),
) -> None:
    """List pending prompts in the queue."""
    from thegent.cli import queue_list_cmd

    queue_list_cmd(watch=watch)


rules_app = typer.Typer(help="Agent rules and instructions synchronization.")
app.add_typer(rules_app, name="rules")


@rules_app.command("sync")
def rules_sync(
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite even if identical"),
    check: bool = typer.Option(False, "--check", help="Check for drift without syncing"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Project directory"),
) -> None:
    """Sync CLAUDE.md to other platform-specific rule files (AGENTS.md, Cursor, Codex)."""
    rules_sync_cmd(force=force, check=check, cd=cd)


policy_app = typer.Typer(help="Governance and security policy commands")
app.add_typer(policy_app, name="policy")


@policy_app.command("show")
@govern_app.command("show-policy")
def policy_show() -> None:
    """Show active governance policies and thresholds."""
    policy_show_cmd()


@policy_app.command("check")
@govern_app.command("check-policy")
def policy_check(
    agent: str = typer.Option("cursor", "--agent", "-a", help="Agent to check"),
    model: str | None = typer.Option(None, "--model", "-m", help="Model to check"),
    lane: str = typer.Option("standard", "--lane", "-l", help="Execution lane"),
    confidence: float = typer.Option(1.0, "--confidence", "-c", help="Confidence score"),
) -> None:
    """Evaluate a hypothetical run against governance policies (WP-3001)."""
    from thegent.cli import policy_check_cmd

    policy_check_cmd(agent=agent, model=model, lane=lane, confidence=confidence)


@policy_app.command("purge")
@govern_app.command("purge-history")
def policy_purge(
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run", help="Dry run or actual purge"),
) -> None:
    """Purge expired history based on tiered retention (WP-3006)."""
    from thegent.cli import policy_purge_cmd

    policy_purge_cmd(dry_run=dry_run)


escalate_app = typer.Typer(help="Governance escalation queue (WP-3008)")
govern_app.add_typer(escalate_app, name="escalate")


@escalate_app.command("add")
def govern_escalate_add(
    run_id: str = typer.Argument(..., help="Run ID that was blocked"),
    reason: str = typer.Argument(..., help="Block reason (e.g. policy violation)"),
    sla_minutes: int = typer.Option(30, "--sla", "-s", help="SLA in minutes (escalate by)"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Owner tag"),
    lane: str = typer.Option("standard", "--lane", "-l", help="Execution lane"),
    priority: int = typer.Option(0, "--priority", "-p", help="Priority (higher = more urgent)"),
) -> None:
    """Add a blocked run to the escalation queue (WP-3008)."""
    escalate_add_cmd(
        run_id=run_id,
        reason=reason,
        sla_minutes=sla_minutes,
        owner=owner,
        lane=lane,
        priority=priority,
    )


@escalate_app.command("list")
def govern_escalate_list(
    past_sla_only: bool = typer.Option(False, "--past-sla", help="Show only items past SLA"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max items to show"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """List governance escalation queue."""
    escalate_list_cmd(past_sla_only=past_sla_only, limit=limit, format=format)


@escalate_app.command("resolve")
def govern_escalate_resolve(
    run_id: str | None = typer.Argument(None, help="Run ID to resolve (auto-detected if missing)"),
    resolution: str = typer.Option("resolved", "--resolution", "-r", help="Resolution status"),
) -> None:
    """Mark an escalation item as resolved."""
    escalate_resolve_cmd(run_id=run_id, resolution=resolution)


@escalate_app.command("approve")
def govern_escalate_approve(
    run_id: str | None = typer.Argument(None, help="Run ID to approve (auto-detected if missing)"),
) -> None:
    """Approve an escalation, recording an override for the owner (G-GP-05)."""
    escalate_approve_cmd(run_id=run_id)


interruption_app = typer.Typer(help="Interruption taxonomy and fatigue controls (WP-4004)")
govern_app.add_typer(interruption_app, name="interruption")


@interruption_app.command("list")
def govern_interruption_list(
    limit: int = typer.Option(20, "--limit", "-n", help="Max items to show"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """List recent interruptions with taxonomy and fatigue score."""
    interruption_list_cmd(limit=limit, format=format)


@interruption_app.command("snooze")
def govern_interruption_snooze(
    alert_id: str = typer.Argument(..., help="Alert/run ID to snooze"),
    minutes: int = typer.Option(5, "--minutes", "-m", help="Snooze duration in minutes"),
    type: str = typer.Option("unknown", "--type", "-t", help="Interruption type for context"),
) -> None:
    """Snooze an alert; auto-escalates when expired."""
    interruption_snooze_cmd(alert_id=alert_id, minutes=minutes, itype=type)


@govern_app.command("calibrate")
def govern_calibrate() -> None:
    """Recalculate trust score calibration factors for all agents (G-GP-09)."""
    from rich.console import Console
    from rich.table import Table

    from thegent.cli_impl import update_calibration_impl

    console = Console()
    results = update_calibration_impl()
    if not results:
        console.print("[dim]No runs with feedback found for calibration.[/dim]")
        return

    table = Table(title="Agent Calibration Factors")
    table.add_column("Agent")
    table.add_column("Factor", justify="right")
    table.add_column("Samples", justify="right")

    for agent, res in sorted(results.items()):
        table.add_row(agent, f"{res['factor']:.3f}", str(res["samples"]))

    console.print(table)
    console.print("[green]Calibration factors persisted.[/green]")


@govern_app.command("cost")
def govern_cost(
    owner: str | None = typer.Option(None, "--owner", "-o", help="Filter by owner"),
    days: int = typer.Option(1, "--days", "-d", help="Number of days to aggregate"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich"),
) -> None:
    """Show daily cost aggregation (FR-GOV-002)."""
    from thegent.cli import govern_cost_cmd

    govern_cost_cmd(owner=owner, days=days, format=format)


@guardrails_app.command("check")
def govern_guardrails_check(
    prompt: str = typer.Argument(..., help="Prompt to check"),
    agent: str | None = typer.Option(None, "--agent", "-a", help="Agent to check"),
    model: str | None = typer.Option(None, "--model", "-m", help="Model to check"),
) -> None:
    """Check a prompt against active guardrails (FR-GOV-003..006)."""
    from thegent.cli import guardrails_check_cmd

    guardrails_check_cmd(prompt=prompt, agent=agent, model=model)


@guardrails_app.command("show")
def govern_guardrails_show() -> None:
    """Show active guardrail configuration (FR-GOV-007)."""
    from thegent.cli import guardrails_show_cmd

    guardrails_show_cmd()


@govern_app.command("sweep")
def govern_sweep(
    drift_window: int = typer.Option(50, "--drift-window", "-w", help="Window size for drift detection"),
    include_audit: bool = typer.Option(False, "--audit", "-a", help="Include registry audit in sweep"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """WP-3005: Policy drift sweep - drift detection, budget check, past-SLA escalations (cron-ready)."""
    sweep_cmd(drift_window=drift_window, include_audit=include_audit, format=format)


@govern_app.command("purge")
def govern_purge(
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run", help="If true, only show what would be purged"),
) -> None:
    """WP-3006: Tiered retention purge (G-GP-07)."""
    purge_cmd(dry_run=dry_run)


@govern_app.command("data-protection")
def govern_data_protection(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Show data protection and privacy controls status (WP-3006)."""
    data_protection_cmd(format=format)


@govern_app.command("compliance-report")
def govern_compliance_report(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | md (default)"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write report to file"),
) -> None:
    """Generate compliance evidence retention report (WP-3006)."""
    compliance_report_cmd(format=format, output=output)


@govern_app.command("contracts")
def govern_contracts(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Show the contract registry and compatibility matrix."""
    contracts_registry_cmd(format=format)


@govern_app.command("conformance")
def govern_conformance(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
    check_drift: bool = typer.Option(False, "--check-drift", help="Run drift alarm on contract telemetry"),
    drift_window: int = typer.Option(50, "--drift-window", "-w", help="Window size for drift detection"),
) -> None:
    """Run provider adapter conformance tests."""
    contracts_conformance_cmd(format=format, check_drift=check_drift, drift_window=drift_window)


@govern_app.command("migration")
def govern_migration(
    contract_id: str = typer.Argument(..., help="Contract ID (e.g. csm)"),
    version: str = typer.Argument(..., help="Version (e.g. csm-v1)"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Evaluate migration status for a contract version."""
    migration_cmd(contract_id=contract_id, version=version, format=format)


@govern_app.command("hook-watcher")
def govern_hook_watcher(
    project_dir: Path = typer.Argument(
        Path(),
        help="Project directory to watch",
    ),
    interval: int = typer.Option(5, "--interval", "-i", help="Poll interval in seconds"),
    foreground: bool = typer.Option(False, "--foreground", "-f", help="Run in foreground (don't daemonize)"),
) -> None:
    """P8: Start hook cache watcher daemon — pre-warms caches on file changes."""
    import subprocess

    from rich.console import Console

    from thegent.infra import run_subprocess_optimized

    console = Console()
    hooks_root = Path(__file__).resolve().parents[2] / "hooks"
    watcher = hooks_root / "hook-watcher.sh"
    if not watcher.exists():
        console.print("[red]hook-watcher.sh not found[/red]")
        raise SystemExit(1)
    env = os.environ.copy()
    env["HOOK_WATCHER_INTERVAL"] = str(interval)
    if foreground:
        run_subprocess_optimized([str(watcher), str(project_dir.resolve())], env=env, check=False)
    else:
        subprocess.Popen(
            [str(watcher), str(project_dir.resolve())],
            env=env,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        console.print(f"[green]Hook watcher started[/green] (project: {project_dir}, interval: {interval}s)")


@observe_app.command("summary")
def observe_summary(
    limit: int = typer.Option(500, "--limit", "-n", help="Events to analyze"),
    drift_window: int = typer.Option(50, "--drift-window", "-w", help="Drift analysis window"),
    structural_budget: float = typer.Option(
        5.0,
        "--structural-budget",
        help="Allowed structural drift percentage before budget alert",
    ),
    semantic_budget: float = typer.Option(
        10.0,
        "--semantic-budget",
        help="Allowed semantic drift percentage before budget alert",
    ),
    provider: str | None = typer.Option(None, "--provider", help="Filter summary to a specific provider"),
    trend_samples: int = typer.Option(
        0,
        "--trend-samples",
        help="Enable historical trend sampling with up to N latest runs (2+ enables trend mode)",
    ),
    top_escalations: int = typer.Option(10, "--top-escalations", help="Escalations to show in panel"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """FR-X08: Unified observability summary (KPIs, drift, escalation)."""
    from thegent.cli import observe_summary_cmd

    observe_summary_cmd(
        limit=limit,
        drift_window=drift_window,
        structural_budget=structural_budget,
        semantic_budget=semantic_budget,
        provider=provider,
        trend_samples=trend_samples,
        top_escalations=top_escalations,
        format=format,
    )


@observe_app.command("kpis")
def observe_kpis(
    limit: int = typer.Option(500, "--limit", "-n", help="Number of events to analyze"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Show fallback KPIs for dashboard/alerting (G-CA-02 B3)."""
    from rich.console import Console
    from rich.table import Table

    from thegent.config import ThegentSettings
    from thegent.contracts.telemetry import ContractTelemetry

    settings = ThegentSettings()
    console = Console()
    ct = ContractTelemetry(settings.session_dir)
    kpis = ct.get_fallback_kpis(limit=limit)

    if format == "json":
        sys.stdout.write(json.dumps(kpis) + "\n")
        return

    table = Table(title=f"Fallback KPIs (last {limit} events)")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Total Events", str(kpis["total"]))
    table.add_row("Fallback Rate", f"{kpis['fallback_rate']:.1%}")
    table.add_row("Success Rate", f"{kpis['success_rate']:.1%}")
    table.add_row("Avg Confidence", f"{kpis['avg_confidence']:.2f}")
    table.add_row("Structural Drift %", f"{kpis['structural_drift_pct']:.2f}")
    table.add_row("Semantic Drift %", f"{kpis['semantic_drift_pct']:.2f}")
    console.print(table)

    by_provider = kpis.get("by_provider", {})
    if by_provider:
        p_table = Table(title="By Provider")
        p_table.add_column("Provider")
        p_table.add_column("Fallback %")
        p_table.add_column("Success %")
        p_table.add_column("Avg Conf")
        p_table.add_column("Total")
        for p, v in sorted(by_provider.items()):
            p_table.add_row(
                p,
                f"{v['fallback_rate']:.1%}",
                f"{v['success_rate']:.1%}",
                f"{v['avg_confidence']:.2f}",
                str(v["total"]),
            )
        console.print(p_table)


@observe_app.command("drift")
def observe_drift(
    window: int = typer.Option(50, "--window", "-w", help="Analysis window size"),
    structural_budget: float = typer.Option(5.0, "--structural-budget", help="Structural drift alert budget %"),
    semantic_budget: float = typer.Option(10.0, "--semantic-budget", help="Semantic drift alert budget %"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Detect significant drift in contract performance and check alert budgets (G-RV-07)."""
    drift_cmd(window=window, format=format, structural_budget=structural_budget, semantic_budget=semantic_budget)


@observe_app.command("dlq")
def observe_dlq(
    status: str | None = typer.Option(None, "--status", help="Filter by status"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """List items in the Dead-Letter Queue (WP-Y2/WP-2008)."""
    from thegent.cli import dlq_list_cmd

    dlq_list_cmd(status=status, format=format)


@observe_app.command("load-status")
def observe_load_status(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Show load classification and safe-mode status (WP-5002)."""
    load_status_cmd(format=format)


@observe_app.command("cost-status")
def observe_cost_status(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Show cost budget utilization and cost-aware routing status (WP-5003)."""
    cost_status_cmd(format=format)


@observe_app.command("usage")
def observe_usage(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
    no_cost: bool = typer.Option(False, "--no-cost", help="Skip cost status section"),
) -> None:
    """Show plan usage: provider metrics from CLIProxyAPIPlus and cost status."""
    usage_cmd(format=format, include_cost=not no_cost)


@observe_app.command("traffic")
def observe_traffic() -> None:
    """TRAFFIC KPI Dashboard (WP-Y7)."""
    from thegent.cli import traffic_cmd

    traffic_cmd()


@observe_app.command("drift-monitor")
def observe_drift_monitor(
    prompt: str = typer.Argument(..., help="Prompt to test for drift"),
    agents: str = typer.Option(
        "cursor,headless_agent,interactive_agent",
        "--agents",
        help="Comma-separated list of agents (codex/claude aliases supported)",
    ),
) -> None:
    """Cross-provider drift monitoring (WP-6002)."""
    from thegent.cli import drift_monitor_cmd

    drift_monitor_cmd(prompt=prompt, agents=agents.split(","))


@observe_app.command("trend")
def observe_trend(
    payload_type: str = typer.Option(
        "session_contract_health_report",
        "--payload-type",
        help="Trend payload type: session_contract_health_report | session_contract_health_gate",
    ),
    all_sessions: bool = typer.Option(False, "--all", help="Trend scope for all owners"),
    owner: str | None = typer.Option(None, "--owner", help="Trend scope owner filter"),
    strict: bool = typer.Option(False, "--strict", help="Trend scope strict checks"),
    limit: int = typer.Option(20, "--limit", help="Max snapshots to return"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default) | md"),
) -> None:
    """Read health trend snapshots for a report/gate policy scope."""
    session_contract_health_trend_cmd(
        payload_type=payload_type,
        all_sessions=all_sessions,
        owner=owner,
        strict=strict,
        limit=limit,
        format=format,
    )


@app.command("cockpit")
@observe_app.command("cockpit")
def cockpit() -> None:
    """Show high-level operator cockpit summary."""
    cockpit_cmd()


@app.command("sitback-dashboard")
@observe_app.command("sitback-dashboard")
def sitback_dashboard(
    refresh: int | None = typer.Option(
        None,
        "--refresh",
        "-r",
        help="Refresh every N seconds (live mode); Ctrl+C to stop",
    ),
    format: str | None = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format: json | rich (default)",
    ),
    profile: str = typer.Option(
        "medium",
        "--profile",
        "-p",
        help="Dashboard tier: light (summary only), medium (panels), full (panels + plugins)",
    ),
) -> None:
    """Unified sitback dashboard: sessions, cockpit, terminals. CLI mirror of MCP tool."""
    sitback_dashboard_cmd(refresh=refresh, format=format, profile=profile)


@app.command("feedback")
@govern_app.command("feedback")
def feedback(
    run_id: str | None = typer.Argument(None, help="Run ID to provide feedback for (auto-detected if missing)"),
    score: float = typer.Argument(1.0, help="Confidence score (0.0 to 1.0)"),
    note: str = typer.Option(None, "--note", "-m", help="Optional feedback note"),
) -> None:
    """Provide operator feedback for a specific run."""
    feedback_cmd(run_id, score, note)


@app.command("archive")
@observe_app.command("archive")
def archive(
    days: int | None = typer.Option(
        None, "--days", "-d", help="Override retention days (default: THGENT_RETENTION_DAYS_SESSIONS)"
    ),
    domain: str | None = typer.Option(None, "--domain", help="Filter by domain tag (WP-3006)"),
    tier: str | None = typer.Option(None, "--tier", "-t", help="Storage tier: hot (30d) | cold (365d)"),
) -> None:
    """Archive old sessions (WP-6005). WP-3006: tiered retention (hot 30d, cold 1yr)."""
    archive_cmd(days=days, domain=domain, tier=tier)


@app.command("operations")
def operations(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
    operation: str | None = typer.Option(
        None, "--operation", "-o", help="Filter by operation: orchestrate | govern | recover | observe | plan"
    ),
) -> None:
    """List universal operation taxonomy (orchestrate, govern, recover, observe, plan)."""
    operations_cmd(format=format, operation=operation)


@app.command("modes")
def modes(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
    mode: str | None = typer.Option(
        None, "--mode", "-m", help="Filter by mode: sequential_delegation | parallel_consensus | review_loop"
    ),
) -> None:
    """List multi-agent orchestration modes (G-KD-04)."""
    modes_cmd(format=format, mode=mode)


@app.command("benchmark")
@observe_app.command("benchmark")
def benchmark() -> None:
    """Report orchestration performance metrics (WP-6001)."""
    benchmark_cmd()


@app.command("closure-pack")
@govern_app.command("closure-pack")
def closure_pack(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Generate a formal closure pack for the current DAG session (WP-6002/6008/FR-024)."""
    closure_pack_cmd(cd=cd)


@govern_app.command("roadmap")
def govern_roadmap() -> None:
    """Successor roadmap generation (WP-6004)."""
    from thegent.cli import roadmap_cmd

    roadmap_cmd()


@govern_app.command("self-heal-tests")
def govern_self_heal_tests(
    test_output: str | None = typer.Option(None, "--output", help="Raw pytest output to analyze"),
) -> None:
    """Self-healing test suite: automated fix recommendations (WP-6006)."""
    from thegent.cli import self_heal_tests_cmd

    self_heal_tests_cmd(test_output=test_output)


@govern_app.command("negotiate")
def govern_negotiate(
    contract_id: str = typer.Argument(..., help="Contract ID (e.g. csm)"),
    supported: str = typer.Argument(..., help="Comma-separated supported versions"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich"),
) -> None:
    """Negotiate a contract version (WP-7001)."""
    from thegent.cli import session_contract_negotiate_cmd

    session_contract_negotiate_cmd(contract_id=contract_id, supported_versions=supported, format=format)


@govern_app.command("trend-analysis")
def govern_trend_analysis() -> None:
    """Detailed contract trend analysis (WP-7009/7010)."""
    from thegent.cli import session_contract_trend_analysis_cmd

    session_contract_trend_analysis_cmd()


@govern_app.command("release-pack")
def govern_release_pack(version: str = typer.Option("2.0", "--version", "-v", help="Release version")) -> None:
    """Automated release documentation packaging (WP-12009)."""
    from thegent.cli import release_pack_cmd

    release_pack_cmd(version=version)


@app.command("history-legacy", hidden=True)
def history_legacy(
    limit: int = typer.Option(50, "--limit", "-l", help="Number of runs to show"),
    format: str | None = typer.Option(
        None,
        "--format",
        help="Output format: json | rich (default) | md",
    ),
    events: bool = typer.Option(False, "--events", help="Show raw telemetry events"),
    run_id: str | None = typer.Option(None, "--run-id", help="Filter events by Run ID"),
) -> None:
    """List execution run history (sync and background)."""
    if events:
        from thegent.cli import events_cmd

        events_cmd(run_id=run_id, limit=limit, format=format)
    else:
        history_cmd(limit=limit, format=format)


@app.command("ps")
@orchestrate_app.command("ps")
def ps(
    all_sessions: bool = typer.Option(False, "--all", help="Show sessions for all owners"),
    owner: str | None = typer.Option(None, "--owner", help="Override owner filter"),
    format: str | None = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format: json | rich (default) | md (agent-friendly)",
    ),
    include_contract: bool = typer.Option(
        False, "--include-contract", help="Include resolved route contract metadata in list payload"
    ),
    scan_ide: bool = typer.Option(
        True,
        "--scan-ide/--no-scan-ide",
        help="Scan for IDE-managed sessions (Cursor, Claude CLI, Codex)",
    ),
) -> None:
    """List registered background sessions."""
    # Note: scan_ide parameter exists but ps_cmd doesn't use it yet (future feature)
    ps_cmd(
        all_sessions=all_sessions,
        owner=owner,
        format=format,
        include_contract=include_contract,
    )



@recover_app.command("status")
def recover_status() -> None:
    """Show recovery stability and suggested playbooks."""
    typer.echo("Command not implemented yet.")


@app.command("status")
@orchestrate_app.command("status")
@observe_app.command("status")
def status(
    session_id: str | None = typer.Argument(None, help="Session id (auto-detected if missing)"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json or rich"),
    include_contract: bool = typer.Option(
        False, "--include-contract", help="Include resolved route contract metadata in output"
    ),
) -> None:
    """Show one session status."""
    status_cmd(session_id=session_id, format=format, include_contract=include_contract)


@app.command("explain")
@orchestrate_app.command("explain")
def explain_run(
    run_id: str | None = typer.Argument(None, help="Run ID to explain (auto-detected if missing)"),
) -> None:
    """Show detailed explanation for an agent run (WP-4002)."""
    from thegent.cli import explain_cmd

    explain_cmd(run_id=run_id)


@orchestrate_app.command("fallbacks")
def orchestrate_fallbacks(
    run_id: str | None = typer.Argument(None, help="Run ID to get fallbacks for (auto-detected if missing)"),
) -> None:
    """Show safe fallback options for a failed run (WP-4003)."""
    # import inside function to avoid import cycles; ensure symbol exists
    import importlib

    cli_mod = importlib.import_module("thegent.cli")
    if not hasattr(cli_mod, "fallbacks_cmd") or not callable(cli_mod.fallbacks_cmd):
        raise RuntimeError("fallbacks_cmd is not available")

    cli_mod.fallbacks_cmd(run_id=run_id)


@orchestrate_app.command("handoff")
def orchestrate_handoff(
    owner: str = typer.Argument(..., help="New owner tag for the handoff"),
) -> None:
    """Create a continuity snapshot for a shift handoff (WP-4006, WP-3008)."""
    from thegent.cli import handoff_cmd

    handoff_cmd(owner=owner)


@orchestrate_app.command("handoff-confirm")
def orchestrate_handoff_confirm(
    snapshot_id: str = typer.Argument(..., help="Snapshot ID to confirm"),
    incoming_owner: str = typer.Argument(..., help="Incoming owner confirming the handoff"),
    confidence: float = typer.Option(1.0, "--confidence", "-c", help="Confidence score (0-1)"),
) -> None:
    """Incoming owner confirms handoff completeness (WP-3008, WP-4006)."""
    from thegent.cli import handoff_confirm_cmd

    handoff_confirm_cmd(snapshot_id=snapshot_id, incoming_owner=incoming_owner, confidence=confidence)


@orchestrate_app.command("handoff-list")
def orchestrate_handoff_list(
    limit: int = typer.Option(10, "--limit", "-n", help="Max snapshots to show"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """List pending handoff snapshots (WP-4006)."""
    handoff_list_cmd(limit=limit, format=format)


@orchestrate_app.command("handoff-show")
def orchestrate_handoff_show(
    snapshot_id: str = typer.Argument(..., help="Snapshot ID to display"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Show full handoff summary: state, evidence, next steps (WP-4006)."""
    handoff_show_cmd(snapshot_id=snapshot_id, format=format)


@orchestrate_app.command("replay")
def orchestrate_replay(
    run_id: str = typer.Argument(..., help="Run ID to replay"),
    what_if_env: str | None = typer.Option(None, "--what-if-env", help="Simulate run in different environment"),
) -> None:
    """Decision replay and rationale snapshots (WP-4007)."""
    from thegent.cli import replay_cmd

    replay_cmd(run_id=run_id, what_if_env=what_if_env)


@orchestrate_app.command("watchdog")
def orchestrate_watchdog(
    max_idle: int = typer.Option(3600, "--max-idle", help="Max idle time in seconds before stale"),
) -> None:
    """Scan for stale sessions and recommend handoffs (WP-5005)."""
    from thegent.cli import watchdog_cmd

    watchdog_cmd(max_idle_s=max_idle)


@orchestrate_app.command("inspect")
@observe_app.command("inspect")
@app.command("inspect")
def inspect(
    session_ids: list[str] = typer.Argument(default=[], help="Session ID(s). Use --owner to inspect all for owner."),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Inspect all sessions for this owner"),
    tail: int = typer.Option(50, "--tail", "-n", help="Log lines per session"),
    stderr: bool = typer.Option(False, "--stderr", help="Show stderr instead of stdout"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json or rich"),
    include_contract: bool = typer.Option(
        False, "--include-contract", help="Include resolved route contract metadata in status payload"
    ),
) -> None:
    """Show status and logs for one or more sessions. No shell loop needed."""
    inspect_cmd(
        session_ids=session_ids or [],
        owner=owner,
        tail=tail,
        stderr=stderr,
        format=format,
        include_contract=include_contract,
    )


@app.command("session-contracts")
@govern_app.command("session-contracts")
def session_contracts(
    all_sessions: bool = typer.Option(False, "--all", help="Audit sessions for all owners"),
    owner: str | None = typer.Option(None, "--owner", help="Filter by owner"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default) | md"),
    missing_only: bool = typer.Option(
        False, "--missing-only", help="Show only sessions with incomplete/missing contract metadata"
    ),
    summary_only: bool = typer.Option(False, "--summary-only", help="Return summary only"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict contract/provider/alias alignment checks"),
) -> None:
    """Audit session routing contract metadata coverage and completeness."""
    session_contracts_cmd(
        all_sessions=all_sessions,
        owner=owner,
        format=format,
        missing_only=missing_only,
        summary_only=summary_only,
        strict=strict,
    )


@app.command("session-contract-health-gate")
@govern_app.command("health-gate")
def session_contract_health_gate(
    all_sessions: bool = typer.Option(False, "--all", help="Evaluate sessions for all owners"),
    owner: str | None = typer.Option(None, "--owner", help="Filter by owner"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default) | md"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict contract/provider/alias alignment checks"),
    min_healthy_ratio: float = typer.Option(1.0, "--min-healthy", help="Minimum healthy ratio required to pass"),
    policy_profile: str | None = typer.Option(
        None,
        "--policy-profile",
        help="Policy profile: strict_ci | warn_only | prod_release",
    ),
    no_worse_than_baseline: bool = typer.Option(
        False,
        "--no-worse-than-baseline",
        help="Fail if blocked ratio regresses beyond baseline + tolerance.",
    ),
    regression_tolerance: float = typer.Option(
        0.0,
        "--regression-tolerance",
        help="Allowed blocked-ratio regression when baseline checks are enabled.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help=(
            "Write gate artifact to path. If --export-format is not set, file extension "
            "(.json/.md/.csv/.jsonl) controls the format; unknown extension defaults to json."
        ),
    ),
    export_format: str | None = typer.Option(
        None,
        "--export-format",
        help="Export format: json | md | csv | jsonl (defaults from --output extension)",
    ),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output artifact if it already exists"),
) -> None:
    """Fail if routing contract health is below threshold."""
    session_contract_health_gate_cmd(
        all_sessions=all_sessions,
        owner=owner,
        strict=strict,
        format=format,
        min_healthy_ratio=min_healthy_ratio,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        output=output,
        export_format=export_format,
        overwrite=overwrite,
    )


@app.command("session-contract-health-report")
@govern_app.command("health-report")
def session_contract_health_report(
    all_sessions: bool = typer.Option(False, "--all", help="Report sessions for all owners"),
    owner: str | None = typer.Option(None, "--owner", help="Filter by owner"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default) | md"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict contract/provider/alias alignment checks"),
    top_blocked: int = typer.Option(25, "--top-blocked", help="Max blocked sessions to show in reports"),
    policy_profile: str | None = typer.Option(
        None,
        "--policy-profile",
        help="Policy profile: strict_ci | warn_only | prod_release",
    ),
    no_worse_than_baseline: bool = typer.Option(
        False,
        "--no-worse-than-baseline",
        help="Fail report policy if blocked ratio regresses beyond baseline + tolerance.",
    ),
    regression_tolerance: float = typer.Option(
        0.0,
        "--regression-tolerance",
        help="Allowed blocked-ratio regression when baseline checks are enabled.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help=(
            "Write report artifact to path. If --export-format is not set, file extension "
            "(.json/.md/.csv/.jsonl) controls the format; unknown extension defaults to json."
        ),
    ),
    export_format: str | None = typer.Option(
        None,
        "--export-format",
        help="Export format: json | md | csv | jsonl (defaults from --output extension)",
    ),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output artifact if it already exists"),
) -> None:
    """Create a policy-friendly session contract health report with issue and owner breakdown."""
    session_contract_health_report_cmd(
        all_sessions=all_sessions,
        owner=owner,
        strict=strict,
        format=format,
        top_blocked=top_blocked,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        output=output,
        export_format=export_format,
        overwrite=overwrite,
    )


@app.command("session-contract-health-trend")
@govern_app.command("health-trend")
def session_contract_health_trend(
    payload_type: str = typer.Option(
        "session_contract_health_report",
        "--payload-type",
        help="Trend payload type: session_contract_health_report | session_contract_health_gate",
    ),
    all_sessions: bool = typer.Option(False, "--all", help="Trend scope for all owners"),
    owner: str | None = typer.Option(None, "--owner", help="Trend scope owner filter"),
    strict: bool = typer.Option(False, "--strict", help="Trend scope strict checks"),
    policy_profile: str | None = typer.Option(
        None,
        "--policy-profile",
        help="Policy profile: strict_ci | warn_only | prod_release",
    ),
    min_healthy_ratio: float = typer.Option(1.0, "--min-healthy", help="Gate trend scope minimum healthy ratio"),
    top_blocked: int = typer.Option(25, "--top-blocked", help="Report trend scope top blocked"),
    limit: int = typer.Option(20, "--limit", help="Max snapshots to return"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default) | md"),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help=(
            "Write trend artifact to path. If --export-format is not set, file extension "
            "(.json/.md/.csv/.jsonl) controls the format; unknown extension defaults to json."
        ),
    ),
    export_format: str | None = typer.Option(
        None,
        "--export-format",
        help="Export format: json | md | csv | jsonl (defaults from --output extension)",
    ),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output artifact if it already exists"),
) -> None:
    """Read health trend snapshots for a report/gate policy scope."""
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
        output=output,
        export_format=export_format,
        overwrite=overwrite,
    )


@app.command("logs")
@orchestrate_app.command("logs")
@observe_app.command("logs")
def logs(
    session_id: str | None = typer.Argument(None, help="Session id (auto-detected if missing)"),
    follow: bool = typer.Option(False, "--follow", "-F", help="Follow log output"),
    stderr: bool = typer.Option(False, "--stderr", help="Show stderr log instead of stdout"),
    tail: int = typer.Option(200, "--tail", help="Initial tail lines"),
    timeout: int = typer.Option(0, "--timeout", help="Max follow timeout seconds (0=unbounded)"),
) -> None:
    """Print session logs."""
    logs_cmd(session_id=session_id, follow=follow, stderr=stderr, tail=tail, timeout=timeout)


@app.command("takeover")
@orchestrate_app.command("takeover")
def takeover(
    session_id: str = typer.Argument(..., help="Tmux session name or pane ID to attach to"),
) -> None:
    """Attach to an interactive tmux session (takeover)."""
    takeover_cmd(session_id=session_id)


@app.command("explorer")
@observe_app.command("explorer")
def terminal_explorer() -> None:
    """Launch the terminal explorer TUI."""
    explorer_cmd()


@app.command("wait")
@orchestrate_app.command("wait")
@observe_app.command("wait")
def wait(
    session_id: str | None = typer.Argument(None, help="Session id (auto-detected if missing)"),
    timeout: int = typer.Option(0, "--timeout", "-t", help="Max wait seconds (0=unbounded)"),
) -> None:
    """Wait for session completion and return session exit code."""
    wait_cmd(session_id=session_id, timeout=timeout)


@app.command("wait-next")
@orchestrate_app.command("wait-next")
def wait_next(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    poll: float = typer.Option(2.0, "--poll", "-p", help="Poll interval in seconds"),
    timeout: float = typer.Option(0.0, "--timeout", "-t", help="Max wait seconds (0=unbounded)"),
    sources: str | None = typer.Option(
        None,
        "--sources",
        "-s",
        help="Comma-separated: dag,do_next,escalation,inbox (default: all)",
    ),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: rich | json"),
) -> None:
    """Block until next actionable work exists. Does not return until DAG ready, work item, escalation, or inbox event."""
    plan_wait_next_cmd(cd=cd, poll=poll, timeout=timeout, sources=sources, format=format)


@app.command("stop")
@orchestrate_app.command("stop")
@recover_app.command("stop")
def stop(
    session_id: str | None = typer.Argument(None, help="Session id (auto-detected if missing)"),
    force: bool = typer.Option(False, "--force", help="Use SIGKILL instead of SIGTERM"),
    wind_down: bool = typer.Option(
        False,
        "--wind-down",
        help="Send SIGTERM and wait up to --grace seconds before returning",
    ),
    grace: int = typer.Option(
        20,
        "--grace",
        min=0,
        help="Wind-down grace window in seconds",
    ),
) -> None:
    """Stop a running session."""
    stop_cmd(session_id=session_id, force=force, wind_down=wind_down, grace=grace)


@app.command("pause")
@orchestrate_app.command("pause")
def pause(
    session_id: str | None = typer.Argument(None, help="Session id to pause (auto-detected if missing)"),
) -> None:
    """Mark a session as PAUSED in the registry (HITL)."""
    pause_cmd(session_id=session_id)


@app.command("resume")
@orchestrate_app.command("resume")
def resume(
    session_id: str | None = typer.Argument(None, help="Session id to resume (auto-detected if missing)"),
) -> None:
    """Mark a paused session as RUNNING in the registry (HITL)."""
    resume_cmd(session_id=session_id)


@app.command("retry")
@orchestrate_app.command("retry")
def retry(
    run_id: str | None = typer.Argument(None, help="Run ID to retry (omit to list recent failed runs)"),
    agent: str | None = typer.Option(None, "--agent", "-a", help="Override agent for retry"),
    failover: bool = typer.Option(False, "--failover", help="Use next agent in fallback chain"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    override: str | None = typer.Option(
        None, "--override", help="Policy override reason (e.g. for policy-blocked retries)"
    ),
) -> None:
    """Retry a failed run. With no run_id, list recent failed runs."""
    retry_cmd(run_id=run_id, agent=agent, failover=failover, cd=cd, override_reason=override)


@app.command("list-agents")
def list_agents() -> None:
    """List available providers."""
    list_agents_cmd()


agents_app = typer.Typer(help="Agent-related commands (list, retry failed runs)")
app.add_typer(agents_app, name="agents")


@agents_app.command("retry")
def agents_retry(
    run_id: str | None = typer.Argument(None, help="Run ID to retry (omit to list recent failed runs)"),
    agent: str | None = typer.Option(None, "--agent", "-a", help="Override agent for retry"),
    failover: bool = typer.Option(False, "--failover", help="Use next agent in fallback chain"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    override: str | None = typer.Option(
        None, "--override", help="Policy override reason (e.g. for policy-blocked retries)"
    ),
) -> None:
    """Retry a failed run. With no run_id, list recent failed runs. Alias for thegent retry."""
    retry_cmd(run_id=run_id, agent=agent, failover=failover, cd=cd, override_reason=override)


@agents_app.command("list")
def agents_list() -> None:
    """List available providers. Alias for thegent list-agents."""
    list_agents_cmd()


@app.command("list-droids")
def list_droids(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory for project droids"),
) -> None:
    """List available droids."""
    list_droids_cmd(cd=cd)


@app.command("list-models")
def list_models(
    provider: str | None = typer.Argument(None, help="Optional provider filter"),
    by_model: bool = typer.Option(False, "--by-model", help="Unified view: model -> providers (routing)"),
    refresh: bool = typer.Option(False, "--refresh", help="Bypass cache, re-scrape providers"),
    include_contract: bool = typer.Option(
        False, "--include-contract", help="Include structured route contract in output"
    ),
) -> None:
    """List known models (optionally filtered by provider)."""
    list_models_cmd(
        provider=provider,
        by_model=by_model,
        refresh=refresh,
        include_contract=include_contract,
    )


@app.command("resolve-model-route")
def resolve_model_route(
    model: str = typer.Argument(..., help="Model identifier (alias or canonical model ID)"),
    provider: str | None = typer.Option(None, "--provider", "-P", help="Optional provider hint"),
    policy: str = typer.Option(
        "prefer_direct",
        "--policy",
        help="Routing policy: prefer_direct, prefer_proxy, failover, cheapest, cost_quality, pareto",
    ),
    quality_floor: float = typer.Option(0.0, "--quality-floor", help="Min quality (0-1) for cost_quality policy"),
    lane: str | None = typer.Option(None, "--lane", help="Lane: critical | speed for pareto strategy"),
) -> None:
    """Resolve a model to a concrete provider+alias route."""
    resolve_model_route_cmd(model=model, provider=provider, policy=policy, quality_floor=quality_floor, lane=lane)


@app.command("route-probe")
def route_probe(
    model: str = typer.Argument(..., help="Model identifier (alias or canonical model ID)"),
    provider: str | None = typer.Option(None, "--provider", "-P", help="Optional provider hint"),
    policy: str = typer.Option(
        "prefer_direct",
        "--policy",
        help="Routing policy: prefer_direct, prefer_proxy, failover, cheapest, cost_quality, pareto",
    ),
    quality_floor: float = typer.Option(0.0, "--quality-floor", help="Min quality (0-1) for cost_quality policy"),
    lane: str | None = typer.Option(None, "--lane", help="Lane: critical | speed for pareto strategy"),
) -> None:
    """Dry-run route resolution: show which provider would be selected (DX-004). Alias for resolve-model-route."""
    resolve_model_route_cmd(model=model, provider=provider, policy=policy, quality_floor=quality_floor, lane=lane)


models_app = typer.Typer(help="Model catalog and cache commands")
app.add_typer(models_app, name="models")


@models_app.command("metrics")
def models_metrics(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass cache"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max rows to show"),
) -> None:
    """Show cost, speed, and quality for all model-provider pairs (unified view)."""
    from thegent.cli import metrics_cmd

    metrics_cmd(format=format, no_cache=no_cache, limit=limit)


@models_app.command("cost-values")
def models_cost_values(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Show cost values ($/1k tokens) for all model-provider pairs. Uses proxy metrics when reachable."""
    from thegent.cli import cost_values_cmd

    cost_values_cmd(format=format)


@models_app.command("speed-index")
def models_speed_index(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass cache, fetch fresh metrics"),
) -> None:
    """Show speed index (0-1) for all model-provider pairs. Uses proxy metrics when reachable."""
    from thegent.cli import speed_index_cmd

    speed_index_cmd(format=format, no_cache=no_cache)


@models_app.command("quality-index")
def models_quality_index(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass cache, fetch fresh data"),
) -> None:
    """Show quality index (0-1) for all models. Uses benchmarks.json (TB2.0, SWE-Bench, AIME)."""
    from thegent.cli import quality_index_cmd

    quality_index_cmd(format=format, no_cache=no_cache)


@models_app.command("refresh")
def models_refresh() -> None:
    """Invalidate models, speed-index, and quality-index caches. Next lookup will re-fetch."""
    from thegent.models import (
        invalidate_models_cache,
        invalidate_quality_index_cache,
        invalidate_speed_index_cache,
    )

    models_invalidated = invalidate_models_cache()
    invalidate_speed_index_cache()
    invalidate_quality_index_cache()
    if models_invalidated:
        typer.echo("Models cache invalidated.")
    else:
        typer.echo("Models cache was empty or already invalidated.")
    typer.echo("Speed and quality index caches cleared.")


@models_app.command("contract")
def models_contract() -> None:
    """Show route contract metadata for model catalog consumers."""
    from thegent.cli import list_model_contract_schema_cmd

    list_model_contract_schema_cmd()


cliproxy_app = typer.Typer(help="CLIProxyAPIPlus OAuth login and config (auth stored in ~/.cli-proxy-api)")
app.add_typer(cliproxy_app, name="cliproxy")


@cliproxy_app.command("ensure-config")
def cliproxy_ensure_config() -> None:
    """Ensure proxy config exists (port, auth-dir). Add provider blocks manually. Restart proxy to apply."""
    from thegent.agents.cliproxy_manager import _ensure_config
    from thegent.config import ThegentSettings

    config_path = _ensure_config(ThegentSettings())
    typer.echo(f"Config ensured: {config_path}")


@cliproxy_app.command("start")
def cliproxy_start() -> None:
    """Start proxy if not running. Uses ensure-config + CLIProxyAPIPlus binary."""
    from thegent.agents.cliproxy_manager import ensure_proxy_running
    from thegent.config import ThegentSettings

    base_url = ensure_proxy_running(ThegentSettings())
    typer.echo(f"Proxy running at {base_url}")


@cliproxy_app.command("stop")
def cliproxy_stop() -> None:
    """Stop proxy (kill process on cliproxy port)."""
    from thegent.agents.cliproxy_manager import kill_proxy
    from thegent.config import ThegentSettings

    if kill_proxy(ThegentSettings()):
        typer.echo("Proxy stopped.")
    else:
        typer.echo("No proxy process found on port.")


@cliproxy_app.command("models-setup")
def cliproxy_models_setup() -> None:
    """Rich TUI for adding models and providers with harness configuration."""
    from thegent.ux.models_providers_tui import run_models_providers_tui

    run_models_providers_tui()


@cliproxy_app.command("restart")
def cliproxy_restart() -> None:
    """Ensure config, stop proxy, then start. Use after config changes."""
    from thegent.agents.cliproxy_manager import _ensure_config, ensure_proxy_running, kill_proxy
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    _ensure_config(settings)
    kill_proxy(settings)
    base_url = ensure_proxy_running(settings)
    typer.echo(f"Proxy restarted at {base_url}")


@cliproxy_app.command("service")
def cliproxy_service(
    action: str = typer.Argument(
        ...,
        help="install | start | stop | uninstall — LaunchAgent (macOS)",
    ),
) -> None:
    """Manage proxy as launchd service (macOS). Runs at login, restarts on crash."""
    from rich.console import Console

    from thegent.agents.cliproxy_manager import (
        proxy_service_install,
        proxy_service_start,
        proxy_service_stop,
        proxy_service_uninstall,
    )
    from thegent.config import ThegentSettings

    console = Console()
    handlers = {
        "install": lambda: proxy_service_install(ThegentSettings()),
        "start": proxy_service_start,
        "stop": proxy_service_stop,
        "uninstall": proxy_service_uninstall,
    }
    if action not in handlers:
        console.print(f"[red]Unknown action: {action}. Use: install, start, stop, uninstall[/red]")
        raise typer.Exit(1)
    ok, msg = handlers[action]()
    if ok:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)


@cliproxy_app.command("login")
def cliproxy_login(
    provider: str = typer.Argument(
        ...,
        help="Provider: claude, codex (proxy API), minimax, glm, nim, kilo, roo, qwen, antigravity, iflow, kiro. gemini/copilot route via Codex proxy.",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Re-enter key even if already configured"),
) -> None:
    """Run login for provider. Unified flow: open URL + prompt for API key. Preflight checks existing credentials."""
    cliproxy_login_cmd(provider, force=force)


control_plane_app = typer.Typer(help="Control plane: multi-tenant config service")
app.add_typer(control_plane_app, name="control-plane")


@control_plane_app.command("serve")
def control_plane_serve(
    socket_path: str | None = typer.Option(None, "--socket", "-s", help="Unix socket path (Unix only)"),
    port: int = typer.Option(3848, "--port", "-p", help="HTTP port (default 3848)"),
    host: str = typer.Option("127.0.0.1", "--host", "-H", help="Bind host"),
) -> None:
    """Start the control plane server. Unix: socket or port. Windows: port only."""
    from thegent.control_plane.server import serve

    serve(socket_path=socket_path, port=port, host=host)


@control_plane_app.command("start")
def control_plane_start() -> None:
    """Start the control plane stack (via process-compose)."""
    from thegent.mcp_manage import mcp_up

    ok, msg = mcp_up()
    if ok:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]Failed to start control plane: {msg}[/red]")
        raise typer.Exit(1)


@control_plane_app.command("stop")
def control_plane_stop() -> None:
    """Stop the control plane stack (via process-compose)."""
    from thegent.mcp_manage import mcp_down

    ok, msg = mcp_down()
    if ok:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]Failed to stop control plane: {msg}[/red]")
        raise typer.Exit(1)


@control_plane_app.command("status")
def control_plane_status() -> None:
    """Check if control plane is running (health endpoint)."""
    import os

    import httpx

    url = os.environ.get("THGENT_CONTROL_PLANE_URL", "http://127.0.0.1:3848")
    url = url.rstrip("/").replace("/v1", "")
    try:
        r = httpx.get(f"{url}/health", timeout=2.0)
        if r.status_code == 200:
            data = r.json()
            console.print(f"[green]Control plane OK[/green] (version: {data.get('version', '?')})")
        else:
            console.print(f"[yellow]Control plane returned {r.status_code}[/yellow]")
    except Exception as e:
        console.print(f"[red]Control plane not reachable: {e}[/red]")
        raise typer.Exit(1)


@app.command("login")
@orchestrate_app.command("login")
def login(
    provider: str = typer.Argument(
        ...,
        help="Provider: claude, codex (proxy API), minimax, glm, nim, kilo, roo, qwen, antigravity, iflow, kiro. Alias for cliproxy login.",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Re-enter key even if already configured"),
) -> None:
    """Run login for provider. Alias for `thegent cliproxy login`. Unified: open URL + prompt for key."""
    cliproxy_login_cmd(provider, force=force)


dag_app = typer.Typer(help="DAG session commands (read .factory/dag-session.md)")
app.add_typer(dag_app, name="dag")


@dag_app.command("list")
@plan_app.command("list")
def dag_list(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory (default: cwd)"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: rich or md"),
) -> None:
    """Parse and display DAG session from .factory/dag-session.md."""
    dag_list_cmd(cd=cd, format=format)


@plan_app.command("incorporate")
def plan_incorporate(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be merged without writing"),
) -> None:
    """Merge fragments from 02-UNIFIED-WBS into WORK_STREAM.md. Preserves CLAIMED and COMPLETED."""
    plan_incorporate_cmd(cd=cd, dry_run=dry_run)


@plan_app.command("do-next")
def plan_do_next(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    limit: int = typer.Option(5, "--limit", "-l", help="Max items to return"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: rich | json"),
) -> None:
    """Find next actionable work items from PLAN_STATUS, FR_TRACKER, docs/plans/, escalation queue.

    Examples:
      thegent plan do-next
      thegent plan do-next -l 10
      thegent run "$(thegent plan get-next)" free
    """
    plan_do_next_cmd(cd=cd, limit=limit, format=format)


@plan_app.command("get-next")
def plan_get_next(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output: plain (default, prompt only) | json"),
) -> None:
    """Get first work item prompt for scripting. Use: PROMPT=$(thegent plan get-next)"""
    plan_get_next_cmd(cd=cd, format=format)


@plan_app.command("loop")
def plan_loop(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    max_iterations: int = typer.Option(0, "--max", "-m", help="Max iterations (0=unbounded)"),
    sleep_seconds: float = typer.Option(5.0, "--sleep", "-s", help="Seconds between iterations"),
    agent: str = typer.Option("free", "--agent", "-a", help="Agent for bg runs (default: free)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print only, do not run"),
) -> None:
    """Loop: get next item -> run bg -> repeat until no items or --max reached."""
    plan_loop_cmd(cd=cd, max_iterations=max_iterations, sleep_seconds=sleep_seconds, agent=agent, dry_run=dry_run)


@plan_app.command("spawn-next")
def plan_spawn_next(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of items to spawn in parallel (1-20)"),
    agent: str = typer.Option("free", "--agent", "-a", help="Agent for bg runs (default: free)"),
    timeout: int | None = typer.Option(None, "--timeout", "-t", help="Per-run timeout seconds (default: 10m)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be spawned"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: rich | json"),
) -> None:
    """Spawn N next work items in background (parallel batch). Manages 10-20 items alongside other agent managers."""
    from rich.console import Console

    console = Console()
    console.print("[yellow]plan spawn-next not yet implemented, use 'plan do-next' with --bg[/yellow]")


@plan_app.command("progress")
def plan_progress(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of runs to show"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: rich | json"),
) -> None:
    """Show recent runs (work-package progress). Alias for history --limit N."""
    plan_progress_cmd(limit=limit, format=format)


@plan_app.command("wait-next")
def plan_wait_next(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    poll: float = typer.Option(2.0, "--poll", "-p", help="Poll interval in seconds"),
    timeout: float = typer.Option(0.0, "--timeout", "-t", help="Max wait seconds (0=unbounded)"),
    sources: str | None = typer.Option(
        None,
        "--sources",
        "-s",
        help="Comma-separated: dag,do_next,escalation,inbox (default: all)",
    ),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: rich | json"),
) -> None:
    """Block until next actionable work exists (DAG ready, do_next, escalation, inbox)."""
    plan_wait_next_cmd(cd=cd, poll=poll, timeout=timeout, sources=sources, format=format)


@plan_app.command("claim")
def plan_claim(
    item_id: str = typer.Argument(..., help="Item ID to claim"),
    agent_id: str | None = typer.Argument(None, help="Agent ID (auto-detected if missing)"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Project directory"),
) -> None:
    """Claim an item in the unified work stream."""
    plan_claim_cmd(item_id=item_id, agent_id=agent_id, cd=cd)


@plan_app.command("complete")
def plan_complete(
    item_id: str = typer.Argument(..., help="Item ID to mark complete"),
    agent_id: str | None = typer.Argument(None, help="Agent ID (auto-detected if missing)"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Project directory"),
) -> None:
    """Mark an item as complete in the unified work stream."""
    plan_complete_cmd(item_id=item_id, agent_id=agent_id, cd=cd)


@plan_app.command("analyze")
def plan_analyze(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    pert: bool = typer.Option(False, "--pert", help="Run PERT overlay on DAG tasks"),
    resources: bool = typer.Option(False, "--resources", help="Simulate resource contention"),
    continuity: bool = typer.Option(False, "--continuity", help="Score continuity risk for handoff"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich"),
) -> None:
    """Run planning simulation overlays (XD1–XD3): PERT, resources, continuity risk."""
    plan_analyze_cmd(cd=cd, pert=pert, resources=resources, continuity=continuity, format=format)


@dag_app.command("validate")
@plan_app.command("validate")
def dag_validate(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory (default: cwd)"),
) -> None:
    """Validate DAG: cycles, orphans, agent names. Exit 2 on failure."""
    dag_validate_cmd(cd=cd)


@dag_app.command("add")
@plan_app.command("add")
def dag_add(
    task_id: str = typer.Argument(..., help="Task ID (e.g. QA-A4)"),
    agent: str = typer.Argument(..., help="Agent name"),
    prompt: str = typer.Argument(..., help="Task prompt (inline or @.factory/prompts/<id>.md)"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    depends_on: str | None = typer.Option(None, "--depends-on", help="Comma-separated task IDs"),
    contract_version: str | None = typer.Option(None, "--contract-version", help="Contract schema version (XA4)"),
) -> None:
    """Add a task to the DAG."""
    dag_add_cmd(
        task_id=task_id, agent=agent, prompt=prompt, cd=cd, depends_on=depends_on, contract_version=contract_version
    )


@dag_app.command("update")
@plan_app.command("update")
def dag_update(
    task_id: str = typer.Argument(..., help="Task ID to update"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    status: str | None = typer.Option(
        None, "--status", "-s", help="Set status: pending|running|done|failed|cancelled|skipped"
    ),
    prompt: str | None = typer.Option(None, "--prompt", "-p", help="Update prompt"),
    agent: str | None = typer.Option(None, "--agent", "-a", help="Update agent"),
    depends_on: str | None = typer.Option(None, "--depends-on", help="Update depends_on (comma-separated)"),
    contract_version: str | None = typer.Option(None, "--contract-version", help="Contract schema version (XA4)"),
) -> None:
    """Update a task in the DAG."""
    dag_update_cmd(
        task_id=task_id,
        cd=cd,
        status=status,
        prompt=prompt,
        agent=agent,
        depends_on=depends_on,
        contract_version=contract_version,
    )


@dag_app.command("remove")
@plan_app.command("remove")
def dag_remove(
    task_id: str = typer.Argument(..., help="Task ID to remove"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Remove a task from the DAG."""
    dag_remove_cmd(task_id=task_id, cd=cd)


@dag_app.command("cancel")
@plan_app.command("cancel")
def dag_cancel(
    task_id: str = typer.Argument(..., help="Task ID to cancel (soft remove)"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Set task status to cancelled."""
    dag_cancel_cmd(task_id=task_id, cd=cd)


@dag_app.command("ready")
@plan_app.command("ready")
def dag_ready(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: rich or md"),
) -> None:
    """List task IDs with satisfied dependencies (ready to run)."""
    dag_ready_cmd(cd=cd, format=format)


@dag_app.command("run")
@plan_app.command("run")
def dag_run(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="List what would run without spawning"),
    task: str | None = typer.Option(None, "--task", "-t", help="Run only this task ID"),
    max_parallel: int | None = typer.Option(None, "--max-parallel", help="Max parallel spawns"),
    lane: str | None = typer.Option(None, "--lane", help="Force all tasks into this lane"),
    check_drift: bool = typer.Option(False, "--check-drift", help="Block run if contract drift detected (XC2)"),
    contract_version: str | None = typer.Option(
        None, "--contract-version", help="Contract schema version (XA4; overrides task-level)"
    ),
) -> None:
    """Spawn thegent bg for each ready task; update status=running and session_id."""
    dag_run_cmd(
        cd=cd,
        dry_run=dry_run,
        task=task,
        max_parallel=max_parallel,
        lane=lane,
        check_drift=check_drift,
        contract_version=contract_version,
    )


@dag_app.command("status")
@plan_app.command("status")
def dag_status(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: rich or md"),
) -> None:
    """Show task + linked session status (running/exited:rc)."""
    dag_status_cmd(cd=cd, format=format)


@dag_app.command("sync")
@plan_app.command("sync")
def dag_sync(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Run in a loop (health check)"),
    interval: int = typer.Option(10, "--interval", "-i", help="Sync interval in seconds"),
    auto_run_next: bool = typer.Option(False, "--auto-run-next", help="Spawn next ready tasks after sync"),
    no_auto_run_next: bool = typer.Option(False, "--no-auto-run-next", help="Disable auto-run when --watch"),
) -> None:
    """Update task status from session exit (running -> done/failed)."""
    import time

    effective_auto_run_next = auto_run_next or (watch and not no_auto_run_next)
    while True:
        dag_sync_cmd(cd=cd, auto_run_next=effective_auto_run_next)
        if not watch:
            break
        time.sleep(interval)


@dag_app.command("wait-next")
def dag_wait_next(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    poll: float = typer.Option(2.0, "--poll", "-p", help="Poll interval in seconds"),
    timeout: float = typer.Option(0.0, "--timeout", "-t", help="Max wait seconds (0=unbounded)"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: rich | json"),
) -> None:
    """Block until DAG has next actionable work (sync + ready tasks). Does not return until ready tasks exist."""
    plan_wait_next_cmd(cd=cd, poll=poll, timeout=timeout, sources="dag", format=format)


@dag_app.command("reconcile")
@recover_app.command("reconcile")
def dag_reconcile(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Reconcile DAG state with reality (clean up stuck 'running' tasks)."""
    dag_reconcile_cmd(cd=cd)


@dag_app.command("checkpoint")
@plan_app.command("checkpoint")
def dag_checkpoint(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    reason: str = typer.Option("Manual checkpoint", "--reason", "-r", help="Reason for checkpoint"),
) -> None:
    """Create a point-in-time checkpoint of the DAG state."""
    dag_checkpoint_cmd(cd=cd, reason=reason)


@dag_app.command("rollback")
@plan_app.command("rollback")
@recover_app.command("rollback")
def dag_rollback(
    checkpoint_id: str | None = typer.Argument(None, help="Checkpoint ID to rollback to (auto-detected if missing)"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Rollback DAG state to a specific checkpoint."""
    dag_rollback_cmd(checkpoint_id=checkpoint_id, cd=cd)


@dag_app.command("checkpoints")
@plan_app.command("checkpoints")
def dag_checkpoints(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of checkpoints to show"),
) -> None:
    """List recent DAG checkpoints."""
    dag_checkpoints_cmd(limit=limit)


@dag_app.command("recover")
@recover_app.command("dag-recover")
def dag_recover(
    action: str = typer.Argument("retry-failed", help="Recovery action: retry-failed | clear-stuck | reset-retries"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Perform recovery playbook actions on the DAG."""
    dag_recover_cmd(cd=cd, action=action)


@dag_app.command("probe")
@plan_app.command("probe")
@observe_app.command("probe")
def dag_probe(
    baseline_id: str | None = typer.Option(None, "--baseline-id", help="Baseline checkpoint ID"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Compare current DAG state with a baseline checkpoint to detect regressions."""
    dag_probe_cmd(cd=cd, baseline_id=baseline_id)


@plan_app.command("decompose")
def plan_decompose(
    goal: str = typer.Argument(..., help="High-level goal to decompose into sub-tasks"),
    max_depth: int = typer.Option(3, "--max-depth", "-d", help="Maximum DAG depth"),
    separator: str = typer.Option(".", "--separator", "-s", help="Separator character for compound goals"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich | json | work-stream"),
) -> None:
    """Decompose a goal into a DAG of sub-tasks (plangent-style planning).

    Uses PlangentPlanner to break down the goal and display the resulting
    task DAG.  With --format=work-stream the output is rendered as WORK_STREAM
    table rows suitable for copy-paste into WORK_STREAM.md.
    """
    import json as _json

    from thegent.agents.plangent import PlangentPlanner

    planner = PlangentPlanner(separator=separator)
    plan = planner.decompose(goal, max_depth=max_depth)

    if format == "json":
        typer.echo(_json.dumps(plan.to_dict(), indent=2))
        return

    if format == "work-stream":
        rows = planner.to_work_stream_rows(plan)
        header = "| ID | Title | Source | Priority | Depends | Status |"
        sep_row = "|----|-------|--------|----------|---------|--------|"
        typer.echo(header)
        typer.echo(sep_row)
        for row in rows:
            typer.echo(
                f"| {row['id'][:8]} | {row['title'][:50]} | {row['source']} "
                f"| {row['priority']} | {row['depends'][:16]} | {row['status']} |"
            )
        return

    # Rich table output (default)
    from rich.table import Table

    table = Table(title=f"Plan: {plan.goal[:60]}", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Task", style="cyan")
    table.add_column("Depends On", style="yellow")
    table.add_column("Status", style="green")
    for idx, node in enumerate(plan.nodes, 1):
        deps = ", ".join(d[:8] for d in node.depends_on) if node.depends_on else "-"
        table.add_row(str(idx), node.task, deps, node.status)
    console.print(table)
    console.print(f"[dim]Plan ID: {plan.id} | Nodes: {len(plan.nodes)} | Created: {plan.created_at.isoformat()}[/dim]")


mcp_app = typer.Typer(
    help="MCP config and service: install thegent into Cursor/Claude Code/Codex; manage HTTP server as startup service",
)
app.add_typer(mcp_app, name="mcp")

acp_app = typer.Typer(
    help="ACP (Agent Client Protocol) adapters: expose thegent agents via ACP, spawn external ACP agents",
)
app.add_typer(acp_app, name="acp")

lsp_app = typer.Typer(help="Headless LSP server management")
app.add_typer(lsp_app, name="lsp")

jetbrains_app = typer.Typer(help="JetBrains IDE MCP integration: detect IDEs and write mcp.json config")
app.add_typer(jetbrains_app, name="jetbrains")

mgmt_app = typer.Typer(
    help="Management commands for agent self-service: ensure proxy, verify integrations",
)
app.add_typer(mgmt_app, name="mgmt")

from thegent.cli_git import app as git_app
app.add_typer(git_app, name="git", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})

@acp_app.command("server")
def acp_server_cmd() -> None:
    """Run ACP server adapter (exposes thegent agents via ACP protocol).

    This command runs an ACP server that exposes thegent agents as ACP-compatible agents.
    Use this with ACP clients like gsh or Zed.

    Example (gsh):
        # In ~/.gsh/repl.gsh:
        acp Thegent {
            command: "thegent",
            args: ["acp", "server"],
        }

    Then use in gsh REPL:
        gsh> @thegent analyze my codebase
    """
    import asyncio
    import logging

    from thegent.acp.server import main

    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())


@acp_app.command("client")
def acp_client_cmd(
    command: str = typer.Argument(..., help="ACP agent command (e.g., 'npx -y @zed-industries/claude-agent-acp')"),
    prompt: str = typer.Option("", "--prompt", "-p", help="Prompt to send to ACP agent"),
    cwd: Path | None = typer.Option(None, "--cwd", "-d", help="Working directory"),
) -> None:
    """Spawn an external ACP agent and run a prompt.

    Example:
        thegent acp client "npx -y @zed-industries/claude-agent-acp" --prompt "Analyze my code"
    """
    from thegent.acp.client import ACPClientAdapter

    cmd_parts = command.split()
    adapter = ACPClientAdapter(cmd_parts, agent_name="external-acp")

    result = adapter.run(
        prompt=prompt or "Hello",
        cwd=cwd,
        mode="default",
        timeout=3600,
    )

    console.print(f"[green]Exit code:[/green] {result.exit_code}")
    if result.stdout:
        console.print(f"[cyan]Stdout:[/cyan]\n{result.stdout}")
    if result.stderr:
        console.print(f"[yellow]Stderr:[/yellow]\n{result.stderr}")


@lsp_app.command("install")
def lsp_install(
    language: str | None = typer.Argument(None, help="Language to install (omit to install all missing)"),
    all_languages: bool = typer.Option(False, "--all", help="Install all LSP servers (even if already installed)"),
    auto_confirm: bool = typer.Option(True, "--yes/--no", help="Auto-confirm installation prompts"),
) -> None:
    """Install LSP servers (specific language or all missing)."""
    from rich.table import Table

    from thegent.lsp.auto_install import auto_install_all_lsp_servers, auto_install_lsp_server

    if language:
        console.print(f"[cyan]Installing {language} LSP server...[/cyan]")
        success = auto_install_lsp_server(language, auto_confirm)
        if success:
            console.print(f"[green]✅ {language} LSP server installed successfully[/green]")
        else:
            console.print(f"[red]❌ Failed to install {language} LSP server[/red]")
            raise typer.Exit(1)
    else:
        console.print("[cyan]Installing all missing LSP servers...[/cyan]")
        results = auto_install_all_lsp_servers(auto_confirm, skip_installed=not all_languages)

        table = Table(title="Installation Results")
        table.add_column("Language", style="cyan")
        table.add_column("Status", style="yellow")

        for lang, success in sorted(results.items()):
            status = "✅ Installed" if success else "❌ Failed"
            table.add_row(lang, status)

        console.print(table)

        failed = [lang for lang, success in results.items() if not success]
        if failed:
            console.print(f"\n[yellow]⚠️  {len(failed)} server(s) failed to install: {', '.join(failed)}[/yellow]")
        else:
            console.print("\n[green]✅ All servers installed successfully[/green]")


@lsp_app.command("start")
def lsp_start(
    language: str = typer.Argument(..., help="Language (python, typescript, rust, go, etc.)"),
    auto_install: bool | None = typer.Option(
        None, "--auto-install/--no-auto-install", help="Auto-install missing LSP servers (default: from config)"
    ),
) -> None:
    """Start headless LSP server for language (auto-installs if missing by default)."""
    from thegent.lsp.headless_manager import HeadlessLSPManager

    manager = HeadlessLSPManager()
    server = manager.ensure_server(language, auto_install=auto_install)

    if server:
        console.print(f"[green]Started LSP server: {language} (PID: {server.pid})[/green]")
    else:
        console.print(f"[red]Failed to start LSP server: {language}[/red]")
        if auto_install:
            console.print("[yellow]Auto-installation attempted. Check logs for details.[/yellow]")
        raise typer.Exit(1)


@lsp_app.command("stop")
def lsp_stop(
    language: str = typer.Argument(..., help="Language to stop"),
) -> None:
    """Stop LSP server for language."""
    from thegent.lsp.headless_manager import HeadlessLSPManager

    manager = HeadlessLSPManager()
    manager.stop_server(language)
    console.print(f"[green]Stopped LSP server: {language}[/green]")


@lsp_app.command("serena-backend")
def lsp_serena_backend() -> None:
    """Show detected Serena backend (LSP or JetBrains plugin)."""
    from thegent.lsp.serena_integration import detect_serena_backend

    backend = detect_serena_backend()
    console.print(f"[green]Serena backend:[/green] {backend}")

    if backend == "jetbrains":
        from thegent.config import ThegentSettings

        settings = ThegentSettings()
        console.print(f"[dim]JetBrains plugin port:[/dim] {settings.serena_jetbrains_port}")
    else:
        console.print("[dim]Using LSP backend (uvx serena start-mcp-server)[/dim]")


@lsp_app.command("serena-jetbrains-setup")
def lsp_serena_jetbrains_setup() -> None:
    """Auto-detect and guide setup for Serena JetBrains plugin."""
    from thegent.ide.auto_setup import auto_setup_serena_jetbrains_plugin

    result = auto_setup_serena_jetbrains_plugin()

    if result["success"]:
        console.print(f"[green]✅ {result['message']}[/green]")
        console.print(f"[dim]Backend:[/dim] {result['backend']}")
        console.print(f"[dim]Port:[/dim] {result['port']}")
    else:
        console.print(f"[yellow]⚠️ {result['message']}[/yellow]")
        console.print("")
        console.print("[bold]Setup Instructions:[/bold]")
        for instruction in result["instructions"]:
            console.print(f"  {instruction}")


@jetbrains_app.command("setup")
def jetbrains_setup(
    mcp_url: str = typer.Option(
        "http://localhost:3847/mcp",
        "--mcp-url",
        help="thegent MCP server URL to write into IDE config",
    ),
    project_root: str = typer.Option(
        "",
        "--project-root",
        help="Serena project root (optional; scopes Serena tools to this directory)",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Detect IDEs but do not write config files"
    ),
) -> None:
    """Detect JetBrains IDEs and write mcp.json with the thegent MCP server URL.

    Writes (or updates) ~/.config/JetBrains/<IDE>/mcp.json so the JetBrains
    AI plugin connects to the running thegent MCP server.

    Example:
        thegent jetbrains setup
        thegent jetbrains setup --mcp-url http://localhost:3847/mcp
        thegent jetbrains setup --dry-run
    """
    from rich.table import Table

    from thegent.integrations.jetbrains import JetBrainsIntegration

    integration = JetBrainsIntegration(
        mcp_server_url=mcp_url,
        serena_project_root=project_root,
    )
    configs = integration.detect_installed_ides()

    if not configs:
        console.print("[yellow]No JetBrains IDEs detected.[/yellow]")
        console.print("[dim]Install a JetBrains IDE to use this command.[/dim]")
        console.print("[dim]  macOS:  brew install --cask intellij-idea[/dim]")
        console.print("[dim]  Linux:  https://www.jetbrains.com/toolbox/[/dim]")
        return

    table = Table(title="JetBrains IDE MCP Setup")
    table.add_column("IDE", style="cyan")
    table.add_column("Config Dir", style="white")
    table.add_column("Status", style="yellow")

    if dry_run:
        console.print(f"[dim]Dry-run: would configure {len(configs)} IDE(s)[/dim]")
        for cfg in configs:
            table.add_row(cfg.ide_type, str(cfg.config_dir), "[dim]dry-run[/dim]")
        console.print(table)
        return

    results = integration.setup_all()

    for r in results:
        if r["success"]:
            table.add_row(r["ide_type"], r["config_dir"], "[green]✅ Written[/green]")
        else:
            table.add_row(
                r["ide_type"], r["config_dir"], f"[red]❌ {r.get('error', 'failed')}[/red]"
            )

    console.print(table)
    success_count = sum(1 for r in results if r["success"])
    console.print(f"\n[green]Configured {success_count}/{len(results)} IDE(s)[/green]")
    console.print(f"[dim]MCP server URL:[/dim] {mcp_url}")


@lsp_app.command("auto-setup")
def lsp_auto_setup(
    install_missing: bool = typer.Option(
        True, "--install-missing/--no-install-missing", help="Auto-install missing LSP servers"
    ),
    install_all: bool = typer.Option(
        False, "--install-all", help="Install all LSP servers (even if already installed)"
    ),
    auto_configure: bool = typer.Option(
        True, "--auto-configure/--no-auto-configure", help="Auto-configure IDE integrations"
    ),
) -> None:
    """Auto-setup all IDE integrations (JetBrains, Serena, Ghostty)."""
    from rich.table import Table

    from thegent.ide.auto_setup import auto_setup_all
    from thegent.lsp.auto_install import auto_install_all_lsp_servers

    console.print("[bold]Auto-Setting Up IDE Integrations[/bold]")
    console.print("")

    # Setup IDE integrations
    setup_results = auto_setup_all(auto_configure=auto_configure, auto_install=True)

    # Install LSP servers if requested
    if install_missing or install_all:
        console.print("[bold]Installing LSP Servers...[/bold]")
        install_results = auto_install_all_lsp_servers(auto_confirm=True, skip_installed=not install_all)
        setup_results["lsp_servers"] = install_results

    # Display results
    table = Table(title="Setup Status")
    table.add_column("Integration", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Details", style="white")

    # JetBrains
    jetbrains_result = setup_results["jetbrains"]
    if isinstance(jetbrains_result, dict):
        jetbrains_status = "✅ Configured" if jetbrains_result.get("success") else "❌ Not Found"
        jetbrains_details = jetbrains_result.get("message", "Install IntelliJ IDEA")
    else:
        # Backward compatibility
        jetbrains_status = "✅ Configured" if jetbrains_result else "❌ Not Found"
        jetbrains_details = "CLI access available" if jetbrains_result else "Install IntelliJ IDEA"
    table.add_row("JetBrains IDE", jetbrains_status, jetbrains_details)

    # Serena JetBrains Plugin
    serena_result = setup_results["serena_jetbrains"]
    serena_status = "✅ Configured" if serena_result.get("success") else "⚠️ Not Detected"
    serena_details = serena_result.get("message", "Plugin not running")
    if serena_result.get("backend"):
        serena_details = f"{serena_details} (Backend: {serena_result['backend']})"
    table.add_row("Serena JetBrains Plugin", serena_status, serena_details)

    # Ghostty
    ghostty_result = setup_results["ghostty"]
    ghostty_status = "✅ Configured" if ghostty_result["success"] else "⚠️ Not Configured"
    ghostty_details = ghostty_result.get("message", "Unknown")
    table.add_row("Ghostty Shell Integration", ghostty_status, ghostty_details)

    # LSP Servers
    if "lsp_servers" in setup_results:
        installed_count = sum(1 for v in setup_results["lsp_servers"].values() if v)
        total_count = len(setup_results["lsp_servers"])
        lsp_status = f"✅ {installed_count}/{total_count} Installed"
        table.add_row("LSP Servers", lsp_status, f"{installed_count} servers available")

    console.print(table)
    console.print("")
    console.print("[green]Auto-setup complete![/green]")


@lsp_app.command("list")
def lsp_list(
    all_servers: bool = typer.Option(False, "--all", "-a", help="List all available servers (not just running)"),
) -> None:
    """List LSP servers (running or all available)."""
    import time

    from rich.table import Table

    from thegent.lsp.commands import list_all_lsp_servers
    from thegent.lsp.headless_manager import HeadlessLSPManager

    if all_servers:
        # List all available servers with installation status
        all_servers_info = list_all_lsp_servers()
        manager = HeadlessLSPManager()
        running_servers = manager.list_servers()

        table = Table(title="All Available LSP Servers")
        table.add_column("Language", style="cyan")
        table.add_column("Command", style="white")
        table.add_column("Installed", style="yellow")
        table.add_column("Running", style="green")
        table.add_column("Install Command", style="dim")

        for lang, info in sorted(all_servers_info.items()):
            installed = "✅ Yes" if info["installed"] else "❌ No"
            running = "✅ Yes" if lang in running_servers and running_servers[lang]["running"] else "❌ No"
            install_cmd = info["install"][:50] + "..." if len(info["install"]) > 50 else info["install"]
            table.add_row(lang, info["command"], installed, running, install_cmd)

        console.print(table)
    else:
        # List only running servers
        manager = HeadlessLSPManager()
        servers = manager.list_servers()

        if not servers:
            console.print("[yellow]No LSP servers currently running.[/yellow]")
            console.print("[dim]Use 'thegent lsp start <language>' to start a server[/dim]")
            console.print("[dim]Use 'thegent lsp list --all' to see all available servers[/dim]")
            return

        table = Table(title="Running LSP Servers")
        table.add_column("Language", style="cyan")
        table.add_column("PID", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Uptime", style="white")

        for lang, info in servers.items():
            status = "✅ Running" if info["running"] else "❌ Stopped"
            uptime = f"{int(time.time() - info['started_at'])}s" if info["started_at"] else "N/A"
            table.add_row(lang, str(info["pid"]), status, uptime)

        console.print(table)


@lsp_app.command("format")
def lsp_format(
    files: list[Path] = typer.Argument(..., help="Files to format"),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project root"),
) -> None:
    """Format files using JetBrains formatter."""
    from thegent.lsp.jetbrains_cli import JetBrainsCLI

    cli = JetBrainsCLI()
    result = cli.format(files, project)

    if result["success"]:
        console.print("[green]Files formatted successfully[/green]")
    else:
        console.print(f"[red]Format failed: {result.get('error', result.get('stderr'))}[/red]")
        raise typer.Exit(1)


@lsp_app.command("inspect")
def lsp_inspect(
    project: Path = typer.Argument(..., help="Project root"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Inspection profile"),
) -> None:
    """Run code inspections using JetBrains."""
    from thegent.lsp.jetbrains_cli import JetBrainsCLI

    cli = JetBrainsCLI()
    result = cli.inspect(project, profile)

    if result["success"]:
        console.print(result["stdout"])
    else:
        console.print(f"[red]Inspection failed: {result.get('error', result.get('stderr'))}[/red]")
        raise typer.Exit(1)


@mgmt_app.command("ensure-proxy")
def mgmt_ensure_proxy(
    timeout: float = typer.Option(30.0, "--timeout", "-t", help="Seconds to wait for proxy readiness"),
) -> None:
    """Ensure MCP + proxy are running. Starts via process-compose if needed. Agent self-service."""
    from rich.console import Console

    from thegent.mgmt_manage import ensure_proxy

    console = Console()
    ok, msg = ensure_proxy(timeout_sec=timeout)
    if ok:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)


@mgmt_app.command("verify-codex-cliproxy")
def mgmt_verify_codex_cliproxy(
    model: str = typer.Option("minimax-m2.5", "--model", "-m", help="Model to test"),
    prompt: str = typer.Option("echo hello", "--prompt", "-p", help="Codex prompt"),
    timeout: float = typer.Option(90.0, "--timeout", "-t", help="Codex exec timeout (seconds)"),
) -> None:
    """Verify Codex works with CLIProxy adapter. Agent self-service: no user intervention needed."""
    from rich.console import Console

    from thegent.mgmt_manage import verify_codex_cliproxy

    console = Console()
    ok, msg = verify_codex_cliproxy(model=model, prompt=prompt, timeout_sec=timeout)
    if ok:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)


@mcp_app.command("install")
def mcp_install(
    client: str = typer.Argument(
        ...,
        help="Client: cursor, claude-code, codex, claude-desktop, droid, or all",
    ),
    url: str | None = typer.Option(None, "--url", "-u", help="MCP URL (default: http://127.0.0.1:3847/mcp)"),
    workspace: Path | None = typer.Option(
        None, "--workspace", "-d", help="Workspace dir for cursor (writes .cursor/mcp.json)"
    ),
    replace_playwright: bool = typer.Option(
        True,
        "--replace-playwright/--keep-playwright",
        help="Remove playwright from MCP config (default); thegent bundles browser tools when THGENT_MCP_MOUNT_PLAYWRIGHT=1",
    ),
    uni_mount: bool = typer.Option(
        False,
        "--uni-mount/--merge",
        help="Replace ALL MCP entries with thegent only (fixes codex_apps/playwright handshake errors)",
    ),
    http: bool = typer.Option(
        False,
        "--http/--stdio",
        help="Force HTTP transport (default: stdio for claude-code, http for others)",
    ),
) -> None:
    """Add thegent to MCP config for Cursor, Claude Code, Codex, or Claude Desktop. Bundles browser tools (playwright) by default."""
    from thegent.config import ThegentSettings
    from thegent.mcp_manage import _get_mcp_url, install_to_client, remove_playwright_from_client

    settings = ThegentSettings()
    mcp_url = url or _get_mcp_url(settings)
    clients = ["cursor", "claude-code", "codex", "claude-desktop", "droid"] if client == "all" else [client]
    from rich.console import Console

    console = Console()
    for c in clients:
        ws = workspace if c == "cursor" else None
        ok, msg = install_to_client(c, mcp_url, workspace=ws, replace_all=uni_mount, force_http=http)
        if ok:
            console.print(f"[green]{msg}[/green]")
        else:
            console.print(f"[red]{c}: {msg}[/red]")
        if not uni_mount and replace_playwright and ok and c != "droid":
            rok, rmsg = remove_playwright_from_client(c, workspace=ws)
            if rok:
                console.print(f"[dim]{rmsg}[/dim]")
            else:
                console.print(f"[yellow]{rmsg}[/yellow]")


@mcp_app.command("introspect")
def mcp_introspect(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output JSON"),
    optimize: bool = typer.Option(False, "--optimize", "-o", help="Include optimization strategies"),
) -> None:
    """Introspect agent processes (Python, node, droid, claude, codex).
    Checks parent chain for true orphans; does NOT assume leak. Use before prune."""
    from thegent.infra import run_subprocess_optimized

    script = Path(__file__).resolve().parents[2] / "scripts" / "agent-process-introspect.py"
    if not script.exists():
        from rich.console import Console

        Console().print(f"[red]Introspect script not found: {script}[/red]")
        raise typer.Exit(1)
    args = [str(Path(sys.executable)), str(script)]
    if json_output:
        args.append("--json")
    if optimize:
        args.append("--optimize")
    run_subprocess_optimized(args, check=False)


@mcp_app.command("spotlight-exclude")
def mcp_spotlight_exclude(
    force: bool = typer.Option(False, "--force", help="Force command even if not on macOS"),
) -> None:
    """Exclude heavy development and thegent metadata directories from Spotlight indexing (macOS).
    Helps reduce mds_stores memory usage and CPU spikes during high-IO agent runs."""
    import subprocess
    import sys

    from thegent.infra import run_subprocess_optimized

    if sys.platform != "darwin" and not force:
        from rich.console import Console

        Console().print("[yellow]Spotlight exclusion only applies to macOS.[/yellow]")
        return

    from thegent.config import ThegentSettings

    settings = ThegentSettings()

    # Target directories
    targets = [
        settings.session_dir,
        settings.cache_dir,
        Path.home() / ".thegent",
        Path.home() / ".claude",
        Path.home() / ".cursor",
        Path.cwd() / "node_modules",
        Path.cwd() / ".venv",
        Path.cwd() / "venv",
        Path.cwd() / "dist",
        Path.cwd() / "build",
        Path.cwd() / ".claude",
        Path.cwd() / ".thegent",
    ]

    from rich.console import Console

    console = Console()
    console.print("[bold blue]Excluding heavy directories from Spotlight...[/bold blue]")

    for t in targets:
        if t.exists():
            console.print(f"  [dim]Excluding {t}[/dim]")
            run_subprocess_optimized(["mdutil", "-i", "off", str(t)], capture_output=True, check=False)
            # Create .noindex file as a fallback/reinforcement
            if t.is_dir():
                noindex = t / ".noindex"
                with contextlib.suppress(Exception):
                    noindex.touch(exist_ok=True)

    console.print("[green]Spotlight exclusion complete. Run 'thegent ps --all' to monitor memory recovery.[/green]")


@mcp_app.command("prune")
def mcp_prune(
    force: bool = typer.Option(False, "--force", "-f", help="Force kill without confirmation"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be killed"),
    parent_pid: int | None = typer.Option(None, "--parent-pid", "-p", help="Target sub-processes of this parent PID"),
) -> None:
    """Kill redundant agent-related Node.js and shell processes (LSPs, MCP servers, leaked shells).
    Use this when memory usage is high (>10GB) and many redundant processes are detected.
    For automatic pruning on Stop, set THGENT_AUTO_PRUNE=1."""
    import os
    import signal
    import subprocess
    import time
    from typing import Any

    from rich.console import Console
    from rich.table import Table

    from thegent.config import ThegentSettings
    from thegent.infra import run_subprocess_optimized
    from thegent.prune_utils import is_orphan_by_ppid

    console = Console()
    settings = ThegentSettings()

    # Patterns for redundant processes (LSPs, MCPs, and leaked shells)
    patterns = [
        "pyright-langserver",
        "typescript-language-server",
        "tsserver.js",
        "@playwright/mcp",
        "context7-mcp",
        "cc-status",
        "octocode-mcp",
        "next-devtools-mcp",
        "sequential-thinking",
        "bash",
        "zsh",
        "sh",
        "node",
        "npm",
        "bun",
        "deno",
    ]

    try:
        from thegent.infra import run_subprocess_optimized

        res = run_subprocess_optimized(
            ["ps", "-eo", "pid,ppid,rss,command"],
            capture_output=True,
            check=False,
        )
        stdout_text = (
            res.stdout
            if isinstance(res.stdout, str)
            else (res.stdout.decode("utf-8", errors="replace") if res.stdout else "")
        )
        lines = stdout_text.strip().splitlines()
        has_rss = True
    except Exception:
        try:
            res = run_subprocess_optimized(
                ["ps", "-eo", "pid,ppid,command"],
                capture_output=True,
                check=False,
            )
            stdout_text = (
                res.stdout
                if isinstance(res.stdout, str)
                else (res.stdout.decode("utf-8", errors="replace") if res.stdout else "")
            )
            lines = stdout_text.strip().splitlines()
            has_rss = False
        except Exception as e:
            console.print(f"[red]Failed to list processes: {e}[/red]")
            return

    # Build parent_map and cmd_map for orphan-by-ppid
    parent_map: dict[int, int] = {}
    cmd_map: dict[int, str] = {}
    candidates: list[dict[str, Any]] = []

    for line in lines[1:]:
        if has_rss:
            parts = line.split(None, 3)
            if len(parts) < 4:
                continue
            pid_s, ppid_s, rss_s, cmd = parts[0], parts[1], parts[2], parts[3]
            try:
                rss_kb = int(rss_s)
            except ValueError:
                rss_kb = 0
        else:
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            pid_s, ppid_s, cmd = parts[0], parts[1], parts[2]
            rss_kb = 0
        try:
            pid_i = int(pid_s)
            ppid_i = int(ppid_s)
        except ValueError:
            continue
        parent_map[pid_i] = ppid_i
        cmd_map[pid_i] = cmd

        cmd_lower = cmd.lower()
        # Never prune cursor-agent (node process that IS the Cursor agent) or thegent itself
        if "cursor-agent" in cmd_lower or "cursor agent" in cmd_lower or "thegent" in cmd_lower:
            continue
        
        # If we have a specific parent PID, only include its children
        if parent_pid:
            if ppid_i == parent_pid:
                candidates.append({"pid": pid_i, "ppid": ppid_i, "cmd": cmd, "rss_kb": rss_kb})
            continue

        match_categories = ("node", "npm", "bun", "deno", "cc-status", "bash", "zsh", "sh")
        if any(x in cmd_lower for x in match_categories):
            for p in patterns:
                if p in cmd:
                    candidates.append({"pid": pid_i, "ppid": ppid_i, "cmd": cmd, "rss_kb": rss_kb})
                    break

    # Filter to true orphans when orphan-by-ppid enabled, unless targeting specific parent
    if parent_pid:
        to_kill = candidates
    elif settings.prune_orphan_by_ppid:
        to_kill = [c for c in candidates if is_orphan_by_ppid(c["pid"], parent_map, cmd_map)]
    else:
        to_kill = candidates

    # RSS-aware sort: kill highest first by default
    sort_by = (settings.prune_sort_by or "rss").lower()
    sort_order = (settings.prune_sort_order or "desc").lower()
    if sort_by == "rss" and to_kill:
        reverse = sort_order == "desc"
        to_kill = sorted(to_kill, key=lambda c: c.get("rss_kb", 0), reverse=reverse)

    if not to_kill:
        if settings.prune_orphan_by_ppid and len(candidates) > 0:
            console.print(
                f"[green]No orphan processes (all {len(candidates)} candidates have living Cursor/Claude/Codex parents).[/green]"
            )
        else:
            console.print("[green]No redundant agent processes found.[/green]")
        return

    if settings.prune_orphan_by_ppid and len(candidates) > len(to_kill):
        console.print(
            f"[dim]Orphan-by-ppid: {len(to_kill)} orphans of {len(candidates)} candidates (kept {len(candidates) - len(to_kill)} with living parents)[/dim]"
        )

    # Zombie count (processes with state Z; parent should reap)
    zombie_count = 0
    try:
        zres = run_subprocess_optimized(["ps", "-eo", "stat"], capture_output=True, check=False)
        if zres.returncode == 0 and zres.stdout:
            stdout_text = zres.stdout if isinstance(zres.stdout, str) else zres.stdout.decode("utf-8", errors="replace")
            zombie_count = sum(1 for line in stdout_text.splitlines()[1:] if "Z" in line.split()[0])
    except Exception:
        pass
    if zombie_count > 0:
        console.print(f"[yellow]Zombie processes: {zombie_count} (parent should reap; not pruned)[/yellow]")

    t = Table(title="Orphan Processes to Prune" if settings.prune_orphan_by_ppid else "Redundant Processes Detected")
    t.add_column("PID")
    if any(c.get("rss_kb", 0) > 0 for c in to_kill):
        t.add_column("RSS (KB)")
    t.add_column("Command")
    for item in to_kill:
        row: list[str] = [str(item["pid"])]
        if any(c.get("rss_kb", 0) > 0 for c in to_kill):
            row.append(str(item.get("rss_kb", 0)))
        row.append(item["cmd"][:80] + ("..." if len(item["cmd"]) > 80 else ""))
        t.add_row(*row)

    console.print(t)

    if dry_run:
        console.print(f"[yellow]Dry run: would kill {len(to_kill)} processes.[/yellow]")
        return

    if not force:
        confirm = typer.confirm(f"Kill these {len(to_kill)} processes?")
        if not confirm:
            return

    killed_count = 0
    grace_period = settings.prune_grace_period
    for item in to_kill:
        pid = item["pid"]
        try:
            os.kill(pid, signal.SIGTERM)
            killed_count += 1
            if grace_period > 0:
                time.sleep(grace_period)
                try:
                    os.kill(pid, 0)  # Check if still alive (raises if not)
                    os.kill(pid, signal.SIGKILL)
                except (ProcessLookupError, OSError):
                    pass  # Process already exited
        except ProcessLookupError:
            pass  # Process already gone
        except Exception:
            try:
                os.kill(pid, signal.SIGKILL)
                killed_count += 1
            except Exception:
                pass

    console.print(f"[green]Successfully pruned {killed_count} processes.[/green]")
    console.print("[dim]Note: Active agents may restart their LSPs on the next interaction.[/dim]")


@mcp_app.command("smart-prune")
def mcp_smart_prune(
    force: bool = typer.Option(False, "--force", "-f", help="Prune even if docs aren't written"),
    no_reprompt: bool = typer.Option(False, "--no-reprompt", help="Do not reprompt if docs missing"),
) -> None:
    """Intelligently prune idle sessions and reprompt for docs."""
    from rich.console import Console

    from thegent.orchestration.smart_prune import smart_prune_main

    console = Console()

    console.print("[yellow]Running Smart Pruning cycle...[/yellow]")
    results = smart_prune_main(force=force, reprompt=not no_reprompt)

    console.print(f"Scanned: {results['scanned']}")
    console.print(f"Pruned: [green]{results['pruned']}[/green]")
    console.print(f"Reprompted: [blue]{results['reprompted']}[/blue]")
    console.print(f"Kept: {results['kept']}")

    for detail in results["details"]:
        console.print(f" - {detail}")


@mcp_app.command("prune-periodic")
def mcp_prune_periodic(
    action: str = typer.Argument(
        ...,
        help="Action: install, start, stop, status, uninstall",
    ),
) -> None:
    """Install periodic prune daemon (launchd on macOS, systemd on Linux).
    Runs thegent mcp prune --force every 15 min. Catches orphans when Stop doesn't fire (headless, Codex)."""
    from rich.console import Console

    from thegent.mcp_manage import (
        prune_periodic_install,
        prune_periodic_start,
        prune_periodic_status,
        prune_periodic_stop,
        prune_periodic_uninstall,
    )

    console = Console()
    if action == "install":
        ok, msg = prune_periodic_install()
    elif action == "start":
        ok, msg = prune_periodic_start()
    elif action == "stop":
        ok, msg = prune_periodic_stop()
    elif action == "status":
        ok, msg = prune_periodic_status()
    elif action == "uninstall":
        ok, msg = prune_periodic_uninstall()
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        raise typer.Exit(1)
    console.print(msg)
    if not ok and action in ("install", "start", "stop", "uninstall"):
        raise typer.Exit(1)


@mcp_app.command("fix")
def mcp_fix(
    client: str = typer.Argument(
        ...,
        help="Client: cursor, claude-code, codex, claude-desktop, or all",
    ),
    workspace: Path | None = typer.Option(None, "--workspace", "-d", help="Workspace dir for cursor"),
) -> None:
    """Remove failing MCP servers (codex_apps, playwright) that cause 'MCP startup incomplete'.
    Use thegent's bundled mounts instead. Run 'thegent mcp up' before using."""
    from thegent.mcp_manage import FAILING_MCP_SERVERS, remove_servers_from_client

    clients = ["cursor", "claude-code", "codex", "claude-desktop"] if client == "all" else [client]
    from rich.console import Console

    console = Console()
    for c in clients:
        ws = workspace if c == "cursor" else None
        ok, msg = remove_servers_from_client(c, list(FAILING_MCP_SERVERS), workspace=ws)
        if ok:
            if "Removed" in msg or "No matching" in msg:
                console.print(f"[green]{c}: {msg}[/green]")
            else:
                console.print(f"[dim]{c}: {msg}[/dim]")
        else:
            console.print(f"[red]{c}: {msg}[/red]")
    console.print("[dim]Ensure thegent MCP is running: thegent mcp up[/dim]")


@mcp_app.command("migrate-unimount")
def mcp_migrate_unimount(
    client: str = typer.Argument(
        ...,
        help="Client: cursor, claude-code, codex, claude-desktop, droid, or all",
    ),
    url: str | None = typer.Option(None, "--url", "-u", help="MCP URL (default: http://127.0.0.1:3847/mcp)"),
    workspace: Path | None = typer.Option(
        None, "--workspace", "-d", help="Workspace dir for cursor (writes .cursor/mcp.json)"
    ),
) -> None:
    """Migrate to uni-mount: replace ALL MCP entries with thegent only. Fixes codex_apps/playwright handshake errors.
    Thegent mounts playwright, serena, octocode — one URL, all tools. Run 'thegent mcp up' before using."""
    from thegent.config import ThegentSettings
    from thegent.mcp_manage import _get_mcp_url, migrate_to_unimount

    settings = ThegentSettings()
    mcp_url = url or _get_mcp_url(settings)
    clients = ["cursor", "claude-code", "codex", "claude-desktop", "droid"] if client == "all" else [client]
    from rich.console import Console

    console = Console()
    for c in clients:
        ws = workspace if c == "cursor" else None
        ok, msg = migrate_to_unimount(c, mcp_url, workspace=ws)
        if ok:
            console.print(f"[green]{msg}[/green]")
        else:
            console.print(f"[red]{c}: {msg}[/red]")
    console.print("[dim]Ensure thegent MCP is running: thegent mcp up[/dim]")


@app.command(
    "install-shims",
    help="MTSP-10: Install optimized accelerators (shims) for common tools.",
)
def install_shims_cmd(
    bin_dir: Path = typer.Option(Path.home() / ".local" / "bin", "--bin-dir", help="Directory for shims"),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite"),
    all_tools: bool = typer.Option(True, "--all", help="Install accelerators for git, grep, fd, jq, etc."),
    system: bool = typer.Option(
        False, "--system", help="Install to system path (requires admin). Uses --prefix if set."
    ),
    prefix: Path | None = typer.Option(
        None, "--prefix", help="Install prefix (e.g. /usr/local). Implies --system for git."
    ),
    uninstall: bool = typer.Option(False, "--uninstall", help="Restore original git when used with --system."),
) -> None:
    """MTSP-10: Install optimized accelerators (shims) for common tools.
    Accelerates git (multi-tenant), grep (rg), find (fd), jq (jaq).
    Use --system to install git wrapper to /usr/local/bin for nix/direnv compatibility."""
    from rich.console import Console

    console = Console()

    if uninstall and (system or prefix):
        _uninstall_system_git(prefix or Path("/usr/local"), console)
        return

    if system or prefix is not None:
        _install_system_shims(prefix or Path("/usr/local"), force, console)
        return

    _install_agent_accelerators(bin_dir=bin_dir, force=force)

    if all_tools:
        _install_tool_accelerators(bin_dir, force)
        _install_role_accelerators(bin_dir, force)
        console.print(f"[green]Tool accelerators installed to {bin_dir}[/green]")
        console.print(
            "[dim]Accelerators: git, grep, find, jq, wc, summarize, research, review, explain, fix, code[/dim]"
        )
        console.print(f"[yellow]Action Required: Ensure {bin_dir} is early in your PATH![/yellow]")


def _ensure_write_access_or_sudo(bin_dir: Path, force: bool, prefix: Path, uninstall: bool) -> None:
    """If no write access and not root, re-exec with sudo."""
    import os

    from thegent.infra import run_subprocess_optimized

    euid = getattr(os, "geteuid", lambda: 0)()
    if euid == 0:
        return  # Already root (or Windows, where geteuid doesn't exist)
    if os.access(bin_dir, os.W_OK):
        return  # Have write access

    if platform.system() == "Windows":
        raise typer.Exit(1)  # No sudo on Windows; caller will show error

    # Re-exec with sudo (use same Python for robustness with venv/python -m)
    cmd = ["sudo", "-E", sys.executable, "-m", "thegent", "install-shims"]
    if uninstall:
        cmd.append("--uninstall")
    if prefix != Path("/usr/local"):
        cmd.extend(["--prefix", str(prefix)])
    elif not uninstall:
        cmd.append("--system")
    if force:
        cmd.append("--force")

    run_subprocess_optimized(cmd, check=True)
    raise typer.Exit(0)


def _install_system_shims(prefix: Path, force: bool, console: "Console") -> None:
    """Install system wrappers for multiple tools to prefix/bin for nix/direnv compatibility.
    Includes: git (multi-tenant), grep (rg), find (fd), jq (jaq), and thegent-shim.
    Requires write access (admin)."""
    import os
    import shutil

    bin_dir = prefix / "bin"
    if not bin_dir.exists():
        console.print(f"[red]Directory {bin_dir} does not exist. Create it or use a valid --prefix.[/red]")
        raise typer.Exit(1)

    # Check write access; re-exec with sudo if needed
    _ensure_write_access_or_sudo(bin_dir, force, prefix, uninstall=False)

    safe_path = "/usr/bin:/opt/homebrew/bin:/bin:/usr/sbin:/sbin"

    # 1. Git Wrapper
    git_path = bin_dir / "git"
    git_bin_path = bin_dir / "git.bin"
    real_git = shutil.which("git", path=safe_path)

    if real_git:
        wrapper_real_git = str(git_bin_path)
        should_install_git = True
        if git_bin_path.exists():
            if not force:
                console.print("[yellow]thegent git wrapper already installed. Skipping (use --force).[/yellow]")
                should_install_git = False
        elif git_path.exists():
            try:
                content = git_path.read_text()
                if "thegent" in content[:500]:
                    if not force:
                        should_install_git = False
                    elif not git_bin_path.exists():
                        shutil.copy2(real_git, git_bin_path)
                        git_bin_path.chmod(0o755)
                else:
                    shutil.copy2(git_path, git_bin_path)
                    git_bin_path.chmod(0o755)
            except OSError as e:
                console.print(f"[red]Failed to backup existing git: {e}[/red]")
                should_install_git = False
        else:
            try:
                shutil.copy2(real_git, git_bin_path)
                git_bin_path.chmod(0o755)
            except OSError as e:
                console.print(f"[red]Failed to copy git to {git_bin_path}: {e}[/red]")
                should_install_git = False

        if should_install_git:
            wrapper = f'''#!/usr/bin/env bash
set -euo pipefail
# thegent git accelerator: Multi-tenant lock coordination (system install)
export THEGENT_GIT_BIN="{wrapper_real_git}"
PROJECT_DIR="$("{wrapper_real_git}" rev-parse --show-toplevel 2>/dev/null || pwd)"
HOOKS_LIB="$(dirname "$(which thegent 2>/dev/null)")/../hooks/lib/common.sh"
if [[ -f "$HOOKS_LIB" ]]; then
    export PROJECT_DIR
    source "$HOOKS_LIB" 2>/dev/null || true
fi
if [[ "$(type -t git)" == "function" ]]; then
    git "$@"
else
    exec "{wrapper_real_git}" "$@"
fi
'''
            git_path.write_text(wrapper)
            git_path.chmod(0o755)
            console.print(f"[green]✓ Git wrapper installed to {git_path}[/green]")

    # 2. Grep (rg) Shim
    grep_path = bin_dir / "grep"
    if force or not grep_path.exists():
        grep_path.write_text("""#!/usr/bin/env bash
if command -v rg &>/dev/null; then
    exec rg --no-config "$@"
else
    exec /usr/bin/grep "$@"
fi
""")
        grep_path.chmod(0o755)
        console.print(f"[green]✓ Grep (rg) shim installed to {grep_path}[/green]")

    # 3. Find (fd) Shim
    find_path = bin_dir / "find"
    if force or not find_path.exists():
        find_path.write_text("""#!/usr/bin/env bash
if command -v fd &>/dev/null; then
    exec fd "$@"
else
    exec /usr/bin/find "$@"
fi
""")
        find_path.chmod(0o755)
        console.print(f"[green]✓ Find (fd) shim installed to {find_path}[/green]")

    # 4. JQ (jaq) Shim
    jq_path = bin_dir / "jq"
    if force or not jq_path.exists():
        jq_path.write_text("""#!/usr/bin/env bash
if command -v jaq &>/dev/null; then
    exec jaq "$@"
else
    exec /usr/bin/jq "$@"
fi
""")
        jq_path.chmod(0o755)
        console.print(f"[green]✓ JQ (jaq) shim installed to {jq_path}[/green]")

    # 5. thegent-shim (Agent Shim)
    shim_path = bin_dir / "thegent-shim"
    if force or not shim_path.exists():
        shim_path.write_text("""#!/usr/bin/env bash
# thegent-shim: Multi-tenant agent execution entry point
exec thegent "$@"
""")
        shim_path.chmod(0o755)
        console.print(f"[green]✓ Agent shim installed to {shim_path}[/green]")

    console.print(f"[bold green]System shims installed successfully to {bin_dir}.[/bold green]")
    console.print("[dim]Ensure this directory is early in your PATH for nix/direnv support.[/dim]")


def _uninstall_system_git(prefix: Path, console: "Console", force: bool = False) -> None:
    """Restore original git from git.bin."""
    import os
    import shutil

    bin_dir = prefix / "bin"
    git_path = bin_dir / "git"
    git_bin_path = bin_dir / "git.bin"

    if not bin_dir.exists():
        console.print(f"[yellow]Directory {bin_dir} does not exist.[/yellow]")
        return

    # Check write access; re-exec with sudo if needed
    _ensure_write_access_or_sudo(bin_dir, force, prefix, uninstall=True)

    if not git_bin_path.exists():
        console.print(f"[yellow]No git.bin found at {git_bin_path}. Nothing to restore.[/yellow]")
        return

    try:
        shutil.copy2(git_bin_path, git_path)
        git_path.chmod(0o755)
        git_bin_path.unlink()
        console.print(f"[green]Restored original git at {git_path}[/green]")
    except OSError as e:
        console.print(f"[red]Failed to restore: {e}[/red]")
        raise typer.Exit(1)


def _get_thegent_root() -> Path:
    """Return thegent root (has hooks/, skills/). Works for dev and installed package."""
    # Installed: hooks/skills are force-included at thegent/hooks, thegent/skills
    try:
        import thegent

        pkg = Path(thegent.__file__).resolve().parent
        if (pkg / "hooks").exists() or (pkg / "skills").exists():
            return pkg
    except Exception:
        pass
    # Dev: main.py is at src/thegent/main.py -> project root is parent.parent.parent
    return Path(__file__).resolve().parent.parent.parent


def _install_agent_accelerators(bin_dir: Path, force: bool) -> None:
    """MTSP-10: Install optimized accelerators (shims) for common agent types (clode, roid, dex).
    Phase 2: Use Rust shims if available, otherwise fallback to legacy links."""
    # Try to find thegent-shims Rust binary
    thegent_shims_bin = None
    thegent_root = _get_thegent_root()
    potential_bins = [
        thegent_root / "crates" / "target" / "release" / "thegent-shims",
        thegent_root / "target" / "release" / "thegent-shims",
        Path.home() / ".local" / "bin" / "thegent-shims",
    ]
    for p in potential_bins:
        if p.exists() and os.access(p, os.X_OK):
            thegent_shims_bin = p
            break

    if thegent_shims_bin:
        agents = ["clode", "roid", "dex", "codex", "copilot", "claude", "cursor"]
        for agent in agents:
            shim = bin_dir / agent
            if force or not shim.exists():
                shim.write_text(f"""#!/usr/bin/env bash
# thegent {agent} accelerator: Rust shim
exec "{thegent_shims_bin}" agent {agent} "$@"
""")
                shim.chmod(0o755)
        return

    from thegent.clode_main import install_links as clode_install_links
    from thegent.dex_main import install_links as dex_install_links
    from thegent.roid_main import install_links as roid_install_links

    clode_install_links(bin_dir=bin_dir, force=force)
    roid_install_links(bin_dir=bin_dir, force=force)
    dex_install_links(bin_dir=bin_dir, force=force)

    # Codex Multi-Harness Accelerator (WP-Y15)
    # This shim routes to either dex (Codex CLI) or clode (Claude Code)
    codex_shim = bin_dir / "codex"
    if force or not codex_shim.exists():
        codex_shim.write_text("""#!/usr/bin/env sh
set -e
# thegent codex accelerator: route to dex or clode
# (avoids "git: 'codex' is not a git command" by direct exec)
if command -v codex >/dev/null 2>&1; then
  HARNESS="dex"
else
  HARNESS="clode"
fi
# Content check parity: dex|clode
export THGENT_HARNESS="$HARNESS"
exec thegent "$HARNESS" "$@"
""")
        codex_shim.chmod(0o755)


def _install_role_accelerators(bin_dir: Path, force: bool) -> None:
    """Install shims for new task roles."""
    from thegent.orchestration.tasks import TaskRole

    for role in TaskRole:
        shim = bin_dir / role.value
        if force or not shim.exists():
            shim.write_text(f"""#!/usr/bin/env bash
# thegent role accelerator: {role.value}
# Generated by thegent install-shims --all
exec thegent {role.value} "$@"
""")
            shim.chmod(0o755)


def _install_tool_accelerators(bin_dir: Path, force: bool) -> None:
    """Write accelerator shims to bin_dir.
    Phase 2: Use Rust shims if available, otherwise fallback to bash shims."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    safe_bin_path = "/usr/bin:/opt/homebrew/bin:/bin:/usr/sbin:/sbin"

    # Try to find thegent-shims Rust binary
    thegent_shims_bin = None
    thegent_root = _get_thegent_root()
    # If in dev mode, it might be in crates/target/release/
    potential_bins = [
        thegent_root / "crates" / "target" / "release" / "thegent-shims",
        thegent_root / "target" / "release" / "thegent-shims",
        Path.home() / ".local" / "bin" / "thegent-shims",
    ]
    for p in potential_bins:
        if p.exists() and os.access(p, os.X_OK):
            thegent_shims_bin = p
            break

    if thegent_shims_bin:
        # Phase 2: Rust Shims
        tools = ["git", "grep", "find", "jq", "pgrep", "wc", "date", "tr"]
        for tool in tools:
            shim = bin_dir / tool
            if force or not shim.exists():
                # We create a symlink to thegent-shims if possible,
                # but symlinking 'git' to 'thegent-shims' only works if thegent-shims
                # knows it's being called as 'git'. The current thegent-shims
                # uses subcommands. So we create a small bash wrapper that calls
                # thegent-shims <tool>
                shim.write_text(f"""#!/usr/bin/env bash
# thegent {tool} accelerator: Rust shim
exec "{thegent_shims_bin}" {tool} "$@"
""")
                shim.chmod(0o755)
        return

    # Fallback: Legacy Bash Shims
    # Git Accelerator (MTSP-09/10)
    git_shim = bin_dir / "git"
    if force or not git_shim.exists():
        git_shim.write_text(f"""#!/usr/bin/env bash
set -euo pipefail
# thegent git accelerator: Multi-tenant lock coordination + caching
# Generated by thegent install-shims --all
THEGENT_TOOL_BIN_PATH="{safe_bin_path}"
resolve_real_binary() {{
  PATH="$THEGENT_TOOL_BIN_PATH" command -v "$1"
}}
REAL_GIT="$(resolve_real_binary git || true)"
if [[ -z "$REAL_GIT" ]]; then
  echo "thegent git shim: failed to resolve real git executable" >&2
  exit 127
fi
export THEGENT_GIT_BIN="$REAL_GIT"
PROJECT_DIR="$( "$REAL_GIT" rev-parse --show-toplevel 2>/dev/null || pwd )"
HOOKS_LIB="$(dirname "$(which thegent)")/../hooks/lib/common.sh"
if [[ -f "$HOOKS_LIB" ]]; then
    export PROJECT_DIR
    source "$HOOKS_LIB" 2>/dev/null || true
fi

# Use the git function defined in common.sh if available
if [[ "$(type -t git)" == "function" ]]; then
    git "$@"
else
    exec "$REAL_GIT" "$@"
fi
""")
        git_shim.chmod(0o755)

    # Grep -> rg
    grep_shim = bin_dir / "grep"
    if force or not grep_shim.exists():
        grep_shim.write_text(f"""#!/usr/bin/env bash
THEGENT_TOOL_BIN_PATH="{safe_bin_path}"
resolve_real_binary() {{
  PATH="$THEGENT_TOOL_BIN_PATH" command -v "$1"
}}
if command -v rg &>/dev/null; then
    exec rg --no-config "$@"
else
    REAL_GREP="$(resolve_real_binary grep || true)"
    if [[ -z "$REAL_GREP" ]]; then
        echo "thegent grep shim: failed to resolve real grep executable" >&2
        exit 127
    fi
    exec "$REAL_GREP" "$@"
fi
""")
        grep_shim.chmod(0o755)

    # find -> fd
    find_shim = bin_dir / "find"
    if force or not find_shim.exists():
        find_shim.write_text(f"""#!/usr/bin/env bash
THEGENT_TOOL_BIN_PATH="{safe_bin_path}"
resolve_real_binary() {{
  PATH="$THEGENT_TOOL_BIN_PATH" command -v "$1"
}}
if command -v fd &>/dev/null; then
    exec fd "$@"
else
    REAL_FIND="$(resolve_real_binary find || true)"
    if [[ -z "$REAL_FIND" ]]; then
        echo "thegent find shim: failed to resolve real find executable" >&2
        exit 127
    fi
    exec "$REAL_FIND" "$@"
fi
""")
        find_shim.chmod(0o755)

    # jq -> jaq
    jq_shim = bin_dir / "jq"
    if force or not jq_shim.exists():
        jq_shim.write_text(f"""#!/usr/bin/env bash
THEGENT_TOOL_BIN_PATH="{safe_bin_path}"
resolve_real_binary() {{
  PATH="$THEGENT_TOOL_BIN_PATH" command -v "$1"
}}
if command -v jaq &>/dev/null; then
    exec jaq "$@"
else
    REAL_JQ="$(resolve_real_binary jq || true)"
    if [[ -z "$REAL_JQ" ]]; then
        echo "thegent jq shim: failed to resolve real jq executable" >&2
        exit 127
    fi
    exec "$REAL_JQ" "$@"
fi
""")
        jq_shim.chmod(0o755)

    # uv accelerator (MTSP-15)
    uv_shim = bin_dir / "uv"
    if force or not uv_shim.exists():
        uv_shim.write_text(f"""#!/usr/bin/env bash
THEGENT_TOOL_BIN_PATH="{safe_bin_path}"
resolve_real_binary() {{
  PATH="$THEGENT_TOOL_BIN_PATH" command -v "$1"
}}
source "$(dirname "$(which thegent)")/../hooks/lib/common.sh" 2>/dev/null || true
if [[ "$(type -t uv)" == "function" ]]; then
    uv "$@"
else
    REAL_UV="$(resolve_real_binary uv || true)"
    if [[ -z "$REAL_UV" ]]; then
        echo "thegent uv shim: failed to resolve real uv executable" >&2
        exit 127
    fi
    exec "$REAL_UV" "$@"
fi
""")
        uv_shim.chmod(0o755)

    # npm accelerator (MTSP-15)
    npm_shim = bin_dir / "npm"
    if force or not npm_shim.exists():
        npm_shim.write_text(f"""#!/usr/bin/env bash
THEGENT_TOOL_BIN_PATH="{safe_bin_path}"
resolve_real_binary() {{
  PATH="$THEGENT_TOOL_BIN_PATH" command -v "$1"
}}
source "$(dirname "$(which thegent)")/../hooks/lib/common.sh" 2>/dev/null || true
if [[ "$(type -t npm)" == "function" ]]; then
    npm "$@"
else
    REAL_NPM="$(resolve_real_binary npm || true)"
    if [[ -z "$REAL_NPM" ]]; then
        echo "thegent npm shim: failed to resolve real npm executable" >&2
        exit 127
    fi
    exec "$REAL_NPM" "$@"
fi
""")
        npm_shim.chmod(0o755)


@mcp_app.command("up")
def mcp_up_cmd(
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable hot reload (HMR)"),
) -> None:
    """Start MCP + proxy via process-compose (bundled mode)."""
    from rich.console import Console

    from thegent.mcp_manage import mcp_up

    console = Console()
    ok, msg = mcp_up(reload=reload)
    if ok:
        console.print(f"[green]{msg}[/green]")
        console.print("[dim]MCP: http://127.0.0.1:3847/mcp | Proxy: http://127.0.0.1:8317[/dim]")
    else:
        console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)


memory_app = typer.Typer(help="Dual system of issue collection and memory collection (WP-MEMORY)")
app.add_typer(memory_app, name="memory")

# Mesh coordination commands (integrated from heliosShield)
from thegent.mesh.cli import app as mesh_app

app.add_typer(mesh_app, name="mesh")


@memory_app.command("add")
def memory_add_cmd(
    content: str = typer.Argument(..., help="The memory content"),
    cat: str = typer.Option("note", "--category", "-c", help="note|lesson_positive|lesson_negative|issue|friction"),
    scope: str = typer.Option(None, "--scope", "-s", help="agent|ephemeral|project|process"),
):
    """MTSP-17: Manually record a memory fragment."""
    from thegent.orchestration.memory import FrictionScope, MemoryCategory, MemorySystem

    system = MemorySystem(Path.cwd())
    system.record(content, MemoryCategory(cat), "cli", scope=FrictionScope(scope) if scope else None)
    from rich.console import Console

    Console().print("[green]Memory recorded.[/green]")


@memory_app.command("remember")
def memory_remember(
    content: str = typer.Argument(..., help="Note to remember"),
):
    """Shortcut for memory add --category note."""
    memory_add_cmd(content=content, cat="note")


@memory_app.command("issue")
def memory_issue(
    content: str = typer.Argument(..., help="Issue or friction point"),
):
    """Shortcut for memory add --category issue."""
    memory_add_cmd(content=content, cat="issue")


@memory_app.command("rule")
def memory_rule(
    content: str = typer.Argument(..., help="Rule or practice"),
    negative: bool = typer.Option(False, "--negative", "-n", help="Mark as a 'don't do this' rule"),
):
    """Shortcut for memory add --category lesson_positive/negative."""
    cat = "lesson_negative" if negative else "lesson_positive"
    memory_add_cmd(content=content, cat=cat)


@memory_app.command("scrape")
def memory_scrape_cmd():
    """MTSP-18: Scrape session history and record prompts to audit log."""
    from thegent.orchestration.memory import MemoryCategory, MemorySystem
    from thegent.orchestration.session_scraper import SessionScraper

    scraper = SessionScraper(Path.cwd())
    system = MemorySystem(Path.cwd())

    # Record current session prompts
    prompts = scraper.collect_all_recent_prompts()
    recorded = 0

    # Basic de-dupe
    recent = system.get_recent(limit=100, category=MemoryCategory.USER_PROMPT)
    recent_contents = {f.content for f in recent}

    for p in prompts:
        if p not in recent_contents:
            system.record(p, MemoryCategory.USER_PROMPT, "cli-scrape", metadata={"scraped": True})
            recorded += 1

    if recorded > 0:
        from rich.console import Console

        Console().print(f"[green]Scraped {recorded} new prompts into memory audit log.[/green]")


@memory_app.command("synthesize")
def memory_synthesize_cmd():
    """MTSP-17: Generate a synthesis report from the audit log."""
    from thegent.orchestration.memory import MemorySystem

    system = MemorySystem(Path.cwd())
    from rich.console import Console
    from rich.markdown import Markdown

    Console().print(Markdown(system.synthesize_to_markdown()))


@memory_app.command("garden")
def memory_garden_cmd():
    """MEM-AUD-02: Run the Gardener agent to prune memory into documentation."""
    import asyncio

    from rich.console import Console

    from thegent.orchestration.gardener import Gardener

    console = Console()
    console.print("[yellow]Gardener is entering the project...[/yellow]")

    gardener = Gardener(Path.cwd())

    # Run async function in a synchronous Typer command
    async def _run():
        return await gardener.run_synthesis()

    result = asyncio.run(_run())
    console.print(result)


def mcp_down_cmd() -> None:
    """Stop MCP + proxy (process-compose)."""
    from rich.console import Console

    from thegent.mcp_manage import mcp_down

    console = Console()
    ok, msg = mcp_down()
    if ok:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)


@mcp_app.command("restart")
def mcp_restart_cmd() -> None:
    """Hot reload: restart MCP + proxy (down then up)."""
    from rich.console import Console

    from thegent.mcp_manage import mcp_restart

    console = Console()
    ok, msg = mcp_restart()
    if ok:
        console.print(f"[green]{msg}[/green]")
        console.print("[dim]MCP: http://127.0.0.1:3847/mcp | Proxy: http://127.0.0.1:8317[/dim]")
    else:
        console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)


@mcp_app.command("service")
def mcp_service(
    action: str = typer.Argument(
        ...,
        help="Action: install, start, stop, restart, status, uninstall",
    ),
) -> None:
    """Manage thegent MCP HTTP server as launchd service (macOS). Start server before clients connect."""
    from rich.console import Console

    from thegent.config import ThegentSettings
    from thegent.mcp_manage import (
        service_install,
        service_start,
        service_status,
        service_stop,
        service_uninstall,
    )

    console = Console()
    settings = ThegentSettings()
    if action == "install":
        ok, msg = service_install()
        console.print(msg)
        if ok:
            console.print("[dim]Then: thegent mcp service start[/dim]")
    elif action == "start":
        ok, msg = service_start()
        console.print(msg)
        if ok:
            console.print(f"[dim]MCP at http://{settings.mcp_host}:{settings.mcp_port}/mcp[/dim]")
    elif action == "stop":
        ok, msg = service_stop()
        console.print(msg)
    elif action == "restart":
        service_stop()
        ok, msg = service_start()
        console.print(msg)
    elif action == "status":
        ok, msg = service_status(settings)
        console.print(msg)
    elif action == "uninstall":
        ok, msg = service_uninstall()
        console.print(msg)
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        raise typer.Exit(1)
    if not ok and action in ("install", "start", "stop", "restart", "uninstall"):
        raise typer.Exit(1)


@app.command("mcp-stdio", hidden=True)
def mcp_stdio() -> None:
    """Start the MCP server in stdio mode (for Claude Code)."""
    try:
        from thegent.mcp_server import mcp

        mcp.run()
    except ImportError:
        from rich.console import Console

        Console().print("[red]fastmcp not installed. Run: pip install thegent[mcp][/red]")
        raise typer.Exit(1)


@app.command("serve")
def serve(
    host: str | None = typer.Option(None, "--host", "-H", help="Bind address (default: THGENT_MCP_HOST or 127.0.0.1)"),
    port: int | None = typer.Option(None, "--port", "-p", help="HTTP port (default: THGENT_MCP_PORT or 3847)"),
    force: bool = typer.Option(False, "--force", "-f", help="Run in foreground even if service is available"),
    http: bool = typer.Option(True, "--http/--no-http", help="Start HTTP server (default)"),
    reload: bool = typer.Option(
        None,
        "--reload/--no-reload",
        "-r",
        help="Enable hot reload (HMR) for development (default: from settings.reload or False)",
    ),
) -> None:
    """Start the MCP server. Defaults to HTTP. Delegates to launchd/Homebrew service when available."""
    try:
        from thegent.mcp_server import run
    except ImportError:
        from rich.console import Console

        Console().print("[red]fastmcp not installed. Run: pip install thegent[mcp][/red]")
        raise typer.Exit(1)

    if not http:
        # Fallback to stdio if explicitly requested via --no-http
        try:
            from thegent.mcp_server import mcp

            mcp.run(transport="stdio")
            return
        except Exception as e:
            from rich.console import Console

            Console().print(f"[red]Failed to start stdio server: {e}[/red]")
            raise typer.Exit(1)

    from thegent.config import ThegentSettings
    from thegent.mcp_manage import serve_delegate_or_run

    settings = ThegentSettings()
    if host is not None:
        settings = settings.model_copy(update={"mcp_host": host})
    if port is not None:
        settings = settings.model_copy(update={"mcp_port": port})

    # Use settings.reload if reload not explicitly set via CLI
    if reload is None:
        reload = settings.reload

    if not force and not reload:
        run_foreground, msg = serve_delegate_or_run(settings)
        if not run_foreground:
            from rich.console import Console

            Console().print(f"[green]{msg}[/green]")
            raise typer.Exit(0)

    # Use settings.reload as default if reload not explicitly set
    effective_reload = reload if reload is not None else settings.reload
    run(host=host or settings.mcp_host, port=port or settings.mcp_port, reload=effective_reload)


@app.command("install")
def install_cmd(
    target: str = typer.Option(
        "all",
        "--target",
        "-t",
        help="Target: claude-code|claude-desktop|cursor|codex|droid|envrc|shell|system|all (default: all)",
    ),
    prefix: Path | None = typer.Option(
        None, "--prefix", help="Install prefix for system target (default: /opt/thegent)"
    ),
    editable: bool = typer.Option(
        False, "--editable", "-e", help="Symlink install instead of copy (bi-directional sync)"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite all files (no merge)"),
    undo: bool = typer.Option(False, "--undo", help="Undo previous installation using manifest"),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Ask before overwriting files with local changes"
    ),
    wizard: bool = typer.Option(False, "--wizard", "-w", help="Run interactive installation wizard"),
    service: bool = typer.Option(False, "--service", help="Install background MCP service (launchd on macOS)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would happen without making changes"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress"),
    url: str = typer.Option(None, "--url", "-u", help="MCP server URL (default: http://127.0.0.1:3847/mcp)"),
    bundle: list[str] = typer.Option(
        [],
        "--bundle",
        "-b",
        help="Install named third-party bundle(s) from manifest file (repeatable)",
    ),
    bundle_manifest: str | None = typer.Option(
        None,
        "--bundle-manifest",
        help="Path to third-party bundle manifest JSON (default: ~/.config/thegent/third_party_bundles.json)",
    ),
    list_bundles: bool = typer.Option(
        False,
        "--list-bundles",
        help="List named bundles from manifest and exit without installing",
    ),
    validate_bundles: bool = typer.Option(
        False,
        "--validate-bundles",
        help="Validate manifest shape and exit without installing",
    ),
    bundle_conflict_policy: str | None = typer.Option(
        None,
        "--bundle-conflict-policy",
        help="Bundle conflict policy for installation mode: smart|force|editable|interactive|copy|symlink",
    ),
    system_deps: bool = typer.Option(
        False, "--system-deps", help="Install system dependencies (Homebrew, mise, git repos)"
    ),
    use_nix: bool = typer.Option(False, "--nix", help="Use Nix for mise installation instead of Homebrew"),
) -> None:
    """Managed installation of thegent components and MCP configuration."""
    from rich.console import Console

    local_console = Console()

    from thegent.install import (
        get_bundle_manifest_path,
        list_bundle_names,
        run_install,
        run_install_system,
        run_wizard,
    )
    from thegent.install import (
        validate_bundle_manifest as validate_bundle_manifest_file,
    )

    if wizard:
        run_wizard(url=url)
        return

    if list_bundles:
        names = list_bundle_names(bundle_manifest)
        local_console.print(f"[bold]Bundle names ({len(names)}):[/bold]")
        for name in names:
            local_console.print(f"  - {name}")
        return

    if validate_bundles:
        valid, issues = validate_bundle_manifest_file(bundle_manifest)
        manifest_path = get_bundle_manifest_path(bundle_manifest)
        if not valid:
            local_console.print(f"[red]Bundle manifest invalid: {manifest_path}[/red]")
            for issue in issues:
                local_console.print(f"  - {issue}")
            raise typer.Exit(1)
        local_console.print(f"[green]Bundle manifest valid: {manifest_path}[/green]")
        return

    if undo:
        mode = "undo"
    elif interactive:
        mode = "interactive"
    else:
        mode = "editable" if editable else ("force" if force else "smart")

    local_console.print(f"[bold]=== thegent install ({mode}) ===[/bold]")
    if not undo:
        local_console.print(f"Target: {target}")
    if dry_run:
        local_console.print("[yellow]Dry run: no changes will be made[/yellow]")
    local_console.print()

    # System target: /opt/thegent layout for agent-as-system-user
    if target == "system":
        install_prefix = prefix or Path("/opt/thegent")
        local_console.print(f"[bold cyan]Installing to {install_prefix} (agent-as-system-user)...[/bold cyan]")
        counts = run_install_system(prefix=install_prefix, dry_run=dry_run, verbose=verbose)
        local_console.print(f"  Copied: {counts['copied']}")
        if not dry_run:
            local_console.print(f"[dim]Run: thegent install-shims --prefix {install_prefix} for git wrapper[/dim]")
        return

    # Install system dependencies if requested
    if system_deps and not undo:
        from thegent.install import install_system_dependencies

        local_console.print("[bold cyan]Installing system dependencies...[/bold cyan]")
        deps_results = install_system_dependencies(
            console=local_console,
            dry_run=dry_run,
            install_homebrew_pkg=True,
            install_mise_pkg=True,
            use_nix=use_nix,
        )
        local_console.print()

    counts = run_install(
        target=target,
        mode=mode,
        dry_run=dry_run,
        verbose=verbose,
        url=url,
        install_service=service,
        bundles=bundle,
        bundle_manifest=bundle_manifest,
        bundle_conflict_policy=bundle_conflict_policy,
    )

    local_console.print()
    local_console.print("[bold]Results:[/bold]")
    if mode == "undo":
        local_console.print(f"  Removed:   {counts.get('removed', 0)}")
        local_console.print(f"  Restored:  {counts.get('restored', 0)}")
        local_console.print(f"  Reverted:  {counts.get('reverted', 0)}")
    else:
        local_console.print(f"  Copied/Linked: {counts['copied']}")
        local_console.print(f"  Skipped:       {counts['skipped']}")
        local_console.print(f"  Conflicts:     {counts['conflicts']}")

    if counts.get("errors", 0) > 0:
        local_console.print(f"  [red]Errors:        {counts['errors']}[/red]")


# ============ Provider/Model Management CLI ============


@app.command("provider")
def provider_cmd() -> None:
    """Interactive provider and model management (CRUD)."""
    from thegent.provider_model_manager import run_provider_form

    run_provider_form()


@app.command("uninstall-system-deps")
def uninstall_system_deps_cmd(
    remove_hooks: bool = typer.Option(True, "--hooks/--no-hooks", help="Remove shell hooks (default: True)"),
    uninstall_mise: bool = typer.Option(False, "--mise", help="Also uninstall mise package"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would happen without making changes"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress"),
) -> None:
    """Uninstall system dependencies: remove mise hooks and optionally uninstall mise."""
    from rich.console import Console

    local_console = Console()

    from thegent.install import uninstall_system_dependencies

    local_console.print("[bold]=== thegent uninstall-system-deps ===[/bold]")
    if dry_run:
        local_console.print("[yellow]Dry run: no changes will be made[/yellow]")
    local_console.print()

    results = uninstall_system_dependencies(
        console=local_console,
        dry_run=dry_run,
        uninstall_mise_pkg=uninstall_mise,
        remove_hooks=remove_hooks,
    )

    local_console.print()
    local_console.print("[bold]Results:[/bold]")
    if results.get("hooks_removed"):
        local_console.print("[green]✓[/green] Shell hooks removed")
    if results.get("mise_uninstalled"):
        local_console.print("[green]✓[/green] mise uninstalled")

    if results.get("messages"):
        local_console.print()
        local_console.print("[bold]Details:[/bold]")
        for msg in results["messages"]:
            local_console.print(f"  {msg}")


@app.command("restore-backup")
def restore_backup_cmd(
    backup_file: str = typer.Argument(None, help="Backup file path (optional, will list if not provided)"),
    list_backups_flag: bool = typer.Option(False, "--list", "-l", help="List all available backups"),
    cleanup: bool = typer.Option(False, "--cleanup", help="Remove old backups (keeps 10 most recent)"),
    keep: int = typer.Option(10, "--keep", "-k", help="Number of backups to keep when cleaning up"),
) -> None:
    """Restore shell config from backup or manage backups."""
    from pathlib import Path

    from rich.console import Console

    local_console = Console()

    from thegent.install import cleanup_old_backups, list_backups, restore_shell_config

    if cleanup:
        local_console.print(f"[bold cyan]Cleaning up old backups (keeping {keep} most recent)...[/bold cyan]")
        removed_count, _removed_files = cleanup_old_backups(keep_count=keep, console=local_console)
        local_console.print(f"[green]Removed {removed_count} old backup(s)[/green]")
        return

    if list_backups_flag or not backup_file:
        backups = list_backups(local_console)
        if not backups:
            local_console.print("[yellow]No backups found[/yellow]")
            return

        local_console.print(f"[bold]Available backups ({len(backups)}):[/bold]")
        from rich.table import Table

        table = Table(show_header=True, header_style="bold")
        table.add_column("Backup File", style="cyan")
        table.add_column("Original", style="dim")
        table.add_column("Date", style="dim")

        for backup in backups[:20]:  # Show first 20
            parts = backup.name.rsplit(".", 2)
            original = parts[0] if len(parts) >= 3 else backup.name
            date_str = parts[1] if len(parts) >= 3 else "unknown"
            # Format date: 20260218_123456 -> 2026-02-18 12:34:56
            if len(date_str) == 15 and "_" in date_str:
                date_part, time_part = date_str.split("_")
                formatted_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]} {time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
            else:
                formatted_date = date_str

            table.add_row(backup.name, original, formatted_date)

        local_console.print(table)
        if len(backups) > 20:
            local_console.print(f"[dim]... and {len(backups) - 20} more[/dim]")
        return

    # Restore from specified backup
    backup_path = Path(backup_file).expanduser()
    if not backup_path.is_absolute():
        # Try in backup directory
        backup_dir = Path.home() / ".thegent" / "backups"
        backup_path = backup_dir / backup_file

    success, msg = restore_shell_config(backup_path, local_console)
    if success:
        local_console.print(f"[green]✓ {msg}[/green]")
    else:
        local_console.print(f"[red]✗ {msg}[/red]")
        raise typer.Exit(1)


@app.command("models-setup")
def models_setup_cmd() -> None:
    """Rich TUI for adding models and providers with full harness configuration."""
    from thegent.ux.models_providers_tui import run_models_providers_tui

    run_models_providers_tui()


@app.command("add-provider")
def add_provider_cmd(
    name: str = typer.Argument(..., help="Provider name (claude/codex use OAuth only)"),
    base_url: str = typer.Option(..., "--base-url", "-b", help="API base URL"),
    model: str = typer.Option(..., "--model", "-m", help="Default model name"),
    alias: str | None = typer.Option(None, "--alias", "-a", help="Model alias"),
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="API key (not for claude/codex)"),
    login_url: str | None = typer.Option(None, "--login-url", help="Login URL for credentials"),
) -> None:
    """Add a new provider."""
    from thegent.provider_model_manager import add_provider

    aliases = [alias] if alias else None
    success, msg = add_provider(
        name=name, base_url=base_url, model=model, extra_aliases=aliases, api_key=api_key, login_url=login_url
    )
    if success:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)


@app.command("list-providers")
def list_providers_cmd(
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, json"),
) -> None:
    """List all configured providers."""
    from thegent.provider_model_manager import list_providers

    providers = list_providers()
    if format == "json":
        import json

        console.print(json.dumps(providers, indent=2))
    else:
        from rich.table import Table

        table = Table(title="Providers")
        table.add_column("Name", style="cyan")
        table.add_column("Base URL", style="dim")
        table.add_column("Model", style="green")
        for p in providers:
            table.add_row(p.get("name", ""), p.get("base_url", "")[:40], p.get("model", ""))
        console.print(table)


@app.command("validate-provider")
def validate_provider_cmd(name: str = typer.Argument(..., help="Provider name")) -> None:
    """Validate a provider by testing connectivity."""
    from thegent.provider_model_manager import validate_provider

    success, msg, _ = validate_provider(name)
    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[red]✗ {msg}[/red]")
        raise typer.Exit(1)


@app.command("add-api-key")
def add_api_key_cmd(
    provider: str = typer.Argument(
        ..., help="Provider name (claude/codex use OAuth: thegent cliproxy login <provider>)"
    ),
    api_key: str = typer.Option(..., "--api-key", "-k", help="API key"),
) -> None:
    """Add API key for a provider."""
    from thegent.provider_model_manager import add_api_key

    success, msg = add_api_key(provider, api_key)
    if success:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)


@app.command("discover-models")
def discover_models_cmd(
    provider: str | None = typer.Option(None, "--provider", "-p", help="Filter by provider"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, json"),
) -> None:
    """Discover available models from providers."""
    from thegent.provider_model_manager import discover_models

    models = discover_models(provider)
    if not models:
        console.print("[yellow]No models discovered[/yellow]")
        return
    if format == "json":
        import json

        console.print(json.dumps(models, indent=2))
    else:
        from rich.table import Table

        table = Table(title="Discovered Models")
        table.add_column("Model ID", style="cyan")
        table.add_column("Provider", style="green")
        for m in models[:50]:
            table.add_row(m.get("id", "")[:50], m.get("provider", ""))
        console.print(table)


# ============ Model Indices CLI ============


@app.command("list-model-indices")
def list_model_indices_cmd(
    provider: str | None = typer.Option(None, "--provider", "-p", help="Filter by provider"),
    sort_by: str = typer.Option("cost", "--sort", "-s", help="Sort by: cost, context, tps, composite_score"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, json"),
    show_modalities: bool = typer.Option(False, "--modalities", "-m", help="Show modality flags"),
) -> None:
    """List models with context limits, cost ($/Mtok), speed (tps), and benchmarks."""
    from thegent.provider_model_manager import list_model_indices

    models = list_model_indices(provider=provider, sort_by=sort_by, include_all=True)
    if not models:
        console.print("[yellow]No model indices found[/yellow]")
        return
    if format == "json":
        import json

        console.print(json.dumps(models, indent=2))
        return

    from rich.table import Table

    table = Table(title="Model Indices")
    table.add_column("Provider", style="cyan")
    table.add_column("Model", style="green")
    table.add_column("Context", justify="right")
    table.add_column("Cost/Mtok", justify="right")
    table.add_column("TPS", justify="right")
    table.add_column("Score", justify="right")
    if show_modalities:
        table.add_column("Modalities", style="dim")

    for m in models:
        ctx = m.get("context_limit")
        cost = m.get("total_cost_per_1m")
        tps = m.get("tps")
        score = m.get("composite_score")
        benchmarks = m.get("benchmarks", {})

        # Format modalities as icons
        if show_modalities:
            modalities = m.get("modalities", {})
            mods_str = " ".join(k[0].upper() for k, v in modalities.items() if v is True) if modalities else "-"
        else:
            mods_str = None

        table.add_row(
            m["provider"][:12],
            m["model"][:18],
            f"{ctx / 1000:.0f}K" if ctx else "N/A",
            f"${cost:.2f}" if cost else "N/A",
            f"{tps}" if tps else "-",
            f"{score:.1f}%" if score else "-",
            mods_str,
        )

    console.print(table)


@app.command("search-models")
def search_models_cmd(
    capability: str = typer.Argument(..., help="Capability: reasoning, vision, swebench, termbench"),
    min_context: int | None = typer.Option(None, "--min-context", "-c", help="Minimum context window"),
    min_tps: int | None = typer.Option(None, "--min-tps", help="Minimum tokens per second"),
    max_cost: float | None = typer.Option(None, "--max-cost", help="Max cost per Mtok"),
) -> None:
    """Search models by capability (reasoning, vision, or benchmark score)."""
    from thegent.provider_model_manager import search_models_by_capability

    models = search_models_by_capability(capability, min_context=min_context, max_cost_per_1m=max_cost, min_tps=min_tps)
    if not models:
        console.print(f"[yellow]No models found with '{capability}'[/yellow]")
        return
    from rich.table import Table

    table = Table(title=f"Models with {capability}")
    table.add_column("Provider")
    table.add_column("Model")
    table.add_column("Context", justify="right")
    table.add_column("Cost/Mtok", justify="right")
    table.add_column("TPS", justify="right")
    for m in models:
        ctx = m.get("context_limit")
        cost = m.get("total_cost_per_1m")
        tps = m.get("tps")
        table.add_row(
            m["provider"][:15],
            m["model"][:25],
            f"{ctx / 1000:.0f}K" if ctx else "N/A",
            f"${cost:.2f}" if cost else "N/A",
            f"{tps}" if tps else "-",
        )
    console.print(table)
    console.print(f"\n[dim]Found {len(models)} models[/dim]")


@app.command("fuzzy-search")
def fuzzy_search_cmd(
    query: str = typer.Argument(..., help="Search query"),
    provider: str | None = typer.Option(None, "--provider", "-p", help="Filter by provider"),
    limit: int = typer.Option(10, "--limit", "-n", help="Maximum results"),
) -> None:
    """Fuzzy search models by name, provider, or notes."""
    from thegent.provider_model_manager import fuzzy_search_models

    results = fuzzy_search_models(query=query, provider=provider, limit=limit)

    if not results:
        console.print(f"[yellow]No models found matching '{query}'[/yellow]")
        return

    from rich.table import Table

    table = Table(title=f"Search: {query}")
    table.add_column("Score")
    table.add_column("Provider")
    table.add_column("Model")
    table.add_column("Context", justify="right")
    table.add_column("Cost/Mtok", justify="right")
    table.add_column("TPS", justify="right")

    for m in results:
        ctx = m.get("context_limit")
        cost = m.get("total_cost_per_1m")
        tps = m.get("tps")
        score = m.get("_fuzzy_score", 0)
        table.add_row(
            f"{score}",
            m["provider"][:12],
            m["model"][:20],
            f"{ctx / 1000:.0f}K" if ctx else "N/A",
            f"${cost:.2f}" if cost else "N/A",
            f"{tps}" if tps else "-",
        )

    console.print(table)
    console.print(f"\n[dim]Found {len(results)} models[/dim]")


@app.command("search-modalities")
def search_modalities_cmd(
    required: list[str] = typer.Option(..., "--require", "-r", help="Required modality (repeatable)"),
    provider: str | None = typer.Option(None, "--provider", "-p", help="Filter by provider"),
    sort_by: str = typer.Option("composite_score", "--sort", "-s", help="Sort by: composite_score, cost, context, tps"),
) -> None:
    """Search models by modality requirements."""
    from thegent.provider_model_manager import search_by_modalities

    results = search_by_modalities(
        required_modalities=required,
        provider=provider,
        sort_by=sort_by,
    )

    if not results:
        console.print(f"[yellow]No models with all modalities: {', '.join(required)}[/yellow]")
        return

    from rich.table import Table

    table = Table(title=f"Models with: {', '.join(required)}")
    table.add_column("Provider")
    table.add_column("Model")
    table.add_column("Score", justify="right")
    table.add_column("Context", justify="right")
    table.add_column("Cost/Mtok", justify="right")
    table.add_column("TPS", justify="right")

    for m in results:
        ctx = m.get("context_limit")
        cost = m.get("cost_per_1m")
        tps = m.get("tps")
        score = m.get("composite_score")
        table.add_row(
            m["provider"][:12],
            m["model"][:20],
            f"{score:.0f}%" if score else "-",
            f"{ctx / 1000:.0f}K" if ctx else "N/A",
            f"${cost:.2f}" if cost else "N/A",
            f"{tps}" if tps else "-",
        )

    console.print(table)


@app.command("show-modalities")
def show_modalities_cmd(
    provider: str | None = typer.Option(None, "--provider", "-p", help="Filter by provider"),
    model: str | None = typer.Option(None, "--model", "-m", help="Filter by model"),
) -> None:
    """Show modality/feature flags for models."""
    from rich.table import Table

    from thegent.provider_model_manager import get_model_modalities, list_available_modalities

    # Show schema
    console.print("[bold]Available Modality Types:[/bold]")
    schema = list_available_modalities()
    schema_table = Table()
    schema_table.add_column("Modality")
    schema_table.add_column("Display")
    schema_table.add_column("Weight")
    for mod, info in schema.items():
        schema_table.add_row(mod, info.get("display", mod), f"{info.get('weight', 1.0):.1f}")
    console.print(schema_table)
    console.print()

    # Show model modalities
    console.print("[bold]Model Modalities:[/bold]")
    modalities = get_model_modalities(provider=provider, model=model)

    for key, data in sorted(modalities.items()):
        console.print(f"\n[cyan]{key}[/cyan]")
        table = Table(show_header=False, box=None)
        for mod, val in data["modalities"].items():
            icon = "✓" if val is True else "✗" if val is False else str(val)
            table.add_row(f"  {mod}: {icon}")
        console.print(table)


@app.command("add-benchmark")
def add_benchmark_cmd(
    provider: str = typer.Argument(..., help="Provider name"),
    model: str = typer.Argument(..., help="Model name"),
    name: str = typer.Argument(..., help="Benchmark name"),
    score: float = typer.Argument(..., help="Score (0-1)"),
    category: str = typer.Option("custom", "--category", "-c", help="Category"),
    description: str = typer.Option("", "--desc", "-d", help="Description"),
) -> None:
    """Add a custom benchmark for a model."""
    from thegent.provider_model_manager import add_custom_benchmark

    success, msg = add_custom_benchmark(
        provider=provider,
        model=model,
        benchmark_name=name,
        score=score,
        category=category,
        description=description,
    )

    if success:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)


@app.command("add-modality")
def add_modality_cmd(
    provider: str = typer.Argument(..., help="Provider name"),
    model: str = typer.Argument(..., help="Model name"),
    modality: str = typer.Argument(..., help="Modality/feature name"),
    value: str = typer.Option("true", help="Value (true/false or custom string)"),
) -> None:
    """Add or update a modality/feature flag for a model."""
    from thegent.provider_model_manager import add_model_modality

    # Parse value
    if value.lower() == "true":
        parsed_value = True
    elif value.lower() == "false":
        parsed_value = False
    else:
        parsed_value = value

    success, msg = add_model_modality(
        provider=provider,
        model=model,
        modality=modality,
        value=parsed_value,
    )

    if success:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)


@app.command("leaderboard")
def leaderboard_cmd(
    provider: str | None = typer.Option(None, "--provider", "-p", help="Filter by provider"),
    min_score: float | None = typer.Option(None, "--min-score", "-s", help="Minimum composite score"),
    limit: int = typer.Option(20, "--limit", "-n", help="Maximum results"),
) -> None:
    """Show model leaderboard by composite performance score."""
    from rich.table import Table

    from thegent.provider_model_manager import list_models_with_scores

    models = list_models_with_scores(
        provider=provider,
        min_score=min_score,
        sort_by="composite_score",
    )[:limit]

    table = Table(title="Model Leaderboard (Composite Score)")
    table.add_column("Rank", justify="right")
    table.add_column("Provider")
    table.add_column("Model")
    table.add_column("Score", justify="right")
    table.add_column("Cost/Mtok", justify="right")
    table.add_column("TPS", justify="right")
    table.add_column("Key Benchmarks", style="dim")

    for i, m in enumerate(models, 1):
        score = m.get("composite_score")
        benchmarks = m.get("benchmarks", {})

        # Show top 3 benchmarks
        bench_str = ", ".join(f"{k}:{v:.0%}" for k, v in sorted(benchmarks.items(), key=lambda x: -x[1])[:3])

        table.add_row(
            f"{i}",
            m["provider"][:12],
            m["model"][:18],
            f"{score:.1f}%" if score else "-",
            f"${m.get('cost_per_1m', 0):.2f}" if m.get("cost_per_1m") else "-",
            f"{m.get('tps')}" if m.get("tps") else "-",
            bench_str[:30],
        )

    console.print(table)


app.command("context-history")(context_history_cmd)
app.command("scratchpad")(scratchpad_cmd)


app.command("memory")(memory_cmd)


# ---------------------------------------------------------------------------
# thegent sync — unified sync command (SY-009)
# ---------------------------------------------------------------------------

sync_app = typer.Typer(help="Unified sync: work-stream, config, agents, hooks")
app.add_typer(sync_app, name="sync")


@sync_app.callback(invoke_without_command=True)
def sync_callback(ctx: typer.Context) -> None:
    """Sync all components when no subcommand is given."""
    if ctx.invoked_subcommand is None:
        _sync_all_cmd(dry_run=False)


def _build_sync_command(cd: Path | None) -> "SyncCommand":
    from thegent.commands.sync import SyncCommand

    return SyncCommand(project_root=cd)


def _print_sync_result(result: "SyncResult") -> None:
    from rich.table import Table

    table = Table(title="Sync Results")
    table.add_column("Operation", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Duration", justify="right")
    table.add_column("Message")

    for op in result.operations:
        if op.status.value == "success":
            status_str = "[green]OK[/green]"
        elif op.status.value == "dry_run":
            status_str = "[cyan]DRY-RUN[/cyan]"
        elif op.status.value == "skipped":
            status_str = "[yellow]SKIPPED[/yellow]"
        else:
            status_str = "[red]FAILED[/red]"

        table.add_row(
            op.operation,
            status_str,
            f"{op.duration:.2f}s",
            op.message,
        )

    console.print(table)
    if not result.success:
        for failed in result.failed_operations:
            for err in failed.errors:
                console.print(f"[red]  {failed.operation}: {err}[/red]")
        raise typer.Exit(1)


def _sync_all_cmd(
    cd: Path | None = None,
    dry_run: bool = False,
) -> None:
    cmd = _build_sync_command(cd)
    result = cmd.sync_all(dry_run=dry_run)
    _print_sync_result(result)


@sync_app.command("all")
def sync_all(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Project root directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Report without writing"),
) -> None:
    """Run all sync operations: work-stream, config, agents, hooks."""
    _sync_all_cmd(cd=cd, dry_run=dry_run)


@sync_app.command("work-stream")
def sync_work_stream(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Project root directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Report without writing"),
) -> None:
    """Incorporate doc fragments from docs/ into WORK_STREAM.md."""
    from thegent.commands.sync import SyncCommand

    cmd = SyncCommand(project_root=cd)
    op = cmd.sync_work_stream(dry_run=dry_run)
    status = "[green]OK[/green]" if op.ok else "[red]FAILED[/red]"
    console.print(f"[bold]{op.operation}[/bold] {status}: {op.message}")
    for change in op.changes[:20]:
        console.print(f"  [dim]{change}[/dim]")
    if not op.ok:
        raise typer.Exit(1)


@sync_app.command("config")
def sync_config(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Project root directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Report without writing"),
) -> None:
    """Refresh ThegentSettings from the current environment."""
    from thegent.commands.sync import SyncCommand

    cmd = SyncCommand(project_root=cd)
    op = cmd.sync_config(dry_run=dry_run)
    status = "[green]OK[/green]" if op.ok else "[red]FAILED[/red]"
    console.print(f"[bold]{op.operation}[/bold] {status}: {op.message}")
    if not op.ok:
        raise typer.Exit(1)


@sync_app.command("agents")
def sync_agents(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Project root directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Report without writing"),
) -> None:
    """Discover new agent files in agents/ and report unregistered personas."""
    from thegent.commands.sync import SyncCommand

    cmd = SyncCommand(project_root=cd)
    op = cmd.sync_agents(dry_run=dry_run)
    status = "[green]OK[/green]" if op.ok else "[red]FAILED[/red]"
    console.print(f"[bold]{op.operation}[/bold] {status}: {op.message}")
    for change in op.changes[:20]:
        console.print(f"  [dim]{change}[/dim]")
    if not op.ok:
        raise typer.Exit(1)


@sync_app.command("hooks")
def sync_hooks(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Project root directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Report without writing"),
) -> None:
    """Validate hook scripts against hook-config.yaml registrations."""
    from thegent.commands.sync import SyncCommand

    cmd = SyncCommand(project_root=cd)
    op = cmd.sync_hooks(dry_run=dry_run)
    status = "[green]OK[/green]" if op.ok else "[red]FAILED[/red]"
    console.print(f"[bold]{op.operation}[/bold] {status}: {op.message}")
    for change in op.changes[:30]:
        console.print(f"  [dim]{change}[/dim]")
    if not op.ok:
        raise typer.Exit(1)


@sync_app.command("status")
def sync_status(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Project root directory"),
) -> None:
    """Show drift between local agent config and expected state."""
    from thegent.commands.sync import SyncCommand

    cmd = SyncCommand(project_root=cd)
    op = cmd.status()
    indicator = "[green]IN SYNC[/green]" if not op.details.get("has_drift") else "[yellow]DRIFT[/yellow]"
    console.print(f"[bold]sync status[/bold] {indicator}: {op.message}")
    for change in op.changes[:30]:
        console.print(f"  [dim]{change}[/dim]")
    if not op.ok:
        raise typer.Exit(1)


@sync_app.command("push")
def sync_push(
    target: str | None = typer.Option(None, "--target", "-t", help="Remote target identifier"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Project root directory"),
) -> None:
    """Push local state to remote (stubbed — wires up when backend is available)."""
    from thegent.commands.sync import SyncCommand

    cmd = SyncCommand(project_root=cd)
    op = cmd.push(target=target)
    status_str = "[green]OK[/green]" if op.ok else "[red]FAILED[/red]"
    console.print(f"[bold]sync push[/bold] {status_str}: {op.message}")
    for change in op.changes[:20]:
        console.print(f"  [dim]{change}[/dim]")
    if not op.ok:
        raise typer.Exit(1)


@sync_app.command("pull")
def sync_pull(
    source: str | None = typer.Option(None, "--source", "-s", help="Remote source identifier"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Project root directory"),
) -> None:
    """Pull remote state locally (stubbed — wires up when backend is available)."""
    from thegent.commands.sync import SyncCommand

    cmd = SyncCommand(project_root=cd)
    op = cmd.pull(source=source)
    status_str = "[green]OK[/green]" if op.ok else "[red]FAILED[/red]"
    console.print(f"[bold]sync pull[/bold] {status_str}: {op.message}")
    if not op.ok:
        raise typer.Exit(1)


@sync_app.command("reset")
def sync_reset(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Project root directory"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Reset local sync state to defaults (stubbed — reports what would change)."""
    from thegent.commands.sync import SyncCommand

    if not confirm:
        console.print(
            "[yellow]Reset will report what would be affected.[/yellow] "
            "Pass --yes to acknowledge."
        )

    cmd = SyncCommand(project_root=cd)
    op = cmd.reset()
    status_str = "[green]OK[/green]" if op.ok else "[red]FAILED[/red]"
    console.print(f"[bold]sync reset[/bold] {status_str}: {op.message}")
    for change in op.changes[:20]:
        console.print(f"  [dim]{change}[/dim]")
    if not op.ok:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
