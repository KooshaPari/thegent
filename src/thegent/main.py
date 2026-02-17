"""Thegent CLI entry point (subcommand-only)."""

import json
import logging
import os
import sys
import warnings

# G-DX-01: Silencing noisy non-fatal warnings for better operator experience.
# Must be before any other imports that might trigger Pydantic plugin loading.
warnings.filterwarnings("ignore", message=".*is not JSON serializable; excluding default from JSON schema.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="uvicorn")
warnings.filterwarnings("ignore", message=".*ImportError while loading the `logfire-plugin` Pydantic plugin.*")

from pathlib import Path
import typer

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
    usage_cmd,
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
    deferral_list_cmd,
    deferral_resume_cmd,
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
    ps_cmd,
    purge_cmd,
    resolve_model_route_cmd,
    resume_cmd,
    retry_cmd,
    rules_sync_cmd,
    run_cmd,
    run_diff_cmd,
    session_contract_health_gate_cmd,
    session_contract_health_report_cmd,
    session_contract_health_trend_cmd,
    session_contracts_cmd,
    setup_cmd,
    sitback_dashboard_cmd,
    status_cmd,
    stop_cmd,
    sweep_cmd,
    takeover_cmd,
    terminal_route_cmd,
    trace_replay_cmd,
    wait_cmd,
    summary_cmd,
    team_create_cmd,
    team_task_add_cmd,
    team_task_list_cmd,
    recover_status_cmd,
    project_register_cmd,
    project_list_cmd,
    forensics_snapshot_cmd,
)

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
    usage_cmd,
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
    deferral_list_cmd,
    deferral_resume_cmd,
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
    ps_cmd,
    purge_cmd,
    resolve_model_route_cmd,
    resume_cmd,
    retry_cmd,
    rules_sync_cmd,
    run_cmd,
    run_diff_cmd,
    session_contract_health_gate_cmd,
    session_contract_health_report_cmd,
    session_contract_health_trend_cmd,
    session_contracts_cmd,
    setup_cmd,
    sitback_dashboard_cmd,
    status_cmd,
    stop_cmd,
    sweep_cmd,
    takeover_cmd,
    terminal_route_cmd,
    trace_replay_cmd,
    wait_cmd,
    summary_cmd,
)


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
    no_args_is_help=True,
)

app.command("init")(init_cmd)
app.command("setup")(setup_cmd)
app.command("summary")(summary_cmd)
app.command("nim-setup", hidden=True)(setup_cmd)

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
    from thegent.cli_impl import financial_dashboard_impl
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
orchestrate_app.add_typer(teammates_app, name="teammates")

deferral_app = typer.Typer(help="Manage deferred non-critical tasks (WP-5004)")
orchestrate_app.add_typer(deferral_app, name="deferral")


@deferral_app.command("list")
def deferral_list() -> None:
    """List all currently deferred tasks."""
    from thegent.cli import deferral_list_cmd

    deferral_list_cmd()


@deferral_app.command("resume")
def deferral_resume(
    run_id: str = typer.Argument(..., help="ID of run to resume"),
) -> None:
    """Manually resume a deferred task."""
    from thegent.cli import deferral_resume_cmd

    deferral_resume_cmd(run_id)


@teammates_app.command("list")
def teammates_list() -> None:
    """List all discovered specialized agents available for delegation (WP-16001)."""
    from thegent.cli import teammates_list_cmd

    teammates_list_cmd()


@teammates_app.command("delegate")
def teammates_delegate(
    teammate_id: str = typer.Argument(..., help="ID of the teammate to delegate to"),
    prompt: str = typer.Argument(..., help="Instruction for the teammate"),
    parent_run_id: str = typer.Option(None, "--parent-run", help="Parent run ID for tracking"),
) -> None:
    """Delegate a sub-task to a specialized teammate (WP-16002)."""
    from thegent.cli import teammates_delegate_cmd

    teammates_delegate_cmd(teammate_id=teammate_id, prompt=prompt, parent_run_id=parent_run_id)


@teammates_app.command("status")
def teammates_status(
    run_id: str = typer.Option(None, "--run-id", help="Filter by parent run ID"),
) -> None:
    """Monitor the status of the teammate swarm (WP-16002)."""
    from thegent.cli import teammates_status_cmd

    teammates_status_cmd(run_id=run_id)


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

    from thegent.config import ThegentSettings

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
config_app = typer.Typer(help="Config validation and introspection")

discovery_app.command("register")(discovery_register_cmd)
discovery_app.command("parse")(discovery_parse_cmd)
discovery_app.command("scan")(discovery_scan_cmd)


@config_app.command("check")
def config_check(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Validate config; fail-fast on misconfig (DX-010, ROB-013)."""
    config_check_cmd(format=format)


from thegent.clode_main import app as clode_app
from thegent.clode_main import sitback_cmd
from thegent.terminal_cli import app as terminal_app

dex_app: typer.Typer | None = None
try:
    from thegent.dex_main import app as _dex_app

    dex_app = _dex_app
except Exception:
    dex_app = None

app.command("sitback")(sitback_cmd)
app.add_typer(clode_app, name="clode")
if dex_app is not None:
    app.add_typer(dex_app, name="dex")
app.add_typer(orchestrate_app, name="orchestrate")
app.add_typer(govern_app, name="govern")

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
    retry_run: bool = typer.Option(False, "--retry", help="Retry failed run by --run-id (looks up prompt from registry)"),
    mode: str = typer.Option("write", "--mode", "-m", help="Mode: read-only, write, full"),
    timeout: int = typer.Option(90, "--timeout", "-t", help="Timeout hint in seconds (tool-call budget injection)"),
    full: bool = typer.Option(False, "--full", "-f", help="Show full raw output (default: stream-json, parsed)"),
    live: bool = typer.Option(False, "--live", help="Stream output live to terminal"),
    model: str | None = typer.Option(None, "--model", "-M", help="Model override or model-first (when agent omitted)"),
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
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode (THGENT_DEBUG=1, proxy -debug for model/provider/latency tags)"),
) -> None:
    """Run a foreground agent invocation. Use -M <model> without agent for model-first routing."""
    if retry_run and run_id:
        retry_cmd(run_id=run_id, agent=agent, failover=failover, cd=cd, override_reason=override)
        return
    if not prompt:
        typer.echo("Error: prompt required (or use --retry --run-id <run_id>)")
        raise typer.Exit(1)
    run_cmd(
        prompt=prompt,
        agent=agent,
        cd=cd,
        mode=mode,
        timeout=timeout,
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
    )


from thegent.orchestration.tasks import TaskRole, ROLE_PROMPTS, get_role_prompt

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
    repeat: int = typer.Option(1, "--repeat", "-r", help="With --do-next: run up to N work packages in sequence (stop on first failure)"),
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
            typer.echo(f"[do-next {attempt + 1}/{repeat}] {items[0].get('id', '?')}: {(prompt[:60] + '...') if len(prompt) > 60 else prompt}")
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
            prompt = None


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
    timeout: int = typer.Option(90, "--timeout", "-t", help="Timeout hint in seconds (tool-call budget injection)"),
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
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode (THGENT_DEBUG=1 for model/provider/latency tags)"),
) -> None:
    """Start a background run and register a session."""
    bg_cmd(
        prompt=prompt,
        agent=agent,
        cd=cd,
        mode=mode,
        timeout=timeout,
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


inbox_app = typer.Typer(
    help="Unified inbox: run registry + escalation events. List, filter, and wait for new events.",
    invoke_without_command=True,
)


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

    console = Console()
    hooks_root = Path(__file__).resolve().parents[2] / "hooks"
    watcher = hooks_root / "hook-watcher.sh"
    if not watcher.exists():
        console.print("[red]hook-watcher.sh not found[/red]")
        raise SystemExit(1)
    env = os.environ.copy()
    env["HOOK_WATCHER_INTERVAL"] = str(interval)
    if foreground:
        subprocess.run([str(watcher), str(project_dir.resolve())], env=env, check=False)
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
    agents: str = typer.Option("cursor,headless_agent,interactive_agent", "--agents", help="Comma-separated list of agents (codex/claude aliases supported)"),
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
) -> None:
    """List registered background sessions."""
    ps_cmd(
        all_sessions=all_sessions,
        owner=owner,
        format=format,
        include_contract=include_contract,
    )


recover_app = typer.Typer(help="Self-healing and automated recovery (WP-2XXX)")
app.add_typer(recover_app, name="recover")


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
    override: str | None = typer.Option(None, "--override", help="Policy override reason (e.g. for policy-blocked retries)"),
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
    override: str | None = typer.Option(None, "--override", help="Policy override reason (e.g. for policy-blocked retries)"),
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
        "prefer_direct", "--policy", help="Routing policy: prefer_direct, prefer_proxy, failover, cheapest, cost_quality, pareto"
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
        "prefer_direct", "--policy", help="Routing policy: prefer_direct, prefer_proxy, failover, cheapest, cost_quality, pareto"
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
    """Find next actionable work items from PLAN_STATUS, FR_TRACKER, docs/plans/, escalation queue."""
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


mcp_app = typer.Typer(
    help="MCP config and service: install thegent into Cursor/Claude Code/Codex; manage HTTP server as startup service",
)
app.add_typer(mcp_app, name="mcp")

mgmt_app = typer.Typer(
    help="Management commands for agent self-service: ensure proxy, verify integrations",
)
app.add_typer(mgmt_app, name="mgmt")


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


@mcp_app.command("spotlight-exclude")
def mcp_spotlight_exclude(
    force: bool = typer.Option(False, "--force", help="Force command even if not on macOS")
) -> None:
    """Exclude heavy development and thegent metadata directories from Spotlight indexing (macOS).
    Helps reduce mds_stores memory usage and CPU spikes during high-IO agent runs."""
    import sys
    import subprocess
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
            subprocess.run(["mdutil", "-i", "off", str(t)], capture_output=True, check=False)
            # Create .noindex file as a fallback/reinforcement
            if t.is_dir():
                noindex = t / ".noindex"
                try:
                    noindex.touch(exist_ok=True)
                except Exception:
                    pass
    
    console.print("[green]Spotlight exclusion complete. Run 'thegent ps --all' to monitor memory recovery.[/green]")


@mcp_app.command("prune")
def mcp_prune(
    force: bool = typer.Option(False, "--force", "-f", help="Force kill without confirmation"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be killed"),
) -> None:
    """Kill redundant agent-related Node.js processes (LSPs, MCP servers, cc-status).
    Use this when memory usage is high (>10GB) and many orphan processes are detected.
    For automatic pruning on Stop, set THGENT_AUTO_PRUNE=1."""
    import os
    import signal
    import subprocess
    import time
    from typing import Any

    from rich.console import Console
    from rich.table import Table

    from thegent.config import ThegentSettings
    from thegent.prune_utils import is_orphan_by_ppid

    console = Console()
    settings = ThegentSettings()

    # Patterns for redundant processes
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
    ]

    try:
        res = subprocess.run(
            ["ps", "-eo", "pid,ppid,rss,command"],
            capture_output=True,
            text=True,
            check=False,
        )
        lines = res.stdout.strip().splitlines()
        has_rss = True
    except Exception:
        try:
            res = subprocess.run(
                ["ps", "-eo", "pid,ppid,command"],
                capture_output=True,
                text=True,
                check=False,
            )
            lines = res.stdout.strip().splitlines()
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
        if any(x in cmd_lower for x in ("node", "npm", "bun", "deno", "cc-status")):
            for p in patterns:
                if p in cmd:
                    candidates.append({"pid": pid_i, "ppid": ppid_i, "cmd": cmd, "rss_kb": rss_kb})
                    break

    # Filter to true orphans when orphan-by-ppid enabled
    if settings.prune_orphan_by_ppid:
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
            console.print(f"[green]No orphan processes (all {len(candidates)} candidates have living Cursor/Claude/Codex parents).[/green]")
        else:
            console.print("[green]No redundant agent processes found.[/green]")
        return

    if settings.prune_orphan_by_ppid and len(candidates) > len(to_kill):
        console.print(f"[dim]Orphan-by-ppid: {len(to_kill)} orphans of {len(candidates)} candidates (kept {len(candidates) - len(to_kill)} with living parents)[/dim]")

    # Zombie count (processes with state Z; parent should reap)
    zombie_count = 0
    try:
        zres = subprocess.run(["ps", "-eo", "stat"], capture_output=True, text=True, check=False)
        if zres.returncode == 0:
            zombie_count = sum(1 for line in zres.stdout.splitlines()[1:] if "Z" in line.split()[0])
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
    workspace: Path | None = typer.Option(
        None, "--workspace", "-d", help="Workspace dir for cursor"
    ),
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
    bin_dir: Path = typer.Option(
        Path.home() / ".local" / "bin", "--bin-dir", help="Directory for shims"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite"),
    all_tools: bool = typer.Option(True, "--all", help="Install accelerators for git, grep, fd, jq, etc."),
) -> None:
    """MTSP-10: Install optimized accelerators (shims) for common tools.
    Accelerates git (multi-tenant), grep (rg), find (fd), jq (jaq)."""
    from thegent.clode_main import install_links as clode_install_links
    from rich.console import Console
    console = Console()
    
    clode_install_links(bin_dir=bin_dir, force=force)

    if all_tools:
        _install_tool_accelerators(bin_dir, force)
        _install_role_accelerators(bin_dir, force)
        console.print(f"[green]Tool accelerators installed to {bin_dir}[/green]")
        console.print("[dim]Accelerators: git, grep, find, jq, wc, summarize, research, review, explain, fix, code[/dim]")
        console.print(f"[yellow]Action Required: Ensure {bin_dir} is early in your PATH![/yellow]")

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
    """Write accelerator shims to bin_dir."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    safe_bin_path = "/usr/bin:/opt/homebrew/bin:/bin:/usr/sbin:/sbin"
    
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
    exec rg "$@"
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


@memory_app.command("add")
def memory_add_cmd(
    content: str = typer.Argument(..., help="The memory content"),
    cat: str = typer.Option("note", "--category", "-c", help="note|lesson_positive|lesson_negative|issue|friction"),
    scope: str = typer.Option(None, "--scope", "-s", help="agent|ephemeral|project|process"),
):
    """MTSP-17: Manually record a memory fragment."""
    from thegent.orchestration.memory import MemoryCategory, FrictionScope, MemorySystem
    system = MemorySystem(Path.cwd())
    system.record(
        content,
        MemoryCategory(cat),
        "cli",
        scope=FrictionScope(scope) if scope else None
    )
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
    from thegent.orchestration.gardener import Gardener
    from rich.console import Console
    
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
        os.environ.get("THGENT_RELOAD") == "1",
        "--reload",
        "-r",
        help="Enable hot reload (HMR) for development",
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

    if not force and not reload:
        run_foreground, msg = serve_delegate_or_run(settings)
        if not run_foreground:
            from rich.console import Console

            Console().print(f"[green]{msg}[/green]")
            raise typer.Exit(0)

    run(host=host or settings.mcp_host, port=port or settings.mcp_port, reload=reload)


@app.command("install")
def install_cmd(
    target: str = typer.Option(
        "all", "--target", "-t", help="Target: claude-code|claude-desktop|cursor|codex|droid|all (default: all)"
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
) -> None:
    """Managed installation of thegent components and MCP configuration."""
    from rich.console import Console

    local_console = Console()

    from thegent.install import (
        get_bundle_manifest_path,
        list_bundle_names,
        run_install,
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


if __name__ == "__main__":
    app()
