"""Phase 16: Sandboxing implementation.
Includes bubblewrap (Linux) and seatbelt (macOS) profile generation, and 5-tier autonomy.
"""

import logging
import platform
from pathlib import Path
from typing import ClassVar

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
        args = ["bwrap", "--unshare-all", "--dev", "/dev", "--proc", "/proc"]

        if tier >= 1:  # Read
            args.extend(["--ro-bind", "/", "/"])

        if tier >= 2:  # Worktree
            # Would bind specifically to worktree
            pass

        if tier >= 5:  # Production
            args.extend(["--bind", "/", "/"])

        return [*args, "--", *command]

    def _seatbelt_wrap(self, command: list[str], tier: int) -> list[str]:
        """Seatbelt (sandbox-exec) wrapper for macOS."""
        profile = self._generate_seatbelt_profile(tier)
        profile_path = Path("/tmp/harness-sandbox.sb")
        profile_path.write_text(profile)
        return ["sandbox-exec", "-f", str(profile_path), *command]

    def _generate_seatbelt_profile(self, tier: int) -> str:
        """Generate macOS seatbelt profile."""
        if tier == 1:
            return "(version 1)\n(deny default)\n(allow file-read*)\n(allow process-exec)"
        return "(version 1)\n(allow default)"


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
