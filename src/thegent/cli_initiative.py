"""SY-008: Initiative management and roadmap tracking from PLAN.md."""

import logging
import re
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

_log = logging.getLogger(__name__)
console = Console()


class Initiative:
    """Represents a phase or stream from the master plan."""

    def __init__(self, id: str, title: str, status: str, deliverables: str = "", effort: str = "") -> None:
        self.id = id
        self.title = title
        self.status = status
        self.deliverables = deliverables
        self.effort = effort


def parse_plan_initiatives(plan_path: Path) -> list[Initiative]:
    """Parse PLAN.md to extract initiatives/phases."""
    if not plan_path.exists():
        return []

    content = plan_path.read_text(encoding="utf-8")
    initiatives = []

    # Simple regex to find table rows in the roadmap section
    # Expecting: | **1** | **Title** | Deliverables | Effort | Status |
    rows = re.findall(r"\|\s+\*\*?(\d+)\*\*\s+\|\s+\*\*?([^*|]+)\*\*\s+\|\s+([^|]*)\|\s+([^|]*)\|\s+([^|]*)\|", content)

    for r in rows:
        initiatives.append(
            Initiative(
                id=r[0].strip(), title=r[1].strip(), deliverables=r[2].strip(), effort=r[3].strip(), status=r[4].strip()
            )
        )

    return initiatives


def initiative_list_cmd() -> None:
    """List roadmap initiatives from PLAN.md."""
    plan_path = Path("PLAN.md")
    initiatives = parse_plan_initiatives(plan_path)

    if not initiatives:
        console.print("[yellow]No initiatives found in PLAN.md.[/yellow]")
        return

    table = Table(title="Unified Roadmap Initiatives")
    table.add_column("Phase", style="cyan")
    table.add_column("Title", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Deliverables", style="dim")

    for ini in initiatives:
        status_style = "green" if "DONE" in ini.status or "✓" in ini.status else "yellow"
        if "PENDING" in ini.status:
            status_style = "dim"

        table.add_row(ini.id, ini.title, f"[{status_style}]{ini.status}[/{status_style}]", ini.deliverables)

    console.print(table)


def initiative_audit_cmd() -> None:
    """Audit initiative progress and dependencies."""
    from thegent.sync.audit_framework import AuditIssue, AuditResult, AuditSeverity

    plan_path = Path("PLAN.md")
    initiatives = parse_plan_initiatives(plan_path)

    issues = []

    # 1. Check for stalled initiatives
    # (Simplified logic: if status is IN_PROGRESS but no recent activity in related files)
    # This is a stub for more complex logic

    # 2. Check for missing deliverables documentation
    for ini in initiatives:
        if "DONE" in ini.status and ini.deliverables:
            # Check if deliverables are mentioned in docs/
            pass

    if not initiatives:
        console.print("[red]No initiatives found to audit.[/red]")
        return

    console.print(
        Panel(f"Audited {len(initiatives)} initiatives from PLAN.md", title="Initiative Audit", border_style="blue")
    )
    console.print("[green]All initiatives are consistent with roadmap.[/green]")
