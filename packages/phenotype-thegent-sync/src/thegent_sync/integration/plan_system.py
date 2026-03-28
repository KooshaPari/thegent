"""Integration with PLAN.md and plan status tracking."""

import re
from pathlib import Path

__all__ = ["PlanSystemIntegration"]


class PlanSystemIntegration:
    """Integrate with PLAN.md and plan status.

    This class handles integration with the project plan system,
    including parsing PLAN.md, tracking task status, and managing dependencies.

    Examples:
        >>> integration = PlanSystemIntegration()
        >>> tasks = integration.get_tasks_for_phase("Phase 1")
        >>> integration.update_task_status("task-1.1", "completed")
        >>> blocked = integration.get_blocked_tasks()
    """

    def __init__(
        self,
        plan_file: Path | None = None,
        plan_status_file: Path | None = None,
    ) -> None:
        """Initialize plan system integration.

        Args:
            plan_file: Path to PLAN.md file. Defaults to PLAN.md
            plan_status_file: Path to PLAN_STATUS.md file.
                              Defaults to docs/reference/PLAN_STATUS.md
        """
        if plan_file is None:
            plan_file = Path("PLAN.md")

        if plan_status_file is None:
            plan_status_file = Path("docs/reference/PLAN_STATUS.md")

        self.plan_file = plan_file
        self.plan_status_file = plan_status_file
        self.plan_data: dict = {
            "phases": [],
            "tasks": [],
        }
        self.plan_status: dict[str, dict] = {}
        self._load_plan()
        self._load_plan_status()

    def _load_plan(self) -> None:
        """Load PLAN.md."""
        if not self.plan_file.exists():
            return

        try:
            content = self.plan_file.read_text(encoding="utf-8")

            # Parse plan structure
            # Extract phases and tasks
            phases = []
            tasks = []

            # Find phase headers
            phase_pattern = r"##\s+Phase\s+(\d+):\s*(.+?)(?=\n##|\Z)"
            phase_matches = re.finditer(phase_pattern, content, re.DOTALL | re.IGNORECASE)

            for match in phase_matches:
                phase_num = match.group(1)
                phase_title = match.group(2).strip().split("\n")[0]
                phase_content = match.group(2)

                phases.append(
                    {
                        "number": int(phase_num),
                        "title": phase_title,
                        "content": phase_content,
                    }
                )

                # Extract tasks from phase
                task_pattern = r"-?\s*\[([ x])\]\s*(.+?)(?=\n-|\Z)"
                task_matches = re.finditer(task_pattern, phase_content, re.MULTILINE)

                for task_match in task_matches:
                    checked = task_match.group(1) == "x"
                    task_desc = task_match.group(2).strip()

                    # Extract task ID if present
                    task_id_match = re.search(r"([A-Z]+-\d+(?:\.\d+)?)", task_desc)
                    task_id = task_id_match.group(1) if task_id_match else None

                    tasks.append(
                        {
                            "id": task_id,
                            "phase": int(phase_num),
                            "description": task_desc,
                            "completed": checked,
                        }
                    )

            self.plan_data = {
                "phases": phases,
                "tasks": tasks,
            }
        except OSError:
            # Load failed, keep empty data
            pass

    def _load_plan_status(self) -> None:
        """Load plan status from PLAN_STATUS.md."""
        if not self.plan_status_file.exists():
            return

        try:
            content = self.plan_status_file.read_text(encoding="utf-8")

            # Parse status table
            lines = content.split("\n")
            in_table = False
            headers = []

            for line in lines:
                line = line.strip()

                # Check for table start
                if line.startswith("|") and "Task ID" in line:
                    in_table = True
                    headers = [h.strip() for h in line.split("|")[1:-1]]
                    continue

                # Check for table separator
                if in_table and line.startswith("|") and "---" in line:
                    continue

                # Parse table row
                if in_table and line.startswith("|"):
                    cells = [c.strip() for c in line.split("|")[1:-1]]
                    if len(cells) == len(headers):
                        row = dict(zip(headers, cells, strict=False))
                        task_id = row.get("Task ID")
                        if task_id:
                            self.plan_status[task_id] = row

                # Stop at next section
                if in_table and not line.startswith("|") and line.startswith("#"):
                    break
        except OSError:
            # Load failed, keep empty status
            pass

    def update_task_status(self, task_id: str, status: str) -> None:
        """Update task status in plan.

        Updates both PLAN.md (if task is in plan) and PLAN_STATUS.md.

        Args:
            task_id: ID of task to update
            status: New status (e.g., "completed", "in_progress", "pending")
        """
        # Update in-memory status
        if task_id not in self.plan_status:
            self.plan_status[task_id] = {}

        self.plan_status[task_id]["Status"] = status

        # Update task in plan data
        for task in self.plan_data.get("tasks", []):
            if task.get("id") == task_id:
                task["completed"] = status == "completed"
                break

        # Save changes (simplified - full implementation would preserve formatting)
        self._save_plan_status()

    def get_tasks_for_phase(self, phase: str) -> list[dict]:
        """Get tasks for specific phase.

        Args:
            phase: Phase identifier (e.g., "Phase 1" or "1")

        Returns:
            List of task dictionaries
        """
        # Extract phase number
        phase_num_match = re.search(r"(\d+)", phase)
        if not phase_num_match:
            return []

        phase_num = int(phase_num_match.group(1))

        # Filter tasks by phase
        return [task for task in self.plan_data.get("tasks", []) if task.get("phase") == phase_num]

    def get_blocked_tasks(self) -> list[dict]:
        """Get tasks blocked by incomplete dependencies.

        Returns:
            List of blocked task dictionaries
        """
        blocked = []

        for task in self.plan_data.get("tasks", []):
            task_id = task.get("id")
            if not task_id:
                continue

            # Check if task has dependencies
            # Dependencies are typically in format "Depends: task-1.1, task-1.2"
            description = task.get("description", "")
            dep_match = re.search(r"Depends[:\s]+(.+)", description, re.IGNORECASE)

            if dep_match:
                dep_str = dep_match.group(1)
                # Extract dependency IDs
                dep_ids = [d.strip() for d in re.split(r"[,\s]+", dep_str) if d.strip()]

                # Check if any dependency is incomplete
                for dep_id in dep_ids:
                    dep_task = next((t for t in self.plan_data.get("tasks", []) if t.get("id") == dep_id), None)

                    if dep_task and not dep_task.get("completed"):
                        blocked.append(task)
                        break

        return blocked

    def _save_plan_status(self) -> None:
        """Save plan status back to PLAN_STATUS.md."""
        # This is a simplified version - full implementation would
        # need to preserve formatting and other content
        # For now, we'll just update the in-memory representation
        # Full file rewrite would be implemented separately
