"""Thegent CLI session commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import json
import os
import signal
import sys
import time
from pathlib import Path

import typer

from rich.table import Table

from thegent.cli.commands._cli_shared import (
    RunRegistry,
    ThegentSettings,
    _coerce_issue_types,
    _default_owner_tag,
    _find_session_meta,
    _is_pid_running,
    _normalize_output_format,
    _read_session_meta,
    _resolve_run_id,
    _resolve_session_id,
    _resolve_session_status,
    _safe_dict,
    _serialize_health_gate_md,
    _serialize_health_report_md,
    _serialize_health_trend_md,
    _session_paths,
    _write_health_gate_export,
    _write_health_trend_export,
    _write_report_export,
    console,
    EXIT_TIMEOUT,
    EXIT_HEALTH_GATE_FAILED,
    _LOG_FOLLOW_POLL_SECONDS,
)
from thegent.cli.commands.session_cmds_helpers import (
    follow_log_stream,
    parse_sources_csv,
    print_high_session_count_tip,
    render_ps_markdown,
    render_ps_rich_table,
    resolve_export_format_with_notice,
)


def history_cmd(limit: int = 50, format: str | None = None) -> None:
    """List execution run history (sync and background)."""
    from thegent.cli.commands.impl import history_impl

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
    from thegent.cli.commands.impl import events_impl

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
    from thegent.cli.commands.impl import inbox_list_impl

    src_tuple = parse_sources_csv(sources)
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
    from thegent.cli.commands.impl import inbox_wait_impl

    _src_tuple = parse_sources_csv(sources)
    events_result = inbox_wait_impl(
        timeout=int(timeout) if timeout else None,
    )
    events = events_result.get("items", []) if isinstance(events_result, dict) else []
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
    from thegent.cli.commands.impl import ps_impl

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
        render_ps_markdown(console=console, rows=rows, include_contract=include_contract)
    else:
        render_ps_rich_table(console=console, rows=rows, include_contract=include_contract)
        print_high_session_count_tip(console=console, rows=rows)


def session_contracts_cmd(
    all_sessions: bool = False,
    owner: str | None = None,
    format: str | None = None,
    missing_only: bool = False,
    summary_only: bool = False,
    strict: bool = False,
) -> None:
    from thegent.cli.commands.impl import session_contract_audit_impl

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
    from thegent.cli.commands.impl import session_contract_health_gate_impl

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
        chosen_format = resolve_export_format_with_notice(
            output=output,
            export_format=export_format,
            console=console,
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
        raise typer.Exit(EXIT_HEALTH_GATE_FAILED)


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
    from thegent.cli.commands.impl import session_contract_health_report_impl

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
        chosen_format = resolve_export_format_with_notice(
            output=output,
            export_format=export_format,
            console=console,
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
    from thegent.cli.commands.impl import session_contract_health_trend_impl

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
        chosen_format = resolve_export_format_with_notice(
            output=output,
            export_format=export_format,
            console=console,
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
    from thegent.cli.commands.impl import logs_impl, ps_impl, status_impl

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
                if include_contract:
                    console.print_json(data=st)
                else:
                    output = {
                        "session_id": sid,
                        "status": st,
                    }
                    console.print_json(data=output)
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
    harness: bool = False,
) -> None:
    settings = ThegentSettings()
    if harness:
        target = Path(settings.harness_root) / "var" / "log" / "harness.log"
        if not target.exists():
            console.print("[yellow]Harness log file not found.[/yellow]")
            return

        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in lines[-tail:]:
            console.print(line)
        return

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

    follow_log_stream(
        target=target,
        pid=pid,
        timeout=timeout,
        poll_seconds=_LOG_FOLLOW_POLL_SECONDS,
        console=console,
    )


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
    meta_path = _find_session_meta(settings, sid)
    m = _read_session_meta(meta_path)
    run_id = m.get("run_id")
    if not run_id:
        # Fallback to finding run_id from registry by correlation_id (sid)
        runs = registry.list_runs(limit=100)
        for r in runs:
            if r.get("correlation_id") == sid:
                run_id = r.get("run_id")
                break

    if not run_id:
        console.print(f"[red]Could not find run_id for session {sid}.[/red]")
        raise typer.Exit(1)

    registry.register_pause(run_id, reason="Manual pause")
    console.print(f"[yellow]Session {sid} marked as PAUSED in registry.[/yellow]")


def resume_cmd(
    session_id: str | None = None,
    prompt: str | None = None,
    skills: list[str] | None = None,
) -> None:
    """Resume a session in the registry state machine."""
    sid = _resolve_session_id(session_id)
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)

    meta_path = _find_session_meta(settings, sid)
    m = _read_session_meta(meta_path)
    run_id = m.get("run_id")
    if not run_id:
        console.print(f"[red]Could not find run_id for session {sid}.[/red]")
        raise typer.Exit(1)

    registry.register_resume(run_id)
    console.print(f"[green]Session {sid} marked as RESUMED in registry.[/green]")


def session_fork_cmd(
    session_id: str,
    from_turn: int | None = None,
    new_session_id: str | None = None,
) -> None:
    """Fork a session via SessionManager API."""
    from thegent.session import SessionManager, SessionManagerError

    session_id = session_id.strip()
    if not session_id:
        console.print("[red]Session fork failed:[/red] session_id must be non-empty")
        raise typer.Exit(2)
    if from_turn is not None and from_turn < 1:
        console.print("[red]Session fork failed:[/red] --from-turn must be >= 1 when provided")
        raise typer.Exit(2)

    if new_session_id is not None:
        cleaned_new_session_id = new_session_id.strip()
        if not cleaned_new_session_id:
            console.print("[red]Session fork failed:[/red] --new-session-id must be non-empty when provided")
            raise typer.Exit(2)
        if cleaned_new_session_id == session_id:
            console.print("[red]Session fork failed:[/red] --new-session-id must differ from source session_id")
            raise typer.Exit(2)
        new_session_id = cleaned_new_session_id

    manager = SessionManager()
    try:
        fork_id = manager.fork_session(
            session_id,
            from_turn=from_turn,
            new_session_id=new_session_id,
        )
    except SessionManagerError as exc:
        console.print(f"[red]Session fork failed:[/red] {exc}")
        raise typer.Exit(2) from exc

    console.print(f"[green]Forked session:[/green] {fork_id}")


def session_rollback_cmd(session_id: str, n_turns: int) -> None:
    """Rollback a session via SessionManager API."""
    from thegent.session import SessionManager, SessionManagerError

    session_id = session_id.strip()
    if not session_id:
        console.print("[red]Session rollback failed:[/red] session_id must be non-empty")
        raise typer.Exit(2)
    if n_turns < 1:
        console.print("[red]Session rollback failed:[/red] --n-turns must be >= 1")
        raise typer.Exit(2)

    manager = SessionManager()
    try:
        remaining = manager.rollback_session(session_id, n_turns=n_turns)
    except SessionManagerError as exc:
        console.print(f"[red]Session rollback failed:[/red] {exc}")
        raise typer.Exit(2) from exc

    console.print(f"[green]Rollback complete:[/green] {session_id} now has {remaining} turns")


def session_cmd(
    session_id: str | None = typer.Argument(None, help="Specific session ID to manage"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch session live"),
    action: str | None = typer.Option(None, "--action", "-a", help="Action to perform (stop, pause, resume, logs)"),
) -> None:
    """Rich TUI for session management with subagent monitoring (WP-8002)."""
    from thegent.ux.session_tui import SessionTUI

    tui = SessionTUI(session_id)

    if action:
        if not session_id:
            console.print("[red]Error: Session ID required for action[/red]")
            raise typer.Exit(1)
        result = tui.manage_session(session_id, action)
        if "error" in result:
            console.print(f"[red]Error:[/red] {result['error']}")
            raise typer.Exit(1)
        console.print(f"[green]✓[/green] {result['message']}")
        return

    if watch:
        tui.watch(session_id)
    else:
        tui.show(session_id)


def session_contract_negotiate_cmd(
    contract_id: str,
    supported_versions: str,
    format: str | None = None,
) -> None:
    """Negotiate a contract version (WP-7001)."""
    versions = [v.strip() for v in supported_versions.split(",") if v.strip()]
    from thegent.cli.commands.impl import session_contract_negotiate_impl

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


__all__ = [
    "deferral_list_cmd",
    "deferral_resume_cmd",
    "events_cmd",
    "feedback_cmd",
    "history_cmd",
    "inbox_list_cmd",
    "inbox_wait_cmd",
    "inspect_cmd",
    "logs_cmd",
    "pause_cmd",
    "ps_cmd",
    "resume_cmd",
    "session_cmd",
    "session_contract_health_gate_cmd",
    "session_contract_health_report_cmd",
    "session_contract_health_trend_cmd",
    "session_contract_negotiate_cmd",
    "session_contract_trend_analysis_cmd",
    "session_contracts_cmd",
    "session_fork_cmd",
    "session_rollback_cmd",
    "status_cmd",
    "stop_cmd",
    "wait_cmd",
]
