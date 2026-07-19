"""CLI command implementations.

This module contains the CLI command functions for session management,
team operations, and other CLI features.
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer

if TYPE_CHECKING:
    from rich.console import Console


def _serialize_health_gate_jsonl(results: list[dict]) -> str:
    """Serialize health gate results to JSONL format.

    Args:
        results: List of health check result dictionaries.

    Returns:
        JSONL string representation.
    """
    import json

    lines = []
    for result in results:
        lines.append(json.dumps(result))
    return "\n".join(lines)


def _inject_skill_instructions(prompt: str, skills: list[str]) -> str:
    """Inject skill instructions into a prompt.

    Args:
        prompt: The prompt to inject instructions into.
        skills: List of skill names to inject.

    Returns:
        Prompt with skill instructions injected.
    """
    if not skills:
        return prompt
    skill_section = "\n\nSkills available:\n" + "\n".join(f"- {s}" for s in skills)
    return prompt + skill_section


def _format_grounding_sources_lines(sources: list[dict]) -> list[str]:
    """Format grounding sources as display lines.

    Args:
        sources: List of source dictionaries.

    Returns:
        List of formatted source lines.
    """
    lines = []
    for i, source in enumerate(sources, 1):
        title = source.get("title", "Untitled")
        url = source.get("url", "")
        lines.append(f"[{i}] {title}")
        if url:
            lines.append(f"    {url}")
    return lines


def _format_context_usage_line(usage: dict) -> str:
    """Format context usage as a display line.

    Args:
        usage: Usage dictionary with tokens and limits.

    Returns:
        Formatted usage line.
    """
    used = usage.get("tokens", 0)
    limit = usage.get("limit", 0)
    pct = (used / limit * 100) if limit > 0 else 0
    return f"Context: {used:,}/{limit:,} tokens ({pct:.1f}%)"


__all__ = [
    "logs_cmd",
    "stop_cmd",
    "team_create_cmd",
    "team_task_add_cmd",
    "team_task_list_cmd",
    "_serialize_health_gate_csv",
    "_serialize_health_gate_jsonl",
    "_serialize_health_trend_csv",
    "_scope_key",
    "_inject_skill_instructions",
    "_format_grounding_sources_lines",
    "_format_context_usage_line",
    "_serialize_health_gate_md",
    "_format_transcript_summary_line",
    "_serialize_health_report_csv",
    "_serialize_health_report_jsonl",
    "_serialize_health_report_md",
    "_serialize_health_trend_jsonl",
    "_serialize_health_trend_md",
]


def _serialize_health_trend_md(results: list[dict]) -> str:
    """Serialize health trend results to Markdown format.

    Args:
        results: List of health trend result dictionaries.

    Returns:
        Markdown string representation.
    """
    if not results:
        return "No health trend data available."
    lines = ["# Health Trend Results", ""]
    for result in results:
        timestamp = result.get("timestamp", "N/A")
        metric = result.get("metric", "unknown")
        value = result.get("value", 0)
        lines.append(f"- **{metric}** ({timestamp}): {value}")
    return "\n".join(lines)


def _serialize_health_trend_jsonl(results: list[dict]) -> str:
    """Serialize health trend results to JSONL format.

    Args:
        results: List of health trend result dictionaries.

    Returns:
        JSONL string representation.
    """
    import json

    lines = []
    for result in results:
        lines.append(json.dumps(result))
    return "\n".join(lines)


def _serialize_health_trend_csv(results: list[dict]) -> str:
    """Serialize health trend results to CSV format.

    Args:
        results: List of health trend result dictionaries.

    Returns:
        CSV string representation.
    """
    if not results:
        return ""
    headers = ["timestamp", "metric", "value"]
    lines = [",".join(headers)]
    for result in results:
        row = [
            result.get("timestamp", ""),
            result.get("metric", ""),
            str(result.get("value", "")),
        ]
        lines.append(",".join(f'"{r}"' for r in row))
    return "\n".join(lines)


def _serialize_health_report_md(results: list[dict]) -> str:
    """Serialize health report results to Markdown format.

    Args:
        results: List of health report result dictionaries.

    Returns:
        Markdown string representation.
    """
    return _serialize_health_gate_md(results)


def _serialize_health_report_jsonl(results: list[dict]) -> str:
    """Serialize health report results to JSONL format.

    Args:
        results: List of health report result dictionaries.

    Returns:
        JSONL string representation.
    """
    return _serialize_health_gate_jsonl(results)


def _serialize_health_report_csv(results: list[dict]) -> str:
    """Serialize health report results to CSV format.

    Args:
        results: List of health report result dictionaries.

    Returns:
        CSV string representation.
    """
    return _serialize_health_gate_csv(results)


def _serialize_health_gate_md(results: list[dict]) -> str:
    """Serialize health gate results to Markdown format.

    Args:
        results: List of health check result dictionaries.

    Returns:
        Markdown string representation.
    """
    if not results:
        return "No health checks performed."

    lines = ["# Health Gate Results", ""]
    for result in results:
        check = result.get("check", "Unknown")
        status = result.get("status", "unknown")
        message = result.get("message", "")
        lines.append(f"- **{check}**: {status} - {message}")

    return "\n".join(lines)


def _format_transcript_summary_line(transcript: dict[str, Any]) -> str:
    """Format a transcript summary line.

    Args:
        transcript: Transcript dictionary.

    Returns:
        Formatted summary line string.
    """
    duration = transcript.get("duration", 0.0)
    word_count = transcript.get("word_count", 0)
    return f"Transcript ({duration:.1f}s, {word_count} words)"


def _serialize_health_gate_csv(results: list[dict]) -> str:
    """Serialize health gate results to CSV format.

    Args:
        results: List of health check result dictionaries.

    Returns:
        CSV string representation.
    """
    if not results:
        return ""
    headers = ["check", "status", "message"]
    lines = [",".join(headers)]
    for result in results:
        row = [
            result.get("check", ""),
            result.get("status", ""),
            result.get("message", ""),
        ]
        lines.append(",".join(f'"{r}"' for r in row))
    return "\n".join(lines)


def _scope_key(scope: str, key: str) -> str:
    """Create a scoped key.

    Args:
        scope: The scope prefix.
        key: The key name.

    Returns:
        Scoped key string.
    """
    return f"{scope}:{key}"


def _is_pid_running(pid: int) -> bool:
    """Check if a process is still running.

    Args:
        pid: Process ID to check.

    Returns:
        True if process is running, False otherwise.
    """
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def logs_cmd(
    session_id: str,
    follow: bool = False,
    tail: int = 20,
    timeout: int | None = None,
) -> int:
    """Display logs for a session.

    Args:
        session_id: The session ID.
        follow: Whether to follow (tail -f style).
        tail: Number of lines to show.
        timeout: Timeout in seconds for follow mode.

    Returns:
        Exit code (0 for success, 124 for timeout).
    """
    from thegent.cli.commands._cli_shared import get_session_dir

    session_dir = get_session_dir()
    log_file = session_dir / f"{session_id}.stdout.log"

    # Owner-scoped probe: log files live under
    # ``session_dir / <owner_with_colons_replaced>`` alongside the meta
    # file. If the direct path doesn't exist, walk one level deep.
    if not log_file.exists():
        try:
            for child in session_dir.iterdir():
                if not child.is_dir():
                    continue
                candidate = child / f"{session_id}.stdout.log"
                if candidate.exists():
                    log_file = candidate
                    break
        except OSError:
            pass
        if not log_file.exists():
            typer.echo(f"Log file not found: {log_file}", err=True)
            return 1

    # Read and display logs
    lines = log_file.read_text().splitlines()
    for line in lines[-tail:]:
        typer.echo(line)

    if follow:
        # Follow mode
        assert timeout is not None
        start_time = time.time()
        last_size = log_file.stat().st_size

        while True:
            current_size = log_file.stat().st_size
            if current_size > last_size:
                new_content = log_file.read_text()[last_size:]
                for line in new_content.splitlines():
                    typer.echo(line)
                last_size = current_size

            if _is_pid_running(_get_session_pid(session_id, session_dir)):
                if time.time() - start_time > timeout:
                    raise typer.Exit(124)
            else:
                break

            time.sleep(0.1)

    return 0


def _get_session_pid(session_id: str, session_dir: Path) -> int:
    """Get the PID for a session from its metadata file.

    Args:
        session_id: The session ID.
        session_dir: The session directory.

    Returns:
        Process ID or 0 if not found.
    """
    import json

    meta_file = session_dir / f"{session_id}.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text())
        return meta.get("pid", 0)
    return 0


def stop_cmd(
    session_id: str,
    force: bool = False,
    wind_down: bool = False,
    grace: int = 5,
) -> None:
    """Stop a running session.

    Args:
        session_id: The session ID to stop.
        force: Force kill the process.
        wind_down: Allow graceful shutdown with grace period.
        grace: Grace period in seconds for wind_down.
    """
    from thegent.cli.commands._cli_shared import get_session_dir

    session_dir = get_session_dir()
    meta_file = session_dir / f"{session_id}.json"

    # Owner-scoped probe: session files live under
    # ``session_dir / <owner_with_colons_replaced>``. If the direct path
    # doesn't exist, walk one level deep to find the meta file.
    if not meta_file.exists():
        try:
            for child in session_dir.iterdir():
                if not child.is_dir():
                    continue
                candidate = child / f"{session_id}.json"
                if candidate.exists():
                    meta_file = candidate
                    break
        except OSError:
            pass
        if not meta_file.exists():
            typer.echo(f"Session not found: {session_id}", err=True)
            raise typer.Exit(1)

    import json

    meta = json.loads(meta_file.read_text())
    pid = meta.get("pid", 0)

    if pid and _is_pid_running(pid):
        if wind_down and not force:
            # Send SIGTERM and wait for graceful shutdown
            os.killpg(pid, 15)  # SIGTERM
            # Wait for graceful shutdown
            deadline = time.time() + grace
            while _is_pid_running(pid) and time.time() < deadline:
                time.sleep(0.1)

            if _is_pid_running(pid):
                typer.echo("Process still running after grace period, force killing...")
                os.killpg(pid, 9)  # SIGKILL
        elif force:
            os.killpg(pid, 9)  # SIGKILL
        else:
            os.killpg(pid, 15)  # SIGTERM
    else:
        typer.echo(f"Process {pid} is not running")


# =============================================================================
# Team Commands
# =============================================================================

console: "Console" = None  # Will be set by CLI framework


def team_create_cmd(
    *,
    name: str,
    leader: str | None = None,
    teammates: str | None = None,
    console: "Console" | None = None,
) -> None:
    """Create a new team.

    Args:
        name: Team name.
        leader: Leader agent name.
        teammates: Comma-separated teammate names.
        console: Rich console for output.
    """
    from thegent.cli.commands.team_commands import team_create_cmd as actual_cmd

    if console is None:
        from rich.console import Console

        console = Console()

    actual_cmd(name=name, leader=leader, teammates=teammates, console=console)


def team_task_add_cmd(
    *,
    team_id: str,
    title: str,
    description: str,
    console: "Console" | None = None,
) -> None:
    """Add a task to a team.

    Args:
        team_id: Team ID.
        title: Task title.
        description: Task description.
        console: Rich console for output.
    """
    from thegent.cli.commands.team_commands import team_task_add_cmd as actual_cmd

    if console is None:
        from rich.console import Console

        console = Console()

    actual_cmd(team_id=team_id, title=title, description=description, console=console)


def team_task_list_cmd(
    *,
    team_id: str,
    console: "Console" | None = None,
) -> None:
    """List tasks for a team.

    Args:
        team_id: Team ID.
        console: Rich console for output.
    """
    from thegent.cli.commands.team_commands import team_task_list_cmd as actual_cmd

    if console is None:
        from rich.console import Console

        console = Console()

    actual_cmd(team_id=team_id, console=console)


# ============================================================================
# WL-124: Re-export block — keep cli.py as the legacy monolith while
# exposing the new domain submodules' names so legacy `from cli import X`
# continues to work and the contract test passes.
# ============================================================================
from thegent.cli.commands.run_cmds import (  # noqa: E402,F401
    bg_cmd,
    deep_research_cmd,
    loop_cmd,
    loop_send_cmd,
    loop_stop_cmd,
    replay_cmd,
    retry_cmd,
    run_cmd,
    run_diff_cmd,
    takeover_cmd,
    terminal_route_cmd,
    trace_replay_cmd,
)
from thegent.cli.commands.session_cmds import (  # noqa: E402,F401
    deferral_list_cmd,
    deferral_resume_cmd,
    events_cmd,
    feedback_cmd,
    history_cmd,
    inbox_list_cmd,
    inbox_wait_cmd,
    inspect_cmd,
    pause_cmd,
    ps_cmd,
    resume_cmd,
    session_cmd,
    session_contract_health_gate_cmd,
    session_contract_health_report_cmd,
    session_contract_health_trend_cmd,
    session_contract_negotiate_cmd,
    session_contract_trend_analysis_cmd,
    session_contracts_cmd,
    session_fork_cmd,
    session_rollback_cmd,
    status_cmd,
    wait_cmd,
)

# NOTE: `logs_cmd` and `stop_cmd` are intentionally NOT re-exported from
# session_cmds. session_cmds.logs_cmd / session_cmds.stop_cmd are thin shims
# that delegate back into this module, which causes import-time name
# shadowing (the shim replaces the real definition in this module's
# namespace, then the shim's delegation call resolves to the shadowed
# shim → infinite recursion). Keep the real `logs_cmd` (line 295) and
# `stop_cmd` (line 370) as the canonical implementations.
from thegent.cli.commands.governance_cmds import (  # noqa: E402,F401
    audit_verify_cmd,
    compliance_plugin_check_cmd,
    compliance_redact_cmd,
    compliance_report_cmd,
    compliance_siem_test_cmd,
    contracts_conformance_cmd,
    contracts_registry_cmd,
    data_protection_cmd,
    discovery_parse_cmd,
    discovery_register_cmd,
    discovery_scan_cmd,
    drift_cmd,
    escalate_add_cmd,
    escalate_approve_cmd,
    escalate_list_cmd,
    escalate_resolve_cmd,
    govern_approve_cmd,
    govern_configure_cmd,
    govern_cost_cmd,
    govern_go_cycle_cmd,
    govern_go_health_cmd,
    govern_go_status_cmd,
    govern_go_watch_cmd,
    govern_list_pending_cmd,
    govern_reject_cmd,
    guardrails_check_cmd,
    guardrails_show_cmd,
    migration_cmd,
    policy_check_cmd,
    policy_purge_cmd,
    policy_show_cmd,
    signatures_list_cmd,
    signatures_verify_cmd,
    sweep_cmd,
    trust_status_cmd,
)
from thegent.cli.commands.plan_cmds import (  # noqa: E402,F401
    closure_pack_cmd,
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
    plan_analyze_cmd,
    plan_claim_cmd,
    plan_complete_cmd,
    plan_do_next_cmd,
    plan_get_next_cmd,
    plan_incorporate_cmd,
    plan_lint_workstream_cmd,
    plan_loop_cmd,
    plan_normalize_workstream_cmd,
    plan_progress_cmd,
    plan_verify_workstream_cmd,
    plan_wait_next_cmd,
    workstream_dashboard_cmd,
    workstream_dependencies_cmd,
    workstream_launch_cmd,
    workstream_query_cmd,
    workstream_stats_cmd,
)  # noqa: E501
from thegent.cli.commands.model_cmds import (  # noqa: E402,F401
    _list_antigravity_models,
    _list_claude_models,
    _list_codex_models,
    _list_codex_models_fallback,
    _list_copilot_models,
    _list_copilot_models_fallback,
    _list_cursor_api_models,
    _list_cursor_models,
    _list_gemini_models,
    _list_glm_models,
    _list_kiro_models,
    _list_minimax_models,
    _models_table,
    cliproxy_login_cmd,
    cost_values_cmd,
    list_agents_cmd,
    list_droids_cmd,
    list_model_contract_schema_cmd,
    list_models_cmd,
    metrics_cmd,
    quality_index_cmd,
    resolve_model_route_cmd,
    rules_sync_cmd,
    setup_cmd,
    speed_index_cmd,
)
from thegent.cli.commands.infra_cmds import (  # noqa: E402,F401
    archive_cmd,
    benchmark_cmd,
    cockpit_cmd,
    concurrency_set_cmd,
    concurrency_show_cmd,
    config_check_cmd,
    context_history_cmd,
    cost_status_cmd,
    explorer_cmd,
    forensics_snapshot_cmd,
    interruption_list_cmd,
    interruption_snooze_cmd,
    load_status_cmd,
    modes_cmd,
    monitor_cmd,
    observe_summary_cmd,
    operations_cmd,
    purge_cmd,
    recover_status_cmd,
    release_pack_cmd,
    scratchpad_cmd,
    sitback_dashboard_cmd,
    usage_cmd,
)
from thegent.cli.commands.team_cmds import (  # noqa: E402,F401
    dlq_list_cmd,
    drift_monitor_cmd,
    explain_cmd,
    fallbacks_cmd,
    handoff_cmd,
    handoff_confirm_cmd,
    handoff_list_cmd,
    handoff_show_cmd,
    project_list_cmd,
    project_register_cmd,
    queue_list_cmd,
    recover_status_cmd as team_recover_status_cmd,
    roadmap_cmd,
    self_heal_tests_cmd,
    summary_cmd,
    team_create_cmd,
    team_task_add_cmd,
    team_task_list_cmd,
    teammates_delegate_cmd,
    teammates_list_cmd,
    teammates_status_cmd,
    traffic_cmd,
    watchdog_cmd,
)
