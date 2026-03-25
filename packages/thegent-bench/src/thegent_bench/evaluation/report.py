"""
Evaluation Report

Generates reports from evaluation results.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import json


@dataclass
class ReportConfig:
    """Report configuration."""

    include_details: bool = True
    include_metrics: bool = True
    format: str = "json"  # json, markdown, html


class EvaluationReport:
    """Generates evaluation reports."""

    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()
        self._sections: list[dict] = []

    def add_section(self, title: str, content: dict) -> None:
        """Add a section to the report."""
        self._sections.append({"title": title, "content": content})

    def add_summary(self, results: list) -> None:
        """Add results summary."""
        if not results:
            return

        success_rate = sum(1 for r in results if r.success) / len(results)
        avg_score = sum(r.score for r in results) / len(results)
        avg_duration = sum(r.duration for r in results) / len(results)

        self.add_section(
            "Summary",
            {
                "total_tasks": len(results),
                "success_rate": f"{success_rate:.1%}",
                "average_score": f"{avg_score:.2f}",
                "average_duration": f"{avg_duration:.2f}s",
            },
        )

    def add_breakdown(self, results: list) -> None:
        """Add breakdown by task type."""
        breakdown = {}

        for result in results:
            task_type = result.task_type
            if task_type not in breakdown:
                breakdown[task_type] = {"count": 0, "success": 0, "total_score": 0}

            breakdown[task_type]["count"] += 1
            if result.success:
                breakdown[task_type]["success"] += 1
            breakdown[task_type]["total_score"] += result.score

        summary = {}
        for task_type, stats in breakdown.items():
            summary[task_type] = {
                "count": stats["count"],
                "success_rate": stats["success"] / stats["count"],
                "avg_score": stats["total_score"] / stats["count"],
            }

        self.add_section("Breakdown by Task Type", summary)

    def add_metrics(self, metrics_summary: dict) -> None:
        """Add metrics section."""
        if not self.config.include_metrics:
            return

        self.add_section("Metrics", metrics_summary)

    def generate(self) -> dict:
        """Generate the report."""
        return {"generated_at": datetime.now().isoformat(), "sections": self._sections}

    def to_json(self) -> str:
        """Export as JSON."""
        return json.dumps(self.generate(), indent=2)

    def to_markdown(self) -> str:
        """Export as Markdown."""
        lines = ["# Evaluation Report", ""]

        for section in self._sections:
            lines.append(f"## {section['title']}")
            lines.append("")

            content = section["content"]
            if isinstance(content, dict):
                for key, value in content.items():
                    if isinstance(value, dict):
                        lines.append(f"### {key}")
                        for k, v in value.items():
                            lines.append(f"- **{k}**: {v}")
                        lines.append("")
                    else:
                        lines.append(f"- **{key}**: {value}")
            else:
                lines.append(str(content))

            lines.append("")

        return "\n".join(lines)

    def save(self, filepath: str) -> None:
        """Save report to file."""
        content = self.to_json() if self.config.format == "json" else self.to_markdown()
        with open(filepath, "w") as f:
            f.write(content)
