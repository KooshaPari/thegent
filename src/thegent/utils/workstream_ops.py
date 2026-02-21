"""Automated work stream operations (read, parse, update)."""

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from thegent.utils.helpers import safe_read_file, safe_write_file
from thegent.utils.reusable_helpers import ReusableHelpers

logger = logging.getLogger(__name__)


class WorkStreamOps:
    """Automated operations on work stream files."""

    def __init__(self, base_dir: Path | None = None) -> None:
        """Initialize work stream operations.

        Args:
            base_dir: Base directory for work stream files
        """
        self.base_dir = base_dir or Path.cwd()
        self.work_stream_path = self.find_work_stream()

    def find_work_stream(self) -> Path:
        """Find the work stream file in common locations."""
        locations = [
            self.base_dir / "docs" / "reference" / "WORK_STREAM.md",
            self.base_dir / "WORK_STREAM.md",
            self.base_dir / "docs" / "WORK_STREAM.md",
        ]
        for loc in locations:
            if loc.exists():
                return loc
        return locations[0]  # Default

    @ReusableHelpers.error_handler
    def read_backlog(self) -> list[dict[str, Any]]:
        """Read all items from BACKLOG section.

        Returns:
            List of backlog items with id, title, priority, depends
        """
        content = safe_read_file(self.work_stream_path)
        if not content:
            logger.warning(f"Work stream file not found or empty: {self.work_stream_path}")
            return []

        lines = content.splitlines()
        backlog_start = None
        next_section_start = None

        for i, line in enumerate(lines):
            if "## BACKLOG" in line:
                backlog_start = i
            elif backlog_start is not None and line.startswith("## "):
                next_section_start = i
                break

        if backlog_start is None:
            return []

        items = []
        # Skip header and separator
        for i in range(backlog_start + 1, next_section_start or len(lines)):
            line = lines[i]
            if line.startswith("|") and "| ID |" not in line and "|----" not in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2:
                    item_id = parts[0].strip("~").strip()
                    if item_id and not item_id.startswith("*"):
                        items.append(
                            {
                                "id": item_id,
                                "title": parts[1] if len(parts) > 1 else "",
                                "source": parts[2] if len(parts) > 2 else "",
                                "priority": parts[3] if len(parts) > 3 else "P2",
                                "depends": parts[4] if len(parts) > 4 else "-",
                            }
                        )

        return items

    @ReusableHelpers.error_handler
    def claim_item(self, item_id: str, agent_id: str) -> bool:
        """Claim an item by adding it to CLAIMED section.

        Args:
            item_id: Work item ID
            agent_id: Agent identifier

        Returns:
            True if successful
        """
        content = safe_read_file(self.work_stream_path)
        if not content:
            return False

        lines = content.splitlines()
        claimed_idx = None
        for i, line in enumerate(lines):
            if "## CLAIMED" in line:
                claimed_idx = i
                break

        if claimed_idx is None:
            # Create CLAIMED section if missing
            lines.append("")
            lines.append("## CLAIMED")
            lines.append("")
            lines.append("| ID | Agent | Claimed At |")
            lines.append("|----|-------|------------|")
            claimed_idx = len(lines) - 3

        # Find insertion point (after table header)
        insert_at = claimed_idx + 1
        for i in range(claimed_idx + 1, len(lines)):
            if lines[i].startswith("## "):
                insert_at = i
                break
            if lines[i].startswith("|") and "| ID |" not in lines[i] and "|----" not in lines[i]:
                insert_at = i + 1

        timestamp = datetime.now(UTC).isoformat()
        claim_line = f"| {item_id} | {agent_id} | {timestamp} |"
        lines.insert(insert_at, claim_line)

        return safe_write_file(self.work_stream_path, "\n".join(lines) + "\n")

    @ReusableHelpers.error_handler
    def complete_item(self, item_id: str, agent_id: str) -> bool:
        """Mark an item as complete.

        Args:
            item_id: Work item ID
            agent_id: Agent identifier

        Returns:
            True if successful
        """
        content = safe_read_file(self.work_stream_path)
        if not content:
            return False

        # Strike through in backlog
        updated = content.replace(f"| {item_id} |", f"| ~~{item_id}~~ |")

        lines = updated.splitlines()

        # Add to COMPLETED section
        completed_idx = None
        for i, line in enumerate(lines):
            if "## COMPLETED" in line:
                completed_idx = i
                break

        if completed_idx is None:
            lines.append("")
            lines.append("## COMPLETED")
            lines.append("")
            lines.append("| ID | Agent | Completed At |")
            lines.append("|----|-------|--------------|")
            completed_idx = len(lines) - 3

        insert_at = completed_idx + 1
        for i in range(completed_idx + 1, len(lines)):
            if lines[i].startswith("## "):
                insert_at = i
                break
            if lines[i].startswith("|") and "| ID |" not in lines[i] and "|----" not in lines[i]:
                insert_at = i + 1

        timestamp = datetime.now(UTC).isoformat()
        complete_line = f"| {item_id} | {agent_id} | {timestamp} |"
        lines.insert(insert_at, complete_line)

        return safe_write_file(self.work_stream_path, "\n".join(lines) + "\n")

    def get_progress(self) -> dict[str, int]:
        """Calculate progress statistics.

        Returns:
            Dictionary with counts of total, completed, and backlog items.
        """
        content = safe_read_file(self.work_stream_path)
        if not content:
            return {"total": 0, "completed": 0, "backlog": 0}

        backlog = self.read_backlog()
        completed_count = content.count("~~") // 2

        return {
            "total": len(backlog) + completed_count,
            "completed": completed_count,
            "backlog": len(backlog),
        }
