import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class ShadowWorkspace:
    """MTSP-12: Shadow Workspace for isolated planning and testing.
    Uses git worktree for a true isolated branch/workspace, or symlink-shadow as fallback.
    """

    def __init__(self, project_root: Path, shadow_id: str) -> None:
        self.project_root = project_root
        self.shadow_id = shadow_id
        self.shadow_root = project_root.parent / f".shadow-{shadow_id}"

    def create(self, branch: str | None = None) -> bool:
        """Create a shadow workspace using git worktree."""
        if self.shadow_root.exists():
            logger.warning(f"Shadow root {self.shadow_root} already exists. Cleaning up...")
            self.destroy()

        try:
            # Check if it's a git repo
            if (self.project_root / ".git").exists():
                # Use git worktree for best isolation
                branch_name = branch or f"shadow-{self.shadow_id}"

                # Ensure we are not on the branch already
                current_branch = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    check=False,
                ).stdout.strip()

                if current_branch == branch_name:
                    logger.error(f"Cannot create shadow workspace: main project is already on branch {branch_name}")
                    return False

                # Create branch if it doesn't exist
                subprocess.run(["git", "branch", branch_name], cwd=self.project_root, capture_output=True, check=False)

                # Add worktree
                # MTSP-12: Use --no-checkout for faster creation if needed, but here we usually want the files
                res = subprocess.run(
                    ["git", "worktree", "add", str(self.shadow_root), branch_name],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if res.returncode != 0:
                    logger.error(f"Failed to add worktree: {res.stderr}")
                    # Try to repair if it's an "already registered" error
                    if "already registered" in res.stderr:
                        subprocess.run(["git", "worktree", "prune"], cwd=self.project_root, check=False)
                        res = subprocess.run(
                            ["git", "worktree", "add", str(self.shadow_root), branch_name],
                            cwd=self.project_root,
                            capture_output=True,
                            text=True,
                            check=False,
                        )

                    if res.returncode != 0:
                        return False

                # MTSP-12: Isolate Claude Code state (dex)
                # Setting this here allows agents running within this workspace to have isolated histories
                claude_config = self.shadow_root / ".claude_config"
                claude_config.mkdir(parents=True, exist_ok=True)

                return True
            # Fallback: Deep copy or symlink-based shadow
            # For now, let's do a copy for safety
            shutil.copytree(self.project_root, self.shadow_root, symlinks=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create shadow workspace: {e}")
            return False

    def get_env(self) -> dict[str, str]:
        """Return environment variables for isolating tools within the shadow workspace."""
        claude_config = self.shadow_root / ".claude_config"
        return {
            "CLAUDE_CONFIG_DIR": str(claude_config),
            "PROJECT_DIR": str(self.shadow_root),  # Override for our shims
        }

    def destroy(self) -> bool:
        """Destroy the shadow workspace and clean up git references."""
        if not self.shadow_root.exists():
            return True

        try:
            if (self.project_root / ".git").exists():
                # Remove git worktree
                subprocess.run(
                    ["git", "worktree", "remove", "--force", str(self.shadow_root)], cwd=self.project_root, check=True
                )
                # Optionally delete the branch
                # subprocess.run(["git", "branch", "-D", f"shadow-{self.shadow_id}"], cwd=self.project_root, check=False)
            else:
                shutil.rmtree(self.shadow_root)
            return True
        except Exception as e:
            logger.error(f"Failed to destroy shadow workspace: {e}")
            # Fallback: just delete the dir if it's orphaned
            if self.shadow_root.exists():
                shutil.rmtree(self.shadow_root, ignore_errors=True)
            return False

    def run(self, cmd: list[str]) -> subprocess.CompletedProcess:
        """Run a command within the shadow workspace."""
        return subprocess.run(cmd, cwd=self.shadow_root, capture_output=True, text=True, check=False)

    def merge_back(self) -> bool:
        """Merge changes from the shadow workspace back to the main project."""
        if not (self.project_root / ".git").exists():
            # Fallback: simple copy back (not recommended for git repos)
            logger.info("Merging back via file copy (non-git fallback)")
            shutil.copytree(self.shadow_root, self.project_root, dirs_exist_ok=True)
            return True

        try:
            branch_name = f"shadow-{self.shadow_id}"
            logger.info(f"Merging branch {branch_name} back to main project...")

            # Ensure all changes are committed in the shadow workspace
            self.run(["git", "add", "."])
            res = self.run(["git", "commit", "-m", f"Shadow changes from {self.shadow_id}"])
            if res.returncode != 0 and "nothing to commit" not in res.stdout:
                logger.warning(f"Commit in shadow failed: {res.stderr}")
                # We proceed anyway, maybe there were no changes

            # In the main project, merge the branch
            res = subprocess.run(
                ["git", "merge", branch_name], cwd=self.project_root, capture_output=True, text=True, check=False
            )
            if res.returncode == 0:
                logger.info("Successfully merged shadow changes.")
                return True
            logger.error(f"Merge conflict or error during shadow merge: {res.stderr}")
            return False
        except Exception as e:
            logger.error(f"Failed to merge back shadow workspace: {e}")
            return False
