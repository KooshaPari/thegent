"""
Comprehensive Reporting and Visualization System

Generates reports, dashboards, and visualizations for governance data.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.tree import Tree

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class ReportFormat(Enum):
    """Report formats."""

    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    HTML = "html"
    CONSOLE = "console"


@dataclass
class GovernanceReport:
    """Comprehensive governance report."""

    project_path: Path
    generated_at: datetime
    project_structure: dict[str, Any] = field(default_factory=dict)
    quality_matrix: dict[str, Any] = field(default_factory=dict)
    audit_results: dict[str, Any] = field(default_factory=dict)
    task_summary: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "project_path": str(self.project_path),
            "generated_at": self.generated_at.isoformat(),
            "project_structure": self.project_structure,
            "quality_matrix": self.quality_matrix,
            "audit_results": self.audit_results,
            "task_summary": self.task_summary,
            "recommendations": self.recommendations,
            "next_actions": self.next_actions,
        }

    def to_markdown(self) -> str:
        """Convert to markdown."""
        md = f"""# Governance Report

**Project:** {self.project_path.name}
**Generated:** {self.generated_at.strftime("%Y-%m-%d %H:%M:%S")}

## Project Structure

"""
        if self.project_structure:
            md += f"- **Governance Level:** {self.project_structure.get('governance_level', 'unknown')}\n"
            md += f"- **Score:** {self.project_structure.get('score', 0)}/200\n"
            md += f"- **Missing Items:** {len(self.project_structure.get('missing_items', []))}\n"

        md += "\n## Quality Matrix\n\n"
        if self.quality_matrix:
            md += f"- **Overall Score:** {self.quality_matrix.get('overall_score', 0):.1f}/100\n"
            md += f"- **Quality Level:** {self.quality_matrix.get('quality_level', 'unknown')}\n"

        md += "\n## Audit Results\n\n"
        if self.audit_results:
            md += f"- **Total Findings:** {self.audit_results.get('total_findings', 0)}\n"
            md += f"- **Critical Findings:** {self.audit_results.get('critical_findings', 0)}\n"

        md += "\n## Recommendations\n\n"
        for rec in self.recommendations:
            md += f"- {rec}\n"

        md += "\n## Next Actions\n\n"
        for action in self.next_actions:
            md += f"- {action}\n"

        return md


class ReportGenerator:
    """Generates comprehensive reports."""

    def __init__(self, project_path: Path) -> None:
        self.project_path = Path(project_path)
        self.console = Console() if RICH_AVAILABLE else None

    def generate_comprehensive_report(
        self,
        structure_data: dict | None = None,
        quality_matrix: dict | None = None,
        audit_results: dict | None = None,
        task_summary: dict | None = None,
    ) -> GovernanceReport:
        """Generate comprehensive governance report."""

        report = GovernanceReport(
            project_path=self.project_path,
            generated_at=datetime.now(),
            project_structure=structure_data or {},
            quality_matrix=quality_matrix or {},
            audit_results=audit_results or {},
            task_summary=task_summary or {},
        )

        # Generate recommendations
        report.recommendations = self._generate_recommendations(structure_data, quality_matrix, audit_results)

        # Generate next actions
        report.next_actions = self._generate_next_actions(structure_data, quality_matrix, audit_results, task_summary)

        return report

    def _generate_recommendations(
        self,
        structure: dict | None,
        quality: dict | None,
        audit: dict | None,
    ) -> list[str]:
        """Generate recommendations."""
        recommendations = []

        if structure:
            score = structure.get("score", 0)
            if score < 80:
                recommendations.append("Improve project structure score")

            missing = structure.get("missing_items", [])
            if missing:
                recommendations.append(f"Add missing items: {', '.join(missing[:5])}")

        if quality:
            overall_score = quality.get("overall_score", 0)
            if overall_score < 75:
                recommendations.append("Improve overall quality score")

            failing_categories = [
                cat["name"] for cat in quality.get("categories", []) if cat.get("status") == "failing"
            ]
            if failing_categories:
                recommendations.append(f"Address failing categories: {', '.join(failing_categories)}")

        if audit:
            critical = audit.get("critical_findings", 0)
            if critical > 0:
                recommendations.append(f"Address {critical} critical audit findings")

        return recommendations

    def _generate_next_actions(
        self,
        structure: dict | None,
        quality: dict | None,
        audit: dict | None,
        tasks: dict | None,
    ) -> list[str]:
        """Generate next actions."""
        actions = []

        if tasks:
            ready = tasks.get("ready_tasks", 0)
            if ready > 0:
                actions.append(f"Start {ready} ready tasks")

            overdue = tasks.get("overdue_tasks", 0)
            if overdue > 0:
                actions.append(f"Address {overdue} overdue tasks")

        if audit:
            critical = audit.get("critical_findings", 0)
            if critical > 0:
                actions.append("Review critical audit findings")

        if structure:
            if structure.get("score", 0) < 100:
                actions.append("Set up basic project structure")

        return actions

    def print_console_report(self, report: GovernanceReport):
        """Print report to console using rich."""
        if not self.console:
            return

        self.console.print(
            Panel.fit(
                f"[bold cyan]{report.project_path.name}[/bold cyan]\n"
                f"Governance Report - {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
                border_style="cyan",
            )
        )

        # Project Structure
        if report.project_structure:
            structure_table = Table(title="Project Structure")
            structure_table.add_column("Metric", style="cyan")
            structure_table.add_column("Value", style="green")

            structure_table.add_row("Governance Level", report.project_structure.get("governance_level", "unknown"))
            structure_table.add_row("Score", f"{report.project_structure.get('score', 0)}/200")
            structure_table.add_row("Missing Items", str(len(report.project_structure.get("missing_items", []))))

            self.console.print(structure_table)

        # Quality Matrix
        if report.quality_matrix:
            quality_table = Table(title="Quality Matrix")
            quality_table.add_column("Category", style="cyan")
            quality_table.add_column("Score", style="green")
            quality_table.add_column("Status", style="yellow")

            for cat in report.quality_matrix.get("categories", []):
                status_style = {"passing": "green", "warning": "yellow", "failing": "red"}.get(
                    cat.get("status", "pending"), "white"
                )

                quality_table.add_row(
                    cat.get("name", "Unknown"),
                    f"{cat.get('score', 0):.1f}",
                    f"[{status_style}]{cat.get('status', 'pending')}[/{status_style}]",
                )

            self.console.print(quality_table)

        # Recommendations
        if report.recommendations:
            self.console.print("\n[bold yellow]Recommendations:[/bold yellow]")
            for rec in report.recommendations:
                self.console.print(f"  • {rec}")

        # Next Actions
        if report.next_actions:
            self.console.print("\n[bold green]Next Actions:[/bold green]")
            for action in report.next_actions:
                self.console.print(f"  • {action}")

    def save_report(self, report: GovernanceReport, output_path: Path, format: ReportFormat = ReportFormat.JSON):
        """Save report to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == ReportFormat.JSON:
            with open(output_path, "w") as f:
                json.dump(report.to_dict(), f, indent=2)
        elif format == ReportFormat.YAML:
            with open(output_path, "w") as f:
                yaml.dump(report.to_dict(), f, default_flow_style=False)
        elif format == ReportFormat.MARKDOWN:
            with open(output_path, "w") as f:
                f.write(report.to_markdown())
        elif format == ReportFormat.HTML:
            # Convert markdown to HTML (simplified)
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Governance Report - {report.project_path.name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; margin-top: 30px; }}
        ul {{ line-height: 1.6; }}
    </style>
</head>
<body>
{report.to_markdown().replace(chr(10), "<br>")}
</body>
</html>
"""
            with open(output_path, "w") as f:
                f.write(html)
