# @trace WL-051
"""WL-051: Enterprise CLI — compliance, GDPR, org hierarchy, and key rotation.

Commands:
  thegent enterprise compliance audit-export
  thegent enterprise compliance evidence list
  thegent enterprise compliance evidence purge
  thegent enterprise gdpr purge
  thegent enterprise org list / create / show
  thegent enterprise keys status / rotate
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()

app = typer.Typer(
    name="enterprise",
    help="Enterprise: compliance evidence, GDPR retention, org hierarchy, key rotation (WL-051).",
    no_args_is_help=True,
)

# -- Sub-apps ----------------------------------------------------------------

compliance_app = typer.Typer(help="SOC-2 compliance evidence and audit export.", no_args_is_help=True)
evidence_app = typer.Typer(help="Evidence store operations.", no_args_is_help=True)
gdpr_app = typer.Typer(help="GDPR data retention enforcement.", no_args_is_help=True)
org_app = typer.Typer(help="Org-level namespace management.", no_args_is_help=True)
keys_app = typer.Typer(help="API key rotation monitoring.", no_args_is_help=True)

app.add_typer(compliance_app, name="compliance")
compliance_app.add_typer(evidence_app, name="evidence")
app.add_typer(gdpr_app, name="gdpr")
app.add_typer(org_app, name="org")
app.add_typer(keys_app, name="keys")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DEFAULT_EVIDENCE_PATH = Path.home() / ".thegent" / "compliance" / "evidence.jsonl"
_DEFAULT_RETENTION_DIR = Path.home() / ".thegent" / "compliance" / "retention"
_DEFAULT_KEY_REGISTRY = Path.home() / ".thegent" / "keys" / "registry.jsonl"
_DEFAULT_ORG_REGISTRY = Path.home() / ".thegent" / "orgs" / "registry.json"


# ---------------------------------------------------------------------------
# compliance audit-export
# ---------------------------------------------------------------------------


@compliance_app.command("audit-export")
def compliance_audit_export(
    output: Path = typer.Option(..., "--output", "-o", help="Output file path"),
    format: str = typer.Option("json", "--format", "-f", help="Export format: json"),
    evidence_path: Path = typer.Option(_DEFAULT_EVIDENCE_PATH, "--evidence", help="Evidence store path"),
    since_days: int | None = typer.Option(None, "--since-days", help="Only export last N days"),
) -> None:
    """Export compliance evidence for regulators (WL-051)."""
    if format != "json":
        console.print(f"[red]Unsupported format: {format!r}. Only 'json' is supported.[/red]")
        raise typer.Exit(1)

    from thegent_audit.governance.compliance import AuditExporter, EvidenceStore

    store = EvidenceStore(evidence_path)
    exporter = AuditExporter(store)
    result = exporter.export_json(output_path=output, since_days=since_days)
    console.print(
        f"[green]Exported {result['record_count']} evidence records to {output}[/green]"
        + (f" (integrity_verified={result['integrity_verified']})" if not result["integrity_verified"] else "")
    )


# ---------------------------------------------------------------------------
# compliance evidence list
# ---------------------------------------------------------------------------


@evidence_app.command("list")
def evidence_list(
    evidence_path: Path = typer.Option(_DEFAULT_EVIDENCE_PATH, "--evidence", help="Evidence store path"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max records to show"),
) -> None:
    """List evidence records from the store (WL-051)."""
    from thegent_audit.governance.compliance import EvidenceStore

    store = EvidenceStore(evidence_path)
    records = store.list_all()
    if not records:
        console.print("[dim]No evidence records found.[/dim]")
        return

    table = Table(title=f"Evidence Store ({evidence_path})")
    table.add_column("ID", style="cyan")
    table.add_column("Kind", style="yellow")
    table.add_column("Actor")
    table.add_column("Resource")
    table.add_column("Timestamp UTC", style="dim")

    for rec in records[-limit:]:
        table.add_row(rec.evidence_id[:12], rec.kind, rec.actor, rec.resource, rec.timestamp_utc[:19])

    console.print(table)
    console.print(f"[dim]Total: {len(records)} records[/dim]")


# ---------------------------------------------------------------------------
# compliance evidence purge
# ---------------------------------------------------------------------------


@evidence_app.command("purge")
def evidence_purge(
    older_than_days: int = typer.Option(..., "--older-than-days", help="Purge records older than N days"),
    evidence_path: Path = typer.Option(_DEFAULT_EVIDENCE_PATH, "--evidence", help="Evidence store path"),
) -> None:
    """Purge evidence records older than N days (WL-051)."""
    if older_than_days < 0:
        console.print("[red]--older-than-days must be >= 0[/red]")
        raise typer.Exit(1)

    from thegent_audit.governance.compliance import EvidenceStore

    store = EvidenceStore(evidence_path)
    purged = store.purge_older_than(older_than_days)
    console.print(f"[green]Purged {purged} evidence records older than {older_than_days} days.[/green]")


# ---------------------------------------------------------------------------
# gdpr purge
# ---------------------------------------------------------------------------


@gdpr_app.command("purge")
def gdpr_purge(
    tenant: str = typer.Option(..., "--tenant", "-t", help="Tenant ID to purge data for"),
    evidence_path: Path = typer.Option(_DEFAULT_EVIDENCE_PATH, "--evidence", help="Evidence store path"),
    retention_dir: Path = typer.Option(_DEFAULT_RETENTION_DIR, "--retention-dir", help="Retention policies dir"),
) -> None:
    """Apply GDPR retention policies and purge expired data for a tenant (WL-051)."""
    from thegent_audit.governance.compliance import EvidenceStore, RetentionEnforcer

    store = EvidenceStore(evidence_path)
    enforcer = RetentionEnforcer(retention_dir)

    try:
        summary = enforcer.purge_tenant_data(tenant_id=tenant, evidence_store=store)
    except KeyError as exc:
        console.print(f"[red]No retention policies found: {exc}[/red]")
        raise typer.Exit(1) from exc
    except RuntimeError as exc:
        console.print(f"[red]Consent error: {exc}[/red]")
        raise typer.Exit(1) from exc

    console.print(f"[green]GDPR purge complete for tenant {tenant!r}:[/green]")
    for policy_id, count in summary["purged_by_policy"].items():
        console.print(f"  policy={policy_id}: {count} records purged")
    console.print(f"  total purged: {summary['total_purged']}")


# ---------------------------------------------------------------------------
# org list
# ---------------------------------------------------------------------------


@org_app.command("list")
def org_list_cmd(
    org_registry: Path = typer.Option(_DEFAULT_ORG_REGISTRY, "--registry", help="Org registry path"),
) -> None:
    """List all org namespaces (WL-051)."""
    from thegent_core.infra.org_tenancy import OrgRegistry

    registry = OrgRegistry(org_registry)
    orgs = registry.list_orgs()

    if not orgs:
        console.print("[dim]No org namespaces registered.[/dim]")
        return

    table = Table(title="Org Namespaces")
    table.add_column("Org ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Tenants")
    table.add_column("Created")

    for org in orgs:
        table.add_row(
            org.org_id,
            org.org_name,
            ", ".join(org.tenants) if org.tenants else "[dim]none[/dim]",
            org.created_at[:10],
        )

    console.print(table)


# ---------------------------------------------------------------------------
# org create
# ---------------------------------------------------------------------------


@org_app.command("create")
def org_create_cmd(
    name: str = typer.Argument(..., help="Org name"),
    org_registry: Path = typer.Option(_DEFAULT_ORG_REGISTRY, "--registry", help="Org registry path"),
    initial_tenants: list[str] | None = typer.Option(None, "--tenant", help="Initial tenant IDs"),
) -> None:
    """Create a new org namespace (WL-051)."""
    from thegent_core.infra.org_tenancy import OrgRegistry

    registry = OrgRegistry(org_registry)
    try:
        org = registry.create_org(org_name=name, initial_tenants=initial_tenants)
    except ValueError as exc:
        console.print(f"[red]Error: {exc}[/red]")
        raise typer.Exit(1) from exc

    console.print(f"[green]Org created:[/green] {org.org_id} ({org.org_name})")


# ---------------------------------------------------------------------------
# org show
# ---------------------------------------------------------------------------


@org_app.command("show")
def org_show_cmd(
    org_id: str = typer.Argument(..., help="Org ID to display"),
    org_registry: Path = typer.Option(_DEFAULT_ORG_REGISTRY, "--registry", help="Org registry path"),
) -> None:
    """Show details for an org namespace (WL-051)."""
    from thegent_core.infra.org_tenancy import OrgRegistry

    registry = OrgRegistry(org_registry)
    try:
        org = registry.get_org(org_id=org_id)
    except KeyError as exc:
        console.print(f"[red]Not found: {exc}[/red]")
        raise typer.Exit(1) from exc

    console.print(f"[bold]Org ID:[/bold]   {org.org_id}")
    console.print(f"[bold]Name:[/bold]     {org.org_name}")
    console.print(f"[bold]Tenants:[/bold]  {', '.join(org.tenants) if org.tenants else '(none)'}")
    console.print(f"[bold]Created:[/bold]  {org.created_at}")
    console.print(f"[bold]Updated:[/bold]  {org.updated_at}")


# ---------------------------------------------------------------------------
# keys status
# ---------------------------------------------------------------------------


@keys_app.command("status")
def keys_status(
    key_registry: Path = typer.Option(_DEFAULT_KEY_REGISTRY, "--registry", help="Key registry path"),
    warn_days: int = typer.Option(7, "--warn-days", help="Warn threshold in days"),
) -> None:
    """Show API key expiry status (WL-051)."""
    from thegent_audit.governance.key_rotation import KeyRegistry, KeyRotationMonitor

    registry = KeyRegistry(key_registry)
    monitor = KeyRotationMonitor(registry, warn_days=warn_days)
    all_keys = registry.list_all()

    if not all_keys:
        console.print("[dim]No API keys registered.[/dim]")
        return

    warnings = {w.record.key_id for w in monitor.check_all()}

    table = Table(title="API Key Status")
    table.add_column("Key ID", style="cyan")
    table.add_column("Provider")
    table.add_column("Expires At")
    table.add_column("Days Left")
    table.add_column("Status")

    for rec in all_keys:
        days = rec.days_until_expiry()
        status = (
            "[red]EXPIRED[/red]"
            if rec.is_expired()
            else ("[yellow]EXPIRING[/yellow]" if rec.key_id in warnings else "[green]OK[/green]")
        )
        table.add_row(
            rec.key_id,
            rec.provider,
            rec.expires_at[:10],
            f"{days:.1f}",
            status,
        )

    console.print(table)


# ---------------------------------------------------------------------------
# keys rotate
# ---------------------------------------------------------------------------


@keys_app.command("rotate")
def keys_rotate(
    provider: str = typer.Argument(..., help="Provider name to rotate keys for"),
    new_expires_at: str = typer.Option(..., "--new-expires-at", help="New expiry ISO-8601 datetime"),
    webhook_url: str = typer.Option(..., "--webhook-url", help="Webhook URL for rotation events"),
    key_registry: Path = typer.Option(_DEFAULT_KEY_REGISTRY, "--registry", help="Key registry path"),
) -> None:
    """Rotate all API keys for a provider and notify via webhook (WL-051)."""
    from thegent_audit.governance.key_rotation import KeyRegistry, KeyRotationWebhook

    registry = KeyRegistry(key_registry)
    webhook = KeyRotationWebhook(webhook_url, registry)
    keys_for_provider = [r for r in registry.list_all() if r.provider == provider]

    if not keys_for_provider:
        console.print(f"[yellow]No keys registered for provider: {provider!r}[/yellow]")
        raise typer.Exit(1)

    for rec in keys_for_provider:
        result = webhook.rotate(key_id=rec.key_id, new_expires_at=new_expires_at)
        console.print(f"[green]Rotated:[/green] {rec.key_id} (status={result['status_code']})")
