"""High-performance parallel git operations for the agent mesh."""

import json
import os
import random
import subprocess
import time
from pathlib import Path


class GitParallelismManager:
    """Manages parallel git operations using per-agent index files and plumbing (SCLI-P4.1–P4.2)."""

    def __init__(self, project_root: Path, agent_id: str, mesh_root: Path = Path("/tmp/agent-mesh")) -> None:  # noqa: S108 -- intentional platform temp dir for agent mesh IPC
        self.project_root = project_root
        self.agent_id = agent_id
        self.git_dir = project_root / ".git"
        self.mesh_root = mesh_root
        self.agent_index = mesh_root / "indices" / f"index-{agent_id}"
        self.agent_index.parent.mkdir(parents=True, exist_ok=True, mode=0o1777)

    def _get_ref_hash(self, ref: str) -> str | None:
        """Get current hash for a ref."""
        try:
            return subprocess.check_output(["git", "rev-parse", ref], cwd=self.project_root, text=True).strip()
        except subprocess.CalledProcessError:
            return None

    def _index_lock_path(self) -> Path:
        """Return .git/index.lock path for this repository."""
        return self.git_dir / "index.lock"

    def wait_for_index_lock(self, timeout_s: float = 8.0, poll_s: float = 0.2) -> bool:
        """Wait briefly for index.lock to clear.

        Returns True when lock is clear, False on timeout.
        """
        lock_path = self._index_lock_path()
        deadline = time.time() + timeout_s
        while lock_path.exists():
            if time.time() >= deadline:
                return False
            time.sleep(poll_s)
        return True

    def ensure_index(self) -> Path:
        """Create or refresh the per-agent index file (SCLI-P4.1)."""
        system_index = self.git_dir / "index"

        # Initialize index from current system index if not exists or outdated
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
        """Stage specific files using the agent's index (SCLI-P4.4)."""
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
        """Git plumbing commit pipeline: hash -> tree -> commit (SCLI-P4.2)."""
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
                    capture_output=True,
                )
                return True
            except subprocess.CalledProcessError:  # noqa: PERF203 -- intentional CAS retry loop, max 5 iterations
                # Collision detected or ref moved. Retry with jitter.
                delay = base_delay * (2**i) + random.uniform(0, 0.1)  # noqa: S311 -- jitter for CAS backoff, not cryptographic
                time.sleep(delay)

                # Refresh old_hash for next attempt
                refreshed = self._get_ref_hash(ref)
                if refreshed is None:
                    return False
                old_hash = refreshed

        return False

    def staged_files(self) -> list[str]:
        """Return staged files from this agent's private index."""
        self.ensure_index()
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(self.agent_index)
        try:
            out = subprocess.check_output(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.project_root,
                env=env,
                text=True,
            )
            return [line.strip() for line in out.splitlines() if line.strip()]
        except subprocess.CalledProcessError:
            return []

    def changed_files_between(self, older: str, newer: str) -> list[str]:
        """Return files changed between two refs/hashes."""
        try:
            out = subprocess.check_output(
                ["git", "diff", "--name-only", older, newer],
                cwd=self.project_root,
                text=True,
            )
            return [line.strip() for line in out.splitlines() if line.strip()]
        except subprocess.CalledProcessError:
            return []

    def related_overlap(self, ours: list[str], theirs: list[str]) -> list[str]:
        """Return sorted overlap between two file lists."""
        ours_set = set(ours)
        theirs_set = set(theirs)
        return sorted(ours_set.intersection(theirs_set))

    def queue_commit_conflict(
        self,
        ref: str,
        reason: str,
        ours: list[str],
        theirs: list[str],
        overlap: list[str],
        old_hash: str | None = None,
        new_hash: str | None = None,
    ) -> Path:
        """Append a conflict record to per-project git conflict queue."""
        queue_path = self.project_root / ".thegent" / "git-conflict-queue.jsonl"
        queue_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": int(time.time()),
            "agent_id": self.agent_id,
            "ref": ref,
            "reason": reason,
            "ours": ours,
            "theirs": theirs,
            "overlap": overlap,
            "old_hash": old_hash or "",
            "new_hash": new_hash or "",
        }
        with queue_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return queue_path

    def get_agent_status(self) -> str:
        """Show per-agent staged changes (SCLI-P4.5)."""
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
    """Entry point for 'harness git status' (TGNT-P6.5 / SCLI-P4.5)."""
    manager = GitParallelismManager(Path.cwd(), agent_id)
    status = manager.get_agent_status()
    print(status)  # noqa: T201 -- intentional CLI output
