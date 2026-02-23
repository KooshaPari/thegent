"""Thegent CLI governance audit, compliance, and data protection commands.

Extracted from governance_cmds.py as part of CLI refactoring (WL-124).
"""

from __future__ import annotations

import hashlib
import json
import sys
import uuid
from pathlib import Path

import typer
from rich.table import Table

from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    _load_artifact,
    _normalize_output_format,
    console,
)


def data_protection_cmd(format: str | None = None) -> None:
    """Show status of data protection and privacy controls."""
    from thegent.cli.commands.observability_main_impl import get_data_protection_status_impl  # pyright: ignore[reportMissingImports]

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
    from thegent.cli.commands.observability_main_impl import get_compliance_report_impl  # pyright: ignore[reportMissingImports]

    report = get_compliance_report_impl()
    fmt = _normalize_output_format(format)

    if fmt == "json":
        out = json.dumps(report, indent=2)
    else:
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
        lines.extend([
            "",
            "## Data Protection",
            f"- Session dir: {dp['session_dir']}",
            f"- Permissions restricted: {dp['permissions_restricted']}",
            f"- Masking enabled: {dp['masking_enabled']}",
        ])
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

    registry_path = settings.session_dir / "run_registry.jsonl"
    auditor = Auditor(registry_path)

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
        total = res["valid_count"]
        if total > 0:
            console.print(f"[dim]Note: All {total} records carry valid signatures.[/dim]")


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
        console.print("[green]SIEM test event pushed successfully (simulated).[/green]")
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
    from thegent.governance.support import SupportRedactor

    redactor = SupportRedactor()
    redacted = redactor.redact_text(text)

    console.print("[bold]Original:[/bold]")
    console.print(text)
    console.print("\n[bold]Redacted:[/bold]")
    console.print(redacted)


def signatures_list_cmd(limit: int = 50, format: str | None = None) -> None:
    """List signed MAIF artifacts (WP-3002)."""
    settings = ThegentSettings()
    artifacts_dir = settings.session_dir / "artifacts"

    artifacts = []
    if artifacts_dir.exists():
        for p in sorted(artifacts_dir.glob("maif.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
            _load_artifact(artifacts, p)

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

        all_blocks_valid = True
        for block in blocks:
            payload = block.get("payload")
            body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            actual_hash = hashlib.sha256(body.encode()).hexdigest()

            if actual_hash != block.get("payload_hash"):
                console.print(f"  [red]✗ Block {block.get('block_id')} payload hash mismatch![/red]")
                all_blocks_valid = False
            else:
                console.print(f"  [green]✓ Block {block.get('block_id')} verified.[/green]")

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

        root_valid = False
        if chain and chain[-1] == header.get("root_hash"):
            root_valid = True
            console.print(f"  [green]✓ Root hash {header.get('root_hash')[:12]}... matches chain.[/green]")
        else:
            console.print("  [red]✗ Root hash mismatch![/red]")

        if all_blocks_valid and chain_valid and root_valid:
            console.print(f"\n[bold green]RESULT: Artifact for {run_id} is VALID.[/bold green]")
        else:
            console.print(f"\n[bold red]RESULT: Artifact for {run_id} is INVALID.[/bold red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Failed to verify artifact: {e}[/red]")
        raise typer.Exit(1)


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


__all__ = [
    "audit_verify_cmd",
    "compliance_plugin_check_cmd",
    "compliance_redact_cmd",
    "compliance_report_cmd",
    "compliance_siem_test_cmd",
    "data_protection_cmd",
    "signatures_list_cmd",
    "signatures_verify_cmd",
    "trust_status_cmd",
]
