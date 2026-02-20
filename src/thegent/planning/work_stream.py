"""WP-13001: Work stream and WBS automation manager."""

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)


class WorkStreamManager:
    """Manages the lifecycle of work packages across WORK_STREAM, WBS_AGENT_PROGRESS, and UNIFIED-WBS."""

    def __init__(self, settings: ThegentSettings, base_dir: Path | None = None) -> None:
        self.settings = settings
        self.base_dir = base_dir or Path.cwd()
        self.work_stream_path = self.base_dir / "docs" / "reference" / "WORK_STREAM.md"
        self.coordination_path = self.base_dir / "docs" / "reference" / "WBS_AGENT_PROGRESS.md"
        self.wbs_path = self.base_dir / "docs" / "plans" / "02-UNIFIED-WBS.md"

    def claim(self, item_id: str, agent_id: str) -> dict[str, Any]:
        """Claim an item across all coordination files."""
        results = {"item_id": item_id, "agent_id": agent_id, "actions": []}

        # 1. Update WORK_STREAM.md
        if self.work_stream_path.exists():
            success = self._update_section(
                self.work_stream_path,
                "## CLAIMED",
                f"| {item_id} | {agent_id} | {datetime.now(UTC).isoformat()} |",
                placeholder="| *(none)*",
            )
            results["actions"].append({"file": "WORK_STREAM.md", "action": "claim", "success": success})

        # 2. Update WBS_AGENT_PROGRESS.md
        if self.coordination_path.exists():
            success = self._update_section(
                self.coordination_path,
                "## CLAIMED",
                f"| {item_id} | {agent_id} | {datetime.now(UTC).isoformat()} |",
                placeholder="| *(none)*",
            )
            results["actions"].append({"file": "WBS_AGENT_PROGRESS.md", "action": "claim", "success": success})

        results["success"] = any(a["success"] for a in results["actions"]) if results["actions"] else True
        if not results["success"]:
            results["error"] = "Failed to update any coordination files."
        return results

    def complete(self, item_id: str, agent_id: str) -> dict[str, Any]:
        """Mark an item as complete across all files."""
        results = {"item_id": item_id, "agent_id": agent_id, "actions": []}

        # 1. Update WORK_STREAM.md (CLAIMED -> COMPLETED)
        if self.work_stream_path.exists():
            s1 = self._remove_from_section(self.work_stream_path, "## CLAIMED", item_id)
            s2 = self._update_section(
                self.work_stream_path,
                "## COMPLETED",
                f"| {item_id} | {agent_id} | {datetime.now(UTC).isoformat()} |",
            )
            results["actions"].append({"file": "WORK_STREAM.md", "action": "complete", "success": s1 and s2})

        # 2. Update WBS_AGENT_PROGRESS.md (CLAIMED -> COMPLETED)
        if self.coordination_path.exists():
            s1 = self._remove_from_section(self.coordination_path, "## CLAIMED", item_id)
            s2 = self._update_section(
                self.coordination_path,
                "## COMPLETED",
                f"| {item_id} | {agent_id} | {datetime.now(UTC).isoformat()} |",
                placeholder="| *(append when done)*",
            )
            results["actions"].append({"file": "WBS_AGENT_PROGRESS.md", "action": "complete", "success": s1 and s2})

        # 3. Update 02-UNIFIED-WBS.md (NOT DONE/PARTIAL -> DONE)
        if self.wbs_path.exists():
            success = self._update_wbs_status(item_id, "DONE")
            results["actions"].append({"file": "02-UNIFIED-WBS.md", "action": "status_update", "success": success})

        results["success"] = any(a["success"] for a in results["actions"]) if results["actions"] else True
        if not results["success"]:
            results["error"] = "Failed to update any coordination files."
        return results

    def _update_section(self, path: Path, section_header: str, row_text: str, placeholder: str | None = None) -> bool:
        """Add a row to a section in a markdown file with OCC."""
        from thegent.utils.helpers import safe_read_file_with_version, safe_write_file

        content, version = safe_read_file_with_version(path)
        if content is None:
            return False

        lines = content.splitlines()
        new_lines = []
        in_section = False
        found = False

        for line in lines:
            if line.strip().startswith(section_header):
                in_section = True
                new_lines.append(line)
                continue

            if in_section and line.strip().startswith("## "):
                if not found:
                    new_lines.append(row_text)
                    found = True
                in_section = False
                new_lines.append(line)
                continue

            if in_section and placeholder and line.strip().startswith(placeholder):
                new_lines.append(row_text)
                found = True
                continue

            new_lines.append(line)

        if in_section and not found:
            new_lines.append(row_text)
            found = True

        if not found and not in_section:
            return False

        new_content = "\n".join(new_lines) + "\n"
        return safe_write_file(path, new_content, expected_version=version)

    def _remove_from_section(self, path: Path, section_header: str, item_id: str) -> bool:
        """Remove a row containing item_id from a section with OCC."""
        from thegent.utils.helpers import safe_read_file_with_version, safe_write_file

        content, version = safe_read_file_with_version(path)
        if content is None:
            return False

        lines = content.splitlines()
        new_lines = []
        in_section = False
        removed = False

        for line in lines:
            if line.strip().startswith(section_header):
                in_section = True
                new_lines.append(line)
                continue

            if in_section and line.strip().startswith("## "):
                in_section = False
                new_lines.append(line)
                continue

            if in_section and f"| {item_id} |" in line:
                removed = True
                continue  # Skip this line

            new_lines.append(line)

        new_content = "\n".join(new_lines) + "\n"
        safe_write_file(path, new_content, expected_version=version)
        return removed

    def _update_wbs_status(self, item_id: str, new_status: str) -> bool:
        """Update status of a WP in 02-UNIFIED-WBS.md with OCC."""
        from thegent.utils.helpers import safe_read_file_with_version, safe_write_file

        content, version = safe_read_file_with_version(self.wbs_path)
        if content is None:
            return False

        lines = content.splitlines()
        new_lines = []
        updated = False

        for line in lines:
            if f"| {item_id} |" in line:
                parts = line.split("|")
                if len(parts) >= 4:
                    parts[3] = f" {new_status} "
                    line = "|".join(parts)
                    updated = True
            new_lines.append(line)

        new_content = "\n".join(new_lines) + "\n"
        safe_write_file(self.wbs_path, new_content, expected_version=version)
        return updated
