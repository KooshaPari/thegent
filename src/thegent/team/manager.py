"""WP-6008: Multi-agent team management and task coordination."""

import orjson as json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


class TeamManager:
    """Manages multi-agent teams and their shared task lists."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.teams_dir = session_dir / "teams"
        self.teams_dir.mkdir(parents=True, exist_ok=True)

    def create_team(self, name: str, leader: str, teammates: list[str]) -> str:
        """Create a new team and return its ID."""
        team_id = f"team_{uuid.uuid4().hex[:8]}"
        team_meta = {
            "id": team_id,
            "name": name,
            "leader": leader,
            "teammates": teammates,
            "created_at": datetime.now(UTC).isoformat(),
            "status": "active",
        }
        (self.teams_dir / f"{team_id}.json").write_text(json.dumps(team_meta).decode().decode(), encoding="utf-8")

        # Initialize empty task list
        (self.teams_dir / f"{team_id}_tasks.jsonl").touch()

        return team_id

    def add_task(self, team_id: str, title: str, description: str, dependencies: list[str] | None = None) -> str:
        """Add a task to the team's shared list."""
        if dependencies is None:
            dependencies = []
        task_id = f"task_{uuid.uuid4().hex[:6]}"
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "status": "pending",
            "assigned_to": None,
            "dependencies": dependencies,
            "created_at": datetime.now(UTC).isoformat(),
        }
        with (self.teams_dir / f"{team_id}_tasks.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(task).decode().decode() + "\n")
        return task_id

    def list_tasks(self, team_id: str) -> list[dict[str, Any]]:
        """List all tasks for a team."""
        tasks_file = self.teams_dir / f"{team_id}_tasks.jsonl"
        if not tasks_file.exists():
            return []

        tasks = []
        with tasks_file.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    tasks.append(json.loads(line))
                except Exception:  # noqa: PERF203 - intentional per-item error handling
                    continue
        return tasks

    def assign_task(self, team_id: str, task_id: str, agent_id: str) -> bool:
        """Assign a task to an agent."""
        return self.update_task(team_id, task_id, {"assigned_to": agent_id, "status": "in_progress"})

    def update_task(self, team_id: str, task_id: str, updates: dict[str, Any]) -> bool:
        """Update a task's fields."""
        tasks = self.list_tasks(team_id)
        updated = False
        new_tasks = []
        for t in tasks:
            if t["id"] == task_id:
                t.update(updates)
                updated = True
            new_tasks.append(t)

        if updated:
            with (self.teams_dir / f"{team_id}_tasks.jsonl").open("w", encoding="utf-8") as f:
                for t in new_tasks:
                    f.write(json.dumps(t).decode().decode() + "\n")
        return updated
