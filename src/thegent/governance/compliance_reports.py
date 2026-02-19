"""Automated compliance reporting."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ComplianceReporter:
    """Generate automated compliance reports."""

    def __init__(self):
        """Initialize compliance reporter."""
        self.reports: list[dict[str, Any]] = []

    def generate_report(
        self,
        compliance_data: dict[str, Any],
        format: str = "json",
    ) -> str:
        """Generate compliance report.
        
        Args:
            compliance_data: Compliance data dictionary
            format: Report format (json, markdown, html)
            
        Returns:
            Report content as string
        """
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "compliance": compliance_data,
        }
        
        if format == "json":
            return json.dumps(report, indent=2)
        elif format == "markdown":
            return self._generate_markdown(report)
        elif format == "html":
            return self._generate_html(report)
        else:
            return json.dumps(report, indent=2)

    def _generate_markdown(self, report: dict[str, Any]) -> str:
        """Generate markdown report.
        
        Args:
            report: Report dictionary
            
        Returns:
            Markdown string
        """
        lines = ["# Compliance Report", ""]
        lines.append(f"**Generated**: {report['timestamp']}")
        lines.append("")
        lines.append("## Compliance Status")
        lines.append("")
        
        compliance = report.get("compliance", {})
        for key, value in compliance.items():
            lines.append(f"- **{key}**: {value}")
        
        return "\n".join(lines)

    def _generate_html(self, report: dict[str, Any]) -> str:
        """Generate HTML report.
        
        Args:
            report: Report dictionary
            
        Returns:
            HTML string
        """
        html = ["<html><head><title>Compliance Report</title></head><body>"]
        html.append("<h1>Compliance Report</h1>")
        html.append(f"<p><strong>Generated</strong>: {report['timestamp']}</p>")
        html.append("<h2>Compliance Status</h2>")
        html.append("<ul>")
        
        compliance = report.get("compliance", {})
        for key, value in compliance.items():
            html.append(f"<li><strong>{key}</strong>: {value}</li>")
        
        html.append("</ul></body></html>")
        return "\n".join(html)

    def export_report(
        self,
        compliance_data: dict[str, Any],
        output_path: Path,
        format: str = "json",
    ) -> Path:
        """Export compliance report to file.
        
        Args:
            compliance_data: Compliance data
            output_path: Output file path
            format: Report format
            
        Returns:
            Path to exported file
        """
        content = self.generate_report(compliance_data, format)
        output_path.write_text(content)
        logger.info(f"Exported compliance report: {output_path}")
        return output_path
