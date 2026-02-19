"""WP-9003: Teammate Coordination Protocol.
Handles inter-agent communication, idle detection, and task completion hooks.
"""

import json
import logging
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from thegent.team.manager import TeamManager

_log = logging.getLogger(__name__)


class TeamCoordinator:
    """Coordinates teammates during a multi-agent run."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.tm = TeamManager(session_dir)

    def detect_idle(self, stdout: str) -> bool:
        """WP-9003: Detect if a teammate agent is idle and needs input.
        Looks for common patterns like 'waiting for input', 'how can I help?', etc.
        """
        # Common idle patterns for various agents
        idle_patterns = [
            r"how can i help you today\?",
            r"waiting for your input\.\.\.",
            r"awaiting next prompt",
            r"enter your request:",
            r"\[idle\]",
        ]

        combined_pattern = "|".join(idle_patterns)
        if re.search(combined_pattern, stdout, re.IGNORECASE):
            return True

        # If output ends with a question mark and is short, it might be idle
        last_line = stdout.strip().split("\n")[-1] if stdout.strip() else ""
        if len(last_line) < 100 and last_line.endswith("?"):
            return True

        return False

    def handle_task_completed(self, team_id: str, task_id: str, result: str) -> None:
        """WP-9003: Handle a task completion event from a teammate."""
        updates = {"status": "completed", "completed_at": datetime.now(UTC).isoformat(), "result": result}
        self.tm.update_task(team_id, task_id, updates)
        _log.info("Task %s completed by teammate in team %s", task_id, team_id)

    def broadcast_message(self, team_id: str, sender: str, message: str) -> None:
        """WP-9003: Broadcast a message to all teammates in a team."""
        # This would typically involve writing to a shared 'bus' or 'inbox' for each agent
        inbox_dir = self.session_dir / "teams" / team_id / "inboxes"
        inbox_dir.mkdir(parents=True, exist_ok=True)

        team_meta_path = self.tm.teams_dir / f"{team_id}.json"
        if not team_meta_path.exists():
            return

        team_meta = json.loads(team_meta_path.read_text(encoding="utf-8"))
        teammates = team_meta.get("teammates", [])

        for teammate in teammates:
            if teammate == sender:
                continue
            t_inbox = inbox_dir / f"{teammate}.jsonl"
            entry = {"ts": datetime.now(UTC).isoformat(), "sender": sender, "message": message}
            with t_inbox.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

        _log.info("Broadcast from %s to team %s: %s", sender, team_id, message[:50])

    def call_vote(self, team_id: str, caller: str, subject: str, options: list[str]) -> str:
        """WP-9003: Call a vote among teammates."""
        vote_id = f"vote_{uuid.uuid4().hex[:6]}"
        vote_meta = {
            "id": vote_id,
            "caller": caller,
            "subject": subject,
            "options": options,
            "votes": {},
            "status": "open",
            "created_at": datetime.now(UTC).isoformat(),
        }
        vote_path = self.session_dir / "teams" / team_id / "votes" / f"{vote_id}.json"
        vote_path.parent.mkdir(parents=True, exist_ok=True)
        vote_path.write_text(json.dumps(vote_meta), encoding="utf-8")

        self.broadcast_message(
            team_id,
            caller,
            f"VOTE REQUIRED: {subject}. Options: {', '.join(options)}. Vote with 'thegent team vote {team_id} {vote_id} <option>'",
        )
        return vote_id

    def cast_vote(self, team_id: str, vote_id: str, voter: str, option: str) -> bool:
        """WP-9003: Cast a vote."""
        vote_path = self.session_dir / "teams" / team_id / "votes" / f"{vote_id}.json"
        if not vote_path.exists():
            return False

        vote_meta = json.loads(vote_path.read_text(encoding="utf-8"))
        if vote_meta["status"] != "open":
            return False

        if option not in vote_meta["options"]:
            return False

        vote_meta["votes"][voter] = option
        vote_path.write_text(json.dumps(vote_meta), encoding="utf-8")
        return True

    def get_vote_result(self, team_id: str, vote_id: str) -> dict[str, Any]:
        """WP-9003: Get current results of a vote."""
        vote_path = self.session_dir / "teams" / team_id / "votes" / f"{vote_id}.json"
        if not vote_path.exists():
            return {}
        return json.loads(vote_path.read_text(encoding="utf-8"))

    def wait_for_task(self, team_id: str, task_id: str, timeout: int = 300) -> dict[str, Any | None]:
        """WP-9003: Wait for a task to be completed by a teammate."""
        import time

        start_time = time.time()
        while time.time() - start_time < timeout:
            tasks = self.tm.list_tasks(team_id)
            for t in tasks:
                if t["id"] == task_id and t["status"] == "completed":
                    return t
            time.sleep(5)
        return None
