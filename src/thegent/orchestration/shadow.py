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

                # Create branch if it doesn't exist
                subprocess.run(["git", "branch", branch_name], cwd=self.project_root, capture_output=True, check=False)

                # Add worktree
                subprocess.run(
                    ["git", "worktree", "add", str(self.shadow_root), branch_name], cwd=self.project_root, check=True
                )
                return True
            # Fallback: Deep copy or symlink-based shadow
            # For now, let's do a copy for safety
            shutil.copytree(self.project_root, self.shadow_root, symlinks=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create shadow workspace: {e}")
            return False

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
        return subprocess.run(cmd, cwd=self.shadow_root, capture_output=True, text=True)
