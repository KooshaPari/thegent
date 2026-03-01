"""Phase 16: Sandboxing implementation.
Includes bubblewrap (Linux) and seatbelt (macOS) profile generation, and 5-tier autonomy.
"""

import logging
import os
import platform
from pathlib import Path
from typing import ClassVar

from thegent_audit.security.macos_sandbox import MacOSSandbox, SandboxLevel

logger = logging.getLogger(__name__)


class SandboxProvider:
    """Generates and executes sandbox profiles."""

    def __init__(self) -> None:
        self.system = platform.system()

    def wrap_command(self, command: list[str], tier: int = 1) -> list[str]:
        """Wrap command with sandbox according to autonomy tier."""
        if self.system == "Linux":
            return self._bwrap_wrap(command, tier)
        if self.system == "Darwin":
            return self._seatbelt_wrap(command, tier)
        return command

    def _bwrap_wrap(self, command: list[str], tier: int) -> list[str]:
        """Bubblewrap wrapper for Linux."""
        args = ["bwrap", "--unshare-all", "--dev", "/dev", "--proc", "/proc", "--die-with-parent"]

        if tier >= 5:  # Production
            args.extend(["--bind", "/", "/"])
            return [*args, "--", *command]

        if tier >= 2:  # Worktree
            worktree = Path(os.environ.get("THGENT_SANDBOX_WORKTREE", str(Path.cwd()))).expanduser().resolve()
            args.extend(["--bind", str(worktree), str(worktree), "--chdir", str(worktree)])
            allowed_reads = [
                p.strip() for p in os.environ.get("THGENT_SANDBOX_ALLOWED_READS", "/usr,/bin,/lib,/lib64").split(",")
            ]
            for read_path in allowed_reads:
                if not read_path:
                    continue
                rp = Path(read_path).expanduser()
                if rp.exists():
                    args.extend(["--ro-bind", str(rp), str(rp)])
            args.extend(["--tmpfs", "/tmp", "--tmpfs", "/var/tmp"])
        elif tier >= 1:  # Read-only full filesystem for baseline read tier
            args.extend(["--ro-bind", "/", "/"])

        return [*args, "--", *command]

    def _seatbelt_wrap(self, command: list[str], tier: int) -> list[str]:
        """Seatbelt (sandbox-exec) wrapper for macOS."""
        sandbox = MacOSSandbox()
        if not sandbox.is_sandbox_available():
            raise RuntimeError("sandbox-exec is required for macOS seatbelt sandboxing")

        level = self._sandbox_level_for_tier(tier)
        project_root = Path(os.environ.get("THGENT_SANDBOX_WORKTREE", str(Path.cwd()))).expanduser().resolve()
        return sandbox.apply_to_command(command, level, project_root=project_root)

    def _sandbox_level_for_tier(self, tier: int) -> SandboxLevel:
        """Map autonomy tier to macOS sandbox level."""
        if tier >= 5:
            return SandboxLevel.FULL
        if tier >= 4:
            return SandboxLevel.NETWORKED
        if tier >= 2:
            return SandboxLevel.RESTRICTED
        return SandboxLevel.READONLY

    def _generate_seatbelt_profile(self, tier: int) -> str:
        """Generate macOS seatbelt profile."""
        level = self._sandbox_level_for_tier(tier)
        sandbox = MacOSSandbox()
        if level in (SandboxLevel.NONE, SandboxLevel.FULL):
            return "(version 1)\n(allow default)"

        project_root = Path(os.environ.get("THGENT_SANDBOX_WORKTREE", str(Path.cwd()))).expanduser().resolve()
        return sandbox.generate_profile(level, project_root)


class AutonomyEnforcer:
    """Enforces 5-tier autonomy levels."""

    TIERS: ClassVar[dict[int, str]] = {1: "read", 2: "worktree", 3: "git", 4: "shared", 5: "production"}

    def classify_operation(self, command: str, target: str) -> int:
        """Determine required tier for an operation."""
        command = command.lower()
        if "rm " in command or "delete" in command:
            return 4
        if "git " in command:
            return 3
        if "cat " in command or "ls " in command:
            return 1
        return 2  # Default to worktree isolation
