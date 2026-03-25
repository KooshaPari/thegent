"""Thegent CLI session commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import orjson as json
import sys
from pathlib import Path

import typer

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
from thegent.cli.commands.session_cmds_helpers import (
    resolve_export_format_with_notice,
)


"""Session contract management commands.

Commands for viewing and managing session contracts.
Extracted from session_cmds.py to manage module size.
"""

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
        sys.stdout.write(json.dumps(result).decode() + "\n")
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
        sys.stdout.write(json.dumps(result).decode() + "\n")
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
            console.print(f"generated_query={json.dumps(result['generated_query']).decode()}")
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
        sys.stdout.write(json.dumps(result).decode() + "\n")
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
        console.print(f"scope_key={json.dumps(result['scope_key']).decode()}")
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




__all__ = [
    "session_contract_health_gate_cmd",
    "session_contract_health_report_cmd",
    "session_contract_health_trend_cmd",
]
