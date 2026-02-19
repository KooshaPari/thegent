"""WP-16003: ShareCLI Coordination Bridge for multi-agent tasks."""

import os
from pathlib import Path
from typing import Any

from thegent.config import ThegentSettings


class ShareCLIBridge:
    """Bridges thegent to ShareCLI's Phase 11 task coordination layer."""

    def __init__(self, settings: ThegentSettings | None = None) -> None:
        # Resolve ShareCLI root from settings
        if settings is None:
            settings = ThegentSettings()
        harness_root = settings.harness_root
        self.task_dir = Path(harness_root) / "var" / "tasks"
        self.intent_dir = Path(harness_root) / "var" / "intents"

    def is_available(self) -> bool:
        """Check if ShareCLI coordination layer is initialized."""
        return self.task_dir.parent.exists()

    def create_shared_task(self, task_id: str, description: str, depends_on: list[str] | None = None) -> bool:
        """WP-16003: Create a task in ShareCLI's global task list."""
        if not self.is_available():
            return False

        self.task_dir.mkdir(parents=True, exist_ok=True)
        task_file = self.task_dir / task_id

        from datetime import datetime

        content = [
            f"id={task_id}",
            f"description={description}",
            f"depends_on={','.join(depends_on or [])}",
            "status=pending",
            "assigned_to=",
            f"created_at={datetime.now().isoformat()}",
            "completed_at=",
        ]

        task_file.write_text("\n".join(content) + "\n")
        return True

    def broadcast_intent(self, agent_id: str, intent_type: str, target: str) -> bool:
        """WP-16003: Broadcast operation intent to the mesh."""
        if not self.is_available():
            return False

        self.intent_dir.mkdir(parents=True, exist_ok=True)
        intent_id = f"{os.getpid()}_{agent_id}_{intent_type}"
        intent_file = self.intent_dir / intent_id

        from datetime import datetime

        content = [
            f"agent={agent_id}",
            f"type={intent_type}",
            f"target={target}",
            f"started={int(datetime.now().timestamp())}",
            "status=active",
        ]

        intent_file.write_text("\n".join(content) + "\n")
        return True

    def get_session_state(self, session_id: str) -> dict[str, Any]:
        """WP-16003: Deep inspection of session state from ShareCLI var/ dirs."""
        state: dict[str, Any] = {"claims": [], "intents": [], "tasks": []}
        if not self.is_available():
            return state

        # Check for intents from this session (PID match or tag match)
        try:
            for f in self.intent_dir.glob("*"):
                content = f.read_text()
                if session_id in content or f.name.startswith(session_id):
                    state["intents"].append(content.splitlines())
        except Exception:
            pass

        # Check for tasks claimed by this session
        try:
            for f in self.task_dir.glob("*"):
                content = f.read_text()
                if f"assigned_to={session_id}" in content:
                    state["tasks"].append(content.splitlines())
        except Exception:
            pass

        return state


class SmartMerge:
    """WP-16004: AST-aware conflict resolution using Mergiraf."""

    def __init__(self) -> None:
        import shutil

        self.mergiraf_path = shutil.which("mergiraf")

    def merge_files(self, base: Path, ours: Path, theirs: Path, output: Path) -> bool:
        """Attempt an AST-aware merge using Mergiraf or standard git merge-file."""
        import subprocess

        if self.mergiraf_path:
            # Mergiraf: mergiraf merge --git %O %A %B -s %S -p %P
            cmd = [self.mergiraf_path, "merge", "--git", str(base), str(ours), str(theirs), "-p", str(output)]
        else:
            # Fallback: git merge-file -p ours base theirs
            cmd = ["git", "merge-file", "-p", str(ours), str(base), str(theirs)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if not self.mergiraf_path:
                output.write_text(result.stdout)

            return result.returncode == 0
        except Exception:
            return False
