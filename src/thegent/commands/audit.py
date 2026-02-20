"""CLI command: thegent audit [--json] [--fix]

Runs the system audit framework and reports drift between declared
configuration and actual on-disk state.
"""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING, Annotated, Optional

import typer

if TYPE_CHECKING:
    from pathlib import Path

app = typer.Typer(help="System audit: detect drift between declared config and actual state.")


@app.callback(invoke_without_command=True)
def audit_cmd(
    ctx: typer.Context,
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Output audit report as JSON."),
    ] = False,
    fix: Annotated[
        bool,
        typer.Option("--fix", help="Print fix suggestions for all issues found."),
    ] = False,
    category: Annotated[
        str | None,
        typer.Option(
            "--category",
            "-c",
            help="Restrict audit to one category: hooks|agents|config|dependencies",
        ),
    ] = None,
    out_file: Annotated[
        Path | None,
        typer.Option("--out", "-o", help="Write JSON report to this file path."),
    ] = None,
) -> None:
    """Run the system audit and detect drift between declared config and actual state.

    Categories audited by default:
    - hooks: hook-config.yaml registrations vs .sh files on disk
    - agents: agent .md persona files vs registry
    - config: ThegentSettings fields vs THGENT_* environment variables
    - dependencies: pyproject.toml deps vs installed packages

    Examples::

        thegent audit
        thegent audit --json
        thegent audit --category hooks
        thegent audit --fix
        thegent audit --json --out report.json
    """
    if ctx.invoked_subcommand is not None:
        return

    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    from thegent.audit.system_audit import AuditReport, AuditStatus, SystemAuditor

    console = Console()
    auditor = SystemAuditor()

    # Run selected category or full audit
    report: AuditReport
    if category:
        category = category.lower().strip()
        dispatch = {
            "hooks": auditor.audit_hooks,
            "agents": auditor.audit_agents,
            "config": auditor.audit_config,
            "dependencies": auditor.audit_dependencies,
        }
        if category not in dispatch:
            console.print(f"[red]Unknown category '{category}'. Choose from: hooks, agents, config, dependencies[/red]")
            raise typer.Exit(1)
        from datetime import UTC, datetime

        from thegent.audit.system_audit import AuditReport

        report = AuditReport(timestamp=datetime.now(UTC).isoformat())
        report.add_results(dispatch[category]())
    else:
        report = auditor.run_full_audit()

    # JSON output path
    if out_file:
        auditor.export_json(report, out_file)
        if not output_json:
            console.print(f"[green]Report written to {out_file}[/green]")

    # Machine-readable JSON to stdout
    if output_json:
        sys.stdout.write(json.dumps(report.to_dict(), indent=2, default=str) + "\n")
        raise typer.Exit(0 if not report.has_drift else 1)

    # Human-readable rich output
    summary = report.summary
    total = summary.get("total", 0)
    ok_count = summary.get("ok", 0)
    issue_count = total - ok_count

    # Build summary table
    table = Table(title="System Audit Summary", show_lines=True)
    table.add_column("Category", style="cyan")
    table.add_column("Item", style="white")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="dim")

    status_styles = {
        AuditStatus.OK: "green",
        AuditStatus.DRIFT: "yellow",
        AuditStatus.MISSING: "red",
        AuditStatus.UNEXPECTED: "magenta",
        AuditStatus.ERROR: "red bold",
        AuditStatus.WARN: "yellow",
    }

    for r in report.results:
        if r.status == AuditStatus.OK and not fix:
            continue  # suppress OK rows for readability unless --fix
        style = status_styles.get(r.status, "white")
        detail = r.actual if r.status != AuditStatus.OK else ""
        if fix and r.fix_suggestion:
            detail = f"{r.actual}\n[italic]Fix: {r.fix_suggestion}[/italic]"
        table.add_row(
            r.category,
            r.item,
            f"[{style}]{r.status.value.upper()}[/{style}]",
            detail,
        )

    if table.row_count == 0 and not report.has_drift:
        console.print(
            Panel(
                f"[green]All {total} checks passed. No drift detected.[/green]",
                title="System Audit",
                border_style="green",
            )
        )
    else:
        console.print(table)
        console.print(f"\n[bold]Total:[/bold] {total}  [green]OK: {ok_count}[/green]  [red]Issues: {issue_count}[/red]")
        for status in AuditStatus:
            count = summary.get(status.value, 0)
            if count and status != AuditStatus.OK:
                style = status_styles.get(status, "white")
                console.print(f"  [{style}]{status.value.upper()}: {count}[/{style}]")

    raise typer.Exit(0 if not report.has_drift else 1)
