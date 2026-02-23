"""Thegent CLI session contract commands (from session_cmds.py)."""

from __future__ import annotations

import orjson as json
import sys
from pathlib import Path

import typer
from rich.table import Table

from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    _coerce_issue_types,
    _default_owner_tag,
    _normalize_output_format,
    _safe_dict,
    _serialize_health_gate_md,
    _serialize_health_report_md,
    _serialize_health_trend_md,
    _write_health_gate_export,
    _write_health_trend_export,
    _write_report_export,
    console,
    EXIT_HEALTH_GATE_FAILED,
)
from thegent.cli.commands.session_cmds_helpers import resolve_export_format_with_notice

__all__ = [
    "inbox_list_cmd",
    "inbox_wait_cmd",
    "session_contract_health_gate_cmd",
    "session_contract_health_report_cmd",
    "session_contract_health_trend_cmd",
    "session_contract_negotiate_cmd",
    "session_contract_trend_analysis_cmd",
    "session_contracts_cmd",
]


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
        sys.stdout.write(json.dumps(audit).decode().decode() + "\n")
        return
    if fmt == "md":
        if summary_only:
            console.print(f"summary: {json.dumps(summary).decode().decode()}")
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
        sys.stdout.write(json.dumps(result).decode().decode() + "\n")
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
        sys.stdout.write(json.dumps(result).decode().decode() + "\n")
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
            console.print(f"generated_query={json.dumps(result['generated_query']).decode().decode()}")
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
        sys.stdout.write(json.dumps(result).decode().decode() + "\n")
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
        console.print(f"scope_key={json.dumps(result['scope_key']).decode().decode()}")
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
        console.print(json.dumps(res, indent=2).decode().decode())
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
    from thegent.cli.commands.session_cmds_helpers import parse_sources_csv

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
    _owner: str | None = None,
    _agent: str | None = None,
    _event_type: str | None = None,
    _status: str | None = None,
    _sources: str | None = None,
    _poll: float = 2.0,
    _timeout: float = 0.0,
    _notify: bool = True,
    format: str | None = None,
) -> None:
    """Wait for next inbox event matching filters. Blocks until new event or timeout."""
    from thegent.cli.commands.impl import inbox_wait_impl
    from thegent.cli.commands.session_cmds_helpers import parse_sources_csv

    _src_tuple = parse_sources_csv(_sources)
    events_result = inbox_wait_impl(
        timeout=int(_timeout) if _timeout else None,
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
