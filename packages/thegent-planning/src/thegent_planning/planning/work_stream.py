"""WP-13001: Work stream and WBS automation manager."""

import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from filelock import FileLock

from thegent_core.config import ThegentSettings

_log = logging.getLogger(__name__)


class WorkStreamManager:
    """Manages the lifecycle of work packages across WORK_STREAM, WBS_AGENT_PROGRESS, and UNIFIED-WBS."""

    def __init__(self, settings: ThegentSettings, base_dir: Path | None = None) -> None:
        self.settings = settings
        self.base_dir = base_dir or Path.cwd()
        self.work_stream_path = self.base_dir / "docs" / "reference" / "WORK_STREAM.md"
        self.coordination_path = self.base_dir / "docs" / "reference" / "WBS_AGENT_PROGRESS.md"
        self.wbs_path = self.base_dir / "docs" / "plans" / "02-UNIFIED-WBS.md"
        self.lock_timeout = 10.0

    def claim(self, item_id: str, agent_id: str) -> dict[str, Any]:
        """Claim an item across all coordination files."""
        results = {"item_id": item_id, "agent_id": agent_id, "actions": []}
        blocked_by = self._unmet_dependencies_for_item(item_id)
        if blocked_by:
            results["success"] = False
            results["dependency_blocked"] = True
            results["blocked_by"] = blocked_by
            results["error"] = f"Cannot claim {item_id}; unmet dependencies: {', '.join(blocked_by)}"
            results["remediation"] = "Complete all listed dependency items first, then retry claim."
            return results

        # 1. Update WORK_STREAM.md
        if self.work_stream_path.exists():
            success = self._with_file_lock(
                self.work_stream_path,
                lambda: self._update_section(
                    self.work_stream_path,
                    "## CLAIMED",
                    f"| {item_id} | {agent_id} | {datetime.now(UTC).isoformat()} |",
                    placeholder="| *(none)*",
                ),
            )
            results["actions"].append({"file": "WORK_STREAM.md", "action": "claim", "success": success})

        # 2. Update WBS_AGENT_PROGRESS.md
        if self.coordination_path.exists():
            success = self._with_file_lock(
                self.coordination_path,
                lambda: self._update_section(
                    self.coordination_path,
                    "## CLAIMED",
                    f"| {item_id} | {agent_id} | {datetime.now(UTC).isoformat()} |",
                    placeholder="| *(none)*",
                ),
            )
            results["actions"].append({"file": "WBS_AGENT_PROGRESS.md", "action": "claim", "success": success})

        results["success"] = all(a["success"] for a in results["actions"]) if results["actions"] else True
        if not results["success"]:
            results["error"] = "Failed to update all coordination files."
        return results

    def complete(self, item_id: str, agent_id: str) -> dict[str, Any]:
        """Mark an item as complete across all files."""
        results = {"item_id": item_id, "agent_id": agent_id, "actions": []}

        # 1. Update WORK_STREAM.md (CLAIMED -> COMPLETED)
        if self.work_stream_path.exists():
            success = self._with_file_lock(
                self.work_stream_path,
                lambda: self._move_item_to_completed(
                    self.work_stream_path,
                    item_id,
                    agent_id,
                    placeholder=None,
                ),
            )
            results["actions"].append({"file": "WORK_STREAM.md", "action": "complete", "success": success})

        # 2. Update WBS_AGENT_PROGRESS.md (CLAIMED -> COMPLETED)
        if self.coordination_path.exists():
            success = self._with_file_lock(
                self.coordination_path,
                lambda: self._move_item_to_completed(
                    self.coordination_path,
                    item_id,
                    agent_id,
                    placeholder="| *(append when done)*",
                ),
            )
            results["actions"].append({"file": "WBS_AGENT_PROGRESS.md", "action": "complete", "success": success})

        # 3. Update 02-UNIFIED-WBS.md (NOT DONE/PARTIAL -> DONE)
        if self.wbs_path.exists():
            success = self._update_wbs_status(item_id, "DONE")
            results["actions"].append({"file": "02-UNIFIED-WBS.md", "action": "status_update", "success": success})

        results["success"] = all(a["success"] for a in results["actions"]) if results["actions"] else True
        if not results["success"]:
            results["error"] = "Failed to update all coordination files."
        return results

    def verify_work_stream_invariants(self) -> dict[str, Any]:
        """Check WORK_STREAM invariants across CLAIMED and COMPLETED sections."""
        from thegent_core.utils.helpers import safe_read_file_with_version

        if not self.work_stream_path.exists():
            return {
                "ok": False,
                "errors": [f"WORK_STREAM not found: {self.work_stream_path}"],
                "counts": {"claimed": 0, "completed": 0, "overlap": 0},
            }

        def _verify() -> dict[str, Any]:
            content, _version = safe_read_file_with_version(self.work_stream_path)
            if content is None:
                return {
                    "ok": False,
                    "errors": [f"Failed to read WORK_STREAM: {self.work_stream_path}"],
                    "counts": {"claimed": 0, "completed": 0, "overlap": 0},
                }

            claimed_ids = self._extract_section_ids(content, "## CLAIMED")
            completed_ids = self._extract_section_ids(content, "## COMPLETED")
            overlaps = sorted(set(claimed_ids).intersection(completed_ids))
            errors = [f"Item appears in both CLAIMED and COMPLETED: {item_id}" for item_id in overlaps]
            return {
                "ok": len(errors) == 0,
                "errors": errors,
                "counts": {
                    "claimed": len(claimed_ids),
                    "completed": len(completed_ids),
                    "overlap": len(overlaps),
                },
            }

        return self._with_file_lock(self.work_stream_path, _verify)

    def _with_file_lock(self, path: Path, operation):
        lock = FileLock(str(path) + ".lock", timeout=self.lock_timeout)
        with lock:
            return operation()

    def _move_item_to_completed(self, path: Path, item_id: str, agent_id: str, placeholder: str | None) -> bool:
        removed = self._remove_from_section(path, "## CLAIMED", item_id)
        added = self._update_section(
            path,
            "## COMPLETED",
            f"| {item_id} | {agent_id} | {datetime.now(UTC).isoformat()} |",
            placeholder=placeholder,
        )
        return removed and added

    def _extract_row_id(self, line: str) -> str | None:
        stripped = line.strip()
        if not stripped.startswith("|"):
            return None
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells:
            return None
        item_id = cells[0]
        if not item_id or item_id.upper() == "ID" or item_id.startswith("*(") or all(ch in "-:" for ch in item_id):
            return None
        return item_id.strip().strip("~")

    def _extract_section_ids(self, content: str, section_header: str) -> list[str]:
        ids: list[str] = []
        in_section = False
        for line in content.splitlines():
            if line.strip().startswith(section_header):
                in_section = True
                continue
            if in_section and line.strip().startswith("## "):
                break
            if in_section:
                item_id = self._extract_row_id(line)
                if item_id:
                    ids.append(item_id)
        return ids

    def _update_section(self, path: Path, section_header: str, row_text: str, placeholder: str | None = None) -> bool:
        """Add a row to a section in a markdown file with OCC."""
        from thegent_core.utils.helpers import safe_read_file_with_version, safe_write_file

        content, version = safe_read_file_with_version(path)
        if content is None:
            return False

        item_id_to_add = self._extract_row_id(row_text)

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

            # Reject duplicate exact ID in this section.
            if in_section and item_id_to_add and self._extract_row_id(line) == item_id_to_add:
                _log.error(
                    "OCC violation: item %s already exists in section %s of %s; concurrent claim detected",
                    item_id_to_add,
                    section_header,
                    path,
                )
                return False

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
        from thegent_core.utils.helpers import safe_read_file_with_version, safe_write_file

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

            if in_section and self._extract_row_id(line) == item_id:
                removed = True
                continue  # Skip this line

            new_lines.append(line)

        new_content = "\n".join(new_lines) + "\n"
        write_success = safe_write_file(path, new_content, expected_version=version)
        return removed and write_success

    def _update_wbs_status(self, item_id: str, new_status: str) -> bool:
        """Update status of a WP in 02-UNIFIED-WBS.md with OCC."""
        from thegent_core.utils.helpers import safe_read_file_with_version, safe_write_file

        content, version = safe_read_file_with_version(self.wbs_path)
        if content is None:
            return False

        lines = content.splitlines()
        new_lines = []
        updated = False

        for line in lines:
            if self._extract_row_id(line) == item_id:
                parts = [part.strip() for part in line.strip().split("|")]
                if len(parts) >= 5:
                    parts[3] = new_status
                    line = "| " + " | ".join(parts[1:-1]) + " |"
                    updated = True
            new_lines.append(line)

        new_content = "\n".join(new_lines) + "\n"
        write_success = safe_write_file(self.wbs_path, new_content, expected_version=version)
        return updated and write_success

    def _unmet_dependencies_for_item(self, item_id: str) -> list[str]:
        from thegent_core.utils.helpers import safe_read_file_with_version

        dependencies: list[str] = []
        completed_ids: set[str] = set()

        if self.work_stream_path.exists():
            work_stream_content, _ = safe_read_file_with_version(self.work_stream_path)
            if work_stream_content:
                dependencies.extend(self._extract_backlog_table_dependencies(work_stream_content, item_id))
                dependencies.extend(self._extract_narrative_blocked_by_dependencies(work_stream_content, item_id))
                completed_ids.update(self._extract_section_ids(work_stream_content, "## COMPLETED"))

        completed_ids.update(self._extract_wbs_done_ids())
        normalized_deps = self._normalize_dependency_ids(dependencies)
        return [dep for dep in normalized_deps if dep not in completed_ids]

    def _extract_backlog_table_dependencies(self, content: str, item_id: str) -> list[str]:
        lines = content.splitlines()
        in_backlog = False
        header_cells: list[str] | None = None

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## BACKLOG"):
                in_backlog = True
                continue
            if in_backlog and stripped.startswith("## "):
                break
            if not in_backlog or not stripped.startswith("|"):
                continue

            raw_cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if not header_cells and any(cell.upper() == "ID" for cell in raw_cells):
                header_cells = [cell.lower() for cell in raw_cells]
                continue
            if all(not cell or set(cell) <= {"-", ":"} for cell in raw_cells):
                continue
            if not header_cells:
                continue

            row_id = raw_cells[0] if raw_cells else ""
            if row_id != item_id:
                continue
            dep_index = self._dependency_column_index(header_cells)
            if dep_index is None or dep_index >= len(raw_cells):
                return []
            return self._parse_dependency_cell(raw_cells[dep_index])

        return []

    def _extract_narrative_blocked_by_dependencies(self, content: str, item_id: str) -> list[str]:
        lines = content.splitlines()
        section_start = None

        heading_pattern = re.compile(r"^#{2,6}\s+\[(?P<id>[^\]]+)\]")
        for index, line in enumerate(lines):
            match = heading_pattern.match(line.strip())
            if match and match.group("id").strip() == item_id:
                section_start = index + 1
                break
        if section_start is None:
            return []

        blocked_pattern = re.compile(r"^\*\*Blocked by:\*\*\s*(?P<deps>.+)$", re.IGNORECASE)
        for line in lines[section_start:]:
            stripped = line.strip()
            if stripped.startswith("### [") or stripped.startswith("## "):
                break
            match = blocked_pattern.match(stripped)
            if match:
                return self._parse_dependency_cell(match.group("deps"))
        return []

    def _extract_wbs_done_ids(self) -> set[str]:
        from thegent_core.utils.helpers import safe_read_file_with_version

        done: set[str] = set()
        if not self.wbs_path.exists():
            return done

        content, _ = safe_read_file_with_version(self.wbs_path)
        if not content:
            return done

        for line in content.splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            if cells[0].upper() == "WP ID":
                continue
            if set(cells[0]) <= {"-", ":"}:
                continue
            status = cells[2].upper()
            if status in {"DONE", "COMPLETED"}:
                done.add(cells[0])
        return done

    def _dependency_column_index(self, headers: list[str]) -> int | None:
        for idx, header in enumerate(headers):
            normalized = header.replace("_", " ").strip()
            if normalized in {"depends", "depends on", "blocked by", "dependencies"}:
                return idx
        return None

    def _parse_dependency_cell(self, value: str) -> list[str]:
        tokens = [token.strip() for token in value.replace(";", ",").split(",")]
        return [token for token in tokens if token and token not in {"-", "—", "none", "None"}]

    def _normalize_dependency_ids(self, deps: list[str]) -> list[str]:
        normalized: list[str] = []
        for dep in deps:
            cleaned = dep.strip()
            if not cleaned:
                continue
            if cleaned.startswith("✅"):
                cleaned = cleaned.lstrip("✅").strip()
            normalized.append(cleaned)
        return sorted(dict.fromkeys(normalized))
