"""WP-12001: Forensic snapshotting for deep debugging and audit."""

import json
import logging
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

_log = logging.getLogger(__name__)

# BKM-06: Native Git support
HAS_NATIVE_GIT = False
try:
    import thegent_git

    HAS_NATIVE_GIT = True
except ImportError:
    pass


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
        path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
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
        path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
        return path

    def _get_git_branch(self, root: Path) -> str:
        if HAS_NATIVE_GIT:
            try:
                res = thegent_git.get_status(str(root))
                return res.get("branch", "n/a")
            except Exception as e:
                _log.debug("native git branch failed: %s", e)

        try:
            return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root).decode().strip()
        except Exception:
            return "n/a"

    def _get_git_status(self, root: Path) -> str:
        if HAS_NATIVE_GIT:
            try:
                # We could return a structured dict, but existing code expects a string summary
                res = thegent_git.get_status(str(root))
                return f"staged:{res['staged']} unstaged:{res['unstaged']} untracked:{res['untracked']}"
            except Exception as e:
                _log.debug("native git status failed: %s", e)

        try:
            return subprocess.check_output(["git", "status", "--short"], cwd=root).decode().strip()
        except Exception:
            return "n/a"

    def _get_git_diff(self, root: Path) -> str:
        if HAS_NATIVE_GIT:
            try:
                return thegent_git.get_diff(str(root), "HEAD")
            except Exception as e:
                _log.debug("native git diff failed: %s", e)

        try:
            return subprocess.check_output(["git", "diff", "HEAD"], cwd=root).decode().strip()
        except Exception:
            return "n/a"
