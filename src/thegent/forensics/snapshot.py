"""WP-12001: Forensic snapshotting for deep debugging and audit."""

import orjson as json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path

_log = logging.getLogger(__name__)

# Native Git support (required)
try:
    import thegent_git
except ImportError:
    raise ImportError("thegent-git not available - install with: pip install thegent-git")


class ForensicSnapshotter:
    """Captures detailed system and project state snapshots."""

    def __init__(self, session_dir: Path) -> None:
        self.snapshot_dir = session_dir / "forensics"
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def capture_pre_run(self, run_id: str, project_root: Path) -> Path:
        """Capture state before a run."""
        snapshot = {
            "run_id": run_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "phase": "pre-run",
            "env": {
                k: v for k, v in os.environ.items() if not k.lower().endswith(("key", "token", "secret", "password"))
            },
            "git_branch": self._get_git_branch(project_root),
            "git_status": self._get_git_status(project_root),
        }
        path = self.snapshot_dir / f"{run_id}_pre.json"
        path.write_text(json.dumps(snapshot, option=json.OPT_INDENT_2).decode(), encoding="utf-8")
        return path

    def capture_post_run(self, run_id: str, project_root: Path, exit_code: int) -> Path:
        """Capture state after a run, including git diff."""
        snapshot = {
            "run_id": run_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "phase": "post-run",
            "exit_code": exit_code,
            "git_diff": self._get_git_diff(project_root),
        }
        path = self.snapshot_dir / f"{run_id}_post.json"
        path.write_text(json.dumps(snapshot, option=json.OPT_INDENT_2).decode(), encoding="utf-8")
        return path

    def _get_git_branch(self, root: Path) -> str:
        """Get git branch using native Rust."""
        res = thegent_git.get_status(str(root))
        return str(res.get("branch", "n/a")) if res else "n/a"

    def _get_git_status(self, root: Path) -> str:
        """Get git status using native Rust."""
        res = thegent_git.get_status(str(root))
        if res:
            return (
                f"staged:{res.get('staged', 0)} unstaged:{res.get('unstaged', 0)} untracked:{res.get('untracked', 0)}"
            )
        return "n/a"

    def _get_git_diff(self, root: Path) -> str:
        """Get git diff using native Rust."""
        # Note: get_diff not yet implemented in thegent-git
        _log.warning("get_diff not implemented in thegent-git yet")
        return ""
