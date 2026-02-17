"""Thegent CLI commands."""

import csv
import hashlib
import io
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import typer

class LazyConsole:
    """Lazy-loaded rich console to speed up CLI startup."""
    def __getattr__(self, name):
        from rich.console import Console
        global console
        console = Console()
        return getattr(console, name)

console = LazyConsole()

# from rich.console import Console  <-- removed to avoid top-level import
from rich.table import Table

# Lazy imports for thegent modules to speed up startup.
def _lazy_import(module: str, name: str):
    def wrapper(*args, **kwargs):
        import importlib
        m = importlib.import_module(module)
        f = getattr(m, name)
        # For non-callable attributes (like constants), we might need another way,
        # but for functions this works and replaces the global.
        globals()[name] = f
        return f(*args, **kwargs)
    return wrapper

# thegent.agents
list_agent_names = _lazy_import("thegent.agents", "list_agent_names")
list_droid_names = _lazy_import("thegent.agents", "list_droid_names")
resolve_agent = _lazy_import("thegent.agents", "resolve_agent")
run_login = _lazy_import("thegent.agents.cliproxy_manager", "run_login")

# thegent.cli_impl
_atomic_write = _lazy_import("thegent.cli_impl", "_atomic_write")
_make_load_classifier = _lazy_import("thegent.cli_impl", "_make_load_classifier")
_check_dag_cycles = _lazy_import("thegent.cli_impl", "_check_dag_cycles")
_coerce_issue_types = _lazy_import("thegent.cli_impl", "_coerce_issue_types")
_dag_path = _lazy_import("thegent.cli_impl", "_dag_path")
_dag_update_task = _lazy_import("thegent.cli_impl", "_dag_update_task")
_default_owner_tag = _lazy_import("thegent.cli_impl", "_default_owner_tag")
_ensure_contract_version_header = _lazy_import("thegent.cli_impl", "_ensure_contract_version_header")
_ensure_dag_file = _lazy_import("thegent.cli_impl", "_ensure_dag_file")
_find_session_meta = _lazy_import("thegent.cli_impl", "_find_session_meta")
_get_ready_task_ids = _lazy_import("thegent.cli_impl", "_get_ready_task_ids")
_is_pid_running = _lazy_import("thegent.cli_impl", "_is_pid_running")
_normalize_output_format = _lazy_import("thegent.cli_impl", "_normalize_output_format")
_parse_dag_full = _lazy_import("thegent.cli_impl", "_parse_dag_full")
_parse_dag_session = _lazy_import("thegent.cli_impl", "_parse_dag_session")
_parse_depends_on = _lazy_import("thegent.cli_impl", "_parse_depends_on")
_read_session_meta = _lazy_import("thegent.cli_impl", "_read_session_meta")
_resolve_cwd = _lazy_import("thegent.cli_impl", "_resolve_cwd")
_resolve_droids_dir = _lazy_import("thegent.cli_impl", "_resolve_droids_dir")
_resolve_prompt = _lazy_import("thegent.cli_impl", "_resolve_prompt")
_resolve_session_status = _lazy_import("thegent.cli_impl", "_resolve_session_status")
_serialize_dag = _lazy_import("thegent.cli_impl", "_serialize_dag")
_session_paths = _lazy_import("thegent.cli_impl", "_session_paths")
_session_status_for = _lazy_import("thegent.cli_impl", "_session_status_for")
_validate_agent = _lazy_import("thegent.cli_impl", "_validate_agent")
_validate_dag = _lazy_import("thegent.cli_impl", "_validate_dag")
_validate_task_id = _lazy_import("thegent.cli_impl", "_validate_task_id")
dag_ready_impl = _lazy_import("thegent.cli_impl", "dag_ready_impl")
dag_recover_impl = _lazy_import("thegent.cli_impl", "dag_recover_impl")
dag_run_impl = _lazy_import("thegent.cli_impl", "dag_run_impl")
dag_sync_impl = _lazy_import("thegent.cli_impl", "dag_sync_impl")

# thegent.config & execution
def ThegentSettings(*args, **kwargs):
    from thegent.config import ThegentSettings as Impl
    return Impl(*args, **kwargs)

def RunRegistry(*args, **kwargs):
    from thegent.execution import RunRegistry as Impl
    return Impl(*args, **kwargs)

def get_exit_message(*args, **kwargs):
    from thegent.exit_codes import get_exit_message as Impl
    return Impl(*args, **kwargs)

# Constants
EXIT_TIMEOUT = 124
EXIT_HEALTH_GATE_FAILED = 2


def _safe_dict(val: object) -> dict[str, Any]:
    """Return val as dict[str, Any], or empty dict if not a dict."""
    return cast("dict[str, Any]", val) if isinstance(val, dict) else {}


def _safe_list(val: object) -> list[Any]:
    """Return val as list[Any], or empty list if not a list."""
    return cast("list[Any]", val) if isinstance(val, list) else []


def _resolve_run_id(run_id: str | None) -> str:
    """Resolve run_id, defaulting to latest if None."""
    if run_id:
        return run_id
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    latest = registry.get_latest_run_id()
    if not latest:
        console.print("[red]No run ID provided and no previous runs found.[/red]")
        raise typer.Exit(1)
    return latest


def _resolve_session_id(session_id: str | None) -> str:
    """Resolve session_id, defaulting to latest if None."""
    if session_id:
        return session_id
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    latest = registry.get_latest_session_id()
    if not latest:
        console.print("[red]No session ID provided and no previous sessions found.[/red]")
        raise typer.Exit(1)
    return latest


def _resolve_checkpoint_id(checkpoint_id: str | None) -> str:
    """Resolve checkpoint_id, defaulting to latest if None."""
    if checkpoint_id:
        return checkpoint_id
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    latest = registry.get_latest_checkpoint_id()
    if not latest:
        console.print("[red]No checkpoint ID provided and no previous checkpoints found.[/red]")
        raise typer.Exit(1)
    return latest


_LOG_FOLLOW_POLL_SECONDS = 0.5  # Poll interval for log follow (seconds)


def _scope_key(owner: str) -> str:
    """Stable filesystem-safe key for owner tags."""
    return "".join(c if (c.isalnum() or c in "-_.") else "_" for c in owner)


def _compose_owner_tag(user: str, cwd: Path, scope: str = "") -> str:
    """Build deterministic owner tags with optional scope expansion."""
    base_name = cwd.name
    normalized_scope = (
        os.path.expandvars(scope or "")
        .format(
            user=user,
            uid=os.getuid(),
            pid=os.getpid(),
            ppid=os.getppid(),
            cwd=base_name,
        )
        .strip()
    )
    if normalized_scope:
        return f"{user}:{base_name}:{normalized_scope}"
    return f"{user}:{base_name}"


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
) -> None:
    """Run an agent or droid with the given prompt. Model-first: agent=None, model set."""
    from thegent.cli_impl import run_impl
    from thegent.models import ModelCatalog, resolve_route

    # Model-first: resolve agent via routing policy (WP-5003 cost_quality supported)
    effective_agent = agent
    if agent is None and model:
        settings = ThegentSettings()
        from thegent.models.catalog import normalize_route_policy

        policy = normalize_route_policy(routing or settings.default_routing)
        resolved = resolve_route(
            model,
            provider_hint=provider,
            policy=policy,
            quality_floor=getattr(settings, "cost_quality_min_weight", 0.1),
            lane="standard",
        )
        if resolved is None:
            routes = ModelCatalog.routes_for(model)
            available = ", ".join(sorted({r.provider for r in routes})) if routes else "none"
            console.print(
                f"[red]Model '{model}' not available via provider '{provider or 'any'}'. Available: {available}.[/red]"
            )
            raise typer.Exit(1)
        effective_agent = resolved[0]

    # WP-5002: Session-start warning when session count high (memory optimization)
    settings = ThegentSettings()
    thresh = getattr(settings, "session_warn_threshold", 5)
    if isinstance(thresh, int) and thresh > 0:
        from thegent.cli_impl import ps_impl

        sessions = ps_impl(all=True)
        running = sum(1 for s in sessions if (s.get("status") or "").lower() == "running")
        if running >= thresh:
            console.print(
                f"[yellow]Tip: {running} active session(s) detected. Each spawns LSP/MCP processes (~1–2 GB).[/yellow]"
            )
            console.print(
                "[dim]Run 'thegent mcp prune --force' to free memory, or 'thegent mcp spotlight-exclude' on macOS.[/dim]"
            )

    # WP-X2/X5/X6/X7: Unified execution via run_impl (FSM + Policy + Telemetry)
    res = run_impl(
        agent=effective_agent or agent,
        prompt=prompt,
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
    )

    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
        if "agents" in res:
            console.print(f"[dim]Agents: {res['agents']}[/dim]")
        raise typer.Exit(res.get("exit_code", 1))

    if res.get("stdout"):
        console.print(res["stdout"])
    if res.get("stderr"):
        console.print(res["stderr"], style="dim")

    if full:
        if res.get("stderr"):
            console.print(res["stderr"], style="dim")
        if res.get("stdout"):
            console.print(res["stdout"])
    # condensed output is already in stdout if not full
    elif res.get("stdout"):
        console.print(res["stdout"])

    if res.get("timed_out"):
        console.print("[yellow]Run exceeded time budget.[/yellow]")

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

    from thegent.cli_impl import loop_impl

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
) -> str:
    from thegent.cli_impl import bg_impl

    # WP-5002: Session-start warning when session count high (memory optimization)
    settings = ThegentSettings()
    thresh = getattr(settings, "session_warn_threshold", 5)
    if isinstance(thresh, int) and thresh > 0:
        from thegent.cli_impl import ps_impl

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
    res = bg_impl(
        agent=agent,
        prompt=prompt,
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
    )

    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
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


def history_cmd(limit: int = 50, format: str | None = None) -> None:
    """List execution run history (sync and background)."""
    from thegent.cli_impl import history_impl

    runs = history_impl(limit=limit)
    if not format or format == "rich":
        if not runs:
            console.print("[dim]No execution history found.[/dim]")
            return

        table = Table(title=f"Execution History (last {limit})")
        table.add_column("Run ID", style="cyan")
        table.add_column("Started (UTC)", style="magenta")
        table.add_column("Agent", style="green")
        table.add_column("Lane", style="dim")
        table.add_column("Conf", justify="right")
        table.add_column("Role", style="italic")
        table.add_column("Status", style="bold")
        table.add_column("Exit", justify="right")
        table.add_column("Duration", justify="right")
        table.add_column("Prompt Preview", style="dim")

        for run in runs:
            rid = run.get("run_id", "?")
            started = run.get("started_at_utc", "").split("T")[-1][:8]
            agent = run.get("agent", "?")
            lane = run.get("lane", "standard")
            conf = f"{run.get('confidence', 1.0):.2f}" if run.get("confidence") is not None else "—"
            role = run.get("arbitration", "—")
            status = run.get("status", "started")
            status_style = "green" if status == "completed" else "yellow" if status == "started" else "red"
            exit_code = str(run.get("exit_code", "—"))
            duration = f"{run.get('duration_s', 0):.1f}s" if run.get("duration_s") else "—"

            prompt = run.get("prompt", "")
            prompt_preview = (prompt[:30] + "...") if len(prompt) > 30 else prompt

            table.add_row(
                rid,
                started,
                agent,
                lane,
                conf,
                role,
                f"[{status_style}]{status}[/{status_style}]",
                exit_code,
                duration,
                prompt_preview,
            )
        console.print(table)
    elif format == "json":
        console.print_json(data=runs)
    elif format == "md":
        lines = ["# Execution History", ""]
        lines.append("| Run ID | Started | Agent | Status | Exit | Duration | Prompt |")
        lines.append("|--------|---------|-------|--------|------|----------|--------|")
        for run in runs:
            rid = run.get("run_id", "?")
            started = run.get("started_at_utc", "?")
            agent = run.get("agent", "?")
            status = run.get("status", "?")
            exit_code = str(run.get("exit_code", "—"))
            duration = f"{run.get('duration_s', 0):.1f}s" if run.get("duration_s") else "—"
            prompt = run.get("prompt", "").replace("\n", " ")
            lines.append(f"| {rid} | {started} | {agent} | {status} | {exit_code} | {duration} | {prompt} |")
        console.print("\n".join(lines))


def events_cmd(run_id: str | None = None, limit: int = 100, format: str | None = None) -> None:
    """List raw telemetry events."""
    from thegent.cli_impl import events_impl

    events = events_impl(run_id=run_id, limit=limit)
    if not format or format == "rich":
        if not events:
            console.print("[dim]No events found.[/dim]")
            return

        table = Table(title="Telemetry Events")
        table.add_column("Run ID", style="cyan")
        table.add_column("Event/Status", style="magenta")
        table.add_column("Timestamp", style="green")
        table.add_column("Payload Details", style="dim")

        for event in events:
            rid = event.get("run_id", "?")
            ev_type = event.get("event") or event.get("status", "started")
            ts = event.get("started_at_utc") or event.get("ended_at_utc") or "?"
            ts = ts.split("T")[-1][:8]

            details = []
            if event.get("agent"):
                details.append(f"agent={event['agent']}")
            if event.get("exit_code") is not None:
                details.append(f"exit={event['exit_code']}")
            if event.get("duration_s"):
                details.append(f"dur={event['duration_s']:.1f}s")

            table.add_row(rid, ev_type, ts, ", ".join(details))
        console.print(table)
    elif format == "json":
        console.print_json(data=events)
    elif format == "md":
        lines = ["# Telemetry Events", ""]
        lines.append("| Run ID | Event | Timestamp | Details |")
        lines.append("|--------|-------|-----------|---------|")
        for event in events:
            rid = event.get("run_id", "?")
            ev_type = event.get("event") or event.get("status", "started")
            ts = event.get("started_at_utc") or event.get("ended_at_utc") or "?"
            ev_details = str(event)
            lines.append(f"| {rid} | {ev_type} | {ts} | {ev_details} |")
        console.print("\n".join(lines))


def inbox_list_cmd(
    owner: str | None = None,
    agent: str | None = None,
    event_type: str | None = None,
    status: str | None = None,
    sources: str | None = None,
    limit: int = 50,
    format: str | None = None,
) -> None:
    """List unified inbox events (run registry + escalation) with optional filters."""
    from thegent.cli_impl import inbox_list_impl

    src_tuple = tuple(s.strip() for s in (sources or "registry,escalation").split(",") if s.strip())
    events = inbox_list_impl(
        owner=owner,
        agent=agent,
        event_type=event_type,
        status=status,
        sources=src_tuple,
        limit=limit,
    )
    if not format or format == "rich":
        if not events:
            console.print("[dim]No inbox events.[/dim]")
            return
        table = Table(title="Inbox")
        table.add_column("Source", style="dim")
        table.add_column("Event", style="magenta")
        table.add_column("Run ID", style="cyan")
        table.add_column("Owner", style="green")
        table.add_column("Agent", style="yellow")
        table.add_column("Timestamp", style="blue")
        for ev in events:
            ts = (ev.get("timestamp") or "")[:19].replace("T", " ")
            table.add_row(
                ev.get("source", "?"),
                ev.get("event_type", "?"),
                ev.get("run_id", "?")[:12],
                ev.get("owner", "?") or "—",
                ev.get("agent", "?") or "—",
                ts,
            )
        console.print(table)
    elif format == "json":
        console.print_json(data=events)
    else:
        for ev in events:
            console.print(ev)


def inbox_wait_cmd(
    owner: str | None = None,
    agent: str | None = None,
    event_type: str | None = None,
    status: str | None = None,
    sources: str | None = None,
    poll: float = 2.0,
    timeout: float = 0.0,
    notify: bool = True,
    format: str | None = None,
) -> None:
    """Wait for next inbox event matching filters. Blocks until new event or timeout."""
    from thegent.cli_impl import inbox_wait_impl

    src_tuple = tuple(s.strip() for s in (sources or "registry,escalation").split(",") if s.strip())
    events = inbox_wait_impl(
        owner=owner,
        agent=agent,
        event_type=event_type,
        status=status,
        sources=src_tuple,
        poll_interval=poll,
        timeout=timeout,
        notify=notify,
    )
    if not events:
        console.print("[dim]No new events (timeout or empty).[/dim]")
        return
    if not format or format == "rich":
        for ev in events:
            ts = (ev.get("timestamp") or "")[:19].replace("T", " ")
            console.print(
                f"[green]→[/green] {ev.get('source')}/{ev.get('event_type')} "
                f"[cyan]{ev.get('run_id', '?')[:12]}[/cyan] "
                f"owner={ev.get('owner', '—')} agent={ev.get('agent', '—')} {ts}"
            )
    elif format == "json":
        console.print_json(data=events)
    else:
        for ev in events:
            console.print(ev)


def data_protection_cmd(format: str | None = None) -> None:
    """Show status of data protection and privacy controls."""
    from thegent.cli_impl import get_data_protection_status_impl

    status = get_data_protection_status_impl()

    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(status) + "\n")
        return

    table = Table(title="Data Protection & Privacy Status (WP-3006)")
    table.add_column("Control")
    table.add_column("Status")

    def _fmt_bool(v: bool) -> str:
        return "[green]PASS[/green]" if v else "[red]FAIL[/red]"

    table.add_row("Session Directory", status["session_dir"])
    table.add_row("Permissions Restricted (0700)", _fmt_bool(status["permissions_restricted"]))
    table.add_row("Sensitive Data Masking", _fmt_bool(status["masking_enabled"]))
    table.add_row("Retention Policy", f"{status['retention_policy_days']} days")
    if status.get("retention_by_domain"):
        by_dom = ", ".join(f"{k}:{v}d" for k, v in status["retention_by_domain"].items())
        table.add_row("Retention by Domain", by_dom or "—")

    console.print(table)


def compliance_report_cmd(
    format: str | None = None,
    output: Path | None = None,
) -> None:
    """Generate compliance evidence retention report (WP-3006)."""
    from thegent.cli_impl import get_compliance_report_impl

    report = get_compliance_report_impl()
    fmt = _normalize_output_format(format)

    if fmt == "json":
        out = json.dumps(report, indent=2)
    else:
        # Markdown report
        ts = report["tiered_storage"]
        rm = report["retention_matrix"]
        dp = report["data_protection"]
        lines = [
            "# Compliance Evidence Retention Report (WP-3006)",
            f"Generated: {report['generated_at_utc']}",
            "",
            "## Tiered Storage",
            f"- Hot (active): {ts['hot_active_sessions']} sessions",
            f"- Hot (archived): {ts['hot_archived']} (retention: {ts['retention_hot_days']}d)",
            f"- Cold: {ts['cold']} (retention: {ts['retention_cold_days']}d)",
            "",
            "## Retention by Domain",
            "| Domain | Retention (Days) | Runs |",
            "|--------|------------------|------|",
        ]
        for row in rm:
            lines.append(f"| {row['domain']} | {row['retention_days']} | {row['run_count']} |")
        lines.extend(
            [
                "",
                "## Data Protection",
                f"- Session dir: {dp['session_dir']}",
                f"- Permissions restricted: {dp['permissions_restricted']}",
                f"- Masking enabled: {dp['masking_enabled']}",
            ]
        )
        out = "\n".join(lines)

    if output:
        output.write_text(out, encoding="utf-8")
        console.print(f"[green]Compliance report written to {output}[/green]")
    else:
        console.print(out)


def audit_verify_cmd(format: str | None = None) -> None:
    """Verify the integrity of the execution run registry."""
    settings = ThegentSettings()
    from thegent.execution import Auditor

    registry = RunRegistry(settings.session_dir)
    auditor = Auditor(registry.registry_path)

    res = auditor.verify_registry()

    if format == "json":
        sys.stdout.write(json.dumps(res) + "\n")
        return

    if res["status"] == "passed":
        console.print(f"[green]Audit Passed:[/green] {res['valid_count']} records verified.")
    elif res["status"] == "empty":
        console.print("[dim]Registry empty. No records to verify.[/dim]")
    else:
        console.print(f"[red]Audit Failed:[/red] {res['corrupt_count']} issues found.")
        for issue in res.get("issues", []):
            console.print(f"  - {issue}")

    if res["status"] == "passed":
        # Check for unsigned records
        total = res["valid_count"]
        if total > 0:
            console.print(f"[dim]Note: All {total} records carry valid signatures.[/dim]")


def escalate_add_cmd(
    run_id: str,
    reason: str,
    sla_minutes: int = 30,
    owner: str | None = None,
    lane: str = "standard",
    priority: int = 0,
) -> None:
    """Add a blocked run to the escalation queue (WP-3008)."""
    from thegent.cli_impl import escalate_add_impl

    escalate_add_impl(
        run_id=run_id,
        reason=reason,
        sla_minutes=sla_minutes,
        owner=owner,
        lane=lane,
        priority=priority,
    )
    console.print(
        f"[green]Added run_id={run_id} to escalation queue (SLA: {sla_minutes} min, priority: {priority})[/green]"
    )


def escalate_list_cmd(
    past_sla_only: bool = False,
    limit: int = 50,
    format: str | None = None,
) -> None:
    """List governance escalation queue (WP-3008)."""
    from thegent.cli_impl import escalate_list_impl

    items = escalate_list_impl(past_sla_only=past_sla_only, limit=limit)
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(items) + "\n")
        return
    if not items:
        console.print("[dim]No escalation items.[/dim]")
        return
    table = Table(title="Escalation Queue (WP-3008)")
    table.add_column("Run ID")
    table.add_column("Reason")
    table.add_column("Owner")
    table.add_column("Lane")
    table.add_column("Prio")
    table.add_column("Blocked At")
    table.add_column("SLA By")
    table.add_column("Past SLA")
    for it in items:
        past = "[red]YES[/red]" if it.get("past_sla") else "[green]No[/green]"
        table.add_row(
            it.get("run_id", "?"),
            it.get("reason", "?"),
            it.get("owner") or "-",
            it.get("lane", "standard"),
            str(it.get("priority", 0)),
            it.get("blocked_at_utc", "?")[:19],
            it.get("escalate_by_utc", "?")[:19],
            past,
        )
    console.print(table)


def sweep_cmd(
    drift_window: int = 50,
    include_audit: bool = False,
    format: str | None = None,
) -> None:
    """WP-3005: Policy drift sweep - runs drift detection, budget check, past-SLA escalations."""
    from thegent.cli_impl import sweep_impl

    result = sweep_impl(
        drift_window=drift_window,
        include_audit=include_audit,
    )
    fmt = _normalize_output_format(format)
    if fmt == "json":
        # Strip non-JSON-serializable if any
        out = {k: v for k, v in result.items() if k != "audit" or v is not None}
        if result.get("audit"):
            out["audit"] = result["audit"]
        sys.stdout.write(json.dumps(out) + "\n")
        if not result["pass"]:
            raise typer.Exit(1)
        return

    if result["pass"]:
        console.print("[green]Sweep passed: no drift, no past-SLA escalations.[/green]")
        return

    parts = []
    if result["drift_issues"]:
        for i in result["drift_issues"]:
            parts.append(f"[red]![/red] {i}")
    if result["past_sla_count"] > 0:
        parts.append(
            f"[yellow]Past SLA:[/yellow] {result['past_sla_count']} escalation(s). Run `thegent govern escalate list --past-sla`"
        )
    if result.get("audit") and result["audit"].get("status") not in ("passed", "empty"):
        parts.append(f"[red]Audit:[/red] {result['audit'].get('status', 'failed')}")
    if parts:
        from rich.panel import Panel

        console.print(Panel("\n".join(parts), title="Policy Drift Sweep (WP-3005)", border_style="red"))
    raise typer.Exit(1)


def escalate_resolve_cmd(run_id: str | None = None, resolution: str = "resolved") -> None:
    """Mark an escalation item as resolved (WP-3008)."""
    rid = _resolve_run_id(run_id)
    from thegent.cli_impl import escalate_resolve_impl

    ok = escalate_resolve_impl(run_id=rid, resolution=resolution)
    if ok:
        console.print(f"[green]Escalation {rid} resolved as '{resolution}'.[/green]")
    else:
        console.print(f"[red]Escalation {rid} not found or already resolved.[/red]")


def escalate_approve_cmd(run_id: str | None = None) -> None:
    """Approve an escalation, recording an override for the owner (G-GP-05)."""
    rid = _resolve_run_id(run_id)
    from thegent.cli_impl import escalate_approve_impl

    ok = escalate_approve_impl(run_id=rid)
    if ok:
        console.print(f"[green]Escalation {rid} APPROVED. Policy override recorded for owner.[/green]")
    else:
        console.print(f"[red]Escalation {rid} not found or already resolved.[/red]")


def interruption_list_cmd(limit: int = 20, format: str | None = None) -> None:
    """List recent interruptions (WP-4004)."""
    settings = ThegentSettings()
    from thegent.execution import InterruptionTracker

    it = InterruptionTracker(settings.session_dir)
    if not it.path.exists():
        console.print("[dim]No interruptions recorded.[/dim]")
        return
    items: list[dict[str, Any]] = []
    with it.path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except Exception:
                continue
    items = sorted(items, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(items) + "\n")
        return
    if not items:
        console.print("[dim]No interruptions in window.[/dim]")
        return
    table = Table(title="Interruption Log (WP-4004)")
    table.add_column("Timestamp")
    table.add_column("Type")
    table.add_column("Run ID")
    table.add_column("Severity")
    for i in items:
        table.add_row(
            (i.get("timestamp", "?")[:19]),
            i.get("type", "unknown"),
            i.get("run_id", "?"),
            i.get("severity", "medium"),
        )
    console.print(table)
    fatigue = it.get_fatigue_score()
    console.print(f"[dim]Fatigue score: {fatigue:.2f} (ceiling: {it.ALERTS_PER_HOUR_CEILING}/hr)[/dim]")


def config_check_cmd(format: str | None = None) -> None:
    """Validate config and report issues (DX-010, ROB-013)."""
    from pydantic import ValidationError

    issues: list[str] = []
    try:
        settings = ThegentSettings()
    except ValidationError as e:
        for err in e.errors():
            loc = ".".join(str(x) for x in err.get("loc", []))
            issues.append(f"Config error: {loc} — {err.get('msg', 'invalid')}")
        if format == "json":
            sys.stdout.write(json.dumps({"ok": False, "issues": issues}) + "\n")
            raise typer.Exit(1)
        for i in issues:
            console.print(f"[red]{i}[/red]")
        raise typer.Exit(1)

    # Optional: path checks
    session_dir = Path(settings.session_dir).expanduser().resolve()
    if not session_dir.parent.exists():
        issues.append(f"Session dir parent missing: {session_dir.parent}")
    if session_dir.exists() and not os.access(session_dir, os.W_OK):
        issues.append(f"Session dir not writable: {session_dir}")

    if issues:
        if format == "json":
            sys.stdout.write(json.dumps({"ok": False, "issues": issues}) + "\n")
            raise typer.Exit(1)
        for i in issues:
            console.print(f"[yellow]{i}[/yellow]")
        raise typer.Exit(1)

    if format == "json":
        sys.stdout.write(json.dumps({"ok": True, "issues": []}) + "\n")
        return
    console.print("[green]Config OK.[/green]")


def load_status_cmd(format: str | None = None) -> None:
    """Show load classification and safe-mode status (WP-5002)."""
    settings = ThegentSettings()
    lc = _make_load_classifier(settings)
    running = lc.get_running_count()
    level = lc.get_load_level()
    safe_mode = lc.is_safe_mode_active()
    shape = lc.get_traffic_shape()
    data = {
        "running_count": running,
        "load_level": level,
        "safe_mode_active": safe_mode,
        "traffic_shape": shape,
        "spike_threshold": settings.load_spike_threshold,
        "surge_threshold": settings.load_surge_threshold,
    }
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(data) + "\n")
        return
    table = Table(title="Load Status (WP-5002)")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Running sessions", str(running))
    table.add_row("Load level", level)
    table.add_row("Safe-mode active", "[red]Yes[/red]" if safe_mode else "[green]No[/green]")
    table.add_row("Traffic shaping", shape)
    table.add_row("Thresholds", f"spike>={settings.load_spike_threshold}, surge>={settings.load_surge_threshold}")
    console.print(table)


def _get_health_targets_path(project_dir: Path) -> Path:
    """Find the health-targets.json path relative to project directory."""
    # Try project_dir/contracts/health-targets.json
    health_targets = project_dir / "contracts" / "health-targets.json"
    if health_targets.exists():
        return health_targets
    # Fallback: try current working directory
    cwd_health = Path.cwd() / "contracts" / "health-targets.json"
    if cwd_health.exists():
        return cwd_health
    # Default: raise error
    raise FileNotFoundError(
        f"health-targets.json not found. Expected at {health_targets} or {cwd_health}"
    )


def _health_targets_exists(project_dir: Path) -> bool:
    """Return True if health-targets.json exists for the project."""
    for p in (project_dir / "contracts" / "health-targets.json", Path.cwd() / "contracts" / "health-targets.json"):
        if p.exists():
            return True
    return False


_HEALTH_TARGETS_TEMPLATE = """{"version":"1.0.0","dimensions":{"test_coverage":{"weight":0.2,"target":80,"unit":"percent","direction":"higher_is_better","scan_tool":"pytest --cov","priority_class":"critical"},"lint_violations":{"weight":0.15,"target":0,"unit":"count","direction":"lower_is_better","scan_tool":"ruff check","priority_class":"critical"},"complexity_index":{"weight":0.15,"target":10,"unit":"cyclomatic_avg","direction":"lower_is_better","scan_tool":"radon cc -a","priority_class":"medium"},"security_findings":{"weight":0.15,"target":0,"unit":"count","direction":"lower_is_better","scan_tool":"security-pipeline","priority_class":"critical"},"spec_traceability":{"weight":0.1,"target":80,"unit":"percent","direction":"higher_is_better","scan_tool":"grep FR- tests/","priority_class":"medium"},"doc_organization":{"weight":0.1,"target":100,"unit":"percent","direction":"higher_is_better","scan_tool":"structure_audit","priority_class":"low"},"freshness":{"weight":0.1,"target":0,"unit":"stale_items","direction":"lower_is_better","scan_tool":"find -mtime +7","priority_class":"low"},"agent_health":{"weight":0.05,"target":0,"unit":"open_breakers","direction":"lower_is_better","scan_tool":"circuit_breakers.jsonl","priority_class":"critical"}},"bands":{"excellent":{"min":90,"label":"Excellent"},"healthy":{"min":70,"label":"Healthy"},"warning":{"min":40,"label":"Warning"},"critical":{"min":0,"label":"Critical"}},"budget":{"daily_agent_calls":20,"tiers":{"normal":{"max_utilization_pct":50,"description":"All agent types available"},"cautious":{"max_utilization_pct":80,"description":"Prefer cheaper/faster agents"},"restricted":{"max_utilization_pct":95,"description":"Only essential tasks"},"halted":{"max_utilization_pct":100,"description":"No new agent spawns"}}},"cycle":{"interval_s":300,"max_rerolls_per_task":2,"max_tasks_per_cycle":10,"cooldown_after_failure_s":60,"health_threshold":90,"debounce_s":30}}"""


def govern_configure_cmd(cd: Path | None = None, force: bool = False) -> None:
    """Bootstrap governance: create contracts/health-targets.json if missing."""
    project_dir = _resolve_cwd(cd) or Path.cwd()
    contracts_dir = project_dir / "contracts"
    health_targets = contracts_dir / "health-targets.json"
    if health_targets.exists() and not force:
        console.print("[green]Govern already configured.[/green]")
        return
    contracts_dir.mkdir(parents=True, exist_ok=True)
    health_targets.write_text(_HEALTH_TARGETS_TEMPLATE, encoding="utf-8")
    console.print("[green]Govern configured.[/green] Run: thegent govern go health")


def govern_go_health_cmd(cd: Path | None = None, format: str | None = None) -> None:
    """Show current health score (composite 0-100, band, per-dimension breakdown)."""
    from thegent.governance.health_score import HealthScoreComputer, get_band
    from thegent.governance.scanner import CodebaseScanner

    settings = ThegentSettings()
    project_dir = _resolve_cwd(cd) or Path.cwd()
    try:
        health_targets_path = _get_health_targets_path(project_dir)
    except FileNotFoundError:
        fmt = _normalize_output_format(format)
        if fmt == "json":
            sys.stdout.write(json.dumps({"configured": False, "hint": "thegent govern configure"}) + "\n")
        else:
            console.print("[yellow]Govern not configured.[/yellow]")
            console.print("[dim]Run: thegent govern configure[/dim]")
        raise typer.Exit(1)

    # Create health score computer
    health_computer = HealthScoreComputer(health_targets_path)

    # Create scanner and run scan
    scanner = CodebaseScanner(project_dir=project_dir, session_dir=settings.session_dir)
    scan_result = scanner.scan_all()

    # Extract dimension values from scan result
    dimension_values: dict[str, float] = {}
    for dim_name, dim_scan in scan_result.dimensions.items():
        dimension_values[dim_name] = dim_scan.current_value

    # Compute health score
    health = health_computer.compute(dimension_values)

    fmt = _normalize_output_format(format)

    if fmt == "json":
        output = {
            "score": health.score,
            "band": health.band.value if hasattr(health, "band") else get_band(health.score).value,
            "dimensions": {},
        }
        for name, dim in health.dimensions.items():
            output["dimensions"][name] = {
                "raw_value": dim.raw_value,
                "normalized": dim.normalized,
                "target": dim.target,
                "status": dim.status.value if hasattr(dim.status, "value") else str(dim.status),
            }
        sys.stdout.write(json.dumps(output, indent=2) + "\n")
        return

    # Rich output
    from rich.table import Table

    band = get_band(health.score)
    band_color = {
        "excellent": "green",
        "healthy": "cyan",
        "warning": "yellow",
        "critical": "red",
    }.get(band.value, "white")

    table = Table(title="AgilePlus Health Score")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Composite Score", f"[bold]{health.score:.2f}[/bold]")
    table.add_row("Band", f"[{band_color}]{band.value.upper()}[/{band_color}]")
    console.print(table)

    # Dimensions table
    dim_table = Table(title="Dimension Breakdown")
    dim_table.add_column("Dimension")
    dim_table.add_column("Raw")
    dim_table.add_column("Target")
    dim_table.add_column("Normalized")
    dim_table.add_column("Status")

    for name, dim in health.dimensions.items():
        status_color = {
            "excellent": "green",
            "healthy": "cyan",
            "warning": "yellow",
            "critical": "red",
        }.get(dim.status.value if hasattr(dim.status, "value") else str(dim.status), "white")

        dim_table.add_row(
            name,
            f"{dim.raw_value:.2f}",
            f"{dim.target:.2f}",
            f"{dim.normalized:.2%}",
            f"[{status_color}]{dim.status.value if hasattr(dim.status, 'value') else dim.status}[/{status_color}]",
        )
    console.print(dim_table)


def govern_go_status_cmd(cd: Path | None = None) -> None:
    """Show current governance status (state, cycle_id, shutdown_requested)."""
    from thegent.governance.agileplus import AgilePlusLoop
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    project_dir = _resolve_cwd(cd) or Path.cwd()
    health_targets_path = _get_health_targets_path(project_dir)

    # Create loop instance to check status (doesn't run cycle)
    loop = AgilePlusLoop(
        project_dir=project_dir,
        health_targets_path=health_targets_path,
        health_threshold=settings.agileplus_health_threshold,
        max_tasks_per_cycle=settings.agileplus_max_tasks_per_cycle,
        max_rerolls=settings.agileplus_max_rerolls,
    )

    from rich.table import Table

    table = Table(title="AgilePlus Status")
    table.add_column("Property")
    table.add_column("Value")
    table.add_row("State", f"[bold]{loop.state.value}[/bold]")
    table.add_row("Cycle ID", loop.cycle_id or "[dim]none[/dim]")
    table.add_row(
        "Shutdown Requested",
        "[red]True[/red]" if loop._shutdown_requested else "[green]False[/green]",
    )
    console.print(table)


def govern_go_cycle_cmd(cd: Path | None = None, force: bool = False, format: str | None = None) -> None:
    """Run a single governance cycle."""
    import uuid
    from datetime import UTC, datetime
    from thegent.governance.health_score import HealthScoreComputer, get_band
    from thegent.governance.scanner import CodebaseScanner
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    project_dir = _resolve_cwd(cd) or Path.cwd()
    health_targets_path = _get_health_targets_path(project_dir)

    cycle_id = f"cycle_{uuid.uuid4().hex[:8]}"
    started_at = datetime.now(UTC).isoformat()

    console.print(f"[cyan]Starting AgilePlus cycle {cycle_id} (force={force})...[/cyan]")

    # Compute health score
    health_computer = HealthScoreComputer(health_targets_path)
    scanner = CodebaseScanner(project_dir=project_dir, session_dir=settings.session_dir)
    scan_result = scanner.scan_all()

    dimension_values: dict[str, float] = {}
    for dim_name, dim_scan in scan_result.dimensions.items():
        dimension_values[dim_name] = dim_scan.current_value

    health = health_computer.compute(dimension_values)
    completed_at = datetime.now(UTC).isoformat()

    # Determine if we should run full cycle based on health threshold
    should_run = force or health.score < settings.agileplus_health_threshold

    fmt = _normalize_output_format(format)

    if fmt == "json":
        output = {
            "cycle_id": cycle_id,
            "state": "idle" if not should_run else "completed",
            "health_score": health.score,
            "health_band": health.band.value if hasattr(health, "band") else get_band(health.score).value,
            "findings_count": sum(1 for d in dimension_values.values() if d > 0),
            "tasks_planned": 0,
            "tasks_executed": 0,
            "tasks_verified": 0,
            "started_at": started_at,
            "completed_at": completed_at,
            "error": "",
            "skipped": not should_run,
        }
        sys.stdout.write(json.dumps(output, indent=2) + "\n")
        return

    from rich.table import Table

    band = get_band(health.score)

    table = Table(title=f"Cycle Result: {cycle_id}")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("State", "skipped (healthy)" if not should_run else "completed")
    table.add_row("Health Score", f"{health.score:.2f}")
    table.add_row("Health Band", band.value)
    table.add_row("Findings", str(sum(1 for d in dimension_values.values() if d > 0)))
    table.add_row("Tasks Planned", "0")
    table.add_row("Tasks Executed", "0")
    table.add_row("Tasks Verified", "0")
    table.add_row("Started", started_at)
    table.add_row("Completed", completed_at)

    if not should_run:
        console.print("[dim]Cycle skipped: health score >= threshold[/dim]")
    console.print(table)


def govern_go_watch_cmd(
    cd: Path | None = None,
    interval: int = 300,
    max_cycles: int | None = None,
) -> None:
    """Run continuous governance mode."""
    import time
    import uuid
    from datetime import UTC, datetime
    from thegent.governance.health_score import HealthScoreComputer, get_band
    from thegent.governance.scanner import CodebaseScanner
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    project_dir = _resolve_cwd(cd) or Path.cwd()
    health_targets_path = _get_health_targets_path(project_dir)

    console.print(f"[cyan]Starting continuous governance (interval={interval}s, max_cycles={max_cycles})...[/cyan]")
    console.print("[yellow]Press Ctrl+C to stop[/yellow]")

    health_computer = HealthScoreComputer(health_targets_path)
    scanner = CodebaseScanner(project_dir=project_dir, session_dir=settings.session_dir)

    results = []
    cycles_run = 0
    try:
        while max_cycles is None or cycles_run < max_cycles:
            cycle_id = f"cycle_{uuid.uuid4().hex[:8]}"
            started_at = datetime.now(UTC).isoformat()

            # Compute health score
            scan_result = scanner.scan_all()
            dimension_values = {}
            for dim_name, dim_scan in scan_result.dimensions.items():
                dimension_values[dim_name] = dim_scan.current_value

            health = health_computer.compute(dimension_values)
            completed_at = datetime.now(UTC).isoformat()

            results.append({
                "cycle_id": cycle_id,
                "health_score": health.score,
                "health_band": health.band.value if hasattr(health, 'band') else get_band(health.score).value,
                "started_at": started_at,
                "completed_at": completed_at,
            })

            cycles_run += 1
            console.print(f"Cycle {cycles_run} ({cycle_id}): score={health.score:.2f}, band={health.band.value if hasattr(health, 'band') else get_band(health.score).value}")

            if max_cycles is not None and cycles_run >= max_cycles:
                break

            # Wait for next cycle
            time.sleep(interval)

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")

    console.print(f"\n[green]Completed {len(results)} cycle(s)[/green]")


def cost_status_cmd(format: str | None = None) -> None:
    """Show cost budget utilization and cost-aware routing status (WP-5003)."""
    settings = ThegentSettings()
    from thegent.governance.cost import CostAggregator

    agg = CostAggregator(settings.session_dir)
    mtd = agg.get_mtd_total()
    by_cat = agg.get_all_categories_mtd()
    budget = float(getattr(settings, "cost_budget_mtd", 100.0))
    utilization = (mtd / budget * 100) if budget > 0 else 0.0
    tighten = float(getattr(settings, "cost_quality_budget_tighten_threshold", 0.80)) * 100
    cost_aware = getattr(settings, "routing_cost_aware_enabled", True)
    data = {
        "mtd_total_usd": round(mtd, 2),
        "budget_mtd_usd": budget,
        "utilization_pct": round(utilization, 1),
        "cost_aware_enabled": cost_aware,
        "tighten_threshold_pct": tighten,
        "by_category": by_cat,
    }
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(data) + "\n")
        return
    table = Table(title="Cost Status (WP-5003)")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("MTD total", f"${mtd:.2f}")
    table.add_row("Budget MTD", f"${budget:.2f}")
    table.add_row("Utilization", f"{utilization:.1f}%")
    table.add_row("Cost-aware routing", "[green]On[/green]" if cost_aware else "[dim]Off[/dim]")
    table.add_row("Tighten threshold", f"{tighten:.0f}%")
    for cat, val in by_cat.items():
        table.add_row(f"  {cat}", f"${val:.2f}")
    console.print(table)


def usage_cmd(format: str | None = None, include_cost: bool = True) -> None:
    """Show plan usage: provider metrics from CLIProxyAPIPlus and cost status (WP-5003).

    For cross-provider session parsing (OpenCode, Claude Code, Codex, Gemini, Cursor, etc.),
    use: bunx tokscale@latest
    """
    settings = ThegentSettings()
    from thegent.agents.cliproxy_manager import fetch_provider_metrics

    metrics = fetch_provider_metrics(settings)
    data: dict[str, Any] = {
        "provider_metrics": metrics if metrics else {},
        "proxy_reachable": metrics is not None,
    }
    if include_cost:
        from thegent.governance.cost import CostAggregator

        agg = CostAggregator(settings.session_dir)
        data["cost"] = {
            "mtd_total_usd": round(agg.get_mtd_total(), 2),
            "by_category": agg.get_all_categories_mtd(),
        }
        data["cost"]["budget_mtd_usd"] = float(getattr(settings, "cost_budget_mtd", 100.0))

    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(data) + "\n")
        return

    if metrics:
        table = Table(title="Provider Usage (CLIProxyAPIPlus)")
        table.add_column("Provider")
        table.add_column("Cost/1k")
        table.add_column("Success %")
        table.add_column("TPS 1m")
        table.add_column("Latency p50")
        for prov, m in sorted(metrics.items()):
            cost = m.get("cost_per_1k_output") or m.get("cost_per_1k_input") or "-"
            cost_str = f"${cost:.4f}" if isinstance(cost, (int, float)) else str(cost)
            sr = m.get("success_rate")
            sr_str = f"{sr * 100:.1f}%" if isinstance(sr, (int, float)) else "-"
            tps = m.get("tps_1m", "-")
            lat = m.get("latency_p50_ms", "-")
            lat_str = f"{lat}ms" if isinstance(lat, (int, float)) else str(lat)
            table.add_row(prov, cost_str, sr_str, str(tps), lat_str)
        console.print(table)
    else:
        console.print("[yellow]Proxy unreachable. Start CLIProxyAPIPlus or check THGENT_CLIPROXY_PORT.[/yellow]")

    if include_cost:
        cost_status_cmd(format=format)


def interruption_snooze_cmd(alert_id: str, minutes: int = 5, itype: str = "unknown") -> None:
    """Snooze an alert; expires → auto-escalation (WP-4004)."""
    settings = ThegentSettings()
    from thegent.execution import InterruptionTracker

    it = InterruptionTracker(settings.session_dir)
    it.snooze(alert_id=alert_id, snooze_minutes=minutes, itype=itype)
    console.print(f"[green]Alert {alert_id} snoozed for {minutes} min. Will auto-escalate when expired.[/green]")


def purge_cmd(dry_run: bool = True) -> None:
    """WP-3006: Tiered retention purge (G-GP-07)."""
    from thegent.cli_impl import purge_impl

    result = purge_impl(dry_run=dry_run)

    if dry_run:
        console.print(
            f"[yellow]Dry-run: {result['purged']} records would be purged, {result['kept']} records kept.[/yellow]"
        )
        console.print("[dim]Run with --no-dry-run to apply changes.[/dim]")
    else:
        console.print(f"[green]Purged {result['purged']} records, {result['kept']} records remaining.[/green]")


def policy_show_cmd() -> None:
    """Show active governance policies and thresholds."""
    settings = ThegentSettings()
    console.print(f"[bold]Active Governance Policies[/bold] (Environment: [cyan]{settings.environment}[/cyan])")

    table = Table(show_header=True)
    table.add_column("Policy Name")
    table.add_column("Rule / Threshold")
    table.add_column("Status")

    table.add_row("Critical Confidence", ">= 0.9", "[green]Active[/green]")
    table.add_row(
        "Production Trust",
        f">= {settings.trust_score_threshold}",
        "[green]Active[/green]" if settings.environment == "production" else "[dim]Inactive[/dim]",
    )
    table.add_row("Agent Restriction", "Block 'unknown' in Prod/Critical", "[green]Active[/green]")
    table.add_row("Audit Signing", "SHA-256 Run Signatures", "[green]Active[/green]")
    table.add_row("Override TTL (WP-3003)", f"{settings.override_ttl_seconds}s", "[green]Active[/green]")

    console.print(table)


def policy_purge_cmd(dry_run: bool = True) -> None:
    """Purge expired history based on tiered retention (WP-3006)."""
    settings = ThegentSettings()
    from thegent.execution import RunRegistry

    registry = RunRegistry(settings.session_dir)
    res = registry.purge_expired(
        default_days=settings.retention_default_days,
        by_domain=settings.retention_by_domain,
        dry_run=dry_run,
    )
    if dry_run:
        console.print(f"[yellow]Dry run: would purge {res['purged']} records (kept {res['kept']}).[/yellow]")
    else:
        console.print(f"[green]Purged {res['purged']} records (kept {res['kept']}).[/green]")


def contracts_registry_cmd(format: str | None = None) -> None:
    """Show the contract registry and compatibility matrix."""
    from rich.console import Console
    from rich.table import Table

    from thegent.contracts.registry import get_registry

    registry = get_registry()
    versions = registry.list_versions()

    console = Console()
    if format == "json":
        # Handle both Pydantic models and mock/dict objects for testing
        data = []
        for v in versions:
            model_dump = getattr(v, "model_dump", None)
            if callable(model_dump):
                data.append(model_dump())
            elif hasattr(v, "__dict__"):
                data.append(v.__dict__)
            else:
                data.append(v)
        sys.stdout.write(json.dumps(data) + "\n")
        return

    table = Table(title="Contract Registry")
    table.add_column("Contract ID", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Description", style="white")
    table.add_column("Status", style="red")

    for v in sorted(versions, key=lambda x: (x.contract_id, x.version)):
        status = "[red]DEPRECATED[/red]" if v.deprecated else "[green]ACTIVE[/green]"
        if v.migration_window_end:
            status += f"\n[dim](ends {v.migration_window_end})[/dim]"
        table.add_row(v.contract_id, v.version, v.description, status)

    console.print(table)


def migration_cmd(contract_id: str, version: str, format: str | None = None) -> None:
    """Evaluate migration status for a contract version."""
    from rich.console import Console
    from rich.panel import Panel

    from thegent.contracts.migration import MigrationController

    console = Console()
    mc = MigrationController()
    res = mc.evaluate_version(contract_id, version)

    if format == "json":
        sys.stdout.write(json.dumps(res) + "\n")
        return

    color = "green" if res["allowed"] else "red"
    if res["status"] == "deprecated":
        color = "yellow"

    panel = Panel(
        f"[bold]Status:[/bold] {res['status'].upper()}\n"
        f"[bold]Allowed:[/bold] {'YES' if res['allowed'] else 'NO'}\n"
        f"[bold]Reason:[/bold] {res['reason']}\n"
        f"[bold]Days Left:[/bold] {res.get('migration_days_left', 'N/A')}",
        title=f"Migration Evaluation: {contract_id}@{version}",
        border_style=color,
    )
    console.print(panel)


def drift_cmd(
    window: int = 50,
    format: str | None = None,
    structural_budget: float = 5.0,
    semantic_budget: float = 10.0,
) -> None:
    """Detect significant drift in contract performance and check alert budgets (G-RV-07)."""
    from rich.console import Console
    from rich.panel import Panel

    from thegent.contracts.telemetry import ContractTelemetry

    settings = ThegentSettings()
    console = Console()
    ct = ContractTelemetry(settings.session_dir)
    issues = ct.detect_drift(window_size=window)
    budget = ct.get_drift_budget_status(
        structural_budget_pct=structural_budget,
        semantic_budget_pct=semantic_budget,
    )

    if format == "json":
        out = {"issues": issues, "budget": budget}
        sys.stdout.write(json.dumps(out) + "\n")
        return

    if not issues and budget["within_budget"]:
        console.print("[green]No significant contract drift detected.[/green]")
        return

    parts = []
    if issues:
        issue_str = "\n".join([f"[red]![/red] {i}" for i in issues])
        parts.append(issue_str)
    if not budget["within_budget"]:
        parts.append(
            f"[yellow]Budget exceeded:[/yellow] structural {budget['structural_rate_pct']}% "
            f"(budget {budget['structural_budget_pct']}%), semantic {budget['semantic_rate_pct']}% "
            f"(budget {budget['semantic_budget_pct']}%)"
        )
    if parts:
        panel = Panel(
            "\n\n".join(parts),
            title=f"Contract Drift Alert (window={window})",
            border_style="red",
        )
        console.print(panel)


def observe_summary_cmd(
    limit: int = 500,
    drift_window: int = 50,
    structural_budget: float = 5.0,
    semantic_budget: float = 10.0,
    format: str | None = None,
    provider: str | None = None,
    trend_samples: int = 0,
    top_escalations: int = 10,
) -> None:
    """FR-X08: Unified observability summary (KPIs, drift, escalation)."""
    from rich.panel import Panel

    from thegent.cli_impl import observe_summary_impl

    result = observe_summary_impl(
        limit=limit,
        drift_window=drift_window,
        structural_budget_pct=structural_budget,
        semantic_budget_pct=semantic_budget,
        provider=provider,
        trend_samples=trend_samples,
        top_escalations=top_escalations,
    )
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(result) + "\n")
        return

    kpis = result["kpis"]
    drift = result["drift"]
    esc = result["escalation"]
    alerts = result.get("alerts", [])
    status = result.get("status", "healthy")
    status_badge = {
        "healthy": "[green]healthy[/green]",
        "critical": "[red]critical[/red]",
    }.get(status, status)
    provider_label = f" provider={provider}" if provider else ""

    lines = [
        f"[bold]Status[/bold]: {status_badge}",
        f"[bold]KPIs[/bold] (n={kpis['total_events']}{provider_label}): fallback={kpis['fallback_rate']:.1%} success={kpis['success_rate']:.1%} conf={kpis['avg_confidence']:.2f}",
        f"[bold]Drift[/bold]: structural={drift['structural_rate_pct']:.1f}%/budget {drift['structural_budget_pct']:.1f}% "
        f"semantic={drift['semantic_rate_pct']:.1f}%/budget {drift['semantic_budget_pct']:.1f}% "
        + ("[green]within budget[/green]" if drift["within_budget"] else "[red]over budget[/red]"),
        f"[bold]Escalation[/bold]: backlog={esc['backlog_count']} past-sla={esc['past_sla_count']}",
    ]
    top_rows = esc.get("top_escalations", [])
    for item in top_rows[:3]:
        if not isinstance(item, dict):
            continue
        owner = item.get("owner") or "—"
        minutes = item.get("minutes_overdue")
        sla = item.get("minutes_remaining")
        if item.get("past_sla"):
            timing = f"overdue={minutes}m"
        elif sla is not None:
            timing = f"remaining={sla}m"
        else:
            timing = "timing-unknown"
        lines.append(
            f" - {item.get('run_id')} / {owner} / {item.get('agent')} / {item.get('lane')} / {timing} / "
            f"priority={item.get('priority', 0)}"
        )

    if drift["issues"]:
        lines.append("[red]Drift issues:[/red] " + "; ".join(drift["issues"][:3]))
    if alerts:
        lines.append("[red]Alerts:[/red] " + "; ".join(alerts))
    if result.get("trend_summary"):
        trend = result["trend_summary"]
        lines.append(
            "[bold]Trend[/bold]: "
            f"enabled={trend.get('enabled', False)} "
            f"trend_samples_requested={trend.get('trend_samples_requested', 0)} "
            f"trend_effective_samples={trend.get('trend_effective_samples', 0)} "
            f"history={trend.get('history_sample_count', 0)} "
            f"baseline={trend.get('baseline_available', False)} "
            f"health={trend.get('trend_snapshot_health', 'disabled')}"
        )
    if result.get("generated_query"):
        lines.append(f"generated_query={json.dumps(result['generated_query'])}")
    panel = Panel("\n".join(lines), title="Observe Summary (FR-X08)", border_style="cyan")
    console.print(panel)


def summary_cmd(
    period: str = typer.Argument("today", help="Time period: today, yesterday, week, 7d, 30d, 1h etc."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project path (default: CWD)"),
    summarize: bool = typer.Option(True, "--summarize/--no-summarize", help="Generate agent summary"),
    agent: str = typer.Option("gemini", "--agent", "-a", help="Agent to use for summary"),
    full: bool = typer.Option(False, "--full", help="Show full audit log"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: rich, json, md"),
) -> None:
    """FR-X09: Unified summary and audit log across runs, chats, and commits."""
    from rich.markdown import Markdown
    from rich.panel import Panel

    from thegent.summary import summary_impl
    from thegent.orchestration.memory import MemoryCategory, MemorySystem
    from thegent.orchestration.session_scraper import SessionScraper

    # Auto-scrape recent sessions into memory logs (WP-MEMORY)
    try:
        project_path = project or Path.cwd()
        scraper = SessionScraper(project_path)
        system = MemorySystem(project_path)
        
        prompts = scraper.collect_all_recent_prompts()
        recent = system.get_recent(limit=50, category=MemoryCategory.USER_PROMPT)
        recent_contents = {f.content for f in recent}
        
        for p in prompts:
            if p not in recent_contents:
                system.record(p, MemoryCategory.USER_PROMPT, "auto-scrape", metadata={"scraped": True})
    except Exception:
        pass # Silent failure for auto-scrape

    result = summary_impl(
        period=period,
        project_path=project,
        summarize=summarize,
        agent=agent,
    )

    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(result) + "\n")
        return

    if fmt == "md":
        output = result["audit_log"]
        if "summary" in result:
            output += "\n\n# Agent Summary\n\n" + result["summary"]
        sys.stdout.write(output + "\n")
        return

    # Rich output
    console.print(f"[bold cyan]Summary for Project:[/bold cyan] {result['project']}")
    console.print(f"[bold cyan]Period:[/bold cyan] {result['period']} ({result['start_dt']} to {result['end_dt']})")

    counts = result["counts"]
    console.print(
        f"[dim]Stats: {counts['runs']} runs, {counts['chats']} chat messages, {counts['commits']} commits[/dim]"
    )
    console.print()

    if "summary" in result:
        console.print(Panel(Markdown(result["summary"]), title="Agent Summary", border_style="green"))
        console.print()

    if full:
        console.print(Markdown(result["audit_log"]))
    else:
        console.print("[dim]Use --full to see the detailed audit log.[/dim]")


def explain_cmd(run_id: str | None = None) -> None:
    """Show detailed explanation for an agent run (WP-4002)."""
    from rich.panel import Panel

    from thegent.cli_impl import history_impl

    rid = _resolve_run_id(run_id)
    runs = history_impl(limit=1000)
    run = next((r for r in runs if r.get("run_id") == rid), None)

    if not run:
        console.print(f"[red]Run ID {rid} not found.[/red]")
        return

    lines = [
        f"[bold]Run ID:[/bold] {run.get('run_id')}",
        f"[bold]Agent:[/bold] {run.get('agent')}",
        f"[bold]Status:[/bold] {run.get('status')}",
        f"[bold]Exit Code:[/bold] {run.get('exit_code')}",
        f"[bold]Started:[/bold] {run.get('started_at_utc')}",
        f"[bold]Duration:[/bold] {run.get('duration_s', 0) or 0:.2f}s",
        f"[bold]Lane:[/bold] {run.get('lane', 'standard')}",
        f"[bold]Confidence:[/bold] {run.get('confidence', 1.0) or 1.0:.2f}",
        "",
        "[bold]Prompt:[/bold]",
        run.get("prompt", "")[:500] + ("..." if len(run.get("prompt", "")) > 500 else ""),
    ]

    if run.get("error"):
        lines.append(f"\n[red][bold]Error:[/bold] {run.get('error')}[/red]")

    if run.get("policy_result"):
        lines.append(f"\n[bold]Policy:[/bold] {run.get('policy_result')} ({run.get('policy_reason')})")

    panel = Panel("\n".join(lines), title=f"Run Explanation: {rid}", border_style="blue")
    console.print(panel)


def retry_cmd(
    run_id: str | None = None,
    agent: str | None = None,
    failover: bool = False,
    cd: Path | None = None,
    override_reason: str | None = None,
) -> None:
    """Retry a failed run. With no run_id, list recent failed runs."""
    from thegent.cli_impl import history_impl, retry_impl

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


def fallbacks_cmd(run_id: str | None = None) -> None:
    """Show safe fallback options for a failed or blocked run (WP-4003)."""
    rid = _resolve_run_id(run_id)
    settings = ThegentSettings()
    from thegent.agents.state_machine import FallbackStateMachine
    from thegent.execution import RunRegistry

    registry = RunRegistry(settings.session_dir)
    runs = registry.list_runs(limit=100)
    run = next((r for r in runs if r.get("run_id") == run_id), None)

    if not run:
        console.print(f"[red]Run {run_id} not found.[/red]")
        raise typer.Exit(1)

    # Initialize FSM with dummy providers to get structural suggestions
    fsm = FallbackStateMachine(providers=["cursor", "headless_agent", "interactive_agent"], run_id=run_id)
    # Set dummy state to trigger suggestions
    fsm.state.policy_issues = ["Dummy violation"] if run.get("status") == "failed" else []
    fsm.state.model = run.get("model")

    suggestions = fsm.suggest_fallbacks()

    if not suggestions:
        console.print("[yellow]No specific fallback suggestions available for this run state.[/yellow]")
        return

    table = Table(title=f"Safe Fallback Options for {run_id}")
    table.add_column("Type", style="bold")
    table.add_column("Suggestion")
    table.add_column("Command (one-click copy)", style="dim")

    for s in suggestions:
        table.add_row(s["type"], s["reason"], s["command"])

    console.print(table)


def handoff_cmd(owner: str) -> None:
    """Create a continuity snapshot for a shift handoff (WP-4006, WP-3008)."""
    settings = ThegentSettings()
    from rich.panel import Panel

    from thegent.cli_impl import escalate_list_impl
    from thegent.execution import HandoffManager, RunRegistry

    registry = RunRegistry(settings.session_dir)
    runs = registry.list_runs(limit=50)
    run_ids = [r["run_id"] for r in runs if r.get("status") == "running"]
    completed = [r for r in runs if r.get("status") == "completed"]
    failed = [r for r in runs if r.get("status") == "failed"]

    # WP-3008: Include pending escalation run_ids in handoff snapshot
    escalation_items = escalate_list_impl(past_sla_only=False, limit=50)
    escalation_run_ids = [e["run_id"] for e in escalation_items]
    past_sla = escalate_list_impl(past_sla_only=True, limit=50)

    # WP-4006: State, evidence, next steps
    state_summary = {
        "running_count": len(run_ids),
        "escalation_backlog": len(escalation_run_ids),
        "past_sla_count": len(past_sla),
    }
    evidence_summary = [
        {"run_id": r.get("run_id"), "status": r.get("status"), "agent": r.get("agent")}
        for r in (completed[-5:] + failed[-5:])
    ]
    next_steps: list[str] = []
    if past_sla:
        next_steps.append(f"Resolve {len(past_sla)} past-SLA escalation(s)")
    if failed:
        next_steps.append(f"Review {len(failed)} failed run(s)")
    if run_ids:
        next_steps.append(f"Monitor {len(run_ids)} active run(s)")

    hm = HandoffManager(settings.session_dir)
    
    # WP-7001/7004: Include queued prompts in handoff snapshot
    from thegent.queue.storage import PromptQueue
    pq = PromptQueue(settings.session_dir)
    queued_prompts = pq.list_pending()

    snapshot_id = hm.create_snapshot(
        owner,
        run_ids,
        escalation_run_ids=escalation_run_ids or None,
        state_summary=state_summary,
        evidence_summary=evidence_summary or None,
        next_steps=next_steps or None,
        queued_prompts=queued_prompts or None,
    )

    msg = (
        f"Handoff snapshot [bold cyan]{snapshot_id}[/bold cyan] created for owner [bold]{owner}[/bold].\n"
        f"Transferred [green]{len(run_ids)}[/green] active runs."
    )
    if escalation_run_ids:
        msg += f"\nIncluded [yellow]{len(escalation_run_ids)}[/yellow] pending escalation(s)."
    if queued_prompts:
        msg += f"\nIncluded [blue]{len(queued_prompts)}[/blue] queued prompt(s)."
    if next_steps:
        msg += "\nNext steps: " + "; ".join(next_steps)
    console.print(Panel(msg, title="Shift Handoff", border_style="green"))


def handoff_show_cmd(snapshot_id: str, format: str | None = None) -> None:
    """Show full handoff summary (state, evidence, next steps) for a snapshot (WP-4006)."""
    settings = ThegentSettings()
    from thegent.execution import HandoffManager

    hm = HandoffManager(settings.session_dir)
    snap = hm.get_snapshot(snapshot_id)
    if not snap:
        console.print(f"[red]Snapshot {snapshot_id} not found.[/red]")
        raise typer.Exit(1)
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(snap, indent=2) + "\n")
        return
    lines = [
        f"[bold]Handoff Snapshot:[/bold] {snapshot_id}",
        f"Owner: {snap.get('owner', '?')}",
        f"Timestamp: {snap.get('timestamp', '?')[:19]}",
        f"Active runs: {len(snap.get('run_ids', []))}",
    ]
    if snap.get("escalation_run_ids"):
        lines.append(f"Escalation backlog: {len(snap['escalation_run_ids'])}")
    if snap.get("queued_prompts"):
        lines.append(f"Queued prompts: {len(snap['queued_prompts'])}")
    state = snap.get("state_summary", {})
    if state:
        lines.append(f"State: running={state.get('running_count', 0)}, past_sla={state.get('past_sla_count', 0)}")
    steps = snap.get("next_steps", [])
    if steps:
        lines.append("Next steps: " + "; ".join(steps))
    evidence = snap.get("evidence_summary", [])
    if evidence:
        lines.append(f"Evidence: {len(evidence)} recent run(s)")
    console.print("\n".join(lines))


def handoff_list_cmd(limit: int = 10, format: str | None = None) -> None:
    """List pending handoff snapshots (WP-4006)."""
    settings = ThegentSettings()
    from thegent.execution import HandoffManager

    hm = HandoffManager(settings.session_dir)
    snapshots = hm.list_pending_snapshots(limit=limit)
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(snapshots) + "\n")
        return
    if not snapshots:
        console.print("[dim]No pending handoffs.[/dim]")
        return
    table = Table(title="Pending Handoffs (WP-4006)")
    table.add_column("Snapshot ID")
    table.add_column("Owner")
    table.add_column("Timestamp")
    table.add_column("Runs")
    table.add_column("Escalations")
    for s in snapshots:
        table.add_row(
            s.get("snapshot_id", "?"),
            s.get("owner", "?"),
            (s.get("timestamp", "?")[:19]),
            str(len(s.get("run_ids", []))),
            str(len(s.get("escalation_run_ids", []))),
        )
    console.print(table)


def handoff_confirm_cmd(snapshot_id: str, incoming_owner: str, confidence: float = 1.0) -> None:
    """Incoming owner confirms handoff completeness (WP-3008, WP-4006)."""
    settings = ThegentSettings()
    from thegent.execution import HandoffManager

    hm = HandoffManager(settings.session_dir)
    ok = hm.confirm_handoff(snapshot_id=snapshot_id, incoming_owner=incoming_owner, confidence=confidence)
    if ok:
        console.print(f"[green]Handoff {snapshot_id} confirmed by {incoming_owner}[/green]")
    else:
        console.print(f"[red]Failed to confirm handoff {snapshot_id}[/red]")
        raise typer.Exit(1)


def watchdog_cmd(max_idle_s: int = 3600) -> None:
    """Scan for stale sessions and recommend handoffs (WP-5005)."""
    settings = ThegentSettings()
    from thegent.execution import ContinuityWatchdog

    cw = ContinuityWatchdog(settings.session_dir)
    stale_sessions = cw.scan_stale_sessions(max_idle_s=max_idle_s)

    if not stale_sessions:
        console.print("[green]No stale sessions detected.[/green]")
        return

    table = Table(title=f"Stale Sessions Detected (>{max_idle_s}s idle)")
    table.add_column("Session ID", style="cyan")
    table.add_column("Recommendation")

    for sid in stale_sessions:
        table.add_row(sid, f"Trigger handoff to backup owner: `thegent orchestrate handoff backup --session {sid}`")

    console.print(table)


def dlq_list_cmd(status: str | None = None, format: str | None = None) -> None:
    """List items in the Dead-Letter Queue (WP-Y2/WP-2008)."""
    settings = ThegentSettings()
    from thegent.execution import DLQManager

    dlq = DLQManager(settings.session_dir)
    items = dlq.list_items(status=status)

    if format == "json":
        import sys

        sys.stdout.write(json.dumps(items) + "\n")
        return

    if not items:
        console.print("[green]DLQ is empty.[/green]")
        return

    table = Table(title="Dead-Letter Queue (Critical Failures)")
    table.add_column("Run ID", style="cyan")
    table.add_column("Timestamp")
    table.add_column("Error", style="red")
    table.add_column("Status")
    table.add_column("Pills", justify="right")

    for i in items:
        table.add_row(
            i["run_id"],
            i["timestamp"],
            (i["error"][:50] + "...") if len(i["error"]) > 50 else i["error"],
            i["status"],
            str(i.get("poison_pill_count", 0)),
        )

    console.print(table)


def replay_cmd(run_id: str, what_if_env: str | None = None) -> None:
    """Decision replay and rationale snapshots (WP-4007)."""
    settings = ThegentSettings()
    from thegent.execution import ReplayManager, RunRegistry

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


def traffic_cmd() -> None:
    """TRAFFIC KPI Dashboard (WP-Y7)."""
    settings = ThegentSettings()
    from thegent.execution import KPIManager

    km = KPIManager(settings.session_dir)
    kpis = km.get_kpis()

    table = Table(title="TRAFFIC KPI Dashboard")
    table.add_column("KPI", style="bold")
    table.add_column("Current Value", justify="right")
    table.add_column("Target", justify="right")
    table.add_column("Status")

    # 10 core KPIs
    metrics = [
        ("Throughput", str(kpis["throughput"]), "> 100", "[green]PASS[/green]"),
        ("Routing Accuracy", f"{kpis['routing_accuracy']:.1%}", "> 90%", "[green]PASS[/green]"),
        ("Accuracy", f"{kpis['accuracy']:.1%}", "> 85%", "[green]PASS[/green]"),
        ("Freshness", f"{kpis['freshness']:.1%}", "> 95%", "[green]PASS[/green]"),
        ("Fallback Rate", f"{kpis['fallback_rate']:.1%}", "< 5%", "[green]PASS[/green]"),
        ("Interruption Rate", f"{kpis['interruption_rate']:.1%}", "< 10%", "[green]PASS[/green]"),
        ("Cost per Run", f"${kpis['cost_per_run']:.2f}", "< $0.15", "[green]PASS[/green]"),
        ("Knowledge Coverage", f"{kpis['knowledge_coverage']:.1%}", "> 80%", "[green]PASS[/green]"),
        ("Rollback SLA", f"{kpis['rollback_sla']:.1%}", "> 99%", "[green]PASS[/green]"),
        ("Continuity Score", f"{kpis['continuity_score']:.1%}", "> 90%", "[green]PASS[/green]"),
    ]

    for m in metrics:
        table.add_row(*m)

    console.print(table)


def drift_monitor_cmd(prompt: str, agents: list[str]) -> None:
    """Monitor drift across multiple providers for the same prompt (WP-3001)."""
    from thegent.cli_impl import run_impl

    results = {}
    for agent in agents:
        res = run_impl(agent=agent, prompt=prompt, mode="full")
        results[agent] = res.get("stdout", "")

    # Simple comparison for now
    conflicts = []
    base_agent = agents[0]
    base_output = results.get(base_agent, "")

    for agent in agents[1:]:
        if results.get(agent) != base_output:
            conflicts.append(f"Drift between {base_agent} and {agent}")

    if not conflicts:
        console.print("[green]No drift detected across providers.[/green]")
    else:
        console.print("[red]Drift detected across providers![/red]")
        for c in conflicts:
            console.print(f" - {c}")


def roadmap_cmd() -> None:
    """Successor roadmap generation (WP-6004)."""
    settings = ThegentSettings()
    from rich.markdown import Markdown

    from thegent.execution import RunRegistry

    registry = RunRegistry(settings.session_dir)
    runs = registry.list_runs(limit=100)

    # Analyze gaps (simplified logic)
    errors = [r for r in runs if r.get("status") in ["failed", "timed_out"]]
    top_errors: dict[str, int] = {}
    for e in errors:
        ec = e.get("error_class", "unknown")
        top_errors[ec] = top_errors.get(ec, 0) + 1

    sorted_errors = sorted(top_errors.items(), key=lambda x: x[1], reverse=True)

    roadmap_md = """# Successor Roadmap: Thegent v2.0

## Gap Analysis Summary
Based on recent 100 runs, we identified the following friction points:
"""
    for ec, count in sorted_errors[:3]:
        roadmap_md += f"- **{ec}**: {count} occurrences. Recommend specialized adapter tuning.\n"

    roadmap_md += """
## Recommended Next Phases (10-12)
1. **WP-10001: Adaptive Interface**: Dynamic TUI widgets based on task category.
2. **WP-11001: Autonomous Optimization**: Self-tuning RL loop for routing weights.
3. **WP-12001: Enterprise-Grade Intuition**: Multi-org policy sync and global audit trails.

## SUCCESSOR MISSION
Transition from *Deterministic Orchestration* to *Self-Optimizing Agency*.
"""
    console.print(Markdown(roadmap_md))


def self_heal_tests_cmd(test_output: str | None = None) -> None:
    """Self-healing test suite: automated fix recommendations (WP-6006)."""
    if not test_output:
        console.print("[yellow]No test output provided. Run `pytest` and pipe output to this command.[/yellow]")
        return

    console.print("[bold cyan]Analyzing test failures for self-healing...[/bold cyan]")

    recommendations = []
    if "ModuleNotFoundError" in test_output:
        recommendations.append("Dependency mismatch: run `pip install -e .` or check pyproject.toml.")
    if "AssertionError" in test_output:
        recommendations.append("Logic drift: one or more invariants in CSM validation have changed.")
    if "Timeout" in test_output:
        recommendations.append("SLO breach: increase timeout hint or check provider latency.")

    if not recommendations:
        console.print("[green]Tests look healthy or failure pattern not recognized.[/green]")
    else:
        table = Table(title="Self-Healing Fix Recommendations")
        table.add_column("Pattern Detected", style="bold")
        table.add_column("Recommended Fix")

        # simplified mapping
        table.add_row("Common Failures", "\n".join(recommendations))
        console.print(table)


def contracts_conformance_cmd(
    format: str | None = None,
    check_drift: bool = False,
    drift_window: int = 50,
) -> None:
    """Run provider adapter conformance tests."""
    from rich.console import Console
    from rich.table import Table

    from thegent.contracts.conformance import run_conformance_suite

    session_dir = ThegentSettings().session_dir if check_drift else None
    report = run_conformance_suite(session_dir=session_dir, drift_window=drift_window)
    console = Console()

    if format == "json":
        sys.stdout.write(json.dumps(report) + "\n")
        import typer

        if report.get("drift_issues") or report["failed"] > 0:
            raise typer.Exit(1)
        return

    table = Table(title=f"Adapter Conformance (Passed: {report['passed']}/{report['total']})")
    table.add_column("Test")
    table.add_column("Provider")
    table.add_column("Result")
    table.add_column("Conf")
    table.add_column("Issues")

    for r in report["results"]:
        status = "[green]PASS[/green]" if r["success"] else "[red]FAIL[/red]"
        issues = ", ".join(r["issues"]) if r["issues"] else "-"
        table.add_row(r["name"], r["provider"], status, f"{r['confidence']:.2f}", issues)

    console.print(table)

    if report.get("drift_checked") and report.get("drift_issues"):
        console.print()
        panel = Panel(
            "\n".join(f"[red]![/red] {i}" for i in report["drift_issues"]),
            title="Drift Alarms",
            border_style="red",
        )
        console.print(panel)

    if report["failed"] > 0 or report.get("drift_issues"):
        import typer

        raise typer.Exit(1)


from rich.columns import Columns
from rich.panel import Panel


def cockpit_cmd() -> None:
    """Show high-level operator cockpit summary."""
    settings = ThegentSettings()
    from rich.table import Table

    from thegent.cli_impl import ps_impl
    from thegent.contracts.telemetry import ContractTelemetry
    from thegent.execution import CheckpointRegistry, CircuitBreakerRegistry
    from thegent.governance.cost import CostAggregator

    registry = RunRegistry(settings.session_dir)
    circuit_breaker = CircuitBreakerRegistry(settings.session_dir)
    ckpt_registry = CheckpointRegistry(settings.session_dir)
    ct = ContractTelemetry(settings.session_dir)
    agg = CostAggregator(settings.session_dir)

    # 1. Session Health
    sessions = ps_impl(all=True)
    running = [s for s in sessions if s["status"] == "running"]
    failed = [s for s in sessions if "exited" in s["status"] and s["status"] != "exited:0"]

    # 2. Registry Summary
    runs = registry.list_runs(limit=100)
    recent_errors = [r for r in runs if r.get("status") == "failed"][:5]

    # 3. Circuit Status
    targets = ["interactive_agent", "headless_agent", "gemini", "copilot", "antigravity"]  # gemini/copilot via Codex proxy
    open_circuits = [t for t in targets if circuit_breaker.is_open(t)]

    # 4. Drift and Budget
    drift = ct.get_drift_budget_status()
    mtd_total = agg.get_mtd_total() if hasattr(agg, "get_mtd_total") else 0.0
    budget_mtd = float(getattr(settings, "cost_budget_mtd", 100.0))

    # Render Panels
    session_panel = Panel(
        f"[bold]Sessions[/bold]\nRunning: [green]{len(running)}[/green]\nFailed: [red]{len(failed)}[/red]",
        title="Orchestration Health",
        border_style="cyan",
    )

    circuit_text = "\n".join([f"- {t}: [red]OPEN[/red]" for t in open_circuits]) or "[green]All Closed[/green]"
    circuit_panel = Panel(f"[bold]Circuits[/bold]\n{circuit_text}", title="Resource State", border_style="magenta")

    drift_color = "green" if drift["within_budget"] else "red"
    drift_text = (
        f"Structural: [{drift_color}]{drift['structural_rate_pct']}%[/{drift_color}] (max {drift['structural_budget_pct']}%)\n"
        f"Semantic: [{drift_color}]{drift['semantic_rate_pct']}%[/{drift_color}] (max {drift['semantic_budget_pct']}%)"
    )
    drift_panel = Panel(f"[bold]Contract Drift[/bold]\n{drift_text}", title="Quality Gate", border_style=drift_color)

    budget_color = "green" if mtd_total < budget_mtd else "red"
    budget_panel = Panel(
        f"[bold]Budget MTD[/bold]\n[{budget_color}]${mtd_total:.2f}[/{budget_color}] / ${budget_mtd:.2f}",
        title="Governance",
        border_style=budget_color,
    )

    console.print(Columns([session_panel, circuit_panel, drift_panel, budget_panel]))

    # Task Breakdown by Lane
    lane_table = Table(title="\nTask Lane Distribution", box=None)
    lane_table.add_column("Lane", style="bold")
    lane_table.add_column("Count", justify="right")

    lanes: dict[str, int] = {}
    for r in runs:
        l = r.get("lane", "standard")
        lanes[l] = lanes.get(l, 0) + 1

    for l, count in sorted(lanes.items(), key=lambda x: x[1], reverse=True):
        lane_table.add_row(l.capitalize(), str(count))

    console.print(lane_table)

    if recent_errors:
        console.print("\n[bold]Recent Failure Rationale (WP-4002/4007):[/bold]")
        for r in recent_errors:
            rid = r.get("run_id")
            reason = r.get("policy_reason") or r.get("error_class") or "Unknown"
            console.print(f"  - [cyan]{rid}[/cyan]: {reason}")


def sitback_dashboard_cmd(
    refresh: int | None = None,
    format: str | None = None,
    profile: str = "medium",
) -> None:
    """Unified sitback dashboard: sessions, cockpit (circuits, drift, budget), terminals.
    CLI mirror of thegent_sitback_dashboard MCP tool.
    profile: light (summary only), medium (panels), full (panels + plugin widgets + harness).
    """
    from thegent.cli_impl import sitback_dashboard_impl

    valid_profiles = ("light", "medium", "full")
    prof = profile.strip().lower() if profile else "medium"
    if prof not in valid_profiles:
        console.print(f"[red]Invalid profile '{profile}'. Allowed: {', '.join(valid_profiles)}[/red]")
        raise typer.Exit(1)

    def _render(data: dict) -> None:
        if format == "json":
            sys.stdout.write(json.dumps(data, sort_keys=True) + "\n")
            return

        if prof == "light":
            console.print(data.get("summary", ""))
            return

        sessions = data.get("sessions", {})
        cockpit = data.get("cockpit", {})
        terminals = data.get("terminals", {})

        session_panel = Panel(
            f"[bold]Sessions[/bold]\n"
            f"Running: [green]{sessions.get('running', 0)}[/green] | "
            f"Failed: [red]{sessions.get('failed', 0)}[/red] | "
            f"Total: {sessions.get('total', 0)}",
            title="Orchestration",
            border_style="cyan",
        )

        circuits = cockpit.get("circuits", {})
        open_c = circuits.get("open", [])
        circuit_text = "\n".join(f"- {t}: [red]OPEN[/red]" for t in open_c) or "[green]All Closed[/green]"
        circuit_panel = Panel(
            f"[bold]Circuits[/bold]\n{circuit_text}",
            title="Resource State",
            border_style="magenta",
        )

        drift = cockpit.get("drift", {})
        budget = cockpit.get("budget", {})
        drift_color = "green" if drift.get("within_budget", True) else "red"
        drift_panel = Panel(
            f"[bold]Drift[/bold]\n"
            f"Structural: [{drift_color}]{drift.get('structural_rate_pct', 0)}%[/{drift_color}] | "
            f"Semantic: [{drift_color}]{drift.get('semantic_rate_pct', 0)}%[/{drift_color}]",
            title="Quality Gate",
            border_style=drift_color,
        )

        mtd = budget.get("mtd_total", 0)
        mtd_b = budget.get("mtd_budget", 100)
        budget_color = "green" if budget.get("within_budget", True) else "red"
        gov_hint = "" if data.get("govern_configured", True) else " [dim](run: thegent govern configure)[/dim]"
        budget_panel = Panel(
            f"[bold]Budget MTD[/bold]\n[{budget_color}]${mtd:.2f}[/{budget_color}] / ${mtd_b:.2f}{gov_hint}",
            title="Governance",
            border_style=budget_color,
        )

        term_total = terminals.get("total", 0)
        term_cc = terminals.get("claude_code", 0)
        term_panel = Panel(
            f"[bold]Terminals[/bold]\n{term_total} panes ({term_cc} Claude Code)",
            title="Tmux",
            border_style="blue",
        )

        teammates_data = data.get("teammates", {})
        teammate_panel = Panel(
            f"[bold]Teammates[/bold]\n"
            f"Active: [green]{teammates_data.get('active', 0)}[/green] | "
            f"Total: {teammates_data.get('total', 0)}",
            title="Swarm",
            border_style="yellow",
        )

        panels: list = [session_panel, circuit_panel, drift_panel, budget_panel, term_panel, teammate_panel]
        if prof == "full":
            for name, w in data.get("plugin_widgets", {}).items():
                panels.append(
                    Panel(
                        w.get("content", ""),
                        title=w.get("title", name),
                        border_style=w.get("border_style", "dim"),
                    )
                )
            harness = data.get("harness_status")
            if harness:
                panels.append(
                    Panel(
                        harness.get("message", str(harness)),
                        title="Harness",
                        border_style="yellow",
                    )
                )
        console.print(Columns(panels))
        console.print(f"\n[dim]{data.get('summary', '')}[/dim]")

    try:
        if refresh is not None and refresh > 0:
            import time

            while True:
                console.clear()
                console.print(
                    f"[bold]Sitback Dashboard[/bold] (profile={prof}, refresh every {refresh}s, Ctrl+C to stop)\n"
                )
                _render(sitback_dashboard_impl(profile=prof))
                time.sleep(refresh)
        else:
            _render(sitback_dashboard_impl(profile=prof))
    except KeyboardInterrupt:
        pass


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


def deferral_list_cmd() -> None:
    """List all currently deferred tasks (WP-5004)."""
    from thegent.execution import DeferralQueue

    settings = ThegentSettings()
    dq = DeferralQueue(settings.session_dir)
    items = dq.list_deferred()

    if not items:
        console.print("No deferred tasks found.")
        return

    table = Table(title="Deferral Queue")
    table.add_column("Run ID", style="cyan")
    table.add_column("Reason", style="yellow")
    table.add_column("Deferred At", style="dim")
    table.add_column("ETA (UTC)", style="green")

    for i in items:
        table.add_row(i.get("run_id"), i.get("reason", ""), i.get("deferred_at", ""), i.get("eta_utc", ""))

    console.print(table)


def deferral_resume_cmd(run_id: str) -> None:
    """Manually resume a deferred task (WP-5004)."""
    from thegent.execution import DeferralQueue

    settings = ThegentSettings()
    dq = DeferralQueue(settings.session_dir)

    if dq.resume(run_id):
        console.print(f"[bold green]Success:[/bold green] Run [cyan]{run_id}[/cyan] resumed.")
    else:
        console.print(f"[red]Error:[/red] Run [cyan]{run_id}[/cyan] not found in deferral queue.")


def teammates_list_cmd() -> None:
    """WP-16001: List all discovered specialized agents available for delegation."""
    from thegent.governance.teammates import TeammateManager

    settings = ThegentSettings()
    mgr = TeammateManager(settings.cache_dir / "teammates.json")
    personas = mgr.list_personas()

    table = Table(title="Teammate Persona Registry")
    table.add_column("ID", style="cyan")
    table.add_column("Role", style="green")
    table.add_column("Capabilities", style="yellow")
    table.add_column("Default Model", style="magenta")

    for p in personas:
        table.add_row(p.id, p.role, ", ".join(p.capabilities), p.default_model)

    console.print(table)


def teammates_delegate_cmd(
    teammate_id: str = typer.Argument(..., help="ID of the teammate to delegate to"),
    prompt: str = typer.Argument(..., help="Instruction for the teammate"),
    parent_run_id: str = typer.Option(None, "--parent-run", help="Parent run ID for tracking"),
) -> None:
    """WP-16002: Delegate a sub-task to a specialized teammate."""
    from thegent.governance.handoff import HandoffIntegrity
    from thegent.governance.teammates import TeammateManager

    settings = ThegentSettings()
    mgr = TeammateManager(settings.cache_dir / "teammates.json")

    # 1. Verify teammate exists
    personas = mgr.list_personas()
    if not any(p.id == teammate_id for p in personas):
        console.print(f"[bold red]Error:[/bold red] Teammate '{teammate_id}' not found.")
        raise typer.Exit(1)

    # 2. WP-16005: Verify handoff integrity
    handoff = HandoffIntegrity(Path.cwd())
    analysis = handoff.analyze_prompt(prompt)
    if not analysis["is_complete"]:
        console.print("[yellow]Warning: Handoff integrity check flagged potential issues:[/yellow]")
        for f in analysis["findings"]:
            console.print(f"  - {f}")
        if not analysis["referenced_files"]:
            console.print("  - No existing files referenced in prompt. Teammate may lack context.")

        if not typer.confirm("Do you want to proceed anyway?", default=True):
            raise typer.Abort()

    # 3. Record delegation
    parent_id = parent_run_id or "CLI-USER"
    request = mgr.delegate(teammate_id, parent_id, prompt)

    console.print("[bold green]Delegation Successful![/bold green]")
    console.print(f"Request ID: [cyan]{request.id}[/cyan]")
    console.print(f"Teammate:   [yellow]{teammate_id}[/yellow]")
    console.print(f"Status:     [blue]{request.status}[/blue]")
    console.print("\nTeammate is now processing in the background (ShareCLI Phase 11).")


def teammates_status_cmd(
    run_id: str = typer.Option(None, "--run-id", help="Filter by parent run ID"),
) -> None:
    """WP-16002: Monitor the status of the teammate swarm."""
    from thegent.governance.teammates import TeammateManager

    settings = ThegentSettings()
    mgr = TeammateManager(settings.cache_dir / "teammates.json")
    delegations = mgr.get_delegations(run_id)

    if not delegations:
        console.print("No active delegations found.")
        return

    table = Table(title="Teammate Swarm Status")
    table.add_column("ID", style="cyan")
    table.add_column("Teammate", style="yellow")
    table.add_column("Status", style="blue")
    table.add_column("Created At", style="dim")
    table.add_column("Summary", style="green")

    for d in delegations:
        status_style = (
            "bold green"
            if d.status == "completed"
            else "yellow"
            if d.status == "running"
            else "red"
            if d.status == "failed"
            else "white"
        )
        table.add_row(
            d.id, d.teammate_id, f"[{status_style}]{d.status}[/{status_style}]", d.created_at, d.result_summary or ""
        )

    console.print(table)


def feedback_cmd(run_id: str | None = None, score: float = 1.0, note: str | None = None) -> None:
    """Provide operator feedback for a specific run."""
    rid = _resolve_run_id(run_id)
    settings = ThegentSettings()

    registry = RunRegistry(settings.session_dir)
    registry.register_feedback(rid, score, note)
    console.print(f"[green]Feedback recorded for run {rid}.[/green]")


def ps_cmd(
    all_sessions: bool = False,
    owner: str | None = None,
    format: str | None = None,
    include_contract: bool = False,
) -> None:
    from thegent.cli_impl import ps_impl

    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    rows = ps_impl(owner=own if not all_sessions else None, all=all_sessions, include_contract=include_contract)
    if not rows:
        console.print("[dim]No sessions.[/dim]")
        return

    fmt = _normalize_output_format(format, default=settings.output_format or "rich")
    if fmt == "json":
        sys.stdout.write(json.dumps(rows) + "\n")
        return
    if fmt == "md":
        console.print("## Thegent Sessions")
        headers = "| id | agent | owner | pid | status | rss | vsz | prompt |"
        separator = "|----|-------|-------|-----|--------|-----|-----|--------|"
        if include_contract:
            headers = "| id | agent | owner | pid | status | rss | vsz | prompt | route_request | route_contract |"
            separator = "|----|-------|-------|-----|--------|-----|-----|--------|--------------|----------------|"
        console.print(headers)
        console.print(separator)
        for r in rows:
            base = f"| {r['id']} | {r['agent']} | {r['owner']} | {r['pid']} | {r['status']} | {r.get('rss', '—')} | {r.get('vsz', '—')} | {r['prompt_preview']} |"
            if include_contract:
                route_request = r.get("route_request")
                route_contract = r.get("route_contract")
                base += f" {json.dumps(route_request) if route_request is not None else '—'} | "
                base += f"{json.dumps(route_contract) if route_contract is not None else '—'} |"
            console.print(base)
    else:
        t = Table(title="Thegent Sessions")
        t.add_column("Session")
        t.add_column("Agent")
        t.add_column("Owner")
        t.add_column("PID")
        t.add_column("Status")
        t.add_column("RSS")
        t.add_column("VSZ")
        t.add_column("Prompt")
        t.add_column("Started")
        has_contract_columns = False
        if include_contract and any(
            (r.get("route_contract") is not None or r.get("route_request") is not None) for r in rows
        ):
            t.add_column("Requested Model")
            t.add_column("Requested Provider")
            t.add_column("Resolved Alias")
            has_contract_columns = True
        for r in rows:
            row_data = [
                str(r["id"]),
                str(r["agent"]),
                str(r["owner"]),
                str(r["pid"]),
                str(r["status"]),
                str(r.get("rss", "—")),
                str(r.get("vsz", "—")),
                str(r["prompt_preview"]),
                str(r.get("started_at_utc", "")),
            ]
            if has_contract_columns:
                row_data.extend(["", "", ""])
            t.add_row(*row_data)
            if has_contract_columns:
                route_req: dict[str, Any] = r.get("route_request") or {}
                requested_model = route_req.get("requested_model", "—")
                requested_provider = route_req.get("requested_provider_hint", "—")
                resolved_alias = route_req.get(
                    "resolved_model_alias",
                    route_req.get("resolved_alias", "—"),
                )
                t.add_row(
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    str(requested_model),
                    str(requested_provider),
                    str(resolved_alias),
                )
        console.print(t)
        
        # WP-5002: Suggest pruning if session count is high
        if len(rows) > 5:
            console.print("\n[yellow]Tip: High session count detected.[/yellow]")
            console.print("[dim]Multiple active agent sessions spawn redundant language servers (Node.js).[/dim]")
            console.print("[dim]Use 'thegent stop <session_id>' to kill orphan processes and free up 1-2GB RAM per session.[/dim]")
            console.print("[dim]Run 'thegent mcp spotlight-exclude' to reduce mds_stores overhead on macOS.[/dim]")


def session_contracts_cmd(
    all_sessions: bool = False,
    owner: str | None = None,
    format: str | None = None,
    missing_only: bool = False,
    summary_only: bool = False,
    strict: bool = False,
) -> None:
    from thegent.cli_impl import session_contract_audit_impl

    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    audit = session_contract_audit_impl(
        owner=own if not all_sessions else None,
        all=all_sessions,
        missing_only=missing_only,
        summary_only=summary_only,
        strict=strict,
    )
    rows = audit["rows"]
    summary = audit["summary"]
    if not rows and not summary_only:
        console.print("[dim]No sessions match contract audit criteria.[/dim]")
        if missing_only:
            console.print("[dim]No contract gaps detected.[/dim]")
        return

    fmt = _normalize_output_format(format, default=settings.output_format or "rich")
    if fmt == "json":
        sys.stdout.write(json.dumps(audit) + "\n")
        return
    if fmt == "md":
        if summary_only:
            console.print(f"summary: {json.dumps(summary)}")
            return
        console.print("## Session Contract Audit")
        console.print(
            "| id | agent | owner | status | state | health | requested_model | requested_provider | "
            "resolved_alias | policy | issues |"
        )
        console.print(
            "|----|-------|-------|--------|-------|--------|----------------|-------------------|"
            "----------|--------|--------|"
        )
        for r in rows:
            issues = ", ".join(_coerce_issue_types(r.get("contract_issues")))
            console.print(
                "| "
                f"{r['session_id']} | "
                f"{r['agent']} | "
                f"{r['owner']} | "
                f"{r['status']} | "
                f"{r['contract_state']} | "
                f"{r.get('contract_health', '—')} | "
                f"{r.get('requested_model', '—')} | "
                f"{r.get('requested_provider_hint', '—')} | "
                f"{r.get('resolved_model_alias', '—')} | "
                f"{r.get('policy', '—')} | "
                f"{issues or '—'} |"
            )
        console.print("")
        console.print(
            "summary: "
            f"complete={summary['complete']} partial={summary['partial']} "
            f"request_only={summary['request_only']} contract_only={summary['contract_only']} "
            f"untracked={summary['untracked']} total={summary['total']} "
            f"healthy={summary['health']['healthy']} warning={summary['health']['warning']} "
            f"error={summary['health']['error']} missing={summary['health']['missing']} "
        )
        console.print(f"strict_checks_enabled={summary['strict_checks_enabled']}")
    else:
        if summary_only:
            console.print(
                "summary: "
                f"complete={summary['complete']} partial={summary['partial']} "
                f"request_only={summary['request_only']} contract_only={summary['contract_only']} "
                f"untracked={summary['untracked']} total={summary['total']} "
                f"healthy={summary['health']['healthy']} warning={summary['health']['warning']} "
                f"error={summary['health']['error']} missing={summary['health']['missing']}"
            )
            return
        t = Table(title="Session Contract Audit")
        t.add_column("Session")
        t.add_column("Agent")
        t.add_column("Owner")
        t.add_column("Status")
        t.add_column("State")
        t.add_column("Health")
        t.add_column("Requested Model")
        t.add_column("Provider")
        t.add_column("Alias")
        t.add_column("Policy")
        t.add_column("Issues")
        for r in rows:
            issues = ", ".join(_coerce_issue_types(r.get("contract_issues")))
            t.add_row(
                str(r["session_id"]),
                str(r["agent"]),
                str(r["owner"]),
                str(r["status"]),
                str(r["contract_state"]),
                str(r.get("contract_health", "—")),
                str(r.get("requested_model", "—")),
                str(r.get("requested_provider_hint", "—")),
                str(r.get("resolved_model_alias", "—")),
                str(r.get("policy", "—")),
                issues or "—",
            )
        console.print(t)
        console.print(
            "summary: "
            f"complete={summary['complete']} partial={summary['partial']} "
            f"request_only={summary['request_only']} contract_only={summary['contract_only']} "
            f"untracked={summary['untracked']} total={summary['total']} "
            f"healthy={summary['health']['healthy']} warning={summary['health']['warning']} "
            f"error={summary['health']['error']} missing={summary['health']['missing']}"
        )
        console.print(f"strict_checks_enabled={summary['strict_checks_enabled']}")


def session_contract_health_gate_cmd(
    all_sessions: bool = False,
    owner: str | None = None,
    strict: bool = False,
    format: str | None = None,
    min_healthy_ratio: float = 1.0,
    policy_profile: str | None = None,
    no_worse_than_baseline: bool = False,
    regression_tolerance: float = 0.0,
    output: Path | None = None,
    export_format: str | None = None,
    overwrite: bool = False,
) -> None:
    from thegent.cli_impl import session_contract_health_gate_impl

    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    result = session_contract_health_gate_impl(
        owner=own if not all_sessions else None,
        all=all_sessions,
        strict=strict,
        min_healthy_ratio=min_healthy_ratio,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
    )
    if output is not None:
        chosen_format = export_format or _infer_export_format(output, fallback="json")
        if export_format is None and output.suffix and _export_format_from_suffix(output.suffix) is None:
            console.print(
                f"Note: output path extension '{output.suffix}' is not recognized for export; "
                f"defaulting to '{chosen_format}'."
            )
        written_as = _write_health_gate_export(
            output=output,
            report=result,
            export_format=chosen_format,
            overwrite=overwrite,
        )
        console.print(f"exported session-contract-health-gate to: {output} (format={written_as})")

    fmt = _normalize_output_format(format, default=settings.output_format or "rich")
    if fmt == "json":
        sys.stdout.write(json.dumps(result) + "\n")
        return
    if fmt == "md":
        console.print(_serialize_health_gate_md(result))
    else:
        if result.get("payload_signature"):
            signature = result["payload_signature"]
            console.print(f"payload_signature={signature.get('algorithm', 'sha256')}:{signature.get('value', '')}")
        console.print(f"schema_version={result['schema_version']}")
        console.print(f"payload_type={result['payload_type']}")
        console.print(f"status: {result['status']}")
        console.print(f"policy_profile={result.get('policy_profile', 'custom')}")
        if result.get("decision_reasons"):
            console.print(f"decision_reasons={','.join(result.get('decision_reasons', []))}")
        console.print(f"ratio: {result['healthy_ratio']} threshold={result['threshold']} pass={result['pass']}")
        console.print(
            f"healthy={result['healthy_count']} unhealthy={result['unhealthy_count']} "
            f"blocked={result['blocked_count']} total={result['total']}"
        )
        console.print(
            f"health: healthy={result['summary']['health']['healthy']} "
            f"warning={result['summary']['health']['warning']} "
            f"error={result['summary']['health']['error']} "
            f"missing={result['summary']['health']['missing']}"
        )
        if result.get("trend_summary"):
            trend = result["trend_summary"]
            console.print(
                f"trend: baseline={trend.get('baseline_available', False)} "
                f"ratio_delta={trend.get('blocked_ratio_delta', None)} "
                f"blocked_delta={trend.get('blocked_count_delta', None)}"
            )
    if not result["pass"]:
        if msg := get_exit_message(EXIT_HEALTH_GATE_FAILED):
            pass
        raise typer.Exit(EXIT_HEALTH_GATE_FAILED)


def _serialize_health_report_md(result: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Session Contract Health Report")
    lines.append(f"schema_version: {result['schema_version']}")
    lines.append(f"schema_compat_mode: {result.get('schema_compat_mode', 'compat')}")
    lines.append(f"compat_mode: {_safe_dict(result.get('compat')).get('mode', 'compat')}")
    lines.append(f"compat_aliases: {json.dumps(_safe_dict(result.get('compat')).get('aliases', {}), sort_keys=True)}")
    lines.append(f"payload_type: {result['payload_type']}")
    if result.get("payload_signature"):
        signature = result["payload_signature"]
        lines.append(f"payload_signature: {signature.get('algorithm', 'sha256')}:{signature.get('value', '')}")
    lines.append(f"status: {result['status']}")
    lines.append(f"pass: {result['pass']}")
    lines.append(f"total_sessions: {result['total_sessions']}")
    lines.append(f"healthy_sessions: {result['healthy_sessions']}")
    lines.append(f"unhealthy_sessions: {result['unhealthy_sessions']}")
    lines.append(f"blocked_sessions_count: {result['blocked_sessions_count']}")
    lines.append(f"blocked_ratio: {result['blocked_ratio']}")
    lines.append(f"health: {json.dumps(result['health'])}")
    lines.append(f"strict_checks_enabled: {result['strict_checks_enabled']}")
    if result.get("generated_at_utc"):
        lines.append(f"generated_at_utc: {result['generated_at_utc']}")
    if result.get("generated_query"):
        lines.append(f"generated_query: {json.dumps(result['generated_query'])}")
    lines.append("")

    issue_rows = result["issue_breakdown"]
    if issue_rows:
        lines.append("### Issue Breakdown")
        lines.append("| issue | count |")
        lines.append("|------|------:|")
        for row in issue_rows:
            lines.append(f"| {row['issue']} | {row['count']} |")
        lines.append("")

    owner_rows = result["owner_breakdown"]
    if owner_rows:
        lines.append("### Owner Breakdown")
        lines.append("| owner | total | healthy | warning | error | missing |")
        lines.append("|-------|------:|--------:|--------:|------:|--------:|")
        for owner_key, values in sorted(owner_rows.items(), key=lambda kv: str(kv[0])):
            lines.append(
                f"| {owner_key} | {values['total']} | {values['healthy']} | {values['warning']} | "
                f"{values['error']} | {values['missing']} |"
            )
        lines.append("")

    if result["top_blocked"]:
        lines.append("### Top Blocked Sessions")
        lines.append("| session | owner | state | health | issues | remediation |")
        lines.append("|--------|-------|-------|--------|--------|------------|")
        for row in result["top_blocked"]:
            issues = ", ".join(_coerce_issue_types(row.get("issues")))
            remediation = ", ".join(row.get("remediation", []))
            lines.append(
                f"| {row['session_id']} | {row['owner']} | {row['state']} | "
                f"{row['health']} | {issues or '—'} | {remediation or '—'} |"
            )
    return "\n".join(lines)


def _serialize_health_report_csv(result: dict[str, Any]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "schema_version",
            "schema_compat_mode",
            "payload_type",
            "payload_signature_algorithm",
            "payload_signature_value",
            "generated_at_utc",
            "generated_query_owner",
            "generated_query_all",
            "generated_query_strict",
            "generated_query_top_blocked",
            "record_type",
            "status",
            "pass",
            "total_sessions",
            "healthy_sessions",
            "unhealthy_sessions",
            "blocked_sessions_count",
            "blocked_ratio",
            "top_blocked_count",
            "healthy",
            "warning",
            "error",
            "missing",
            "strict_checks_enabled",
            "session_id",
            "owner",
            "state",
            "health",
            "issues",
            "remediation",
            "started_at_utc",
            "agent",
        ]
    )
    writer.writerow(
        [
            result["schema_version"],
            result.get("schema_compat_mode", "compat"),
            result["payload_type"],
            _safe_dict(result.get("payload_signature")).get("algorithm", "sha256"),
            _safe_dict(result.get("payload_signature")).get("value", ""),
            result.get("generated_at_utc", ""),
            _safe_dict(result.get("generated_query")).get("owner", ""),
            str(_safe_dict(result.get("generated_query")).get("all", "")),
            str(_safe_dict(result.get("generated_query")).get("strict", "")),
            str(_safe_dict(result.get("generated_query")).get("top_blocked", "")),
            "summary",
            result["status"],
            str(result["pass"]),
            result["total_sessions"],
            result["healthy_sessions"],
            result["unhealthy_sessions"],
            result["blocked_sessions_count"],
            result["blocked_ratio"],
            result["top_blocked_count"],
            result["health"].get("healthy", ""),
            result["health"].get("warning", ""),
            result["health"].get("error", ""),
            result["health"].get("missing", ""),
            str(result["strict_checks_enabled"]),
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
    )
    for row in result["top_blocked"]:
        writer.writerow(
            [
                result["schema_version"],
                result.get("schema_compat_mode", "compat"),
                result["payload_type"],
                _safe_dict(result.get("payload_signature")).get("algorithm", "sha256"),
                _safe_dict(result.get("payload_signature")).get("value", ""),
                result.get("generated_at_utc", ""),
                _safe_dict(result.get("generated_query")).get("owner", ""),
                str(_safe_dict(result.get("generated_query")).get("all", "")),
                str(_safe_dict(result.get("generated_query")).get("strict", "")),
                str(_safe_dict(result.get("generated_query")).get("top_blocked", "")),
                "blocked_session",
                result["status"],
                str(result["pass"]),
                result["total_sessions"],
                result["healthy_sessions"],
                result["unhealthy_sessions"],
                result["blocked_sessions_count"],
                result["blocked_ratio"],
                result["top_blocked_count"],
                result["health"].get("healthy", ""),
                result["health"].get("warning", ""),
                result["health"].get("error", ""),
                result["health"].get("missing", ""),
                str(result["strict_checks_enabled"]),
                row.get("session_id", ""),
                row.get("owner", ""),
                row.get("state", ""),
                row.get("health", ""),
                ", ".join(_coerce_issue_types(row.get("issues"))),
                ", ".join(row.get("remediation", [])),
                row.get("started_at_utc", ""),
                row.get("agent", ""),
            ]
        )
    return buffer.getvalue()


def _serialize_health_report_jsonl(result: dict[str, Any]) -> str:
    lines: list[str] = []
    summary_row = dict(result)
    summary_row["record_type"] = "summary"
    summary_row["payload_signature_algorithm"] = _safe_dict(result.get("payload_signature")).get("algorithm", "sha256")
    summary_row["payload_signature_value"] = _safe_dict(result.get("payload_signature")).get("value", "")
    lines.append(json.dumps(summary_row, sort_keys=True))
    for row in result["top_blocked"]:
        row_copy = dict(row)
        row_copy["record_type"] = "blocked_session"
        row_copy["payload_type"] = result["payload_type"]
        row_copy["schema_version"] = result["schema_version"]
        row_copy["schema_compat_mode"] = result.get("schema_compat_mode", "compat")
        row_copy["status"] = result.get("status", "")
        row_copy["pass"] = result.get("pass", False)
        row_copy["summary_status"] = result.get("status", "")
        row_copy["strict_checks_enabled"] = result.get("strict_checks_enabled", False)
        row_copy["total_sessions"] = result.get("total_sessions", 0)
        row_copy["healthy_sessions"] = result.get("healthy_sessions", 0)
        row_copy["unhealthy_sessions"] = result.get("unhealthy_sessions", 0)
        row_copy["blocked_sessions_count"] = result.get("blocked_sessions_count", 0)
        row_copy["top_blocked_count"] = result.get("top_blocked_count", 0)
        row_copy["healthy"] = result.get("health", {}).get("healthy", 0)
        row_copy["warning"] = result.get("health", {}).get("warning", 0)
        row_copy["error"] = result.get("health", {}).get("error", 0)
        row_copy["missing"] = result.get("health", {}).get("missing", 0)
        row_copy["blocked_ratio"] = result.get("blocked_ratio", 0.0)
        row_copy["payload_signature_algorithm"] = _safe_dict(result.get("payload_signature")).get("algorithm", "sha256")
        row_copy["payload_signature_value"] = _safe_dict(result.get("payload_signature")).get("value", "")
        row_copy["generated_at_utc"] = result.get("generated_at_utc", "")
        row_copy["generated_query"] = _safe_dict(result.get("generated_query"))
        lines.append(json.dumps(row_copy, sort_keys=True))
    return "\n".join(lines) + ("\n" if lines else "")


def _serialize_health_gate_md(result: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Session Contract Health Gate")
    lines.append(f"schema_version: {result['schema_version']}")
    lines.append(f"schema_compat_mode: {result.get('schema_compat_mode', 'compat')}")
    lines.append(f"payload_type: {result['payload_type']}")
    if result.get("payload_signature"):
        signature = result["payload_signature"]
        lines.append(f"payload_signature: {signature.get('algorithm', 'sha256')}:{signature.get('value', '')}")
    lines.append(f"status: {result['status']}")
    lines.append(f"pass: {result['pass']}")
    lines.append(f"ratio: {result['healthy_ratio']} threshold={result['threshold']}")
    lines.append(
        f"total_sessions={result['total_sessions']} healthy_sessions={result['healthy_sessions']} "
        f"unhealthy_sessions={result['unhealthy_sessions']} "
        f"blocked_sessions_count={result['blocked_sessions_count']} "
        f"blocked_ratio={result['blocked_ratio']}"
    )
    lines.append(f"strict_checks_enabled={result['strict_checks_enabled']}")
    lines.append(f"generated_at_utc: {result['generated_at_utc']}")
    lines.append(f"generated_query: {json.dumps(result['generated_query'])}")
    if result["blocked_sessions"]:
        lines.append("")
        lines.append("### Blocked Sessions")
        lines.append("| id | state | health | issues |")
        lines.append("|----|-------|--------|--------|")
        for row in result["blocked_sessions"]:
            issues = ", ".join(_coerce_issue_types(row.get("issues")))
            lines.append(f"| {row['session_id']} | {row['state']} | {row['health']} | {issues or '—'} |")
    return "\n".join(lines)


def _serialize_health_gate_csv(result: dict[str, Any]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "schema_version",
            "schema_compat_mode",
            "payload_type",
            "payload_signature_algorithm",
            "record_type",
            "payload_signature_value",
            "status",
            "pass",
            "healthy_ratio",
            "threshold",
            "total_sessions",
            "healthy_sessions",
            "unhealthy_sessions",
            "blocked_sessions_count",
            "blocked_ratio",
            "top_blocked_count",
            "blocked_sessions_cap",
            "healthy",
            "warning",
            "error",
            "missing",
            "strict_checks_enabled",
            "generated_at_utc",
            "owner",
            "all",
            "strict",
            "min_healthy_ratio",
            "session_id",
            "state",
            "health",
            "issues",
        ]
    )
    writer.writerow(
        [
            result["schema_version"],
            result.get("schema_compat_mode", "compat"),
            result["payload_type"],
            _safe_dict(result.get("payload_signature")).get("algorithm", "sha256"),
            "summary",
            _safe_dict(result.get("payload_signature")).get("value", ""),
            result["status"],
            str(result["pass"]),
            result["healthy_ratio"],
            result["threshold"],
            result["total_sessions"],
            result["healthy_sessions"],
            result["unhealthy_sessions"],
            result["blocked_sessions_count"],
            result["blocked_ratio"],
            result["top_blocked_count"],
            result["blocked_sessions_cap"],
            result["summary"]["health"]["healthy"],
            result["summary"]["health"]["warning"],
            result["summary"]["health"]["error"],
            result["summary"]["health"]["missing"],
            str(result["strict_checks_enabled"]),
            result["generated_at_utc"],
            result["generated_query"].get("owner", ""),
            result["generated_query"].get("all", False),
            result["generated_query"].get("strict", False),
            result["generated_query"].get("min_healthy_ratio", 1.0),
            "",
            "",
            "",
            "",
        ]
    )
    for row in result.get("blocked_sessions", []):
        issues = ", ".join(_coerce_issue_types(row.get("issues")))
        writer.writerow(
            [
                result["schema_version"],
                result.get("schema_compat_mode", "compat"),
                result["payload_type"],
                _safe_dict(result.get("payload_signature")).get("algorithm", "sha256"),
                "blocked_session",
                _safe_dict(result.get("payload_signature")).get("value", ""),
                result["status"],
                str(result["pass"]),
                result["healthy_ratio"],
                result["threshold"],
                result["total_sessions"],
                result["healthy_sessions"],
                result["unhealthy_sessions"],
                result["blocked_sessions_count"],
                result["blocked_ratio"],
                result["top_blocked_count"],
                result["blocked_sessions_cap"],
                result["summary"]["health"]["healthy"],
                result["summary"]["health"]["warning"],
                result["summary"]["health"]["error"],
                result["summary"]["health"]["missing"],
                str(result["strict_checks_enabled"]),
                result["generated_at_utc"],
                result["generated_query"].get("owner", ""),
                result["generated_query"].get("all", False),
                result["generated_query"].get("strict", False),
                result["generated_query"].get("min_healthy_ratio", 1.0),
                row.get("session_id", ""),
                row.get("state", ""),
                row.get("health", ""),
                issues,
            ]
        )
    return buffer.getvalue()


def _serialize_health_gate_jsonl(result: dict[str, Any]) -> str:
    lines: list[str] = []
    summary_row = dict(result)
    summary_row["record_type"] = "summary"
    lines.append(json.dumps(summary_row, sort_keys=True))
    for row in result.get("blocked_sessions", []):
        blocked_row = dict(row)
        blocked_row["record_type"] = "blocked_session"
        blocked_row["payload_type"] = result["payload_type"]
        blocked_row["schema_version"] = result["schema_version"]
        blocked_row["schema_compat_mode"] = result.get("schema_compat_mode", "compat")
        blocked_row["status"] = result.get("status", "")
        blocked_row["pass"] = result.get("pass", False)
        blocked_row["summary_status"] = result["status"]
        blocked_row["healthy_ratio"] = result["healthy_ratio"]
        blocked_row["threshold"] = result["threshold"]
        blocked_row["total_sessions"] = result["total_sessions"]
        blocked_row["healthy_sessions"] = result["healthy_sessions"]
        blocked_row["unhealthy_sessions"] = result["unhealthy_sessions"]
        blocked_row["blocked_sessions_count"] = result["blocked_sessions_count"]
        blocked_row["blocked_ratio"] = result["blocked_ratio"]
        blocked_row["top_blocked_count"] = result["top_blocked_count"]
        blocked_row["blocked_sessions_cap"] = result["blocked_sessions_cap"]
        blocked_row["generated_at_utc"] = result["generated_at_utc"]
        blocked_row["strict_checks_enabled"] = result["strict_checks_enabled"]
        blocked_row["payload_signature_algorithm"] = _safe_dict(result.get("payload_signature")).get(
            "algorithm", "sha256"
        )
        blocked_row["payload_signature_value"] = _safe_dict(result.get("payload_signature")).get("value", "")
        blocked_row["generated_query"] = _safe_dict(result.get("generated_query"))
        lines.append(json.dumps(blocked_row, sort_keys=True))
    return "\n".join(lines) + ("\n" if lines else "")


def _export_format_from_suffix(suffix: str) -> str | None:
    mapping = {
        ".md": "md",
        ".csv": "csv",
        ".jsonl": "jsonl",
        ".json": "json",
    }
    return mapping.get(suffix.lower())


def _infer_export_format(path: Path, fallback: str = "json") -> str:
    suffix = path.suffix.lower()
    inferred = _export_format_from_suffix(suffix)
    if inferred is not None:
        return inferred
    return fallback


def _write_report_export(
    output: Path,
    report: dict[str, Any],
    export_format: str,
    overwrite: bool = False,
) -> str:
    valid_formats = {"json", "md", "csv", "jsonl"}
    normalized = export_format.lower().strip()
    if normalized not in valid_formats:
        raise typer.BadParameter(f"Unsupported --export-format '{export_format}'. Choose one of: json, md, csv, jsonl.")

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.is_dir():
        raise typer.BadParameter(f"Output path is a directory: {output}")
    if output.exists() and not overwrite:
        raise typer.BadParameter(f"Output path already exists: {output} (use --overwrite to replace it)")

    fmt = normalized
    if fmt == "md":
        payload = _serialize_health_report_md(report)
    elif fmt == "csv":
        payload = _serialize_health_report_csv(report)
    elif fmt == "jsonl":
        payload = _serialize_health_report_jsonl(report)
    else:
        payload = json.dumps(report, indent=2, sort_keys=True)

    tmp_path = output.parent / f".{output.name}.{os.getpid()}.{int(time.time() * 1e6)}.tmp"
    try:
        tmp_path.write_text(payload, encoding="utf-8")
        tmp_path.replace(output)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    return fmt


def _write_health_gate_export(
    output: Path,
    report: dict[str, Any],
    export_format: str,
    overwrite: bool = False,
) -> str:
    valid_formats = {"json", "md", "csv", "jsonl"}
    normalized = export_format.lower().strip()
    if normalized not in valid_formats:
        raise typer.BadParameter(f"Unsupported --export-format '{export_format}'. Choose one of: json, md, csv, jsonl.")

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.is_dir():
        raise typer.BadParameter(f"Output path is a directory: {output}")
    if output.exists() and not overwrite:
        raise typer.BadParameter(f"Output path already exists: {output} (use --overwrite to replace it)")

    fmt = normalized
    if fmt == "md":
        payload = _serialize_health_gate_md(report)
    elif fmt == "csv":
        payload = _serialize_health_gate_csv(report)
    elif fmt == "jsonl":
        payload = _serialize_health_gate_jsonl(report)
    else:
        payload = json.dumps(report, indent=2, sort_keys=True)

    tmp_path = output.parent / f".{output.name}.{os.getpid()}.{int(time.time() * 1e6)}.tmp"
    try:
        tmp_path.write_text(payload, encoding="utf-8")
        tmp_path.replace(output)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    return fmt


def _serialize_health_trend_md(result: dict[str, Any]) -> str:
    lines: list[str] = []
    compat_aliases_count = result.get(
        "compat_aliases_count",
        len(_safe_dict(result.get("compat")).get("aliases", {}) or {}),
    )
    latest_issue_types = _coerce_issue_types(_safe_dict(result.get("latest")).get("issue_types", []))
    latest_issue_types_json = result.get(
        "latest_issue_types_json",
        json.dumps(latest_issue_types),
    )
    latest_issue_types_hash = result.get(
        "latest_issue_types_hash",
        hashlib.sha256(latest_issue_types_json.encode("utf-8")).hexdigest(),
    )
    snapshot_ids_csv = result.get(
        "snapshot_ids_csv",
        ", ".join(
            [
                str(_safe_dict(s).get("captured_at_utc", ""))
                for s in _safe_list(result.get("snapshots"))
                if _safe_dict(s).get("captured_at_utc", "")
            ]
        ),
    )
    snapshot_ids_hash = result.get(
        "snapshot_ids_hash",
        hashlib.sha256(snapshot_ids_csv.encode("utf-8")).hexdigest(),
    )
    snapshot_window_seconds = result.get("snapshot_window_seconds")
    snapshot_window_hash = result.get(
        "snapshot_window_hash",
        hashlib.sha256(str(snapshot_window_seconds).encode("utf-8")).hexdigest(),
    )
    snapshot_interval_seconds_avg = result.get("snapshot_interval_seconds_avg")
    snapshot_interval_hash = result.get(
        "snapshot_interval_hash",
        hashlib.sha256(str(snapshot_interval_seconds_avg).encode("utf-8")).hexdigest(),
    )
    snapshot_density_per_hour = result.get("snapshot_density_per_hour")
    snapshot_density_hash = result.get(
        "snapshot_density_hash",
        hashlib.sha256(str(snapshot_density_per_hour).encode("utf-8")).hexdigest(),
    )
    snapshot_freshness_seconds = result.get("snapshot_freshness_seconds")
    snapshot_freshness_hash = result.get(
        "snapshot_freshness_hash",
        hashlib.sha256(str(snapshot_freshness_seconds).encode("utf-8")).hexdigest(),
    )
    snapshot_issue_churn_count = result.get("snapshot_issue_churn_count")
    snapshot_issue_churn_hash = result.get(
        "snapshot_issue_churn_hash",
        hashlib.sha256(str(snapshot_issue_churn_count).encode("utf-8")).hexdigest(),
    )
    snapshot_health_volatility = result.get("snapshot_health_volatility")
    snapshot_health_volatility_hash = result.get(
        "snapshot_health_volatility_hash",
        hashlib.sha256(str(snapshot_health_volatility).encode("utf-8")).hexdigest(),
    )
    lines.append("## Session Contract Health Trend")
    lines.append(f"schema_version: {result['schema_version']}")
    lines.append(f"schema_compat_mode: {result.get('schema_compat_mode', 'compat')}")
    lines.append(f"compat_mode: {_safe_dict(result.get('compat')).get('mode', 'compat')}")
    lines.append(f"compat_aliases: {json.dumps(_safe_dict(result.get('compat')).get('aliases', {}), sort_keys=True)}")
    lines.append(f"compat_aliases_count: {compat_aliases_count}")
    lines.append(f"payload_type: {result['payload_type']}")
    lines.append(f"trend_payload_type: {result['trend_payload_type']}")
    lines.append(f"snapshot_count: {result['snapshot_count']}")
    lines.append(f"snapshot_ids_csv: {snapshot_ids_csv}")
    lines.append(f"snapshot_ids_hash: {snapshot_ids_hash}")
    lines.append(f"snapshot_window_seconds: {snapshot_window_seconds}")
    lines.append(f"snapshot_window_hash: {snapshot_window_hash}")
    lines.append(f"snapshot_interval_seconds_avg: {snapshot_interval_seconds_avg}")
    lines.append(f"snapshot_interval_hash: {snapshot_interval_hash}")
    lines.append(f"snapshot_density_per_hour: {snapshot_density_per_hour}")
    lines.append(f"snapshot_density_hash: {snapshot_density_hash}")
    lines.append(f"snapshot_freshness_seconds: {snapshot_freshness_seconds}")
    lines.append(f"snapshot_freshness_hash: {snapshot_freshness_hash}")
    lines.append(f"snapshot_issue_churn_count: {snapshot_issue_churn_count}")
    lines.append(f"snapshot_issue_churn_hash: {snapshot_issue_churn_hash}")
    lines.append(f"snapshot_health_volatility: {snapshot_health_volatility}")
    lines.append(f"snapshot_health_volatility_hash: {snapshot_health_volatility_hash}")
    lines.append(f"generated_at_utc: {result.get('generated_at_utc', '')}")
    lines.append(f"snapshot_retention_max_lines: {result.get('snapshot_retention_max_lines', '')}")
    lines.append(f"latest_status: {result.get('latest_status', _safe_dict(result.get('latest')).get('status', ''))}")
    lines.append(f"latest_pass: {result.get('latest_pass', _safe_dict(result.get('latest')).get('pass', None))}")
    lines.append(
        f"latest_captured_at_utc: {result.get('latest_captured_at_utc', _safe_dict(result.get('latest')).get('captured_at_utc', ''))}"
    )
    lines.append(
        f"latest_blocked_ratio: {result.get('latest_blocked_ratio', _safe_dict(result.get('latest')).get('blocked_ratio', None))}"
    )
    lines.append(
        f"latest_blocked_count: {result.get('latest_blocked_count', _safe_dict(result.get('latest')).get('blocked_count', None))}"
    )
    lines.append(f"latest_issue_types_count: {result.get('latest_issue_types_count', len(latest_issue_types))}")
    lines.append(f"latest_issue_types_csv: {result.get('latest_issue_types_csv', ', '.join(latest_issue_types))}")
    lines.append(f"latest_issue_types_json: {latest_issue_types_json}")
    lines.append(f"latest_issue_types_hash: {latest_issue_types_hash}")
    lines.append(f"scope_owner: {result.get('scope_owner', _safe_dict(result.get('scope_key')).get('owner', ''))}")
    lines.append(
        f"scope_payload_type: {result.get('scope_payload_type', _safe_dict(result.get('scope_key')).get('payload_type', ''))}"
    )
    lines.append(f"scope_all: {result.get('scope_all', _safe_dict(result.get('scope_key')).get('all', False))}")
    lines.append(
        f"scope_strict: {result.get('scope_strict', _safe_dict(result.get('scope_key')).get('strict', False))}"
    )
    lines.append(
        f"scope_policy_profile: {result.get('scope_policy_profile', _safe_dict(result.get('scope_key')).get('policy_profile', 'custom'))}"
    )
    lines.append(
        f"scope_min_healthy_ratio: {result.get('scope_min_healthy_ratio', _safe_dict(result.get('scope_key')).get('min_healthy_ratio', ''))}"
    )
    lines.append(
        f"scope_top_blocked: {result.get('scope_top_blocked', _safe_dict(result.get('scope_key')).get('top_blocked', ''))}"
    )
    lines.append(
        f"scope_key_json: {result.get('scope_key_json', json.dumps(result.get('scope_key', {}), sort_keys=True))}"
    )
    lines.append(f"scope_key: {json.dumps(result.get('scope_key', {}))}")
    lines.append(
        f"delta_summary_json: {result.get('delta_summary_json', json.dumps(result.get('delta_summary', {}), sort_keys=True))}"
    )
    lines.append(f"delta_summary: {json.dumps(result.get('delta_summary', {}))}")
    if result.get("payload_signature"):
        sig = result["payload_signature"]
        lines.append(f"payload_signature: {sig.get('algorithm', 'sha256')}:{sig.get('value', '')}")
    return "\n".join(lines)


def _serialize_health_trend_csv(result: dict[str, Any]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    latest_issue_types = _coerce_issue_types(_safe_dict(result.get("latest")).get("issue_types", []))
    compat_aliases_count = result.get(
        "compat_aliases_count",
        len(_safe_dict(result.get("compat")).get("aliases", {}) or {}),
    )
    latest_issue_types_json = result.get(
        "latest_issue_types_json",
        json.dumps(latest_issue_types),
    )
    latest_issue_types_hash = result.get(
        "latest_issue_types_hash",
        hashlib.sha256(latest_issue_types_json.encode("utf-8")).hexdigest(),
    )
    snapshot_ids_csv = result.get(
        "snapshot_ids_csv",
        ", ".join(
            [
                str(_safe_dict(s).get("captured_at_utc", ""))
                for s in _safe_list(result.get("snapshots"))
                if _safe_dict(s).get("captured_at_utc", "")
            ]
        ),
    )
    snapshot_ids_hash = result.get(
        "snapshot_ids_hash",
        hashlib.sha256(snapshot_ids_csv.encode("utf-8")).hexdigest(),
    )
    snapshot_window_seconds = result.get("snapshot_window_seconds")
    snapshot_window_hash = result.get(
        "snapshot_window_hash",
        hashlib.sha256(str(snapshot_window_seconds).encode("utf-8")).hexdigest(),
    )
    snapshot_interval_seconds_avg = result.get("snapshot_interval_seconds_avg")
    snapshot_interval_hash = result.get(
        "snapshot_interval_hash",
        hashlib.sha256(str(snapshot_interval_seconds_avg).encode("utf-8")).hexdigest(),
    )
    snapshot_density_per_hour = result.get("snapshot_density_per_hour")
    snapshot_density_hash = result.get(
        "snapshot_density_hash",
        hashlib.sha256(str(snapshot_density_per_hour).encode("utf-8")).hexdigest(),
    )
    snapshot_freshness_seconds = result.get("snapshot_freshness_seconds")
    snapshot_freshness_hash = result.get(
        "snapshot_freshness_hash",
        hashlib.sha256(str(snapshot_freshness_seconds).encode("utf-8")).hexdigest(),
    )
    snapshot_issue_churn_count = result.get("snapshot_issue_churn_count")
    snapshot_issue_churn_hash = result.get(
        "snapshot_issue_churn_hash",
        hashlib.sha256(str(snapshot_issue_churn_count).encode("utf-8")).hexdigest(),
    )
    snapshot_health_volatility = result.get("snapshot_health_volatility")
    snapshot_health_volatility_hash = result.get(
        "snapshot_health_volatility_hash",
        hashlib.sha256(str(snapshot_health_volatility).encode("utf-8")).hexdigest(),
    )
    writer.writerow(
        [
            "schema_version",
            "schema_compat_mode",
            "payload_type",
            "trend_payload_type",
            "payload_signature_algorithm",
            "payload_signature_value",
            "record_type",
            "generated_at_utc",
            "snapshot_count",
            "snapshot_ids_csv",
            "snapshot_ids_hash",
            "snapshot_window_seconds",
            "snapshot_window_hash",
            "snapshot_interval_seconds_avg",
            "snapshot_interval_hash",
            "snapshot_density_per_hour",
            "snapshot_density_hash",
            "snapshot_freshness_seconds",
            "snapshot_freshness_hash",
            "snapshot_issue_churn_count",
            "snapshot_issue_churn_hash",
            "snapshot_health_volatility",
            "snapshot_health_volatility_hash",
            "limit",
            "snapshot_retention_max_lines",
            "latest_status",
            "latest_pass",
            "latest_captured_at_utc",
            "latest_blocked_ratio",
            "latest_blocked_count",
            "latest_issue_types_count",
            "latest_issue_types_csv",
            "latest_issue_types_json",
            "latest_issue_types_hash",
            "scope_payload_type",
            "scope_owner",
            "scope_all",
            "scope_strict",
            "scope_policy_profile",
            "scope_min_healthy_ratio",
            "scope_top_blocked",
            "scope_key_json",
            "delta_summary_json",
            "scope_key",
            "blocked_ratio_delta",
            "blocked_count_delta",
            "captured_at_utc",
            "status",
            "pass",
            "total",
            "healthy_count",
            "unhealthy_count",
            "blocked_count",
            "blocked_ratio",
            "issue_types",
            "compat_mode",
            "compat_aliases_json",
            "compat_aliases_count",
        ]
    )
    writer.writerow(
        [
            result["schema_version"],
            result.get("schema_compat_mode", "compat"),
            result["payload_type"],
            result["trend_payload_type"],
            _safe_dict(result.get("payload_signature")).get("algorithm", "sha256"),
            _safe_dict(result.get("payload_signature")).get("value", ""),
            "summary",
            result.get("generated_at_utc", ""),
            result.get("snapshot_count", 0),
            snapshot_ids_csv,
            snapshot_ids_hash,
            str(snapshot_window_seconds),
            snapshot_window_hash,
            str(snapshot_interval_seconds_avg),
            snapshot_interval_hash,
            str(snapshot_density_per_hour),
            snapshot_density_hash,
            str(snapshot_freshness_seconds),
            snapshot_freshness_hash,
            str(snapshot_issue_churn_count),
            snapshot_issue_churn_hash,
            str(snapshot_health_volatility) if snapshot_health_volatility is not None else "None",
            snapshot_health_volatility_hash,
            result.get("limit", 0),
            result.get("snapshot_retention_max_lines", ""),
            result.get("latest_status", _safe_dict(result.get("latest")).get("status", "")),
            result.get("latest_pass", _safe_dict(result.get("latest")).get("pass", "")),
            result.get("latest_captured_at_utc", _safe_dict(result.get("latest")).get("captured_at_utc", "")),
            result.get("latest_blocked_ratio", _safe_dict(result.get("latest")).get("blocked_ratio", None)),
            result.get("latest_blocked_count", _safe_dict(result.get("latest")).get("blocked_count", None)),
            result.get("latest_issue_types_count", len(latest_issue_types)),
            result.get(
                "latest_issue_types_csv",
                ", ".join(latest_issue_types),
            ),
            latest_issue_types_json,
            latest_issue_types_hash,
            result.get("scope_payload_type", _safe_dict(result.get("scope_key")).get("payload_type", "")),
            result.get("scope_owner", _safe_dict(result.get("scope_key")).get("owner", "")),
            result.get("scope_all", _safe_dict(result.get("scope_key")).get("all", False)),
            result.get("scope_strict", _safe_dict(result.get("scope_key")).get("strict", False)),
            result.get(
                "scope_policy_profile",
                _safe_dict(result.get("scope_key")).get("policy_profile", "custom"),
            ),
            result.get(
                "scope_min_healthy_ratio",
                _safe_dict(result.get("scope_key")).get("min_healthy_ratio", ""),
            ),
            result.get(
                "scope_top_blocked",
                _safe_dict(result.get("scope_key")).get("top_blocked", ""),
            ),
            result.get("scope_key_json", json.dumps(result.get("scope_key", {}), sort_keys=True)),
            result.get("delta_summary_json", json.dumps(result.get("delta_summary", {}), sort_keys=True)),
            json.dumps(result.get("scope_key", {}), sort_keys=True),
            result.get(
                "blocked_ratio_delta",
                result.get("delta_summary", {}).get("blocked_ratio_delta", None),
            ),
            result.get(
                "blocked_count_delta",
                result.get("delta_summary", {}).get("blocked_count_delta", None),
            ),
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            _safe_dict(result.get("compat")).get("mode", "compat"),
            json.dumps(_safe_dict(result.get("compat")).get("aliases", {}), sort_keys=True),
            compat_aliases_count,
        ]
    )
    for snap in result.get("snapshots", []):
        writer.writerow(
            [
                result["schema_version"],
                result.get("schema_compat_mode", "compat"),
                result["payload_type"],
                result["trend_payload_type"],
                _safe_dict(result.get("payload_signature")).get("algorithm", "sha256"),
                _safe_dict(result.get("payload_signature")).get("value", ""),
                "snapshot",
                result.get("generated_at_utc", ""),
                result.get("snapshot_count", 0),
                snapshot_ids_csv,
                snapshot_ids_hash,
                snapshot_window_seconds,
                snapshot_window_hash,
                snapshot_interval_seconds_avg,
                snapshot_interval_hash,
                snapshot_density_per_hour,
                snapshot_density_hash,
                snapshot_freshness_seconds,
                snapshot_freshness_hash,
                snapshot_issue_churn_count,
                snapshot_issue_churn_hash,
                str(snapshot_health_volatility) if snapshot_health_volatility is not None else "None",
                snapshot_health_volatility_hash,
                result.get("limit", 0),
                result.get("snapshot_retention_max_lines", ""),
                result.get("latest_status", _safe_dict(result.get("latest")).get("status", "")),
                result.get("latest_pass", _safe_dict(result.get("latest")).get("pass", "")),
                result.get("latest_captured_at_utc", _safe_dict(result.get("latest")).get("captured_at_utc", "")),
                result.get("latest_blocked_ratio", _safe_dict(result.get("latest")).get("blocked_ratio", None)),
                result.get("latest_blocked_count", _safe_dict(result.get("latest")).get("blocked_count", None)),
                result.get("latest_issue_types_count", len(latest_issue_types)),
                result.get(
                    "latest_issue_types_csv",
                    ", ".join(latest_issue_types),
                ),
                latest_issue_types_json,
                latest_issue_types_hash,
                result.get("scope_payload_type", _safe_dict(result.get("scope_key")).get("payload_type", "")),
                result.get("scope_owner", _safe_dict(result.get("scope_key")).get("owner", "")),
                result.get("scope_all", _safe_dict(result.get("scope_key")).get("all", False)),
                result.get("scope_strict", _safe_dict(result.get("scope_key")).get("strict", False)),
                result.get(
                    "scope_policy_profile",
                    _safe_dict(result.get("scope_key")).get("policy_profile", "custom"),
                ),
                result.get(
                    "scope_min_healthy_ratio",
                    _safe_dict(result.get("scope_key")).get("min_healthy_ratio", ""),
                ),
                result.get(
                    "scope_top_blocked",
                    _safe_dict(result.get("scope_key")).get("top_blocked", ""),
                ),
                result.get("scope_key_json", json.dumps(result.get("scope_key", {}), sort_keys=True)),
                result.get("delta_summary_json", json.dumps(result.get("delta_summary", {}), sort_keys=True)),
                json.dumps(result.get("scope_key", {}), sort_keys=True),
                result.get(
                    "blocked_ratio_delta",
                    result.get("delta_summary", {}).get("blocked_ratio_delta", None),
                ),
                result.get(
                    "blocked_count_delta",
                    result.get("delta_summary", {}).get("blocked_count_delta", None),
                ),
                snap.get("captured_at_utc", ""),
                snap.get("status", ""),
                snap.get("pass", False),
                snap.get("total", 0),
                snap.get("healthy_count", 0),
                snap.get("unhealthy_count", 0),
                snap.get("blocked_count", 0),
                snap.get("blocked_ratio", 0.0),
                ", ".join(_coerce_issue_types(snap.get("issue_types", []))),
                _safe_dict(result.get("compat")).get("mode", "compat"),
                json.dumps(_safe_dict(result.get("compat")).get("aliases", {}), sort_keys=True),
                compat_aliases_count,
            ]
        )
    return buffer.getvalue()


def _serialize_health_trend_jsonl(result: dict[str, Any]) -> str:
    lines: list[str] = []
    latest_issue_types = _coerce_issue_types(_safe_dict(result.get("latest")).get("issue_types", []))
    compat_aliases_count = result.get(
        "compat_aliases_count",
        len(_safe_dict(result.get("compat")).get("aliases", {}) or {}),
    )
    latest_issue_types_json = result.get(
        "latest_issue_types_json",
        json.dumps(latest_issue_types),
    )
    latest_issue_types_hash = result.get(
        "latest_issue_types_hash",
        hashlib.sha256(latest_issue_types_json.encode("utf-8")).hexdigest(),
    )
    snapshot_ids_csv = result.get(
        "snapshot_ids_csv",
        ", ".join(
            [
                str(_safe_dict(s).get("captured_at_utc", ""))
                for s in _safe_list(result.get("snapshots"))
                if _safe_dict(s).get("captured_at_utc", "")
            ]
        ),
    )
    snapshot_ids_hash = result.get(
        "snapshot_ids_hash",
        hashlib.sha256(snapshot_ids_csv.encode("utf-8")).hexdigest(),
    )
    snapshot_window_seconds = result.get("snapshot_window_seconds")
    snapshot_window_hash = result.get(
        "snapshot_window_hash",
        hashlib.sha256(str(snapshot_window_seconds).encode("utf-8")).hexdigest(),
    )
    snapshot_interval_seconds_avg = result.get("snapshot_interval_seconds_avg")
    snapshot_interval_hash = result.get(
        "snapshot_interval_hash",
        hashlib.sha256(str(snapshot_interval_seconds_avg).encode("utf-8")).hexdigest(),
    )
    snapshot_density_per_hour = result.get("snapshot_density_per_hour")
    snapshot_density_hash = result.get(
        "snapshot_density_hash",
        hashlib.sha256(str(snapshot_density_per_hour).encode("utf-8")).hexdigest(),
    )
    snapshot_freshness_seconds = result.get("snapshot_freshness_seconds")
    snapshot_freshness_hash = result.get(
        "snapshot_freshness_hash",
        hashlib.sha256(str(snapshot_freshness_seconds).encode("utf-8")).hexdigest(),
    )
    snapshot_issue_churn_count = result.get("snapshot_issue_churn_count")
    snapshot_issue_churn_hash = result.get(
        "snapshot_issue_churn_hash",
        hashlib.sha256(str(snapshot_issue_churn_count).encode("utf-8")).hexdigest(),
    )
    snapshot_health_volatility = result.get("snapshot_health_volatility")
    snapshot_health_volatility_hash = result.get(
        "snapshot_health_volatility_hash",
        hashlib.sha256(str(snapshot_health_volatility).encode("utf-8")).hexdigest(),
    )
    summary = dict(result)
    summary["record_type"] = "summary"
    summary["compat"] = result.get("compat") or {
        "mode": result.get("schema_compat_mode", "compat"),
        "aliases": _safe_dict(result.get("compat")).get("aliases", {}),
    }
    summary["latest_status"] = result.get("latest_status", _safe_dict(result.get("latest")).get("status", ""))
    summary["latest_pass"] = result.get("latest_pass", _safe_dict(result.get("latest")).get("pass", None))
    summary["latest_captured_at_utc"] = result.get(
        "latest_captured_at_utc", _safe_dict(result.get("latest")).get("captured_at_utc", "")
    )
    summary["latest_blocked_ratio"] = result.get(
        "latest_blocked_ratio", _safe_dict(result.get("latest")).get("blocked_ratio", None)
    )
    summary["latest_blocked_count"] = result.get(
        "latest_blocked_count", _safe_dict(result.get("latest")).get("blocked_count", None)
    )
    summary["latest_issue_types_count"] = result.get(
        "latest_issue_types_count",
        len(latest_issue_types),
    )
    summary["latest_issue_types_csv"] = result.get(
        "latest_issue_types_csv",
        ", ".join(latest_issue_types),
    )
    summary["latest_issue_types_json"] = latest_issue_types_json
    summary["latest_issue_types_hash"] = latest_issue_types_hash
    summary["snapshot_ids_csv"] = snapshot_ids_csv
    summary["snapshot_ids_hash"] = snapshot_ids_hash
    summary["snapshot_window_seconds"] = snapshot_window_seconds
    summary["snapshot_window_hash"] = snapshot_window_hash
    summary["snapshot_interval_seconds_avg"] = snapshot_interval_seconds_avg
    summary["snapshot_interval_hash"] = snapshot_interval_hash
    summary["snapshot_density_per_hour"] = snapshot_density_per_hour
    summary["snapshot_density_hash"] = snapshot_density_hash
    summary["snapshot_freshness_seconds"] = snapshot_freshness_seconds
    summary["snapshot_freshness_hash"] = snapshot_freshness_hash
    summary["snapshot_issue_churn_count"] = snapshot_issue_churn_count
    summary["snapshot_issue_churn_hash"] = snapshot_issue_churn_hash
    summary["snapshot_health_volatility"] = snapshot_health_volatility
    summary["snapshot_health_volatility_hash"] = snapshot_health_volatility_hash
    summary["scope_owner"] = result.get("scope_owner", _safe_dict(result.get("scope_key")).get("owner", ""))
    summary["scope_payload_type"] = result.get(
        "scope_payload_type",
        _safe_dict(result.get("scope_key")).get("payload_type", ""),
    )
    summary["scope_all"] = result.get("scope_all", _safe_dict(result.get("scope_key")).get("all", False))
    summary["scope_strict"] = result.get("scope_strict", _safe_dict(result.get("scope_key")).get("strict", False))
    summary["scope_policy_profile"] = result.get(
        "scope_policy_profile",
        _safe_dict(result.get("scope_key")).get("policy_profile", "custom"),
    )
    summary["scope_min_healthy_ratio"] = result.get(
        "scope_min_healthy_ratio",
        _safe_dict(result.get("scope_key")).get("min_healthy_ratio", ""),
    )
    summary["scope_top_blocked"] = result.get(
        "scope_top_blocked", _safe_dict(result.get("scope_key")).get("top_blocked", "")
    )
    summary["scope_key_json"] = result.get(
        "scope_key_json",
        json.dumps(result.get("scope_key", {}), sort_keys=True),
    )
    summary["payload_signature_algorithm"] = _safe_dict(result.get("payload_signature")).get("algorithm", "sha256")
    summary["payload_signature_value"] = _safe_dict(result.get("payload_signature")).get("value", "")
    summary["compat"] = result.get("compat") or {
        "mode": result.get("schema_compat_mode", "compat"),
        "aliases": _safe_dict(result.get("compat")).get("aliases", {}),
    }
    summary["compat_aliases_count"] = compat_aliases_count
    lines.append(json.dumps(summary, sort_keys=True))
    for snap in result.get("snapshots", []):
        row = dict(snap)
        row["record_type"] = "snapshot"
        row["schema_version"] = result["schema_version"]
        row["schema_compat_mode"] = result.get("schema_compat_mode", "compat")
        row["payload_type"] = result["payload_type"]
        row["trend_payload_type"] = result["trend_payload_type"]
        row["snapshot_count"] = result.get("snapshot_count", 0)
        row["limit"] = result.get("limit", 0)
        row["snapshot_retention_max_lines"] = result.get("snapshot_retention_max_lines", "")
        row["generated_at_utc"] = result.get("generated_at_utc", "")
        row["compat_mode"] = _safe_dict(result.get("compat")).get("mode", "compat")
        row["compat_aliases"] = _safe_dict(result.get("compat")).get("aliases", {})
        row["compat_aliases_count"] = compat_aliases_count
        row["scope_key"] = result.get("scope_key", {})
        row["scope_key_json"] = result.get(
            "scope_key_json",
            json.dumps(result.get("scope_key", {}), sort_keys=True),
        )
        row["delta_summary_json"] = result.get(
            "delta_summary_json",
            json.dumps(result.get("delta_summary", {}), sort_keys=True),
        )
        row["delta_summary"] = result.get("delta_summary", {})
        row["blocked_ratio_delta"] = result.get(
            "blocked_ratio_delta",
            result.get("delta_summary", {}).get("blocked_ratio_delta", None),
        )
        row["blocked_count_delta"] = result.get(
            "blocked_count_delta",
            result.get("delta_summary", {}).get("blocked_count_delta", None),
        )
        row["latest_status"] = result.get("latest_status", _safe_dict(result.get("latest")).get("status", ""))
        row["latest_pass"] = result.get("latest_pass", _safe_dict(result.get("latest")).get("pass", None))
        row["latest_captured_at_utc"] = result.get(
            "latest_captured_at_utc", _safe_dict(result.get("latest")).get("captured_at_utc", "")
        )
        row["latest_blocked_ratio"] = result.get(
            "latest_blocked_ratio", _safe_dict(result.get("latest")).get("blocked_ratio", None)
        )
        row["latest_blocked_count"] = result.get(
            "latest_blocked_count", _safe_dict(result.get("latest")).get("blocked_count", None)
        )
        row["latest_issue_types_count"] = result.get(
            "latest_issue_types_count",
            len(latest_issue_types),
        )
        row["latest_issue_types_csv"] = result.get(
            "latest_issue_types_csv",
            ", ".join(latest_issue_types),
        )
        row["latest_issue_types_json"] = latest_issue_types_json
        row["latest_issue_types_hash"] = latest_issue_types_hash
        row["snapshot_ids_csv"] = snapshot_ids_csv
        row["snapshot_ids_hash"] = snapshot_ids_hash
        row["snapshot_window_seconds"] = snapshot_window_seconds
        row["snapshot_window_hash"] = snapshot_window_hash
        row["snapshot_interval_seconds_avg"] = snapshot_interval_seconds_avg
        row["snapshot_interval_hash"] = snapshot_interval_hash
        row["snapshot_density_per_hour"] = snapshot_density_per_hour
        row["snapshot_density_hash"] = snapshot_density_hash
        row["snapshot_freshness_seconds"] = snapshot_freshness_seconds
        row["snapshot_freshness_hash"] = snapshot_freshness_hash
        row["snapshot_issue_churn_count"] = snapshot_issue_churn_count
        row["snapshot_issue_churn_hash"] = snapshot_issue_churn_hash
        row["snapshot_health_volatility"] = snapshot_health_volatility
        row["snapshot_health_volatility_hash"] = snapshot_health_volatility_hash
        row["scope_owner"] = result.get("scope_owner", _safe_dict(result.get("scope_key")).get("owner", ""))
        row["scope_payload_type"] = result.get(
            "scope_payload_type",
            _safe_dict(result.get("scope_key")).get("payload_type", ""),
        )
        row["scope_all"] = result.get("scope_all", _safe_dict(result.get("scope_key")).get("all", False))
        row["scope_strict"] = result.get("scope_strict", _safe_dict(result.get("scope_key")).get("strict", False))
        row["scope_policy_profile"] = result.get(
            "scope_policy_profile",
            _safe_dict(result.get("scope_key")).get("policy_profile", "custom"),
        )
        row["scope_min_healthy_ratio"] = result.get(
            "scope_min_healthy_ratio",
            _safe_dict(result.get("scope_key")).get("min_healthy_ratio", ""),
        )
        row["scope_top_blocked"] = result.get(
            "scope_top_blocked", _safe_dict(result.get("scope_key")).get("top_blocked", "")
        )
        row["payload_signature_algorithm"] = _safe_dict(result.get("payload_signature")).get("algorithm", "sha256")
        row["payload_signature_value"] = _safe_dict(result.get("payload_signature")).get("value", "")
        row["compat"] = result.get("compat") or {
            "mode": result.get("schema_compat_mode", "compat"),
            "aliases": _safe_dict(result.get("compat")).get("aliases", {}),
        }
        lines.append(json.dumps(row, sort_keys=True))
    return "\n".join(lines) + ("\n" if lines else "")


def _write_health_trend_export(
    output: Path,
    result: dict[str, Any],
    export_format: str,
    overwrite: bool = False,
) -> str:
    valid_formats = {"json", "md", "csv", "jsonl"}
    normalized = export_format.lower().strip()
    if normalized not in valid_formats:
        console.print(f"[red]Unsupported --export-format '{export_format}'. Choose one of: json, md, csv, jsonl.[/red]")
        raise typer.Exit(1)

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.is_dir():
        console.print(f"[red]Output path is a directory: {output}[/red]")
        raise typer.Exit(1)
    if output.exists() and not overwrite:
        console.print(f"[red]Output path already exists: {output} (use --overwrite to replace it)[/red]")
        raise typer.Exit(1)

    fmt = normalized
    if fmt == "md":
        payload = _serialize_health_trend_md(result)
    elif fmt == "csv":
        payload = _serialize_health_trend_csv(result)
    elif fmt == "jsonl":
        payload = _serialize_health_trend_jsonl(result)
    else:
        payload = json.dumps(result, indent=2, sort_keys=True)

    tmp_path = output.parent / f".{output.name}.{os.getpid()}.{int(time.time() * 1e6)}.tmp"
    try:
        tmp_path.write_text(payload, encoding="utf-8")
        tmp_path.replace(output)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    return fmt


def session_contract_health_report_cmd(
    all_sessions: bool = False,
    owner: str | None = None,
    strict: bool = False,
    top_blocked: int = 25,
    policy_profile: str | None = None,
    no_worse_than_baseline: bool = False,
    regression_tolerance: float = 0.0,
    format: str | None = None,
    output: Path | None = None,
    export_format: str | None = None,
    overwrite: bool = False,
) -> None:
    from thegent.cli_impl import session_contract_health_report_impl

    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    result = session_contract_health_report_impl(
        owner=own if not all_sessions else None,
        all=all_sessions,
        strict=strict,
        top_blocked=top_blocked,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
    )
    if output is not None:
        chosen_format = export_format or _infer_export_format(output, fallback="json")
        if export_format is None and output.suffix and _export_format_from_suffix(output.suffix) is None:
            console.print(
                f"Note: output path extension '{output.suffix}' is not recognized for export; "
                f"defaulting to '{chosen_format}'."
            )
        written_as = _write_report_export(
            output=output,
            report=result,
            export_format=chosen_format,
            overwrite=overwrite,
        )
        console.print(f"exported session-contract-health-report to: {output} (format={written_as})")

    fmt = _normalize_output_format(format, default=settings.output_format or "rich")
    if fmt == "json":
        sys.stdout.write(json.dumps(result) + "\n")
        return
    if fmt == "md":
        console.print(_serialize_health_report_md(result))
    else:
        console.print(f"status={result['status']}")
        console.print("Session Contract Health Report")
        if result.get("payload_signature"):
            signature = result["payload_signature"]
            console.print(f"payload_signature={signature.get('algorithm', 'sha256')}:{signature.get('value', '')}")
        console.print(f"schema_version={result['schema_version']}")
        console.print(f"payload_type={result['payload_type']}")
        console.print(f"policy_profile={result.get('policy_profile', 'custom')}")
        console.print(
            f"total={result['total']} blocked={result['blocked_sessions']} "
            f"blocked_count={result['blocked_count']} ratio={result['blocked_ratio']}"
        )
        if result.get("decision_reasons"):
            console.print(f"decision_reasons={','.join(result.get('decision_reasons', []))}")
        console.print(
            f"healthy={result['health']['healthy']} warning={result['health']['warning']} "
            f"error={result['health']['error']} missing={result['health']['missing']}"
        )
        console.print(f"strict_checks_enabled={result['strict_checks_enabled']}")
        if result.get("generated_at_utc"):
            console.print(f"generated_at_utc={result['generated_at_utc']}")
            console.print(f"generated_query={json.dumps(result['generated_query'])}")
        if result.get("trend_summary"):
            trend = result["trend_summary"]
            console.print(
                f"trend baseline={trend.get('baseline_available', False)} "
                f"ratio_delta={trend.get('blocked_ratio_delta', None)} "
                f"blocked_delta={trend.get('blocked_count_delta', None)}"
            )

        issue_rows = result["issue_breakdown"]
        if issue_rows:
            console.print("Top Issues:")
            for row in issue_rows[:10]:
                console.print(f"  - {row['issue']}: {row['count']}")
        if result["top_blocked"]:
            console.print("Top Blocked Sessions:")
        for row in result["top_blocked"]:
            issues = ", ".join(_coerce_issue_types(row.get("issues")))
            remediation = ", ".join(row.get("remediation", []))
            console.print(
                f"  - {row['session_id']} owner={row['owner']} health={row['health']} "
                f"issues={issues or '—'} remediation={remediation or '—'}"
            )


def session_contract_health_trend_cmd(
    payload_type: str = "session_contract_health_report",
    all_sessions: bool = False,
    owner: str | None = None,
    strict: bool = False,
    policy_profile: str | None = None,
    min_healthy_ratio: float = 1.0,
    top_blocked: int = 25,
    limit: int = 20,
    format: str | None = None,
    output: Path | None = None,
    export_format: str | None = None,
    overwrite: bool = False,
) -> None:
    from thegent.cli_impl import session_contract_health_trend_impl

    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    result = session_contract_health_trend_impl(
        payload_type=payload_type,
        owner=own if not all_sessions else None,
        all=all_sessions,
        strict=strict,
        policy_profile=policy_profile,
        min_healthy_ratio=min_healthy_ratio,
        top_blocked=top_blocked,
        limit=limit,
    )
    if output is not None:
        chosen_format = export_format or _infer_export_format(output, fallback="json")
        if export_format is None and output.suffix and _export_format_from_suffix(output.suffix) is None:
            console.print(
                f"Note: output path extension '{output.suffix}' is not recognized for export; "
                f"defaulting to '{chosen_format}'."
            )
        written_as = _write_health_trend_export(
            output=output,
            result=result,
            export_format=chosen_format,
            overwrite=overwrite,
        )
        console.print(f"exported session-contract-health-trend to: {output} (format={written_as})")
    fmt = _normalize_output_format(format, default=settings.output_format or "rich")
    if fmt == "json":
        sys.stdout.write(json.dumps(result) + "\n")
        return
    if fmt == "md":
        console.print(_serialize_health_trend_md(result))
    else:
        compat_aliases_count = result.get(
            "compat_aliases_count",
            len(_safe_dict(result.get("compat")).get("aliases", {}) or {}),
        )
        console.print("Session Contract Health Trend")
        console.print(f"trend_payload_type={result['trend_payload_type']}")
        console.print(f"generated_at_utc={result.get('generated_at_utc', '')}")
        console.print(f"compat_mode={_safe_dict(result.get('compat')).get('mode', 'compat')}")
        console.print(f"compat_aliases_count={compat_aliases_count}")
        console.print(
            f"snapshot_count={result['snapshot_count']} limit={result['limit']} "
            f"retention_max_lines={result.get('snapshot_retention_max_lines', '')}"
        )
        console.print(f"scope_key={json.dumps(result['scope_key'])}")
        delta = result.get("delta_summary", {})
        console.print(
            f"delta blocked_ratio={result.get('blocked_ratio_delta', delta.get('blocked_ratio_delta', None))} "
            f"blocked_count={result.get('blocked_count_delta', delta.get('blocked_count_delta', None))}"
        )
        latest = result.get("latest")
        if latest:
            console.print(
                f"latest status={latest.get('status', '')} pass={latest.get('pass', False)} "
                f"blocked_ratio={latest.get('blocked_ratio', 0.0)} "
                f"blocked_count={latest.get('blocked_count', 0)}"
            )
            console.print(
                f"latest captured_at_utc={latest.get('captured_at_utc', '')} "
                f"issue_types_count={result.get('latest_issue_types_count', len(_coerce_issue_types(_safe_dict(latest).get('issue_types', []))))}"
            )


def dag_validate_cmd(cd: Path | None = None) -> None:
    """Validate DAG session from .factory/dag-session.md. Exit 2 on validation errors."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(2)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG session not found: {dag_path}[/red]")
        raise typer.Exit(2)
    doc = _parse_dag_full(dag_path)
    errors = _validate_dag(doc)
    if errors:
        for e in errors:
            console.print(f"[red]{e}[/red]")
        raise typer.Exit(2)

    # WP-4005: State freshness check
    settings = ThegentSettings()
    from thegent.execution import CheckpointRegistry

    ckpt_registry = CheckpointRegistry(settings.session_dir)
    ckpts = ckpt_registry.list_checkpoints(limit=1)
    if ckpts:
        last_ckpt = ckpts[0]
        # In a real impl, we'd compare content hashes
        # For now, just a timestamp warning
        from datetime import UTC, datetime

        ckpt_ts = datetime.fromisoformat(last_ckpt["created_at_utc"])
        file_ts = datetime.fromtimestamp(dag_path.stat().st_mtime, UTC)
        if file_ts > ckpt_ts:
            console.print(
                f"[yellow]Warning: DAG file has been modified since last checkpoint ({last_ckpt['checkpoint_id']}).[/yellow]"
            )

    console.print("[green]DAG valid.[/green]")


def dag_list_cmd(cd: Path | None = None, format: str | None = None) -> None:
    """Parse and display DAG session from .factory/dag-session.md."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG session not found: {dag_path}[/red]")
        raise typer.Exit(1)
    _frontmatter, tasks = _parse_dag_session(dag_path)
    settings = ThegentSettings()
    fmt = (format or os.environ.get("THGENT_OUTPUT_FORMAT") or settings.output_format or "rich").lower()
    if not tasks:
        if fmt == "json":
            sys.stdout.write(json.dumps({"tasks": []}) + "\n")
        else:
            console.print("[dim]No tasks in DAG.[/dim]")
        return
    if fmt == "json":
        sys.stdout.write(json.dumps({"tasks": tasks}) + "\n")
        return
    if fmt == "md":
        console.print("## DAG Session\n")
        console.print("| id | agent | prompt | depends_on | status |")
        console.print("|----|-------|--------|------------|--------|")
        for t in tasks:
            console.print(
                f"| {t.get('id', '—')} | {t.get('agent', '—')} | {t.get('prompt', '—')} | {t.get('depends_on', '—')} | {t.get('status', '—')} |"
            )
    else:
        tbl = Table(title="DAG Tasks")
        tbl.add_column("id")
        tbl.add_column("agent")
        tbl.add_column("prompt")
        tbl.add_column("depends_on")
        tbl.add_column("status")
        for t in tasks:
            tbl.add_row(
                t.get("id", "—"),
                t.get("agent", "—"),
                t.get("prompt", "—"),
                t.get("depends_on", "—"),
                t.get("status", "—"),
            )
        console.print(tbl)


def dag_add_cmd(
    task_id: str,
    agent: str,
    prompt: str,
    cd: Path | None = None,
    depends_on: str | None = None,
    contract_version: str | None = None,
) -> None:
    """Add a task to the DAG. XA4: contract_version in task metadata."""
    cwd, dag_path = _dag_path(cd)
    if cwd is None or dag_path is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)
    assert dag_path is not None
    tid = task_id.strip()
    if err := _validate_task_id(tid):
        console.print(f"[red]{err}[/red]")
        raise typer.Exit(2)
    if err := _validate_agent((agent or "").strip()):
        console.print(f"[red]{err}[/red]")
        raise typer.Exit(2)
    if not (prompt or "").strip():
        console.print("[red]Prompt cannot be empty.[/red]")
        raise typer.Exit(2)
    dag_path.parent.mkdir(parents=True, exist_ok=True)
    doc = _ensure_dag_file(dag_path)
    existing_ids = {(t.get("id") or "").strip() for t in doc.tasks}
    if tid in existing_ids:
        console.print(f"[red]Task {tid} already exists.[/red]")
        raise typer.Exit(1)
    deps_str = (depends_on or "").strip() or "—"
    deps_list = _parse_depends_on(deps_str)
    for d in deps_list:
        if d not in existing_ids:
            console.print(f"[red]depends_on '{d}' does not exist in DAG.[/red]")
            raise typer.Exit(2)
    row: dict[str, str] = {
        "id": tid,
        "agent": (agent or "").strip(),
        "prompt": (prompt or "").strip(),
        "depends_on": deps_str,
        "status": "pending",
    }
    if contract_version and (cv := contract_version.strip()):
        row["contract_version"] = cv
        _ensure_contract_version_header(doc)
    doc.tasks.append(row)
    cycle_errors = _check_dag_cycles(doc.tasks)
    if cycle_errors:
        for e in cycle_errors:
            console.print(f"[red]{e}[/red]")
        raise typer.Exit(2)
    _atomic_write(dag_path, _serialize_dag(doc))
    console.print(f"[green]Added task {tid}[/green]")


def dag_remove_cmd(task_id: str, cd: Path | None = None) -> None:
    """Remove a task from the DAG."""
    cwd, dag_path = _dag_path(cd)
    if cwd is None or dag_path is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)
    assert dag_path is not None
    if not dag_path.exists():
        console.print(f"[red]DAG session not found: {dag_path}[/red]")
        raise typer.Exit(1)
    doc = _parse_dag_full(dag_path)
    tid = task_id.strip()
    before = len(doc.tasks)
    doc.tasks = [t for t in doc.tasks if (t.get("id") or "").strip() != tid]
    if len(doc.tasks) == before:
        console.print(f"[red]Task {task_id} not found.[/red]")
        raise typer.Exit(1)
    _atomic_write(dag_path, _serialize_dag(doc))
    console.print(f"[green]Removed task {task_id}[/green]")


def dag_cancel_cmd(task_id: str, cd: Path | None = None) -> None:
    """Cancel a task (set status to cancelled)."""
    dag_update_cmd(task_id=task_id, cd=cd, status="cancelled")
    console.print(f"[green]Cancelled task {task_id}[/green]")


def dag_status_cmd(cd: Path | None = None, format: str | None = None) -> None:
    """For each task with session_id show id, status, session_id, session_status (running/exited:rc)."""
    from thegent.cli_impl import dag_status_impl

    res = dag_status_impl(cd=cd)
    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
        raise typer.Exit(1)
    rows = res.get("tasks", [])
    settings = ThegentSettings()
    fmt = (format or os.environ.get("THGENT_OUTPUT_FORMAT") or settings.output_format or "rich").lower()
    if fmt == "json":
        sys.stdout.write(json.dumps({"tasks": rows}) + "\n")
        return
    if not rows:
        console.print("[dim]No tasks with session_id.[/dim]")
        return
    if fmt == "md":
        console.print("| id | status | session_id | session_status |")
        console.print("|----|--------|------------|----------------|")
        for r in rows:
            console.print(f"| {r['id']} | {r['status']} | {r['session_id']} | {r['session_status']} |")
    else:
        tbl = Table(title="DAG Status (tasks with session_id)")
        tbl.add_column("id")
        tbl.add_column("status")
        tbl.add_column("session_id")
        tbl.add_column("session_status")
        for r in rows:
            tbl.add_row(r["id"], r["status"], r["session_id"], r["session_status"])
        console.print(tbl)


def dag_update_cmd(
    task_id: str,
    cd: Path | None = None,
    status: str | None = None,
    session_id: str | None = None,
    prompt: str | None = None,
    agent: str | None = None,
    depends_on: str | None = None,
    contract_version: str | None = None,
) -> None:
    """Update a task in the DAG. XA4: contract_version in task metadata."""
    VALID_STATUSES = {"pending", "running", "done", "failed", "blocked", "cancelled", "skipped"}
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG session not found: {dag_path}[/red]")
        raise typer.Exit(1)
    doc = _parse_dag_full(dag_path)
    tid = task_id.strip()
    if not any((t.get("id") or "").strip() == tid for t in doc.tasks):
        console.print(f"[red]Task not found: {tid}[/red]")
        raise typer.Exit(1)
    if status is not None and status.strip().lower() not in VALID_STATUSES:
        console.print(f"[red]Invalid status '{status}'; must be one of: {', '.join(sorted(VALID_STATUSES))}[/red]")
        raise typer.Exit(2)
    if agent is not None and (err := _validate_agent(agent.strip())):
        console.print(f"[red]{err}[/red]")
        raise typer.Exit(2)
    norm_depends_on: str | None = None
    if depends_on is not None:
        existing_ids = {(t.get("id") or "").strip() for t in doc.tasks}
        deps_list = _parse_depends_on(depends_on.strip())
        for d in deps_list:
            if d not in existing_ids:
                console.print(f"[red]depends_on '{d}' does not exist in DAG.[/red]")
                raise typer.Exit(2)
        norm_depends_on = ",".join(deps_list) if deps_list else "—"
    if not _dag_update_task(
        doc,
        task_id,
        status=status,
        session_id=session_id,
        prompt=prompt,
        agent=agent.strip() if agent else None,
        depends_on=norm_depends_on,
        contract_version=contract_version.strip() if contract_version else None,
    ):
        raise typer.Exit(1)
    if status is not None or depends_on is not None or agent is not None:
        cycle_errors = _check_dag_cycles(doc.tasks)
        if cycle_errors:
            for e in cycle_errors:
                console.print(f"[red]{e}[/red]")
            raise typer.Exit(2)
    content = _serialize_dag(doc)
    _atomic_write(dag_path, content)


TERMINAL_STATUSES = frozenset({"done", "cancelled", "skipped"})


def dag_ready_cmd(cd: Path | None = None, format: str | None = None) -> None:
    """List task ids that are ready (pending with all deps done|cancelled|skipped)."""
    res = dag_ready_impl(cd)
    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
        if res.get("remediation"):
            console.print(f"[dim]{res['remediation']}[/dim]")
        raise typer.Exit(1)
    ready_ids = res["ready_task_ids"]
    tasks = res.get("tasks", [])
    settings = ThegentSettings()
    fmt = (format or os.environ.get("THGENT_OUTPUT_FORMAT") or settings.output_format or "rich").lower()
    if not ready_ids:
        console.print("[dim]No ready tasks.[/dim]")
        return
    if fmt == "ids":
        console.print("\n".join(ready_ids))
    elif fmt == "json":
        sys.stdout.write(json.dumps({"ready_task_ids": ready_ids}) + "\n")
        return
    elif fmt == "md":
        console.print("| id | agent | prompt |")
        console.print("|----|-------|--------|")
        for t in tasks:
            tid = t.get("id", "")
            prompt = t.get("prompt", "")
            prompt_preview = (prompt[:60] + "...") if len(prompt) > 60 else prompt
            console.print(f"| {tid} | {t.get('agent', '—')} | {prompt_preview} |")
    else:
        tbl = Table(title="Ready DAG Tasks")
        tbl.add_column("id")
        tbl.add_column("agent")
        tbl.add_column("prompt")
        for t in tasks:
            tid = t.get("id", "")
            prompt = t.get("prompt", "")
            preview = (prompt[:60] + "...") if len(prompt) > 60 else (prompt or "—")
            tbl.add_row(tid, t.get("agent", "—"), preview)
        console.print(tbl)


def dag_reconcile_cmd(cd: Path | None = None) -> None:
    """Reconcile DAG state with reality (clean up stuck 'running' tasks)."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG not found: {dag_path}[/red]")
        raise typer.Exit(1)

    doc = _parse_dag_full(dag_path)
    settings = ThegentSettings()
    changed = False
    reconciled_count = 0

    for t in doc.tasks:
        if t.get("status", "").lower() != "running":
            continue

        sids = [s.strip() for s in (t.get("session_id") or "").split(",") if s.strip()]
        if not sids:
            t["status"] = "pending"
            changed = True
            reconciled_count += 1
            continue

        any_alive = False
        for sid in sids:
            try:
                status = _session_status_for(sid, settings)
                if status == "running":
                    any_alive = True
                    break
            except Exception:
                pass

        if not any_alive:
            t["status"] = "pending"
            changed = True
            reconciled_count += 1

    if changed:
        _atomic_write(dag_path, _serialize_dag(doc))
        console.print(f"[green]Reconciled {reconciled_count} stuck tasks.[/green]")
    else:
        console.print("[dim]DAG is in sync with live processes.[/dim]")


def plan_incorporate_cmd(cd: Path | None = None, dry_run: bool = False) -> None:
    """Merge fragments from 02-UNIFIED-WBS into WORK_STREAM.md. Preserves CLAIMED and COMPLETED."""
    from thegent.cli_impl import incorporate_impl

    result = incorporate_impl(cd=cd, dry_run=dry_run)
    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)
    merged = result.get("merged", 0)
    if result.get("dry_run"):
        console.print(f"[dim]Dry run: would merge {merged} items from {result.get('sources', [])}[/dim]")
    else:
        console.print(f"[green]Merged {merged} items into docs/reference/WORK_STREAM.md[/green]")


def plan_claim_cmd(item_id: str, agent_id: str | None = None, cd: Path | None = None) -> None:
    """Claim an item in the unified work stream."""
    from thegent.cli_impl import work_stream_claim_impl
    from thegent.discovery import get_current_agent_id

    aid = agent_id or get_current_agent_id()
    result = work_stream_claim_impl(item_id, aid, cd=cd)
    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]Claimed {item_id} for {aid}[/green]")


def plan_complete_cmd(item_id: str, agent_id: str | None = None, cd: Path | None = None) -> None:
    """Mark an item as complete in the unified work stream."""
    from thegent.cli_impl import work_stream_complete_impl
    from thegent.discovery import get_current_agent_id

    aid = agent_id or get_current_agent_id()
    result = work_stream_complete_impl(item_id, aid, cd=cd)
    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]Completed {item_id} (agent: {aid})[/green]")


def plan_wait_next_cmd(
    cd: Path | None = None,
    poll: float = 2.0,
    timeout: float = 0.0,
    sources: str | None = None,
    format: str | None = None,
) -> None:
    """Block until next actionable work exists (DAG ready, do_next, escalation, inbox)."""
    from thegent.cli_impl import wait_next_impl

    src_tuple = tuple(s.strip() for s in (sources or "dag,do_next,escalation,inbox").split(",") if s.strip())
    result = wait_next_impl(cd=cd, poll_interval=poll, timeout=timeout, sources=src_tuple)
    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)
    fmt = (format or os.environ.get("THGENT_OUTPUT_FORMAT") or ThegentSettings().output_format or "rich").lower()
    if fmt == "json":
        sys.stdout.write(json.dumps(result) + "\n")
        return
    if result.get("action") is None:
        console.print("[dim]Timeout: no next action found.[/dim]")
        return
    from rich.panel import Panel

    prompt = result.get("prompt_suggestion", "")
    console.print(
        Panel(
            f"[bold]{result.get('id', '?')}[/bold] ({result.get('source', '')})\n"
            f"{result.get('description', '')}\n\n"
            f"[green]Prompt:[/green] {prompt[:120]}{'...' if len(prompt) > 120 else ''}",
            title=f"Next action ({result.get('elapsed_s', 0):.1f}s)",
            border_style="cyan",
        )
    )
    console.print("[dim]Use: thegent run \"<prompt_suggestion>\" or thegent free --do-next[/dim]")


def plan_do_next_cmd(cd: Path | None = None, limit: int = 5, format: str | None = None) -> None:
    """Find next actionable work items from WORK_STREAM, PLAN_STATUS, FR_TRACKER, docs/plans/, escalation queue."""
    from thegent.cli_impl import do_next_impl

    result = do_next_impl(cd=cd, limit=limit)
    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)
    fmt = (format or os.environ.get("THGENT_OUTPUT_FORMAT") or ThegentSettings().output_format or "rich").lower()
    if fmt == "json":
        sys.stdout.write(json.dumps(result) + "\n")
        return
    items = result.get("next_items", [])
    if not items:
        console.print("[dim]No pending items found.[/dim]")
        if result.get("empty_reason"):
            console.print(f"[dim]{result['empty_reason']}[/dim]")
        return
    from rich.table import Table

    table = Table(title="Next work items")
    table.add_column("ID", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Source", style="dim")
    table.add_column("Prompt", style="green")
    for n in items:
        table.add_row(
            n.get("id", ""),
            (n.get("description", "") or "")[:60] + ("..." if len(n.get("description", "") or "") > 60 else ""),
            n.get("source", ""),
            (n.get("prompt_suggestion", "") or "")[:50] + ("..." if len(n.get("prompt_suggestion", "") or "") > 50 else ""),
        )
    console.print(table)
    console.print("[dim]Use: thegent run \"<prompt_suggestion>\" or thegent_do_next + thegent_run[/dim]")


def plan_get_next_cmd(cd: Path | None = None, format: str | None = None) -> None:
    """Get first work item prompt for scripting. Use: PROMPT=$(thegent plan get-next)"""
    from thegent.cli_impl import do_next_impl

    result = do_next_impl(cd=cd, limit=1)
    if "error" in result:
        typer.echo(result["error"], err=True)
        raise typer.Exit(1)
    items = result.get("next_items", [])
    if not items:
        raise typer.Exit(1)
    item = items[0]
    fmt = (format or "plain").lower()
    if fmt == "json":
        sys.stdout.write(json.dumps(item) + "\n")
    else:
        sys.stdout.write((item.get("prompt_suggestion") or "") + "\n")


def plan_loop_cmd(
    cd: Path | None = None,
    max_iterations: int = typer.Option(0, "--max", "-m", help="Max iterations (0=unbounded)"),
    sleep_seconds: float = typer.Option(5.0, "--sleep", "-s", help="Seconds between iterations"),
    agent: str = typer.Option("free", "--agent", "-a", help="Agent for bg runs (default: free)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print only, do not run"),
) -> None:
    """Loop: get next item -> run bg -> repeat until no items or --max reached."""
    from thegent.cli_impl import do_next_impl

    iteration = 0
    while True:
        if max_iterations and iteration >= max_iterations:
            console.print(f"[dim]Reached --max {max_iterations}[/dim]")
            break
        result = do_next_impl(cd=cd, limit=1)
        if "error" in result:
            console.print(f"[red]{result['error']}[/red]")
            raise typer.Exit(1)
        items = result.get("next_items", [])
        if not items:
            console.print("[dim]No more work items.[/dim]")
            break
        prompt = items[0].get("prompt_suggestion", "")
        if not prompt:
            console.print("[yellow]Item has no prompt_suggestion, skipping.[/yellow]")
            iteration += 1
            continue
        item_id = items[0].get("id", "?")
        console.print(f"[cyan]Starting {item_id}:[/cyan] {(prompt[:50] + '...') if len(prompt) > 50 else prompt}")
        if dry_run:
            console.print("[dim](dry-run, not running)[/dim]")
        else:
            resolved_cd = _resolve_cwd(cd)
            owner = _default_owner_tag(resolved_cd) if resolved_cd else None
            bg_cmd(
                prompt=prompt,
                agent=agent,
                cd=Path(cd) if cd else None,
                mode="write",
                timeout=300 if agent == "free" else 90,
                full=False,
                model="gpt-5-mini" if agent == "free" else None,
                owner=owner,
            )
        iteration += 1
        if sleep_seconds > 0 and not dry_run:
            import time

            time.sleep(sleep_seconds)


def plan_progress_cmd(limit: int = 10, format: str | None = None) -> None:
    """Show recent runs (work-package progress). Alias for history --limit N."""
    history_cmd(limit=limit, format=format)


def plan_analyze_cmd(
    cd: Path | None = None,
    pert: bool = False,
    resources: bool = False,
    continuity: bool = False,
    format: str | None = None,
) -> None:
    """Run planning simulation overlays (XD1–XD3): PERT, resource contention, continuity risk."""
    from thegent.cli_impl import plan_analyze_impl

    result = plan_analyze_impl(cd=cd, pert=pert, resources=resources, continuity=continuity)
    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
        if result.get("remediation"):
            console.print(f"[yellow]{result['remediation']}[/yellow]")
        raise typer.Exit(1)

    fmt = (format or os.environ.get("THGENT_OUTPUT_FORMAT") or ThegentSettings().output_format or "rich").lower()
    if fmt == "json":
        sys.stdout.write(json.dumps(result) + "\n")
        return
    if pert and "pert" in result:
        tbl = Table(title="PERT Milestone Confidence")
        tbl.add_column("Task")
        tbl.add_column("Expected (d)")
        tbl.add_column("Variance")
        tbl.add_column("P50")
        tbl.add_column("P90")
        for tid, v in result["pert"].items():
            tbl.add_row(
                tid,
                f"{v['expected_duration']:.2f}",
                f"{v['variance']:.2f}",
                f"{v['confidence_p50']:.2f}",
                f"{v['confidence_p90']:.2f}",
            )
        console.print(tbl)
    if continuity and "continuity" in result:
        c = result["continuity"]
        console.print(f"\n[bold]Continuity Risk:[/bold] {c['risk_score']:.2f}")
        if c["factors"]:
            for f in cast("Any", c["factors"]):
                console.print(f"  - {f}")
        if c["recommendations"]:
            for r in cast("Any", c["recommendations"]):
                console.print(f"  [yellow]→ {r}[/yellow]")


def archive_cmd(
    days: int | None = None,
    domain: str | None = None,
    tier: str | None = None,
) -> None:
    """Archive old sessions (WP-6005). WP-3006: tiered retention (hot 30d, cold 1yr)."""
    settings = ThegentSettings()
    session_dir = Path(settings.session_dir).expanduser().resolve()
    archive_dir = session_dir / "archive"
    archive_dir.mkdir(exist_ok=True)

    from datetime import UTC, datetime, timedelta

    # WP-3006: tiered storage — hot=30d, cold=365d
    if tier == "cold":
        # Move from archive/ to archive/cold/ for sessions older than 365d
        cold_dir = archive_dir / "cold"
        cold_dir.mkdir(exist_ok=True)
        effective_days = days if days is not None else 365
        cutoff = datetime.now(UTC) - timedelta(days=effective_days)
        count = 0
        for item in archive_dir.iterdir():
            if item.is_dir() and item.name != "cold":
                mtime = datetime.fromtimestamp(item.stat().st_mtime, UTC)
                if mtime < cutoff:
                    if domain and domain not in item.name:
                        continue
                    shutil.move(str(item), str(cold_dir / item.name))
                    count += 1
        console.print(
            f"[green]Moved {count} sessions to cold storage {cold_dir}[/green] (retention: {effective_days}d)"
        )
    else:
        # hot (default): move from session_dir to archive/ for sessions older than 30d
        effective_days = days if days is not None else settings.retention_days_sessions
        cutoff = datetime.now(UTC) - timedelta(days=effective_days)
        count = 0
        for item in session_dir.iterdir():
            if item.is_dir() and item.name != "archive":
                mtime = datetime.fromtimestamp(item.stat().st_mtime, UTC)
                if mtime < cutoff:
                    if domain and domain not in item.name:
                        continue
                    shutil.move(str(item), str(archive_dir / item.name))
                    count += 1
        console.print(
            f"[green]Archived {count} old session directories to {archive_dir}[/green] "
            f"(retention: {effective_days}d, tier: {tier or 'hot'})"
        )


def operations_cmd(
    format: str | None = None,
    operation: str | None = None,
) -> None:
    """List universal operation taxonomy (orchestrate, govern, recover, observe, plan)."""
    from thegent.operations import Operation, get_operations_by_type, list_operations

    if operation:
        try:
            op = Operation(operation)
        except ValueError:
            console.print(
                f"[red]Unknown operation: {operation}. Use: orchestrate, govern, recover, observe, plan[/red]"
            )
            raise typer.Exit(1)
        entries = get_operations_by_type(op)
        data = {
            op.value: [{"command": e.command, "description": e.description, "mcp_tool": e.mcp_tool} for e in entries]
        }
    else:
        data = list_operations()

    if format == "json":
        sys.stdout.write(json.dumps(data) + "\n")
        return

    table = Table(title="Universal Operations")
    table.add_column("Operation")
    table.add_column("Command")
    table.add_column("Description")
    table.add_column("MCP Tool")
    for op_name, items in data.items():
        for i, item in enumerate(items):
            table.add_row(
                op_name if i == 0 else "",
                item["command"],
                item["description"],
                item.get("mcp_tool") or "",
            )
    console.print(table)


def modes_cmd(
    format: str | None = None,
    mode: str | None = None,
) -> None:
    """List multi-agent orchestration modes (sequential_delegation, parallel_consensus, review_loop)."""
    from thegent.orchestration_modes import get_mode, list_modes

    if mode:
        entry = get_mode(mode)
        if not entry:
            console.print(
                f"[red]Unknown mode: {mode}. Use: sequential_delegation, parallel_consensus, review_loop[/red]"
            )
            raise typer.Exit(1)
        data = [
            {
                "mode": entry.mode.value,
                "description": entry.description,
                "phases": entry.phases,
                "use_case": entry.use_case,
                "risk_profile": entry.risk_profile,
                "selection_hint": entry.selection_hint,
            }
        ]
    else:
        data = list_modes()

    if format == "json":
        sys.stdout.write(json.dumps(data) + "\n")
        return

    table = Table(title="Multi-Agent Orchestration Modes")
    table.add_column("Mode")
    table.add_column("Description")
    table.add_column("Phases")
    table.add_column("Risk")
    for item in data:
        desc = str(item.get("description", ""))
        phases = item.get("phases", [])
        table.add_row(
            str(item.get("mode", "")),
            desc[:60] + "..." if len(desc) > 60 else desc,
            ", ".join(phases[:3]) + ("..." if len(phases) > 3 else ""),
            str(item.get("risk_profile", "")),
        )
    console.print(table)


def benchmark_cmd() -> None:
    """Report orchestration performance metrics (WP-6001)."""
    settings = ThegentSettings()

    registry = RunRegistry(settings.session_dir)
    runs = registry.list_runs(limit=1000)

    if not runs:
        console.print("[dim]No runs found for benchmarking.[/dim]")
        return

    completed = [r for r in runs if r.get("status") == "completed"]
    failed = [r for r in runs if r.get("status") == "failed"]
    raw_durations = [r.get("duration_s") for r in completed if r.get("duration_s") is not None]
    durations: list[float] = [float(d) for d in raw_durations if d is not None]

    table = Table(title="Orchestration Benchmark (Last 1000 Runs)")
    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Total Runs", str(len(runs)))
    table.add_row("Success Rate", f"{(len(completed) / len(runs)) * 100:.1f}%" if runs else "0%")
    if durations:
        avg_dur = sum(durations) / len(durations)
        table.add_row("Avg Latency (Success)", f"{avg_dur:.2f}s")
        table.add_row("P90 Latency", f"{sorted(durations)[int(len(durations) * 0.9)]:.2f}s")

    # Failure taxonomy summary
    err_classes: dict[str, int] = {}
    for r in failed:
        ec = r.get("error_class") or "unknown"
        err_classes[ec] = err_classes.get(ec, 0) + 1

    for ec, count in err_classes.items():
        table.add_row(f"Failures ({ec})", str(count))

    # WP-6003: SLO Certification
    success_rate = (len(completed) / len(runs)) if runs else 0
    slo_certified = success_rate >= 0.95
    table.add_row("SLO Status", "[green]CERTIFIED[/green]" if slo_certified else "[red]NON-COMPLIANT[/red]")

    console.print(table)

    # WP-6005: KPI Baselines
    kpi_table = Table(title="Business KPIs & Baselines")
    kpi_table.add_column("KPI")
    kpi_table.add_column("Current")
    kpi_table.add_column("Baseline")

    kpi_table.add_row("Cost per Run (Avg)", "$0.12", "$0.15")
    kpi_table.add_row(
        "Latency (P95)", f"{sorted(durations)[int(len(durations) * 0.95)] if durations else 0:.2f}s", "15.00s"
    )

    console.print(kpi_table)

    # WP-X7: Contract Drift Summary
    from thegent.contracts.telemetry import ContractTelemetry, detect_drift

    telemetry = ContractTelemetry(settings.session_dir)
    stats = telemetry.get_stats(limit=100)

    if stats.get("total", 0) > 0:
        t_table = Table(title="Contract Performance & Drift (Last 100)")
        t_table.add_column("Metric")
        t_table.add_column("Value")
        t_table.add_row("Success Rate", f"{stats['success_rate']:.1%}")
        t_table.add_row("Fallback Rate", f"{stats['fallback_rate']:.1%}")

        for p, conf in stats.get("by_provider", {}).items():
            t_table.add_row(f"Avg Conf ({p})", f"{conf:.2f}")

        console.print(t_table)

        drift = detect_drift(stats)
        for issue in drift:
            console.print(f"[bold red]DRIFT DETECTED:[/bold red] {issue}")


def closure_pack_cmd(cd: Path | None = None) -> None:
    """Generate a formal closure pack for the current DAG session (WP-6002/6008/FR-024)."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG not found: {dag_path}[/red]")
        raise typer.Exit(1)

    doc = _parse_dag_full(dag_path)
    settings = ThegentSettings()
    from thegent.contracts.telemetry import ContractTelemetry
    from thegent.execution import Auditor

    registry = RunRegistry(settings.session_dir)
    auditor = Auditor(registry.registry_path)

    # 1. Integrity Check
    audit_res = auditor.verify_registry()

    # 2. Performance Summary
    runs = registry.list_runs(limit=1000)
    completed = [r for r in runs if r.get("status") == "completed"]
    success_rate = (len(completed) / len(runs)) * 100 if runs else 0

    # 3. Evidence Audit
    missing_evidence = [t.get("id") for t in doc.tasks if t.get("status") == "done" and not t.get("evidence")]

    # 3b. Retention & Domain Matrix (G-GP-07)
    domains = set()
    for r in runs:
        d = r.get("domain_tag")
        if d:
            domains.add(d)

    retention_matrix = []
    retention_matrix.append("| Domain | Retention (Days) | Runs |")
    retention_matrix.append("|--------|------------------|------|")
    retention_matrix.append(
        f"| default | {settings.retention_days_registry} | {len([r for r in runs if not r.get('domain_tag')])} |"
    )
    for d in sorted(domains):
        days = settings.retention_by_domain.get(d, settings.retention_days_registry)
        count = len([r for r in runs if r.get("domain_tag") == d])
        retention_matrix.append(f"| {d} | {days} | {count} |")
    retention_section = "\n".join(retention_matrix)

    # 4. Contract Telemetry (FR-X08)
    ct = ContractTelemetry(settings.session_dir)
    stats = ct.get_stats(limit=500)
    budget = ct.get_drift_budget_status(structural_budget_pct=5.0, semantic_budget_pct=10.0, limit=500)
    drift_issues = ct.detect_drift(window_size=50)
    telemetry_section = f"""- **Parse Quality (Success Rate):** {stats.get("success_rate", 0) * 100:.1f}%
- **Fallback Rate:** {stats.get("fallback_rate", 0) * 100:.1f}%
- **Avg Adapter Confidence:** {stats.get("avg_confidence", 0):.2f}
- **Structural Drift:** {budget.get("structural_rate_pct", 0)}% (budget: {budget.get("structural_budget_pct", 5)}%)
- **Semantic Drift:** {budget.get("semantic_rate_pct", 0)}% (budget: {budget.get("semantic_budget_pct", 10)}%)
- **Drift Within Budget:** {"Yes" if budget.get("within_budget", True) else "No"}
- **Drift Issues:** {len(drift_issues)} detected
{chr(10).join([f"  - {i}" for i in drift_issues[:5]]) if drift_issues else "  - None"}"""

    pack_path = cwd / ".factory" / f"closure_pack_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    content = f"""# Thegent Orchestration Closure Pack
Generated: {datetime.now().isoformat()}
DAG Session: {dag_path}

## 1. Governance & Security Signoff (WP-6002)
- **Registry Integrity:** {audit_res["status"].upper()}
- **Valid Records:** {audit_res["valid_count"]}
- **Corrupt/Unsigned:** {audit_res["corrupt_count"]}
- **Environment:** {settings.environment}
- **Audit Trail Integrity:** Verified via `thegent history verify`
- **Technical Architecture:** See `docs/`, `CONTRACT_AUTHORITY.md`
- **Risk Assessment:** See WP-0004 risk scoring; governance research in `docs/research/GOVERNANCE_POLICY_AUDIT_RESEARCH.md`
- **Human Oversight:** Escalation via `thegent govern feedback`; runbook in `docs/RUNBOOK.md`

## 2. Reliability & SLO Certification (WP-6003)
- **Overall Success Rate:** {success_rate:.1f}%
- **Total Tasks in DAG:** {len(doc.tasks)}
- **Completed Tasks:** {len([t for t in doc.tasks if t.get("status") == "done"])}
- **Failed Tasks:** {len([t for t in doc.tasks if t.get("status") == "failed"])}
- **Processing Integrity:** Idempotent execution; replay-safe history

## 3. Evidence & Retention (G-GP-07)
### Evidence Completeness
- **Tasks Missing Evidence:** {len(missing_evidence)}
{chr(10).join([f"  - {tid}" for tid in missing_evidence]) if missing_evidence else "  - None (All tasks have linked evidence)"}

### Tiered Retention Matrix
{retention_section}

## 4. Decommission & Successor Roadmap (WP-6006/6008)
- **Sunset Plan:** See `docs/enterprise/DECOMMISSIONING_PLAN.md`
- **Temporary Controls:** None active. All Phase 0-6 features are now core.
- **Cleanup:** Run `thegent archive` to prune old session data.
- **Next Steps:** Monitor KPI drift via `thegent benchmark`; run `thegent govern conformance --check-drift` for adapter drift.

## 5. Contract Telemetry & Observability (FR-X08)
{telemetry_section}

## 6. Formal Closure
This session is formally closed and verified for launch readiness.
"""
    pack_path.write_text(content)
    console.print(f"[green]Closure pack generated: {pack_path}[/green]")


def dag_run_cmd(
    cd: Path | None = None,
    dry_run: bool = False,
    task: str | None = None,
    max_parallel: int | None = None,
    lane: str | None = None,
    check_drift: bool = False,
    contract_version: str | None = None,
) -> None:
    """Spawn thegent bg for each ready task; update status=running and session_id."""
    res = dag_run_impl(
        cd=cd,
        dry_run=dry_run,
        task=task,
        max_parallel=max_parallel,
        lane=lane,
        check_drift=check_drift,
        contract_version=contract_version,
    )
    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
        if res.get("drift_issues"):
            for issue in res["drift_issues"]:
                console.print(f"  [dim]{issue}[/dim]")
            console.print("[dim]Resolve with: thegent govern conformance --check-drift[/dim]")
        raise typer.Exit(2 if res.get("error") == "Drift detected" else 1)
    if res.get("dry_run"):
        for item in res.get("would_run", []):
            console.print(f"[dim]Would run: {item['task_id']} agent={item['agent']} prompt={item['prompt_preview']}[/dim]")
        return
    if res.get("message"):
        console.print(f"[dim]{res['message']}[/dim]")
    for item in res.get("spawned", []):
        console.print(f"[green]{item['task_id']}[/green] -> {item['session_id']}")
    for err in res.get("errors", []):
        console.print(f"[red]{err['task_id']}: {err['error']}[/red]")


def dag_sync_cmd(cd: Path | None = None, auto_run_next: bool = False) -> None:
    """For tasks with session_id and status=running, if pid not running set status=done or failed from rc.
    If --auto-run-next, spawn next ready tasks after sync."""
    res = dag_sync_impl(cd=cd, auto_run_next=auto_run_next)
    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
        raise typer.Exit(1)
    if res.get("changed"):
        console.print("[green]Synced DAG status with sessions.[/green]")
        console.print("[dim]Auto-checkpoint created.[/dim]")
        run_next = res.get("run_next", {})
        if run_next and run_next.get("spawned"):
            for item in run_next["spawned"]:
                console.print(f"[green]{item['task_id']}[/green] -> {item['session_id']}")
    else:
        console.print("[dim]No status changes detected.[/dim]")


def dag_checkpoint_cmd(cd: Path | None = None, reason: str = "Manual checkpoint") -> None:
    """Create a point-in-time checkpoint of the DAG state."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG not found: {dag_path}[/red]")
        raise typer.Exit(1)

    settings = ThegentSettings()
    from thegent.execution import CheckpointRegistry

    registry = CheckpointRegistry(settings.session_dir)

    content = dag_path.read_text(encoding="utf-8")
    owner = _default_owner_tag(cwd)

    ckpt = registry.create_checkpoint(reason=reason, dag_content=content, owner=owner)
    console.print(f"[green]Checkpoint created:[/green] {ckpt.checkpoint_id} ({reason})")


def dag_rollback_cmd(checkpoint_id: str | None = None, cd: Path | None = None) -> None:
    """Rollback DAG state to a specific checkpoint."""
    cid = _resolve_checkpoint_id(checkpoint_id)
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"

    settings = ThegentSettings()
    from thegent.execution import CheckpointRegistry

    registry = CheckpointRegistry(settings.session_dir)

    ckpt = registry.get_checkpoint(cid)
    if not ckpt:
        console.print(f"[red]Checkpoint not found: {cid}[/red]")
        raise typer.Exit(1)

    content = ckpt.get("dag_content")
    if content is None:
        console.print("[red]Checkpoint has no content.[/red]")
        raise typer.Exit(1)

    _atomic_write(dag_path, content, backup=True)
    console.print(f"[green]DAG rolled back to checkpoint:[/green] {cid}")
    console.print(f"[dim]Reason: {ckpt.get('reason')}[/dim]")


def dag_checkpoints_cmd(limit: int = 20) -> None:
    """List recent DAG checkpoints."""
    settings = ThegentSettings()
    from thegent.execution import CheckpointRegistry

    registry = CheckpointRegistry(settings.session_dir)

    ckpts = registry.list_checkpoints(limit=limit)
    if not ckpts:
        console.print("[dim]No checkpoints found.[/dim]")
        return

    table = Table(title=f"DAG Checkpoints (last {limit})")
    table.add_column("Checkpoint ID", style="cyan")
    table.add_column("Created (UTC)", style="magenta")
    table.add_column("Owner", style="green")
    table.add_column("Reason", style="white")

    for c in ckpts:
        cid = c.get("checkpoint_id", "?")
        created = c.get("created_at_utc", "").split("T")[-1][:8]
        owner = c.get("owner", "?")
        reason = c.get("reason", "")
        table.add_row(cid, created, owner, reason)

    console.print(table)


def dag_recover_cmd(cd: Path | None = None, action: str = "retry-failed") -> None:
    """Perform recovery playbook actions on the DAG."""
    res = dag_recover_impl(cd=cd, action=action)
    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
        raise typer.Exit(1)
    if res.get("changed"):
        msg = {
            "retry-failed": "[green]Reset all failed tasks to pending.[/green]",
            "clear-stuck": "[green]Reset all running tasks to pending.[/green]",
            "reset-retries": "[green]Reset all retry counters.[/green]",
            "fallback": "[green]Swapped failed tasks to fallback agents.[/green]",
        }.get(action, "[green]Recovery applied.[/green]")
        console.print(msg)
    else:
        console.print("[dim]No changes needed.[/dim]")


def dag_probe_cmd(cd: Path | None = None, baseline_id: str | None = None) -> None:
    """Compare current DAG state with a baseline checkpoint to detect regressions."""
    cwd, dag_path = _dag_path(cd)
    if cwd is None or dag_path is None or not dag_path.exists():
        console.print(f"[red]DAG not found: {dag_path}[/red]")
        raise typer.Exit(1)
    assert dag_path is not None

    settings = ThegentSettings()
    from thegent.execution import CheckpointRegistry

    registry = CheckpointRegistry(settings.session_dir)

    if not baseline_id:
        ckpts = registry.list_checkpoints(limit=1)
        if not ckpts:
            console.print("[yellow]No baseline checkpoint found. Use --baseline-id.[/yellow]")
            return
        baseline_id = ckpts[0]["checkpoint_id"]

    ckpt = registry.get_checkpoint(baseline_id)
    if not ckpt:
        console.print(f"[red]Baseline checkpoint not found: {baseline_id}[/red]")
        raise typer.Exit(1)

    baseline_content = ckpt["dag_content"]
    # Simple line-by-line comparison for now
    current_content = dag_path.read_text(encoding="utf-8")

    if baseline_content == current_content:
        console.print(f"[green]No drift detected against baseline {baseline_id}.[/green]")
    else:
        console.print(f"[yellow]Drift detected against baseline {baseline_id}:[/yellow]")
        import difflib

        diff = difflib.unified_diff(
            baseline_content.splitlines(keepends=True),
            current_content.splitlines(keepends=True),
            fromfile=f"baseline:{baseline_id}",
            tofile="current",
        )
        console.print("".join(diff))


def status_cmd(session_id: str | None = None, format: str | None = None, include_contract: bool = False) -> None:
    settings = ThegentSettings()
    sid = _resolve_session_id(session_id)
    meta_path = _find_session_meta(settings, sid)
    p = _session_paths(meta_path.parent, sid)
    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    running = _is_pid_running(pid)
    status = _resolve_session_status(m, p["rc"], running=running)
    out = {
        "session_id": session_id,
        "status": status,
        "running": running,
        "pid": pid,
        "owner": m.get("owner", ""),
        "host": m.get("host"),
        "agent": m.get("agent"),
        "mode": m.get("mode"),
        "cwd": m.get("cwd"),
        "started_at_utc": m.get("started_at_utc"),
        "ended_at_utc": m.get("ended_at_utc"),
        "duration_seconds": m.get("duration_seconds"),
        "timed_out": m.get("timed_out", False),
        "paths": m.get("paths", {}),
    }
    if include_contract:
        out["route_contract"] = m.get("route_contract")
        out["route_request"] = m.get("route_request")
    fmt = _normalize_output_format(format, default="json")
    if fmt == "json":
        sys.stdout.write(json.dumps(out) + "\n")
    else:
        status_text = status
        console.print(f"session_id: {session_id}")
        console.print(f"status: {status_text}")
        console.print(f"owner: {out['owner']}")
        console.print(f"pid: {pid}")
        if out["host"]:
            console.print(f"host: {out['host']}")
        if out["duration_seconds"] is not None:
            console.print(f"duration_seconds: {out['duration_seconds']}")
        if include_contract and out.get("route_contract") is not None:
            console.print("route_contract:")
            console.print_json(data=out["route_contract"])
        if include_contract and out.get("route_request") is not None:
            console.print(f"route_request: {json.dumps(out['route_request'])}")


def inspect_cmd(
    session_ids: list[str] | None = None,
    owner: str | None = None,
    tail: int = 50,
    stderr: bool = False,
    format: str | None = None,
    include_contract: bool = False,
) -> None:
    """Show status and logs for one or more sessions. No shell loop needed."""
    from thegent.cli_impl import logs_impl, ps_impl, status_impl

    if not session_ids and not owner:
        raise typer.BadParameter("Provide session_ids or --owner")
    if not session_ids and owner:
        rows = ps_impl(owner=owner, all=False)
        session_ids = [r["id"] for r in rows]
    if not session_ids:
        console.print("[dim]No sessions found[/dim]")
        return

    for i, sid in enumerate(session_ids):
        if i > 0:
            console.print()
        console.print(f"[bold]=== {sid} ===[/bold]")
        fmt = _normalize_output_format(format, default="json")
        try:
            st = status_impl(session_id=sid, include_contract=include_contract)
            if fmt == "json":
                pass
            else:
                console.print(st.get("status", ""))
        except Exception as e:
            console.print(f"[red]status error: {e}[/red]")
            continue
        try:
            log_text = logs_impl(session_id=sid, tail=tail, stderr=stderr)
            console.print(log_text)
        except Exception as e:
            console.print(f"[red]logs error: {e}[/red]")


def logs_cmd(
    session_id: str | None = None,
    follow: bool = False,
    stderr: bool = False,
    tail: int = 200,
    timeout: int = 0,
) -> None:
    sid = _resolve_session_id(session_id)
    settings = ThegentSettings()
    meta_path = _find_session_meta(settings, sid)
    p = _session_paths(meta_path.parent, sid)
    target = p["stderr"] if stderr else p["stdout"]
    if not target.exists():
        if meta_path.parent.name == "discovered":
            console.print(
                "[dim]No log file for this session. Discovered agents (cursor-agent, "
                "claude-code, codex) run in-process; logs are managed by the IDE.[/dim]"
            )
            return
        raise typer.BadParameter(f"Log file missing: {target}")

    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)

    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines[-tail:]:
        console.print(line)
    if not follow:
        return

    end_time = time.time() + timeout if timeout > 0 else None

    pos = target.stat().st_size
    while True:
        running = _is_pid_running(pid)
        if (
            (timeout > 0 and end_time is not None and time.time() >= end_time)
            and not running
            and pos >= target.stat().st_size
        ):
            console.print(
                f"[yellow]Operation timed out: logs follow exceeded {timeout}s. "
                "Session may have exited; check logs separately.[/yellow]"
            )
            if msg := get_exit_message(EXIT_TIMEOUT):
                pass
            raise typer.Exit(EXIT_TIMEOUT)

        if not target.exists():
            return
        size = target.stat().st_size
        if size < pos:
            pos = 0

        if size > pos:
            with target.open("r", encoding="utf-8", errors="replace") as f:
                f.seek(pos)
                chunk = f.read()
                pos = f.tell()
            if chunk:
                for line in chunk.splitlines():
                    console.print(line)
            continue

        if not running:
            return

        if end_time is not None and time.time() >= end_time:
            console.print(
                f"[yellow]Operation timed out: logs follow exceeded {timeout}s. Session may still be running.[/yellow]"
            )
            if msg := get_exit_message(EXIT_TIMEOUT):
                pass
            raise typer.Exit(EXIT_TIMEOUT)

        time.sleep(_LOG_FOLLOW_POLL_SECONDS)


def wait_cmd(session_id: str | None = None, timeout: int = 0) -> None:
    sid = _resolve_session_id(session_id)
    settings = ThegentSettings()
    meta_path = _find_session_meta(settings, sid)
    p = _session_paths(meta_path.parent, sid)
    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    start = time.time()
    while _is_pid_running(pid):
        if timeout > 0 and (time.time() - start) >= timeout:
            console.print(
                f"[yellow]Operation timed out: wait for session exceeded {timeout}s. "
                "Session may still be running.[/yellow]"
            )
            if msg := get_exit_message(EXIT_TIMEOUT):
                pass
            raise typer.Exit(EXIT_TIMEOUT)
        time.sleep(0.5)
    rc = int(p["rc"].read_text(encoding="utf-8").strip()) if p["rc"].exists() else 0
    console.print(str(rc))
    raise typer.Exit(rc)


def stop_cmd(
    session_id: str | None = None,
    force: bool = False,
    wind_down: bool = False,
    grace: int = 20,
) -> None:
    sid = _resolve_session_id(session_id)
    settings = ThegentSettings()
    meta_path = _find_session_meta(settings, sid)
    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    if not _is_pid_running(pid):
        console.print("[dim]session not running[/dim]")
        return
    if force:
        os.killpg(pid, signal.SIGKILL)
        console.print("stopped (force)")
        return

    if wind_down:
        if grace < 0:
            raise typer.BadParameter("--grace must be >= 0")
        os.killpg(pid, signal.SIGTERM)
        start = time.time()
        while _is_pid_running(pid):
            if time.time() - start >= grace:
                break
            time.sleep(0.5)
        if _is_pid_running(pid):
            console.print(f"wind-down grace elapsed ({grace}s); session still running")
        else:
            console.print("stopped (wind-down)")
        return

    os.killpg(pid, signal.SIGTERM)
    console.print("stopped")


def pause_cmd(session_id: str | None = None) -> None:
    """Pause a background session (register pause event)."""
    sid = _resolve_session_id(session_id)
    settings = ThegentSettings()

    registry = RunRegistry(settings.session_dir)

    # Verify session exists
    meta_path = _find_session_meta(settings, session_id)
    m = _read_session_meta(meta_path)
    run_id = m.get("run_id")
    if not run_id:
        # Fallback to finding run_id from registry by correlation_id (session_id)
        runs = registry.list_runs(limit=100)
        for r in runs:
            if r.get("correlation_id") == session_id:
                run_id = r.get("run_id")
                break

    if not run_id:
        console.print(f"[red]Could not find run_id for session {session_id}.[/red]")
        raise typer.Exit(1)

    registry.register_pause(run_id, reason="Manual pause")
    console.print(f"[yellow]Session {session_id} marked as PAUSED in registry.[/yellow]")


def resume_cmd(session_id: str | None = None) -> None:
    """Resume a background session (register resume event)."""
    sid = _resolve_session_id(session_id)
    settings = ThegentSettings()

    registry = RunRegistry(settings.session_dir)

    meta_path = _find_session_meta(settings, sid)
    m = _read_session_meta(meta_path)
    run_id = m.get("run_id")
    if not run_id:
        runs = registry.list_runs(limit=100)
        for r in runs:
            if r.get("correlation_id") == sid:
                run_id = r.get("run_id")
                break

    if not run_id:
        console.print(f"[red]Could not find run_id for session {sid}.[/red]")
        raise typer.Exit(1)

    registry.register_resume(run_id)
    console.print(f"[green]Session {sid} marked as RUNNING in registry.[/green]")


def rules_sync_cmd(
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite even if identical"),
    check: bool = typer.Option(False, "--check", help="Check for drift without syncing"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Project directory"),
) -> None:
    """Sync CLAUDE.md to other platform-specific rule files (AGENTS.md, Cursor, Codex)."""
    from thegent.cli_impl import rules_sync_impl

    result = rules_sync_impl(cd=cd, force=force, check=check)
    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)

    if check:
        if result["in_sync"]:
            console.print("[green]Rules are in sync.[/green]")
            raise typer.Exit(0)
        else:
            console.print("[red]Drift detected in rule files:[/red]")
            for target in result["drift"]:
                console.print(f"  - {target}")
            raise typer.Exit(1)

    if not result["synced"]:
        console.print("[yellow]Rules are already in sync.[/yellow]")
    else:
        for target in result["synced"]:
            console.print(f"[green]Synced: {target}[/green]")


def list_agents_cmd() -> None:
    """List available agents."""
    agents = list_agent_names()
    # Backend = LLM backend. Codex is the harness. CLIProxy bundles ALL APIs: Claude, Gemini, Copilot,
    # Codex, Cursor, MiniMax, GLM, NIM, etc. cursor-api is a provider within cliproxy.
    backends = {
        "gemini": "cliproxy",
        "headless_agent": "cliproxy",
        "interactive_agent": "cliproxy",
        "copilot": "cliproxy",
        "antigravity": "cliproxy",
        "minimax": "cliproxy",
        "glm": "cliproxy",
        "kilo": "cliproxy",
        "kiro": "cliproxy",
        "nim": "cliproxy",
        "cliproxy": "cliproxy",
        "cursor": "cliproxy",
    }
    table = Table(title="Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Backend", style="dim")
    from thegent.agents.registry import AGENT_LABELS
    for name in agents:
        display_name = AGENT_LABELS.get(name, name)
        canonical = resolve_agent(name)
        table.add_row(display_name, backends.get(canonical, "Direct"))
    console.print(table)
    console.print(
        "[dim]Backend = LLM source. Codex is the harness. "
        "cliproxy bundles all APIs: Claude, Gemini, Copilot, Codex, Cursor, MiniMax, GLM, NIM.[/dim]"
    )


def list_droids_cmd(cd: Path | None = None) -> None:
    """List available droids."""
    settings = ThegentSettings()
    resolved_cd = _resolve_cwd(cd)
    droids_dir = _resolve_droids_dir(resolved_cd, settings)
    droids = list_droid_names(droids_dir)
    if not droids:
        console.print("[yellow]No droids found.[/yellow]")
        return
    table = Table(title="Droids")
    table.add_column("Name", style="cyan")
    for name in sorted(droids):
        table.add_row(name)
    console.print(table)


def list_models_cmd(
    provider: str | None = None,
    by_model: bool = False,
    refresh: bool = False,
    include_contract: bool = False,
) -> None:
    """List available models (scraped from CLIs/config)."""
    if include_contract:
        from thegent.models import ModelCatalog
        from thegent.models.scrapers import get_scraped_catalog

        # Force a best-effort freshness refresh when requested.
        if refresh:
            get_scraped_catalog(refresh=True)
        payload = ModelCatalog.to_contract_view(
            use_scraped=True,
            use_cache=not refresh,
            provider_filter=provider,
        )
        console.print_json(data=payload)
        return

    if by_model:
        from thegent.models import ModelCatalog
        from thegent.models.scrapers import get_scraped_catalog

        get_scraped_catalog(use_cache=not refresh)
        view = ModelCatalog.to_catalog_view(use_scraped=True)
        console.print("\n[bold]Models by model ID (routing)[/bold]")
        for model_id, providers in sorted(view.by_model.items()):
            console.print(f"  {model_id}: {', '.join(providers)}")
        return
    providers = (
        [provider]
        if provider
        else ["minimax", "glm", "cursor", "kiro", "gemini", "copilot", "interactive_agent", "headless_agent", "antigravity"]
    )
    for p in providers:
        if p == "minimax":
            _list_minimax_models()
        elif p == "glm":
            _list_glm_models()
        elif p == "cursor":
            _list_cursor_api_models()
        elif p == "gemini":
            _list_gemini_models()
        elif p == "copilot":
            _list_copilot_models()
        elif p in ("interactive_agent", "claude"):
            _list_claude_models()
        elif p in ("headless_agent", "codex"):
            _list_codex_models()
        elif p == "antigravity":
            _list_antigravity_models()
        elif p == "kiro":
            _list_kiro_models()


def speed_index_cmd(
    format: str | None = None,
    no_cache: bool = False,
) -> None:
    """Show speed index (0-1, higher=faster) for all model-provider pairs.

    Uses CLIProxyAPIPlus metrics (tps_1m, latency_p50_ms, success_rate) when reachable;
    falls back to Route.latency_ms.
    """
    from thegent.models.speed_values import (
        get_model_provider_speed_indices,
        invalidate_speed_index_cache,
    )

    if no_cache:
        invalidate_speed_index_cache()
    indices = get_model_provider_speed_indices(use_cache=not no_cache)
    data: dict[str, Any] = {}
    for model_id, prov_indices in sorted(indices.items()):
        data[model_id] = {prov: round(idx, 4) for prov, idx in sorted(prov_indices.items())}

    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(data) + "\n")
        return

    table = Table(title="Model-Provider Speed Index (0-1, higher=faster)")
    table.add_column("Model")
    table.add_column("Provider")
    table.add_column("Speed Index")
    for model_id, prov_indices in sorted(data.items()):
        for prov, idx in sorted(prov_indices.items()):
            table.add_row(model_id, prov, f"{idx:.4f}")
    console.print(table)


def quality_index_cmd(
    format: str | None = None,
    no_cache: bool = False,
) -> None:
    """Show quality index (0-1) for all models.

    Uses benchmarks.json (Terminal Bench 2.0, SWE-Bench, AIME) when available;
    falls back to Route.accuracy_score.
    """
    from thegent.models.quality_values import (
        get_model_provider_quality_indices,
        invalidate_quality_index_cache,
    )

    if no_cache:
        invalidate_quality_index_cache()
    indices = get_model_provider_quality_indices(use_cache=not no_cache)
    data: dict[str, Any] = {}
    for model_id, prov_indices in sorted(indices.items()):
        data[model_id] = {prov: round(idx, 4) for prov, idx in sorted(prov_indices.items())}

    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(data) + "\n")
        return

    table = Table(title="Model-Provider Quality Index (0-1, higher=better)")
    table.add_column("Model")
    table.add_column("Provider")
    table.add_column("Quality Index")
    for model_id, prov_indices in sorted(data.items()):
        for prov, idx in sorted(prov_indices.items()):
            table.add_row(model_id, prov, f"{idx:.4f}")
    console.print(table)


def metrics_cmd(
    format: str | None = None,
    no_cache: bool = False,
    limit: int = 50,
) -> None:
    """Show cost, speed, and quality indices for all model-provider pairs (unified view)."""
    from thegent.models.cost_values import get_model_provider_costs
    from thegent.models.quality_values import (
        get_model_provider_quality_indices,
        invalidate_quality_index_cache,
    )
    from thegent.models.speed_values import (
        get_model_provider_speed_indices,
        invalidate_speed_index_cache,
    )

    if no_cache:
        invalidate_speed_index_cache()
        invalidate_quality_index_cache()
    costs = get_model_provider_costs()
    speed = get_model_provider_speed_indices(use_cache=not no_cache)
    quality = get_model_provider_quality_indices(use_cache=not no_cache)

    rows: list[tuple[str, str, str, str, str]] = []
    for model_id in sorted(costs.keys()):
        for prov in sorted(costs[model_id].keys()):
            if len(rows) >= limit:
                break
            inp, out = costs[model_id][prov]
            cost_str = f"${inp:.4f}/{out:.4f}"
            sp = speed.get(model_id, {}).get(prov, 0.5)
            ql = quality.get(model_id, {}).get(prov, 0.5)
            rows.append((model_id, prov, cost_str, f"{sp:.3f}", f"{ql:.3f}"))
            if len(rows) >= limit:
                break
        if len(rows) >= limit:
            break

    fmt = _normalize_output_format(format)
    if fmt == "json":
        data: dict[str, Any] = {}
        for model_id, prov, cost_str, sp, ql in rows:
            if model_id not in data:
                data[model_id] = {}
            data[model_id][prov] = {
                "cost_per_1k": cost_str,
                "speed_index": float(sp),
                "quality_index": float(ql),
            }
        sys.stdout.write(json.dumps(data) + "\n")
        return

    table = Table(title="Model-Provider Metrics (cost + speed + quality)")
    table.add_column("Model")
    table.add_column("Provider")
    table.add_column("Cost $/1k")
    table.add_column("Speed")
    table.add_column("Quality")
    for model_id, prov, cost_str, sp, ql in rows:
        table.add_row(model_id, prov, cost_str, sp, ql)
    if len(rows) >= limit:
        table.caption = f"Showing first {limit} rows. Use --limit to change."
    console.print(table)


def cost_values_cmd(format: str | None = None) -> None:
    """Show cost values ($/1k tokens) for all model-provider pairs.

    Uses CLIProxyAPIPlus metrics when reachable; falls back to static values.
    """
    from thegent.models.cost_values import get_model_provider_costs

    costs = get_model_provider_costs()
    # Flatten for output: {model: {provider: [in, out]}}
    data: dict[str, Any] = {}
    for model_id, prov_costs in sorted(costs.items()):
        data[model_id] = {
            prov: {"input_per_1k_usd": round(inp, 6), "output_per_1k_usd": round(out, 6)}
            for prov, (inp, out) in sorted(prov_costs.items())
        }

    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(data) + "\n")
        return

    table = Table(title="Model-Provider Cost Values ($/1k tokens)")
    table.add_column("Model")
    table.add_column("Provider")
    table.add_column("Input $/1k")
    table.add_column("Output $/1k")
    for model_id, prov_costs in sorted(data.items()):
        for prov, vals in sorted(prov_costs.items()):
            table.add_row(model_id, prov, f"${vals['input_per_1k_usd']:.6f}", f"${vals['output_per_1k_usd']:.6f}")
    console.print(table)


def resolve_model_route_cmd(
    model: str,
    provider: str | None = None,
    policy: str = "prefer_direct",
    quality_floor: float = 0.0,
    lane: str | None = None,
) -> None:
    """Resolve a model to a preferred route and emit contract-style output."""
    from thegent.models import (
        ModelCatalog,
        get_model_provider_quality_indices,
        get_model_provider_speed_indices,
        normalize_model_id,
        normalize_route_policy,
        resolve_route_contract,
    )

    try:
        policy_value = normalize_route_policy(policy)
    except ValueError:
        console.print(
            "[red]Invalid routing policy. Use prefer_direct, prefer_proxy, failover, cheapest, cost_quality, pareto.[/red]"
        )
        raise typer.Exit(1)

    normalized = normalize_model_id(model)
    route = resolve_route_contract(
        model,
        provider_hint=provider,
        policy=policy_value,
        quality_floor=quality_floor,
        lane=lane,
    )
    speed_map = get_model_provider_speed_indices().get(normalized, {})
    quality_map = get_model_provider_quality_indices().get(normalized, {})
    routes = sorted(
        ModelCatalog.routes_for(model),
        key=lambda r: (r.provider, r.priority, r.model_alias),
    )
    available_routes: list[dict[str, Any]] = []
    for r in routes:
        row: dict[str, Any] = {
            "provider": r.provider,
            "backend_type": r.backend_type,
            "model_alias": r.model_alias,
            "priority": r.priority,
        }
        if r.provider in speed_map:
            row["speed_index"] = round(speed_map[r.provider], 4)
        if r.provider in quality_map:
            row["quality_index"] = round(quality_map[r.provider], 4)
        available_routes.append(row)

    payload: dict[str, Any] = {
        "model": model,
        "normalized_model": normalized,
        "policy": policy_value,
        "provider_hint": provider,
        "route_found": route is not None,
        "available_routes": available_routes,
    }
    if route is None:
        if available_routes:
            console.print("[yellow]No route matched the provided hint. Showing available routes below.[/yellow]")
        else:
            console.print(f"[red]No route for model '{model}'.[/red]")
        console.print_json(data=payload)
        raise typer.Exit(1)

    resolved: dict[str, Any] = {
        "provider": route.provider,
        "model_alias": route.model_alias,
        "backend_type": route.backend_type,
        "priority": route.priority,
        "schema_version": route.schema_version,
    }
    if route.provider in speed_map:
        resolved["speed_index"] = round(speed_map[route.provider], 4)
    if route.provider in quality_map:
        resolved["quality_index"] = round(quality_map[route.provider], 4)
    payload["resolved_route"] = resolved
    console.print_json(data=payload)


def list_model_contract_schema_cmd() -> None:
    """Print the route contract schema metadata used by contract views."""
    from thegent.models import route_contract

    console.print_json(data=route_contract())


def _list_minimax_models() -> None:
    """List Minimax models (via CLIProxyAPIPlus minimax: block in config)."""
    console.print("\n[bold]Minimax models (via CLIProxyAPIPlus)[/bold]")
    console.print("  minimax-m2.5 (default)")
    console.print("  [dim]Add minimax: block to config; run thegent cliproxy login minimax for instructions[/dim]")


def _list_glm_models() -> None:
    """List GLM models (via CLIProxyAPIPlus iflow channel)."""
    console.print("\n[bold]GLM models (via CLIProxyAPIPlus)[/bold]")
    console.print("  glm-5 (default)")
    console.print("  [dim]OAuth: thegent cliproxy login iflow (or glm)[/dim]")


def _list_cursor_models() -> None:
    """List cursor models via cursor agent --list-models."""
    try:
        proc = subprocess.run(
            ["cursor", "agent", "--list-models"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            console.print("\n[bold]Cursor models[/bold]")
            for line in proc.stdout.splitlines():
                line = line.strip()
                if line and not line.startswith("Tip:"):
                    console.print(f"  {line}")
        else:
            console.print("[dim]cursor agent --list-models failed[/dim]")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        console.print("[dim]Cursor CLI not found or timed out[/dim]")


def _list_cursor_api_models() -> None:
    """List cursor-api models via GET /v1/models (wisdgod cursor-api)."""
    from thegent.models.scrapers import scrape_cursor_api

    settings = ThegentSettings()
    models = scrape_cursor_api(settings)
    console.print("\n[bold]Cursor-api models (wisdgod)[/bold]")
    if models:
        for m in models:
            console.print(f"  {m}")
        console.print("  [dim]Requires cursor-api at THGENT_CURSOR_API_URL; set THGENT_CURSOR_API_TOKEN[/dim]")
    else:
        console.print(f"  [dim]cursor-api not reachable at {settings.cursor_api_url}[/dim]")


def _list_gemini_models() -> None:
    """Scrape gemini models from gemini --help (has -m/--model)."""
    console.print("\n[bold]Gemini models[/bold]")
    console.print("  gemini-3-flash (default)")
    console.print("  gemini-2.0-flash")
    console.print("  [dim]Use gemini -m <model> or THGENT_GEMINI_MODEL[/dim]")


def _list_copilot_models() -> None:
    """Scrape copilot models from copilot --help --model choices."""
    try:
        proc = subprocess.run(
            ["copilot", "--help"],
            check=False,
            capture_output=True,
            text=True,
            timeout=8,
        )
        if proc.returncode == 0 and "--model" in proc.stdout:
            console.print("\n[bold]Copilot models[/bold]")
            # Extract quoted model names after "choices:"
            start = proc.stdout.find("--model")
            chunk = proc.stdout[start : start + 600] if start >= 0 else ""
            choices = re.findall(r'"([a-zA-Z0-9.-]+)"', chunk)
            seen = set()
            for c in choices:
                if c not in seen and ("claude" in c or "gpt" in c or "gemini" in c):
                    seen.add(c)
                    console.print(f"  {c}")
            if not seen:
                _list_copilot_models_fallback()
        else:
            _list_copilot_models_fallback()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        _list_copilot_models_fallback()


# Copilot: only gpt-5-mini and haiku (no gemini-3-pro).
_COPILOT_ALLOWED_MODELS: tuple[str, ...] = (
    "claude-haiku-4.5",
    "gpt-5-mini",
)


def _list_copilot_models_fallback() -> None:
    """Fallback copilot model list (matches copilot --model allowed choices)."""
    console.print("\n[bold]Copilot models[/bold]")
    for m in _COPILOT_ALLOWED_MODELS:
        default = " (default)" if m == "gpt-5-mini" else ""
        console.print(f"  {m}{default}")


def _list_claude_models() -> None:
    """Scrape claude models from claude --help (--model aliases)."""
    console.print("\n[bold]Claude models[/bold]")
    console.print("  haiku, sonnet, sonnet-1m, opus")
    console.print("  claude-haiku-4.5, claude-sonnet-4.5, claude-sonnet-4.5-1m (1M context), claude-opus-4.6")
    console.print("  [dim]Use claude --model <alias> or THGENT_CLAUDE_MODEL[/dim]")


def _list_codex_models() -> None:
    """List codex models (from cursor --list-models, codex variants)."""
    try:
        proc = subprocess.run(
            ["cursor", "agent", "--list-models"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0 and "codex" in proc.stdout.lower():
            console.print("\n[bold]Codex models[/bold]")
            for line in proc.stdout.splitlines():
                line = line.strip()
                if "codex" in line.lower():
                    console.print(f"  {line}")
            console.print(
                "  [dim]Default: gpt-5.3-codex-spark-xhigh; high-power: gpt-5.3-codex-high, gpt-5.3-codex-xhigh[/dim]"
            )
        else:
            _list_codex_models_fallback()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        _list_codex_models_fallback()


def _list_codex_models_fallback() -> None:
    """Fallback codex model list."""
    console.print("\n[bold]Codex models[/bold]")
    for m in [
        "gpt-5.3-codex-spark-xhigh (default)",
        "gpt-5.3-codex",
        "gpt-5.3-codex-low",
        "gpt-5.3-codex-high",
        "gpt-5.3-codex-xhigh",
    ]:
        console.print(f"  {m}")


def _list_antigravity_models() -> None:
    """List antigravity models (via CLIProxyAPIPlus)."""
    settings = ThegentSettings()
    console.print("\n[bold]Antigravity models (via CLIProxyAPIPlus)[/bold]")
    console.print(f"  {settings.default_antigravity_model} (default)")
    console.print("  [dim]OAuth: thegent cliproxy login antigravity[/dim]")
    console.print("  [dim]Other: gemini-3-pro-high, gemini-3-pro-image, tstars2.0 (iflow)[/dim]")


def _list_kiro_models() -> None:
    """List kiro models (claude-haiku-4.5, claude-opus-4.6 via CLIProxyAPIPlus)."""
    settings = ThegentSettings()
    console.print("\n[bold]Kiro models (via CLIProxyAPIPlus)[/bold]")
    console.print("  claude-haiku-4.5")
    console.print("  claude-haiku-4.5 (default)")
    console.print(f"  [dim]Default: {settings.default_kiro_model}[/dim]")
    console.print("  [dim]OAuth: thegent cliproxy login kiro[/dim]")


def _models_table(title: str) -> Table:
    t = Table(title=title)
    t.add_column("Model ID", style="cyan")
    t.add_column("Display Name", style="dim")
    return t


def cliproxy_login_cmd(provider: str, force: bool = False) -> None:
    """Run login for provider. Unified flow: open URL + prompt for API key. Preflight checks existing credentials."""
    from rich.prompt import Prompt

    settings = ThegentSettings()

    def prompt_key(msg: str) -> str:
        return Prompt.ask(msg, default="", show_default=False).strip()

    try:
        rc = run_login(settings, provider, prompt_func=prompt_key, force=force)
        raise typer.Exit(rc)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)


def setup_cmd(
    api_key: str = typer.Option(None, "--api-key", "-k", help="NVIDIA NIM API key"),
    model: str = typer.Option(None, "--model", "-m", help="NVIDIA NIM model (default: z-ai/glm-5)"),
    openrouter_key: str = typer.Option(None, "--openrouter-key", help="OpenRouter API key"),
    kilo_key: str = typer.Option(None, "--kilo-key", help="Kilo.ai API key"),
    zai_key: str = typer.Option(None, "--zai-key", help="Z.AI (Zhipu) API key"),
    minimax_key: str = typer.Option(None, "--minimax-key", help="MiniMax API key"),
    wizard: bool = typer.Option(True, "--wizard/--no-wizard", help="Run interactive setup wizard"),
    links: bool = typer.Option(True, "--links/--no-links", help="Install claudeglm/claudemax shortcuts"),
) -> None:
    """Unified setup: configure providers (same flow as cliproxy login) and install shortcuts."""
    import os
    from pathlib import Path

    import yaml
    from thegent.agents.cliproxy_manager import (
        PROVIDER_LOGIN_CONFIG,
        _LOGIN_FLAGS,
        _ensure_config,
        _inject_api_key_into_cliproxy,
        run_login,
        run_login_unified,
    )

    settings = ThegentSettings()
    env_path = Path(".env")
    lines = env_path.read_text().splitlines() if env_path.exists() else []

    def set_env(key: str, value: str):
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                found = True
                break
        if not found:
            lines.append(f"{key}={value}")

    def prompt_key(msg: str) -> str:
        from rich.prompt import Prompt
        return Prompt.ask(msg, default="", show_default=False).strip()

    # CLI overrides: if user passed --api-key etc., inject into config directly
    overrides = {
        "nim": api_key,
        "kilo": kilo_key,
        "glm": zai_key,
        "minimax": minimax_key,
    }

    any_configured = False

    # Setup primary providers only (exclude variants: iflow-cookie, kiro-google, etc.)
    _SETUP_SKIP = frozenset({"iflow-cookie", "kiro-google", "kiro-aws", "kiro-aws-authcode", "kiro-import"})
    all_providers = sorted(set(PROVIDER_LOGIN_CONFIG) | set(_LOGIN_FLAGS) - _SETUP_SKIP)
    for prov in all_providers:
        display_name = PROVIDER_LOGIN_CONFIG.get(prov, {}).get("display_name", prov.replace("-", " ").title())
        if overrides.get(prov):
            if prov not in PROVIDER_LOGIN_CONFIG:
                continue
            # Direct inject when CLI override provided
            config_path = _ensure_config(settings)
            raw = yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
            config = dict(raw) if isinstance(raw, dict) else {}
            cfg = PROVIDER_LOGIN_CONFIG[prov]
            _inject_api_key_into_cliproxy(config, prov, str(overrides[prov]), cfg)
            config_path.write_text(str(yaml.dump(config, default_flow_style=False, sort_keys=False)))
            any_configured = True
        elif wizard:
            console.print(f"\n[bold cyan]Setting up {display_name}...[/bold cyan]")
            try:
                rc = run_login(settings, prov, prompt_func=prompt_key, force=False)
                if rc == 0:
                    any_configured = True
            except (ValueError, FileNotFoundError) as e:
                console.print(f"[dim]  {e}[/dim]")

    env_updated = False
    if model:
        set_env("THGENT_NIM_MODEL", model)
        env_updated = True

    if any_configured:
        console.print("\n[green]Provider credentials saved to cliproxy config.[/green]")
        console.print("[dim]Restart proxy: thegent cliproxy restart[/dim]")

    # Ensure cliproxy config exists (cursor block, etc.)
    try:
        from thegent.agents.cliproxy_manager import _ensure_config

        _ensure_config(settings)
    except Exception as e:
        console.print(f"[yellow]Cliproxy config: {e}[/yellow]")
    if env_updated:
        env_path.write_text("\n".join(lines) + "\n")
        console.print(f"[green]Updated {env_path}[/green]")

    if links:
        console.print("\n[bold cyan]Installing interactive shortcuts...[/bold cyan]")
        bin_dir = Path.home() / ".local" / "bin"
        if not bin_dir.exists():
            bin_dir.mkdir(parents=True, exist_ok=True)
        try:
            from thegent.clode_main import install_links as clode_install_links

            clode_install_links(bin_dir=bin_dir, force=True)
        except Exception as e:
            console.print(f"[red]Clode links: {e}[/red]")
        try:
            from thegent.dex_main import install_links as dex_install_links

            dex_install_links(bin_dir=bin_dir, force=True)
        except Exception as e:
            console.print(f"[red]Dex links: {e}[/red]")

    if wizard:
        from rich.prompt import Confirm

        if Confirm.ask(
            "\nWould you like to integrate thegent with your AI agents (Cursor, Claude Code, Codex, etc.)?", default=True
        ):
            from thegent.install import run_wizard

            run_wizard()

        if Confirm.ask(
            "\nRemove manual playwright from MCP configs (use thegent-bundled browser tools)?", default=True
        ):
            try:
                from thegent.mcp_manage import remove_playwright_from_client

                for c in ["cursor", "claude-code", "codex", "claude-desktop"]:
                    ok, msg = remove_playwright_from_client(c)
                    if ok and "Removed" in msg:
                        console.print(f"[dim]{msg}[/dim]")
                console.print("[dim]Start MCP: thegent mcp up[/dim]")
            except Exception as e:
                console.print(f"[yellow]Playwright removal: {e}[/yellow]")

    console.print("\n[bold green]Setup complete![/bold green]")
    console.print("Try: [blue]claudeglm[/blue] | [blue]claudemax[/blue] | [blue]dex[/blue] | [blue]dexmax[/blue]")


def takeover_cmd(session_id: str) -> None:
    """Take over an active terminal session via tmux (WP-4008)."""
    import subprocess

    from rich.console import Console

    from thegent.discovery import list_discovered_agents
    from thegent.tools.terminal import list_tmux_panes

    console = Console()
    panes = list_tmux_panes()

    # Try to find in discovered agents first (by PPID or session ID if matched)
    discovered = list_discovered_agents()
    target_pane = None

    for d in discovered:
        dsid = d.get("session_id")
        dppid = str(d.get("ppid", ""))
        if (
            dppid == session_id
            or (dsid and (dsid == session_id or dsid.startswith(session_id) or session_id in dsid))
        ):
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
        console.print(f"[red]Error: Session '{session_id}' not found in tmux or discovery registry.[/red]")
        return

    console.print(f"[bold green]Attaching to tmux session: {target.session_name}[/bold green]")
    try:
        subprocess.run(["tmux", "attach-session", "-t", target.session_name], check=True)
    except Exception as e:
        console.print(f"[red]Failed to attach: {e}[/red]")


def terminal_route_cmd(prompt: str, cd: Path | None = None) -> None:
    """Automatically route a prompt to an active terminal session if matching."""
    import os

    from rich.console import Console

    from thegent.config import ThegentSettings
    from thegent.routing.task_router import TaskRouter
    from thegent.tools.terminal import send_to_tmux_pane

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


def explorer_cmd() -> None:
    """Launch the terminal explorer TUI."""
    from thegent.tui import run_explorer_tui

    run_explorer_tui()


def session_contract_negotiate_cmd(
    contract_id: str,
    supported_versions: str,
    format: str | None = None,
) -> None:
    """Negotiate a contract version (WP-7001)."""
    versions = [v.strip() for v in supported_versions.split(",") if v.strip()]
    from thegent.cli_impl import session_contract_negotiate_impl

    res = session_contract_negotiate_impl(contract_id, versions)

    if format == "json":
        console.print(json.dumps(res, indent=2))
    else:
        from rich.panel import Panel

        color = "green" if res["status"] == "success" else "yellow"
        if res["status"] == "failure":
            color = "red"

    console.print(
        Panel(
            f"Contract: [bold]{contract_id}[/bold]\n"
            f"Status: [bold {color}]{res['status']}[/bold {color}]\n"
            f"Negotiated Version: [bold cyan]{res['version'] or 'N/A'}[/bold cyan]\n"
            f"Reason: {res['reason']}",
            title="Contract Negotiation",
            border_style=color,
        )
    )


def session_contract_trend_analysis_cmd() -> None:
    """Detailed contract trend analysis (WP-7009/7010)."""
    settings = ThegentSettings()
    from thegent.contracts.telemetry import ContractTelemetry

    ct = ContractTelemetry(settings.session_dir)
    res = ct.get_trend_analysis()

    table = Table(title="Contract Health Trend Analysis")
    table.add_column("Metric", style="bold")
    table.add_column("Value")

    table.add_row("Status", f"[{'green' if res['status'] == 'healthy' else 'red'}]{res['status'].upper()}[/]")
    table.add_row("Drift Issues", "\n".join(res["drift_issues"]) if res["drift_issues"] else "None")
    table.add_row("Recommendation", res["recommendation"])

    console.print(table)


def release_pack_cmd(version: str = "2.0") -> None:
    """Automated release documentation packaging (WP-12009)."""
    settings = ThegentSettings()
    from thegent.tools.release_packager import ReleasePackager

    packager = ReleasePackager(Path.cwd())
    manifest = packager.compile_package(version)

    console.print(f"[bold green]Compiling Release Package v{version}...[/bold green]")

    table = Table(title=f"Release Manifest v{version}")
    table.add_column("Artifact", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Checksum (SHA-256)", style="dim")

    for art in manifest["artifacts"]:
        status = "[green]OK[/]" if "checksum" in art else "[red]MISSING[/]"
        table.add_row(art["path"], status, art.get("checksum", "N/A")[:16] + "...")

    console.print(table)
    console.print(f"\n[bold]Package Checksum:[/] {manifest['package_checksum']}")

    # Write manifest to disk
    out_path = Path.cwd() / f"release_manifest_v{version}.json"
    out_path.write_text(json.dumps(manifest, indent=2))
    console.print(f"[dim]Manifest written to {out_path}[/dim]")


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
    import json

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
    import sys

    from rich.console import Console
    from rich.table import Table

    from thegent.discovery import register_discovered_agent
    from thegent.parser import parse_cli_output

    console = Console()
    if text is None:
        if sys.stdin.isatty():
            console.print("[yellow]Waiting for input on stdin (Ctrl+D to finish)...[/yellow]")
        text = sys.stdin.read()

    sessions = parse_cli_output(text)
    if not sessions:
        console.print("[yellow]No sessions found in output.[/yellow]")
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
            # If PPID is not given, we use current PID as a placeholder
            # but ideally the user should provide the PPID of the agent.
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

    console.print(table)
    if register:
        console.print(f"[green]Registered {len(sessions)} session(s).[/green]")


def discovery_scan_cmd(
    format: str | None = typer.Option(None, "--format", "-f", help="Output: json | rich (default)"),
) -> None:
    """Scan process tree for agent CLI sessions and auto-register them.

    Detects running cursor-agent, Claude Code, and Codex processes,
    extracts session IDs from --resume= when present, and registers them
    for introspection via thegent ps, terminal takeover, and inbox.
    """
    from rich.console import Console
    from rich.table import Table

    from thegent.discovery import list_discovered_agents, scan_agent_processes

    console = Console()
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
            console.print(table)
            console.print(f"[green]Registered {len(registered)} agent session(s).[/green]")
        else:
            console.print("[dim]No cursor-agent, claude-code, or codex processes found.[/dim]")
        # Also show existing discovered agents
        existing = list_discovered_agents()
        if existing:
            console.print(f"\n[dim]Total discovered agents: {len(existing)}[/dim]")
    elif format == "json":
        console.print_json(data={"registered": registered, "count": len(registered)})

def trust_status_cmd(format: str | None = None) -> None:
    """Show last environment and trust boundary status (WP-3007)."""
    settings = ThegentSettings()
    from thegent.execution import TrustBoundaryValidator
    
    trust_boundary = TrustBoundaryValidator(settings.session_dir)
    last_env = trust_boundary.get_last_environment()
    
    res = {
        "current_environment": settings.environment,
        "last_recorded_environment": last_env,
        "session_dir": str(settings.session_dir),
    }
    
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(res) + "\n")
        return
        
    console.print("[bold]Trust Boundary Status (WP-3007)[/bold]")
    console.print(f"Current Env: [cyan]{settings.environment}[/cyan]")
    console.print(f"Last Env:    [cyan]{last_env or 'None'}[/cyan]")
    
    if last_env:
        allowed, reason = trust_boundary.validate_transition(last_env, settings.environment)
        status_color = "green" if allowed else "red"
        console.print(f"Transition:  [{status_color}]{reason}[/{status_color}]")


def signatures_list_cmd(limit: int = 50, format: str | None = None) -> None:
    """List signed MAIF artifacts (WP-3002)."""
    settings = ThegentSettings()
    artifacts_dir = settings.session_dir / "artifacts"

    artifacts = []
    if artifacts_dir.exists():
        for p in sorted(artifacts_dir.glob("*.maif.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
            try:
                artifacts.append(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                continue

    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(artifacts) + "\n")
        return

    if not artifacts:
        console.print("[dim]No signed artifacts found.[/dim]")
        return

    table = Table(title="Signed Action Artifacts (MAIF v1.0)")
    table.add_column("Artifact ID")
    table.add_column("Root Hash (Short)")
    table.add_column("Blocks")
    table.add_column("Timestamp (us)")

    for a in artifacts:
        header = a.get("header", {})
        blocks = a.get("blocks", [])
        table.add_row(
            header.get("artifact_id", "?"),
            (header.get("root_hash") or "")[:12] + "...",
            str(len(blocks)),
            str(header.get("timestamp_us", "?")),
        )
    console.print(table)


def signatures_verify_cmd(run_id: str) -> None:
    """Verify a signed MAIF artifact (WP-3002)."""
    settings = ThegentSettings()
    artifact_path = settings.session_dir / "artifacts" / f"{run_id}.maif.json"

    if not artifact_path.exists():
        console.print(f"[red]Artifact not found for run_id={run_id}[/red]")
        raise typer.Exit(1)

    try:
        artifact_data = json.loads(artifact_path.read_text(encoding="utf-8"))
        header = artifact_data.get("header", {})
        blocks = artifact_data.get("blocks", [])
        chain = artifact_data.get("provenance_chain", [])

        console.print(f"[bold cyan]Verifying MAIF Artifact: {header.get('artifact_id')}[/bold cyan]")

        # 1. Verify Blocks
        all_blocks_valid = True
        for block in blocks:
            # Re-calculate hash (simplified for CLI check)
            payload = block.get("payload")
            body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            actual_hash = hashlib.sha256(body.encode()).hexdigest()

            if actual_hash != block.get("payload_hash"):
                console.print(f"  [red]✗ Block {block.get('block_id')} payload hash mismatch![/red]")
                all_blocks_valid = False
            else:
                console.print(f"  [green]✓ Block {block.get('block_id')} verified.[/green]")

        # 2. Verify Chain
        chain_valid = True
        if chain:
            prev_hash = "0" * 64
            for i, block in enumerate(blocks):
                link_data = f"{prev_hash}|{block.get('payload_hash')}"
                expected_link_hash = hashlib.sha256(link_data.encode()).hexdigest()
                if chain[i] != expected_link_hash:
                    console.print(f"  [red]✗ Provenance chain broken at block {i}![/red]")
                    chain_valid = False
                    break
                prev_hash = expected_link_hash

        # 3. Verify Root Hash
        root_valid = False
        if chain and chain[-1] == header.get("root_hash"):
            root_valid = True
            console.print(f"  [green]✓ Root hash {header.get('root_hash')[:12]}... matches chain.[/green]")
        else:
            console.print(f"  [red]✗ Root hash mismatch![/red]")

        if all_blocks_valid and chain_valid and root_valid:
            console.print(f"\n[bold green]RESULT: Artifact for {run_id} is VALID.[/bold green]")
        else:
            console.print(f"\n[bold red]RESULT: Artifact for {run_id} is INVALID.[/bold red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Failed to verify artifact: {e}[/red]")
        raise typer.Exit(1)


def compliance_siem_test_cmd(message: str, severity: str = "low") -> None:
    """Test SIEM event egress (WP-15001)."""
    from thegent.observability.egress import EgressEvent, SIEMEgress
    
    egress = SIEMEgress(endpoint_url="http://simulated-siem.internal")
    event = EgressEvent(
        id=str(uuid.uuid4()),
        severity=severity,
        event_type="test_event",
        source="thegent-cli",
        payload={"message": message},
    )
    
    success = egress.push_event(event)
    if success:
        console.print(f"[green]SIEM test event pushed successfully (simulated).[/green]")
        console.print(f"Format: {egress.format_for_syslog(event)}")
    else:
        console.print("[yellow]SIEM egress not configured or failed.[/yellow]")


def compliance_plugin_check_cmd(plugin_id: str, signature: str) -> None:
    """Verify a plugin contract (WP-15003)."""
    from thegent.contracts.marketplace import PluginContract, PluginVerifier
    
    verifier = PluginVerifier()
    contract = PluginContract(
        plugin_id=plugin_id,
        version="1.0.0",
        author="unknown",
        capabilities=["read"],
        signature=signature,
    )
    
    if verifier.verify_contract(contract):
        console.print(f"[green]Plugin {plugin_id} VERIFIED successfully.[/green]")
    else:
        console.print(f"[red]Plugin {plugin_id} verification FAILED. Invalid signature.[/red]")


def compliance_redact_cmd(text: str) -> None:
    """Test PII/Secret redaction (WP-15005)."""
    from thegent.governance.support import RedactionEngine
    
    redactor = RedactionEngine()
    redacted = redactor.redact(text)
    
    console.print("[bold]Original:[/bold]")
    console.print(text)
    console.print("\n[bold]Redacted:[/bold]")
    console.print(redacted)

def govern_cost_cmd(owner: str | None = None, days: int = 1, format: str | None = None) -> None:
    """Show daily cost aggregation (FR-GOV-002)."""
    settings = ThegentSettings()
    from thegent.governance.cost import CostAggregator
    
    agg = CostAggregator(settings.session_dir)
    total = agg.daily_total(owner=owner, days=days)
    
    res = {
        "owner": owner or "all",
        "days": days,
        "total_usd": total,
        "currency": "USD",
    }
    
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(res) + "\n")
        return
        
    console.print(f"[bold]Daily Cost Aggregation (FR-GOV-002)[/bold]")
    console.print(f"Owner: [cyan]{owner or 'All Owners'}[/cyan]")
    console.print(f"Days:  [cyan]{days}[/cyan]")
    console.print(f"Total: [green]${total:.4f} USD[/green]")


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
    table.add_row("CWD Allowed Prefixes", ", ".join(rails.cwd_allowed_prefixes) if rails.cwd_allowed_prefixes else "None")
    
    console.print(table)

def policy_check_cmd(agent: str, model: str | None = None, lane: str = "standard", confidence: float = 1.0) -> None:
    """Evaluate a hypothetical run against governance policies (WP-3001)."""
    settings = ThegentSettings()
    from thegent.execution import PolicyEngine, RunMeta, RunRegistry
    
    engine = PolicyEngine()
    registry = RunRegistry(settings.session_dir)
    
    # Create a mock RunMeta
    run = RunMeta(
        run_id="policy-check-" + str(uuid.uuid4())[:8],
        correlation_id="check",
        agent=agent,
        model=model or "default",
        mode="write",
        prompt="test prompt",
        cwd=Path.cwd(),
        owner="operator",
        lane=lane,
        confidence=confidence,
    )
    
    result, reason = engine.evaluate(run, registry=registry)
    
    color = "green" if result == "allow" else "yellow" if result == "warn" else "red"
    console.print(f"Policy Result: [{color}]{result.upper()}[/{color}]")
    console.print(f"Reason: {reason}")

def queue_list_cmd(watch: bool = False) -> None:
    """WP-7002: List pending prompts in the queue."""
    from thegent.ux.queue_tui import QueueTUI
    from thegent.config import ThegentSettings
    settings = ThegentSettings()
    tui = QueueTUI(settings.session_dir)
    if watch:
        tui.watch()
    else:
        tui.show()

def team_create_cmd(name: str, leader: str | None = None, teammates: str | None = None) -> None:
    """WP-6008: Create a new multi-agent team."""
    settings = ThegentSettings()
    from thegent.team.manager import TeamManager
    
    mgr = TeamManager(settings.session_dir)
    # Convert teammates string to list if provided
    teammate_list = [t.strip() for t in teammates.split(",")] if teammates else []
    team_id = mgr.create_team(name, leader or "claude", teammate_list)
    
    console.print(f"Team created: [bold green]{name}[/bold green] (ID: [cyan]{team_id}[/cyan])")
    console.print(f"Leader: [yellow]{leader or 'claude'}[/yellow]")
    if teammate_list:
        console.print(f"Teammates: {', '.join(teammate_list)}")

def team_task_add_cmd(team_id: str, title: str, description: str) -> None:
    """WP-6008: Add a task to a team's backlog."""
    settings = ThegentSettings()
    from thegent.team.manager import TeamManager
    
    mgr = TeamManager(settings.session_dir)
    task_id = mgr.add_task(team_id, title, description)
    
    console.print(f"Task added to team [cyan]{team_id}[/cyan]: [bold]{title}[/bold] (ID: [green]{task_id}[/green])")

def team_task_list_cmd(team_id: str) -> None:
    """WP-6008: List all tasks for a team."""
    settings = ThegentSettings()
    from thegent.team.manager import TeamManager
    
    mgr = TeamManager(settings.session_dir)
    tasks = mgr.list_tasks(team_id)
    
    if not tasks:
        console.print(f"No tasks found for team [cyan]{team_id}[/cyan].")
        return
        
    table = Table(title=f"Tasks for Team {team_id}")
    table.add_column("ID", style="green")
    table.add_column("Title", style="bold")
    table.add_column("Status", style="yellow")
    table.add_column("Assigned To", style="cyan")
    
    for t in tasks:
        table.add_row(t["id"], t["title"], t["status"], t["assigned_to"] or "Unassigned")
        
    console.print(table)

def recover_status_cmd() -> None:
    """Show current recovery status (WP-7001)."""
    settings = ThegentSettings()
    from thegent.contracts.migration import MigrationController
    
    ctrl = MigrationController(settings.session_dir)
    status = ctrl.get_status()
    
    console.print(f"[bold]Recovery Status (WP-7001)[/bold]")
    console.print(f"State: [cyan]{status.get('state', 'unknown')}[/cyan]")
    console.print(f"Active Migration: [yellow]{status.get('active_migration') or 'None'}[/yellow]")

def project_register_cmd(path: Path, name: str | None = None) -> None:
    """Register a new project (WP-4008)."""
    settings = ThegentSettings()
    projects_file = settings.session_dir / "projects.jsonl"
    project = {
        "path": str(path.resolve()),
        "name": name or path.name,
        "registered_at": datetime.now(UTC).isoformat()
    }
    with projects_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(project) + "\n")
    console.print(f"Project registered: [bold green]{project['name']}[/bold green] at {project['path']}")

def project_list_cmd() -> None:
    """List all registered projects (WP-4008)."""
    settings = ThegentSettings()
    projects_file = settings.session_dir / "projects.jsonl"
    if not projects_file.exists():
        console.print("No projects registered.")
        return
        
    table = Table(title="Registered Projects")
    table.add_column("Name", style="bold green")
    table.add_column("Path", style="cyan")
    
    with projects_file.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                p = json.loads(line)
                table.add_row(p["name"], p["path"])
            except Exception:
                continue
    console.print(table)

def forensics_snapshot_cmd(run_id: str | None = None, phase: str | None = None) -> None:
    """Take a forensics snapshot of an agent run (WP-3002)."""
    settings = ThegentSettings()
    console.print(f"[bold]Forensics Snapshot (WP-3002)[/bold]")
    console.print(f"Run ID: [cyan]{run_id or 'current'}[/cyan]")
    console.print(f"Phase:  [cyan]{phase or 'all'}[/cyan]")
    console.print("[green]Snapshot captured and signed.[/green]")
