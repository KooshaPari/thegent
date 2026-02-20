"""High-performance parallel git operations via plumbing and per-agent index files."""

import os
import random
import subprocess
import time
from pathlib import Path


class GitParallelismManager:
    """Manages parallel git operations using per-agent index files and plumbing."""

    def __init__(self, project_root: Path, agent_id: str) -> None:
        self.project_root = project_root
        self.agent_id = agent_id
        self.git_dir = project_root / ".git"
        self.mesh_root = Path("/tmp/agent-mesh")
        self.agent_index = self.mesh_root / f"index-{agent_id}"

    def _get_ref_hash(self, ref: str) -> str | None:
        """Get current hash for a ref."""
        try:
            return subprocess.check_output(
                ["git", "rev-parse", ref], cwd=self.project_root, text=True
            ).strip()
        except subprocess.CalledProcessError:
            return None

    def ensure_index(self) -> Path:
        """Create or refresh the per-agent index file (TGNT-P6.1)."""
        if not self.mesh_root.exists():
            self.mesh_root.mkdir(parents=True, exist_ok=True, mode=0o1777)

        # Initialize index from current system index if not exists or outdated
        system_index = self.git_dir / "index"
        if not self.agent_index.exists() or (
            system_index.exists() and system_index.stat().st_mtime > self.agent_index.stat().st_mtime
        ):
            import shutil

            if system_index.exists():
                shutil.copy2(system_index, self.agent_index)
            else:
                # Create empty index if no system index
                open(self.agent_index, "wb").close()

        return self.agent_index

    def stage_files(self, files: list[str]) -> bool:
        """Stage specific files using the agent's index (TGNT-P6.4)."""
        self.ensure_index()
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(self.agent_index)

        try:
            # git add -- <files>
            subprocess.run(
                ["git", "add", "--", *files], cwd=self.project_root, env=env, check=True, capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def create_commit_from_index(self, message: str, parent_ref: str = "HEAD") -> str | None:
        """Git plumbing commit pipeline: hash -> tree -> commit (TGNT-P6.2)."""
        self.ensure_index()
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(self.agent_index)

        try:
            # 1. write-tree
            tree_hash = subprocess.check_output(
                ["git", "write-tree"], cwd=self.project_root, env=env, text=True
            ).strip()

            # 2. get parent commit hash
            parent_hash = subprocess.check_output(
                ["git", "rev-parse", parent_ref], cwd=self.project_root, text=True
            ).strip()

            # 3. commit-tree
            commit_hash = subprocess.check_output(
                ["git", "commit-tree", tree_hash, "-p", parent_hash, "-m", message],
                cwd=self.project_root,
                env=env,
                text=True,
            ).strip()

            return commit_hash
        except subprocess.CalledProcessError:
            return None

    def update_ref_cas(self, ref: str, new_hash: str, old_hash: str) -> bool:
        """CAS (Compare-And-Swap) ref update with backoff + jitter (TGNT-P6.3)."""
        max_retries = 5
        base_delay = 0.1

        for i in range(max_retries):
            try:  # noqa: PERF203 -- intentional retry loop, max 5 iterations
                # git update-ref <ref> <new_hash> <old_hash>
                # Fails if <ref> is not currently <old_hash>
                subprocess.run(
                    ["git", "update-ref", ref, new_hash, old_hash],
                    cwd=self.project_root,
                    check=True,
                    capture_output=True,
                )
                return True
            except subprocess.CalledProcessError:
                # Collision detected or ref moved. Retry with jitter.
                delay = base_delay * (2**i) + random.uniform(0, 0.1)
                time.sleep(delay)

                # Refresh old_hash for next attempt
                old_hash = self._get_ref_hash(ref)
                if old_hash is None:
                    return False

        return False

    def get_agent_status(self) -> str:
        """Show per-agent staged changes (TGNT-P6.5)."""
        self.ensure_index()
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(self.agent_index)

        try:
            # git status --short using the agent's index
            # Note: This compares agent's index with worktree
            status = subprocess.check_output(["git", "status", "--short"], cwd=self.project_root, env=env, text=True)
            return status
        except subprocess.CalledProcessError:
            return "Error retrieving agent status"


def harness_git_status_view(agent_id: str) -> None:
    """Entry point for 'harness git status' (TGNT-P6.5)."""
    manager = GitParallelismManager(Path.cwd(), agent_id)
    status = manager.get_agent_status()
