"""High-performance parallel git operations for the agent mesh."""

import os
import random
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class GitParallelismManager:
    """Manages parallel git operations using per-agent index files and plumbing (SCLI-P4.1–P4.2)."""

    def __init__(self, project_root: Path, agent_id: str, mesh_root: Path = Path("/tmp/agent-mesh")) -> None:
        self.project_root = project_root
        self.agent_id = agent_id
        self.git_dir = project_root / ".git"
        self.mesh_root = mesh_root
        self.agent_index = mesh_root / "indices" / f"index-{agent_id}"
        self.agent_index.parent.mkdir(parents=True, exist_ok=True, mode=0o1777)

    def ensure_index(self) -> Path:
        """Create or refresh the per-agent index file (SCLI-P4.1)."""
        system_index = self.git_dir / "index"

        # Initialize index from current system index if not exists or outdated
        if not self.agent_index.exists() or (system_index.exists() and system_index.stat().st_mtime > self.agent_index.stat().st_mtime):
            import shutil
            if system_index.exists():
                shutil.copy2(system_index, self.agent_index)
            else:
                # Create empty index if no system index
                open(self.agent_index, "wb").close()

        return self.agent_index

    def stage_files(self, files: list[str]) -> bool:
        """Stage specific files using the agent's index (SCLI-P4.4)."""
        self.ensure_index()
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(self.agent_index)

        try:
            # git add -- <files>
            subprocess.run(
                ["git", "add", "--", *files],
                cwd=self.project_root,
                env=env,
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def create_commit_from_index(self, message: str, parent_ref: str = "HEAD") -> str | None:
        """Git plumbing commit pipeline: hash -> tree -> commit (SCLI-P4.2)."""
        self.ensure_index()
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(self.agent_index)

        try:
            # 1. write-tree
            tree_hash = subprocess.check_output(
                ["git", "write-tree"],
                cwd=self.project_root,
                env=env,
                text=True
            ).strip()

            # 2. get parent commit hash
            parent_hash = subprocess.check_output(
                ["git", "rev-parse", parent_ref],
                cwd=self.project_root,
                text=True
            ).strip()

            # 3. commit-tree
            commit_hash = subprocess.check_output(
                ["git", "commit-tree", tree_hash, "-p", parent_hash, "-m", message],
                cwd=self.project_root,
                env=env,
                text=True
            ).strip()

            return commit_hash
        except subprocess.CalledProcessError:
            return None

    def update_ref_cas(self, ref: str, new_hash: str, old_hash: str) -> bool:
        """CAS (Compare-And-Swap) ref update with backoff + jitter (SCLI-P4.3)."""
        max_retries = 5
        base_delay = 0.1

        for i in range(max_retries):
            try:
                # git update-ref <ref> <new_hash> <old_hash>
                # Fails if <ref> is not currently <old_hash>
                subprocess.run(
                    ["git", "update-ref", ref, new_hash, old_hash],
                    cwd=self.project_root,
                    check=True,
                    capture_output=True
                )
                return True
            except subprocess.CalledProcessError:
                # Collision detected or ref moved. Retry with jitter.
                delay = base_delay * (2 ** i) + random.uniform(0, 0.1)
                time.sleep(delay)

                # Refresh old_hash for next attempt
                try:
                    old_hash = subprocess.check_output(
                        ["git", "rev-parse", ref],
                        cwd=self.project_root,
                        text=True
                    ).strip()
                except subprocess.CalledProcessError:
                    # Ref might have been deleted?
                    return False

        return False

    def get_agent_status(self) -> str:
        """Show per-agent staged changes (SCLI-P4.5)."""
        self.ensure_index()
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(self.agent_index)

        try:
            # git status --short using the agent's index
            # Note: This compares agent's index with worktree
            status = subprocess.check_output(
                ["git", "status", "--short"],
                cwd=self.project_root,
                env=env,
                text=True
            )
            return status
        except subprocess.CalledProcessError:
            return "Error retrieving agent status"
