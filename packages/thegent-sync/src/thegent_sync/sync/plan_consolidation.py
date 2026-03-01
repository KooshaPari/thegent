"""Plan consolidation automation."""

import logging
from pathlib import Path
from typing import Any

from thegent.utils.batch_ops import batch_read, batch_write

logger = logging.getLogger(__name__)


class PlanConsolidation:
    """Automate plan consolidation."""

    def __init__(self, plans_dir: Path | None = None) -> None:
        """Initialize plan consolidation.

        Args:
            plans_dir: Plans directory path
        """
        self.plans_dir = plans_dir or Path("docs/plans")

    def find_plans(self) -> list[Path]:
        """Find all plan files.

        Returns:
            List of plan file paths
        """
        if not self.plans_dir.exists():
            return []

        plan_files = list(self.plans_dir.glob("*.md"))
        logger.info(f"Found {len(plan_files)} plan files")
        return plan_files

    def consolidate(self, output_file: Path | None = None) -> dict[str, Any]:
        """Consolidate all plans.

        Args:
            output_file: Output file path

        Returns:
            Consolidation results
        """
        plan_files = self.find_plans()

        if not output_file:
            output_file = self.plans_dir / "CONSOLIDATED_PLAN.md"

        # Batch read all plan files at once
        file_contents = batch_read(plan_files)

        consolidated_content = ["# Consolidated Plan\n"]
        for plan_file in plan_files:
            content = file_contents.get(plan_file, "")
            consolidated_content.append(f"## {plan_file.name}\n")
            consolidated_content.append(content)
            consolidated_content.append("\n---\n")

        # Batch write the consolidated output
        batch_write([(output_file, "\n".join(consolidated_content))])

        return {
            "plans_consolidated": len(plan_files),
            "output_file": str(output_file),
        }
