"""SY-007: Unified CLI commands for sync, update, and audit."""

import logging
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from thegent.sync.audit_framework import AuditResult, AuditSeverity, SystemAuditFramework
from thegent.sync.orchestrator import SyncOrchestrator, SyncResult, SyncStatus

_log = logging.getLogger(__name__)
console = Console()


async def sync_cmd_impl(
    components: list[str] | None = None,
    force: bool = False,
    dry_run: bool = False,
    watch: bool = False,
    interval: int = 10,
    output: Path | None = None,
    format: str = "rich",
) -> None:
    """Implementation for the unified sync command."""
    orchestrator = SyncOrchestrator()

    if watch:
        import asyncio

        console.print(f"[bold cyan]Starting watch mode (interval: {interval}s)...[/bold cyan]")
        try:
            while True:
                results = await orchestrator.sync_all(components, dry_run=dry_run, force=force)
                _display_sync_results(results, format)
                await asyncio.sleep(interval)
        except KeyboardInterrupt:
            console.print("[yellow]Watch mode stopped.[/yellow]")
            return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Syncing components...", total=None)
        results = await orchestrator.sync_all(components, dry_run=dry_run, force=force)

    _display_sync_results(results, format)

    if output:
        _save_sync_report(results, output)


async def update_cmd_impl(
    components: list[str] | None = None,
    check: bool = False,
    force: bool = False,
    dry_run: bool = False,
    output: Path | None = None,
) -> None:
    """Implementation for the unified update command."""
    orchestrator = SyncOrchestrator()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Updating components...", total=None)
        results = await orchestrator.update_all(components, dry_run=dry_run, force=force)

    _display_sync_results(results, "rich", title="Update Results")

    if output:
        _save_sync_report(results, output)


async def audit_cmd_impl(
    audit_types: list[str] | None = None,
    output: Path | None = None,
    format: str = "rich",
    fix: bool = False,
    severity: str = "all",
) -> None:
    """Implementation for the system audit command."""
    orchestrator = SystemAuditFramework()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Running system audit...", total=None)
        result = await orchestrator.run_audit(audit_types, fix=fix)

    _display_audit_results(result, format, severity)

    if output:
        _save_audit_report(result, output)


def _display_sync_results(results: list[SyncResult], format: str, title: str = "Sync Results") -> None:
    """Display sync results in the specified format."""
    if format == "rich":
        table = Table(title=title)
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Duration", justify="right")
        table.add_column("Message")

        for r in results:
            status = "[green]SUCCESS[/green]" if r.status == SyncStatus.SUCCESS else "[red]FAILED[/red]"
            table.add_row(
                r.component,
                status,
                f"{r.duration:.2f}s",
                r.message,
            )

        console.print(table)
    elif format == "json":
        import json

        console.print(json.dumps([r.to_dict() for r in results], indent=2))


def _display_audit_results(result: AuditResult, format: str, severity_filter: str) -> None:
    """Display audit results in the specified format."""
    issues = result.issues
    if severity_filter != "all":
        issues = [i for i in issues if i.severity == severity_filter]

    if format == "rich":
        console.print(
            Panel(
                f"Audit Summary: {result.summary['total_issues']} issues found in {result.summary['duration']:.2f}s",
                title="System Audit",
                border_style="blue",
            )
        )

        if not issues:
            console.print("[green]No issues found.[/green]")
            return

        table = Table(title="Audit Issues")
        table.add_column("ID", style="dim")
        table.add_column("Component", style="cyan")
        table.add_column("Severity", style="bold")
        table.add_column("Title")
        table.add_column("Remediation")

        for i in issues:
            sev_color = {
                AuditSeverity.CRITICAL: "red",
                AuditSeverity.HIGH: "magenta",
                AuditSeverity.MEDIUM: "yellow",
                AuditSeverity.LOW: "blue",
            }.get(i.severity, "white")

            table.add_row(
                i.id,
                i.component,
                f"[{sev_color}]{i.severity.upper()}[/{sev_color}]",
                i.title,
                i.remediation or "N/A",
            )

        console.print(table)
    elif format == "json":
        import json

        console.print(json.dumps(result.to_dict(), indent=2))


def _save_sync_report(results: list[SyncResult], path: Path) -> None:
    """Save sync results to a file."""
    import json

    path.write_text(json.dumps([r.to_dict() for r in results], indent=2))
    console.print(f"[dim]Sync report saved to {path}[/dim]")


def _save_audit_report(result: AuditResult, path: Path) -> None:
    """Save audit result to a file."""
    import json

    path.write_text(json.dumps(result.to_dict(), indent=2))
    console.print(f"[dim]Audit report saved to {path}[/dim]")
