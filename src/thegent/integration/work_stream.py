"""Integration with WORK_STREAM.md system."""

import re
from pathlib import Path

__all__ = ["WorkStreamIntegration"]


class WorkStreamIntegration:
    """Integrate with WORK_STREAM.md system.

    This class handles integration with the unified work stream system,
    including parsing WORK_STREAM.md, claiming work items, and tracking completion.

    Examples:
        >>> integration = WorkStreamIntegration()
        >>> next_item = integration.get_next_item()
        >>> if next_item:
        ...     integration.claim_work_item(next_item["id"], "agent-1")
        ...     # ... do work ...
        ...     integration.complete_work_item(next_item["id"], "agent-1")
    """

    def __init__(self, work_stream_file: Path | None = None) -> None:
        """Initialize work stream integration.

        Args:
            work_stream_file: Path to WORK_STREAM.md file.
                             Defaults to docs/reference/WORK_STREAM.md
        """
        if work_stream_file is None:
            # Try to find WORK_STREAM.md relative to project root
            # Look for it in common locations
            possible_paths = [
                Path("docs/reference/WORK_STREAM.md"),
                Path("../docs/reference/WORK_STREAM.md"),
                Path("../../docs/reference/WORK_STREAM.md"),
            ]

            for path in possible_paths:
                if path.exists():
                    work_stream_file = path
                    break

            if work_stream_file is None:
                # Fallback to default
                work_stream_file = Path("docs/reference/WORK_STREAM.md")

        self.work_stream_file = work_stream_file
        self.work_stream_data: dict[str, list[dict]] = {
            "pending": [],
            "claimed": [],
            "completed": [],
        }
        self._load_work_stream()

    def _load_work_stream(self) -> None:
        """Load work stream data from WORK_STREAM.md."""
        if not self.work_stream_file.exists():
            return

        try:
            content = self.work_stream_file.read_text(encoding="utf-8")

            # Extract sections
            self.work_stream_data = {
                "pending": self._extract_section(content, "BACKLOG"),
                "claimed": self._extract_section(content, "CLAIMED"),
                "completed": self._extract_section(content, "COMPLETED"),
            }
        except OSError:
            # Load failed, keep empty data
            pass

    def _extract_section(self, content: str, section: str) -> list[dict]:
        """Extract section from WORK_STREAM.md.

        Parses markdown table and extracts work items.

        Args:
            content: Content of WORK_STREAM.md
            section: Section name (PENDING, CLAIMED, COMPLETED)

        Returns:
            List of work items as dictionaries
        """
        items = []

        # Find section header
        section_pattern = rf"##\s+{section}\s*\n"
        match = re.search(section_pattern, content, re.IGNORECASE)
        if not match:
            return items

        # Extract table after section header
        section_start = match.end()
        next_section_match = re.search(r"##\s+\w+\s*\n", content[section_start:], re.IGNORECASE)

        if next_section_match:
            section_content = content[section_start : section_start + next_section_match.start()]
        else:
            section_content = content[section_start:]

        # Parse markdown table
        lines = section_content.split("\n")
        in_table = False
        headers = []

        for line in lines:
            line = line.strip()

            # Check for table start
            if line.startswith("|") and "ID" in line:
                in_table = True
                # Extract headers
                headers = [h.strip() for h in line.split("|")[1:-1]]
                continue

            # Check for table separator
            if in_table and line.startswith("|") and "---" in line:
                continue

            # Parse table row
            if in_table and line.startswith("|"):
                cells = [c.strip() for c in line.split("|")[1:-1]]
                if len(cells) == len(headers):
                    item = dict(zip(headers, cells, strict=False))
                    items.append(item)

            # Stop at next section or empty line after table
            if in_table and not line.startswith("|") and line:
                break

        return items

    def claim_work_item(self, item_id: str, agent_id: str) -> bool:
        """Claim work item from work stream.

        Moves item from PENDING to CLAIMED section.

        Args:
            item_id: ID of work item to claim
            agent_id: ID of agent claiming the item

        Returns:
            True if successfully claimed, False otherwise
        """
        # Find item in pending
        pending_items = self.work_stream_data.get("pending", [])
        item = next((i for i in pending_items if i.get("ID") == item_id), None)

        if not item:
            return False

        # Add to claimed with agent info
        claimed_item = item.copy()
        claimed_item["Agent"] = agent_id
        claimed_item["Started"] = self._get_timestamp()

        # Remove from pending, add to claimed
        self.work_stream_data["pending"] = [i for i in pending_items if i.get("ID") != item_id]
        self.work_stream_data["claimed"].append(claimed_item)

        # Save changes
        self._save_work_stream()

        return True

    def complete_work_item(self, item_id: str, agent_id: str) -> bool:
        """Complete work item.

        Moves item from CLAIMED to COMPLETED section.

        Args:
            item_id: ID of work item to complete
            agent_id: ID of agent completing the item

        Returns:
            True if successfully completed, False otherwise
        """
        # Find item in claimed
        claimed_items = self.work_stream_data.get("claimed", [])
        item = next((i for i in claimed_items if i.get("ID") == item_id), None)

        if not item:
            return False

        # Verify agent matches
        if item.get("Agent") != agent_id:
            return False

        # Add to completed
        completed_item = item.copy()
        completed_item["Completed"] = self._get_timestamp()

        # Remove from claimed, add to completed
        self.work_stream_data["claimed"] = [i for i in claimed_items if i.get("ID") != item_id]
        self.work_stream_data["completed"].append(completed_item)

        # Save changes
        self._save_work_stream()

        return True

    def get_next_item(self) -> dict | None:
        """Get next actionable item from work stream.

        Returns highest priority item from PENDING that is not in CLAIMED.

        Returns:
            Work item dictionary, or None if no items available
        """
        pending = self.work_stream_data.get("pending", [])
        claimed_ids = {item.get("ID") for item in self.work_stream_data.get("claimed", [])}

        # Filter out claimed items
        available = [item for item in pending if item.get("ID") not in claimed_ids]

        if not available:
            return None

        # Sort by priority (if Priority column exists)
        def get_priority(item: dict) -> int:
            priority_str = item.get("Priority", "").upper()
            priority_map = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
            return priority_map.get(priority_str, 99)

        available.sort(key=get_priority)

        return available[0]

    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime

        return datetime.now().isoformat()

    def _save_work_stream(self) -> None:
        """Save work stream data back to WORK_STREAM.md."""
        if not self.work_stream_file.exists():
            return

        try:
            content = self.work_stream_file.read_text(encoding="utf-8")

            # Helper to generate markdown table from list of dicts
            def generate_table(items: list[dict], section_name: str) -> str:
                if not items:
                    return ""

                # Get headers from first item or define them based on section
                if section_name == "BACKLOG":
                    headers = ["ID", "Title", "Source", "Priority", "Depends"]
                elif section_name == "CLAIMED":
                    headers = ["ID", "Agent", "Started"]
                elif section_name == "COMPLETED":
                    headers = ["ID", "Agent", "Completed", "Notes"]
                else:
                    headers = list(items[0].keys())

                table = f"| {' | '.join(headers)} |\n"
                table += f"| {' | '.join(['---'] * len(headers))} |\n"

                for item in items:
                    row = [str(item.get(h, "")) for h in headers]
                    table += f"| {' | '.join(row)} |\n"

                return table

            # Replace each section's table
            new_content = content
            for section, status_key in [("BACKLOG", "pending"), ("CLAIMED", "claimed"), ("COMPLETED", "completed")]:
                items = self.work_stream_data.get(status_key, [])
                new_table = generate_table(items, section)

                match = re.search(rf"##\s+{section}.*?\n", new_content, re.IGNORECASE)
                if match:
                    section_start = match.end()
                    # Find end of current table/section
                    # Look for next ## header
                    next_header = re.search(r"\n##\s+", new_content[section_start:])
                    section_end = section_start + next_header.start() if next_header else len(new_content)

                    # Construct new section content: newline + table + newline
                    replacement = "\n" + new_table + "\n"
                    new_content = new_content[:section_start] + replacement + new_content[section_end:]

            if new_content != content:
                self.work_stream_file.write_text(new_content, encoding="utf-8")

        except OSError as e:
            import logging

            logging.getLogger(__name__).warning(f"Failed to save WORK_STREAM.md: {e}")
