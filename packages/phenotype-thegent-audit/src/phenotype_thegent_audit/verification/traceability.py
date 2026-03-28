"""WP-25003: Automated Spec-to-Code Traceability.
Scans source code and tests for FR-ID and WP-ID tags to ensure spec adherence.
Provides a coverage report mapping requirements to implementation artifacts.
"""

import logging
import re
from pathlib import Path

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class TraceabilityReport(BaseModel):
    """Result of a traceability audit."""

    implemented_ids: list[str]
    missing_ids: list[str]
    coverage_pct: float
    files_scanned: int


class TraceabilityAuditor:
    """Audits code and specs for traceability links."""

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        # Patterns for finding IDs in comments or docstrings
        self.id_patterns = [
            r"WP-\d+",  # Work Package IDs
            r"FR-\d+",  # Functional Requirement IDs
            r"MTSP-\d+",  # Master Plan IDs
        ]

    def audit(self, expected_ids: list[str]) -> TraceabilityReport:
        """Scan the project for implementation of expected IDs."""
        _log.info("Starting traceability audit for %d expected IDs", len(expected_ids))

        found_ids: set[str] = set()
        files_scanned = 0

        # Scan src and tests
        for path in self.root_dir.rglob("*.py"):
            files_scanned += 1
            content = path.read_text(encoding="utf-8")
            for pattern in self.id_patterns:
                matches = re.findall(pattern, content)
                found_ids.update(matches)

        implemented = [requirement_id for requirement_id in expected_ids if requirement_id in found_ids]
        missing = [requirement_id for requirement_id in expected_ids if requirement_id not in found_ids]

        coverage = (len(implemented) / len(expected_ids)) * 100 if expected_ids else 0.0

        _log.info("Audit complete. Coverage: %.1f%% (%d/%d)", coverage, len(implemented), len(expected_ids))

        return TraceabilityReport(
            implemented_ids=implemented, missing_ids=missing, coverage_pct=coverage, files_scanned=files_scanned
        )

    def generate_markdown_report(self, report: TraceabilityReport) -> str:
        """Format the traceability report as Markdown."""
        md = "# 🔍 Traceability Audit Report\n\n"
        md += f"**Coverage**: {report.coverage_pct:.1f}%\n"
        md += f"**Files Scanned**: {report.files_scanned}\n\n"

        md += "## ✅ Implemented IDs\n"
        for requirement_id in sorted(report.implemented_ids):
            md += f"- {requirement_id}\n"

        md += "\n## ❌ Missing Implementation\n"
        for requirement_id in sorted(report.missing_ids):
            md += f"- {requirement_id}\n"

        return md
