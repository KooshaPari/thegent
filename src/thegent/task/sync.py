"""WORK_STREAM.md bidirectional sync with task files."""

from datetime import datetime
from pathlib import Path
from typing import Any

from thegent.task.parser import parse_task_file


class WorkStreamSync:
    """Synchronize task files with WORK_STREAM.md."""

    def __init__(self, work_stream_path: Path, tasks_dir: Path) -> None:
        """Initialize sync manager.

        Args:
            work_stream_path: Path to WORK_STREAM.md
            tasks_dir: Directory containing task files
        """
        self.work_stream_path = work_stream_path
        self.tasks_dir = tasks_dir

    def update_work_stream_from_tasks(self) -> dict[str, Any]:
        """Update WORK_STREAM.md BACKLOG section from task files.

        Returns:
            dict with update results
        """
        if not self.work_stream_path.exists():
            return {"error": f"WORK_STREAM.md not found: {self.work_stream_path}"}

        if not self.tasks_dir.exists():
            return {"error": f"Tasks directory not found: {self.tasks_dir}"}

        # Read current WORK_STREAM.md
        content = self.work_stream_path.read_text(encoding="utf-8")

        # Parse all task files
        task_files = sorted(self.tasks_dir.glob("*.md"))
        tasks = []
        parse_errors: list[str] = []
        task_ids: set[str] = set()
        for task_file in task_files:
            try:
                task = parse_task_file(task_file)
                task_id = str(task.get("id", "")).strip()
                if task_id in task_ids:
                    parse_errors.append(
                        f"duplicate task id {task_id} in {task_file.name}"
                    )
                task_ids.add(task_id)
                tasks.append(task)
            except Exception as exc:
                parse_errors.append(f"{task_file.name}: {exc}")

        if parse_errors:
            return {
                "error": "One or more task files failed to parse",
                "task_parse_errors": parse_errors,
                "tasks_synced": 0,
            }

        # Build BACKLOG table rows
        backlog_rows = []
        for task in tasks:
            task_id = task.get("id", "")
            title = task.get("title", "")
            source = task.get("source", "")
            priority = task.get("priority", "P2")
            depends = ", ".join(task.get("depends", [])) or "-"

            backlog_rows.append(f"| {task_id} | {title} | {source} | {priority} | {depends} |")

        # Find BACKLOG section and replace
        lines = content.splitlines()
        new_lines = []
        in_backlog = False
        _backlog_start_idx = None
        _backlog_end_idx = None

        for i, line in enumerate(lines):
            if line.strip().startswith("## BACKLOG") or line.strip().startswith("## PENDING"):
                in_backlog = True
                _backlog_start_idx = i
                new_lines.append(line)
                # Add header row
                new_lines.append("| ID | Title | Source | Priority | Depends |")
                new_lines.append("|----|-------|--------|----------|---------|")
                continue

            if in_backlog:
                if line.strip().startswith("##"):
                    _backlog_end_idx = i
                    in_backlog = False
                    # Insert backlog rows
                    new_lines.extend(backlog_rows)
                    new_lines.append("")  # Empty line before next section
                    new_lines.append(line)
                    continue
                # Skip old backlog rows
                if line.strip().startswith("|") and "ID" not in line:
                    continue

            if not in_backlog:
                new_lines.append(line)

        # If we're still in backlog at the end, close it
        if in_backlog:
            new_lines.extend(backlog_rows)

        new_content = "\n".join(new_lines)
        self.work_stream_path.write_text(new_content, encoding="utf-8")

        return {
            "updated": True,
            "tasks_synced": len(tasks),
            "backlog_rows": len(backlog_rows),
        }

    def claim_task(self, task_id: str, agent_id: str) -> dict[str, Any]:
        """Claim a task (move from BACKLOG to CLAIMED).

        Args:
            task_id: Task ID to claim
            agent_id: Agent ID claiming the task

        Returns:
            dict with claim results
        """
        if not self.work_stream_path.exists():
            return {"error": f"WORK_STREAM.md not found: {self.work_stream_path}"}

        # Check dependencies before claiming
        task_file = self.tasks_dir / f"{task_id}.md"
        if task_file.exists():
            try:
                task = parse_task_file(task_file)
                parsed_task_id = str(task.get("id", "")).strip()
                if parsed_task_id and parsed_task_id != task_id:
                    return {
                        "error": (
                            f"Task file id mismatch for {task_id}: "
                            f"expected {task_id}, found {parsed_task_id}"
                        )
                    }
                depends = task.get("depends", [])
                if depends:
                    dep_check = self.check_dependencies_satisfied(task_id, depends)
                    if not dep_check["satisfied"]:
                        return {
                            "error": f"Task {task_id} has unmet dependencies: {', '.join(dep_check['unmet'])}",
                            "unmet_dependencies": dep_check["unmet"],
                            "dependency_status": dep_check,
                        }
            except Exception as e:
                return {"error": f"Failed dependency validation for {task_id}: {e}"}

        lines = self.work_stream_path.read_text(encoding="utf-8").splitlines()
        backlog_bounds = self._find_section_bounds(lines, ("BACKLOG", "PENDING"))
        claimed_bounds = self._find_section_bounds(lines, ("CLAIMED",))
        completed_bounds = self._find_section_bounds(lines, ("COMPLETED",))

        if not backlog_bounds:
            return {"error": "BACKLOG/PENDING section not found"}
        if not claimed_bounds:
            return {"error": "CLAIMED section not found"}

        claimed_idx = self._find_row_index_by_id(lines, claimed_bounds[0], claimed_bounds[1], task_id)
        completed_idx = (
            self._find_row_index_by_id(lines, completed_bounds[0], completed_bounds[1], task_id)
            if completed_bounds
            else None
        )
        if claimed_idx is not None and completed_idx is not None:
            return {"error": f"Invariant violation: {task_id} exists in both CLAIMED and COMPLETED"}
        if claimed_idx is not None:
            return {"error": f"Task {task_id} is already claimed"}
        if completed_idx is not None:
            return {"error": f"Task {task_id} is already completed"}

        backlog_idx = self._find_row_index_by_id(lines, backlog_bounds[0], backlog_bounds[1], task_id)
        if backlog_idx is None:
            return {"error": f"Task {task_id} not found in BACKLOG"}

        # Remove from backlog first.
        lines.pop(backlog_idx)

        # Recompute claimed bounds after list mutation.
        claimed_bounds = self._find_section_bounds(lines, ("CLAIMED",))
        if not claimed_bounds:
            return {"error": "CLAIMED section not found after update"}
        self._ensure_table_header(
            lines, claimed_bounds[0], claimed_bounds[1], "| ID | Agent | Started |", "|----|-------|---------|"
        )
        claimed_bounds = self._find_section_bounds(lines, ("CLAIMED",))
        if not claimed_bounds:
            return {"error": "CLAIMED section bounds failed after header ensure"}

        started = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_idx = self._table_insert_index(lines, claimed_bounds[0], claimed_bounds[1])
        lines.insert(insert_idx, f"| {task_id} | {agent_id} | {started} |")

        self.work_stream_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return {"claimed": True, "task_id": task_id, "agent_id": agent_id}

    def complete_task(self, task_id: str, agent_id: str) -> dict[str, Any]:
        """Complete a task (move from CLAIMED to COMPLETED).

        Args:
            task_id: Task ID to complete
            agent_id: Agent ID completing the task

        Returns:
            dict with completion results
        """
        if not self.work_stream_path.exists():
            return {"error": f"WORK_STREAM.md not found: {self.work_stream_path}"}

        lines = self.work_stream_path.read_text(encoding="utf-8").splitlines()
        claimed_bounds = self._find_section_bounds(lines, ("CLAIMED",))
        completed_bounds = self._find_section_bounds(lines, ("COMPLETED",))

        if not claimed_bounds:
            return {"error": "CLAIMED section not found"}
        if not completed_bounds:
            return {"error": "COMPLETED section not found"}

        claimed_idx = self._find_row_index_by_id(lines, claimed_bounds[0], claimed_bounds[1], task_id)
        completed_idx = self._find_row_index_by_id(lines, completed_bounds[0], completed_bounds[1], task_id)
        if claimed_idx is not None and completed_idx is not None:
            return {"error": f"Invariant violation: {task_id} exists in both CLAIMED and COMPLETED"}
        if claimed_idx is None and completed_idx is not None:
            return {"error": f"Task {task_id} is already completed"}
        if claimed_idx is None:
            return {"error": f"Task {task_id} not found in CLAIMED"}

        # Remove from claimed first.
        lines.pop(claimed_idx)

        completed_bounds = self._find_section_bounds(lines, ("COMPLETED",))
        if not completed_bounds:
            return {"error": "COMPLETED section not found after update"}

        has_notes = False
        for i in range(completed_bounds[0] + 1, min(completed_bounds[1], completed_bounds[0] + 6)):
            if "Notes" in lines[i]:
                has_notes = True
                break
        self._ensure_table_header(
            lines,
            completed_bounds[0],
            completed_bounds[1],
            "| ID | Agent | Completed | Notes |" if has_notes else "| ID | Agent | Completed |",
            "|----|-------|-----------|-------|" if has_notes else "|----|-------|-----------|",
        )
        completed_bounds = self._find_section_bounds(lines, ("COMPLETED",))
        if not completed_bounds:
            return {"error": "COMPLETED section bounds failed after header ensure"}

        completed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = (
            f"| {task_id} | {agent_id} | {completed} | - |"
            if has_notes
            else f"| {task_id} | {agent_id} | {completed} |"
        )
        insert_idx = self._table_insert_index(lines, completed_bounds[0], completed_bounds[1])
        lines.insert(insert_idx, row)

        self.work_stream_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return {"completed": True, "task_id": task_id, "agent_id": agent_id}

    def get_task_status(self, task_id: str) -> str | None:
        """Get current status of a task in WORK_STREAM.md.

        Args:
            task_id: Task ID to check

        Returns:
            Status: "BACKLOG", "CLAIMED", "COMPLETED", or None if not found
        """
        if not self.work_stream_path.exists():
            return None

        lines = self.work_stream_path.read_text(encoding="utf-8").splitlines()
        sections: list[tuple[tuple[str, ...], str]] = [
            (("BACKLOG", "PENDING"), "BACKLOG"),
            (("CLAIMED",), "CLAIMED"),
            (("COMPLETED",), "COMPLETED"),
        ]
        for names, status in sections:
            bounds = self._find_section_bounds(lines, names)
            if not bounds:
                continue
            if self._find_row_index_by_id(lines, bounds[0], bounds[1], task_id) is not None:
                return status
        return None

    def _find_section_bounds(self, lines: list[str], names: tuple[str, ...]) -> tuple[int, int] | None:
        start = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            if any(stripped.startswith(f"## {name}") for name in names):
                start = i
                break
        if start is None:
            return None

        end = len(lines)
        for j in range(start + 1, len(lines)):
            if lines[j].strip().startswith("## "):
                end = j
                break
        return (start, end)

    def _parse_row_id(self, line: str) -> str | None:
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.startswith("|----"):
            return None
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if not parts:
            return None
        cell0 = parts[0]
        if cell0.startswith("~~") and cell0.endswith("~~"):
            cell0 = cell0[2:-2].strip()
        if not cell0:
            return None
        if cell0.startswith("**") and cell0.endswith("**") and len(cell0) > 4:
            cell0 = cell0[2:-2].strip()
        if cell0.startswith("[") and "](" in cell0 and cell0.endswith(")"):
            cell0 = cell0.split("]", 1)[0].lstrip("[").strip()
        if not cell0 or cell0.lower() == "id" or cell0.startswith("*("):
            return None
        if all(ch == "-" for ch in cell0):
            return None
        return cell0

    def _find_row_index_by_id(self, lines: list[str], start: int, end: int, task_id: str) -> int | None:
        for idx in range(start + 1, end):
            row_id = self._parse_row_id(lines[idx])
            if row_id == task_id:
                return idx
        return None

    def _ensure_table_header(self, lines: list[str], start: int, _end: int, header: str, separator: str) -> None:
        insert_at = start + 1
        if insert_at >= len(lines):
            lines.append(header)
            lines.append(separator)
            return
        next_line = lines[insert_at].strip()
        if not next_line.startswith("| ID"):
            lines.insert(insert_at, header)
            lines.insert(insert_at + 1, separator)
        elif insert_at + 1 >= len(lines) or not lines[insert_at + 1].strip().startswith("|----"):
            lines.insert(insert_at + 1, separator)

    def _table_insert_index(self, lines: list[str], start: int, end: int) -> int:
        idx = end
        while idx > start + 1 and not lines[idx - 1].strip():
            idx -= 1
        return idx

    def check_dependencies_satisfied(self, task_id: str, depends: list[str]) -> dict[str, Any]:
        """Check if all dependencies for a task are satisfied (COMPLETED).

        Args:
            task_id: Task ID to check dependencies for
            depends: List of dependency task IDs

        Returns:
            dict with keys:
                - satisfied: bool - True if all dependencies are satisfied
                - unmet: list[str] - List of unmet dependency IDs
                - status_map: dict[str, str] - Map of dependency ID to status
        """
        if not depends:
            return {
                "satisfied": True,
                "unmet": [],
                "status_map": {},
            }

        status_map: dict[str, str | None] = {}
        unmet: list[str] = []

        for dep_id in depends:
            dep_status = self.get_task_status(dep_id)
            status_map[dep_id] = dep_status

            # Dependency is satisfied only if it's COMPLETED
            if dep_status != "COMPLETED":
                unmet.append(dep_id)

        return {
            "satisfied": len(unmet) == 0,
            "unmet": unmet,
            "status_map": {k: (v or "NOT_FOUND") for k, v in status_map.items()},
        }
