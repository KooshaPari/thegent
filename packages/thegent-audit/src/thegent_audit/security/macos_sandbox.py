"""macOS sandbox profile management for secure agent execution.

Provides finer-grained security control over agent subprocesses using macOS
Seatbelt (sandbox-exec). Supports five security levels from no restrictions
to read-only filesystem access.

Integration: set ``THGENT_SANDBOX_LEVEL`` to one of:
    none | readonly | restricted | networked | full

The ``restricted`` and ``networked`` levels require the project root to be
resolvable (falls back to cwd when not determinable).
"""

from __future__ import annotations

import logging
import os
import platform
import shutil
import tempfile
from enum import Enum
from pathlib import Path

_log = logging.getLogger(__name__)

# Directory containing static .sb profile templates
SANDBOX_PROFILE_DIR = Path(__file__).parent / "profiles"

# Placeholder token replaced with the actual project root at runtime
_PROJECT_ROOT_PLACEHOLDER = "PROJECT_ROOT_PLACEHOLDER"

# Environment variable that controls the sandbox level
SANDBOX_LEVEL_ENV_VAR = "THGENT_SANDBOX_LEVEL"


class SandboxLevel(Enum):
    """Enumeration of macOS sandbox security levels.

    Levels progress from most permissive (FULL/NONE) to most restrictive
    (READONLY).

    NONE      — no sandbox applied; subprocess runs unrestricted.
    FULL      — no restrictions (alias for NONE; for trusted agents).
    READONLY  — read filesystem, no network, no writes.
    RESTRICTED— read/write project dir only, no network.
    NETWORKED — restricted + outbound HTTPS (port 443) allowed.
    """

    NONE = "none"
    READONLY = "readonly"
    RESTRICTED = "restricted"
    NETWORKED = "networked"
    FULL = "full"


class MacOSSandbox:
    """macOS Seatbelt sandbox profile manager.

    Wraps agent subcommands with ``sandbox-exec -f <profile>`` so that agents
    run with the requested level of filesystem and network isolation.

    Example usage::

        sandbox = MacOSSandbox()
        if sandbox.is_sandbox_available():
            cmd = sandbox.apply_to_command(["claude", "--dangerously-skip-permissions"], SandboxLevel.NETWORKED)
        subprocess.Popen(cmd, ...)

    Profile files live in ``security/profiles/``.  The ``restricted`` and
    ``networked`` templates contain a ``PROJECT_ROOT_PLACEHOLDER`` token that
    is substituted with the real project root before writing to a temp file.
    """

    def __init__(self, profile_dir: Path | None = None) -> None:
        self._profile_dir = profile_dir or SANDBOX_PROFILE_DIR
        self._sandbox_exec: str | None = None  # lazily resolved

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_sandbox_available(self) -> bool:
        """Return True when ``sandbox-exec`` is present on this system.

        ``sandbox-exec`` ships with macOS but is absent on Linux/Windows.
        """
        if platform.system() != "Darwin":
            return False
        if self._sandbox_exec is not None:
            return True
        found = shutil.which("sandbox-exec")
        if found:
            self._sandbox_exec = found
            return True
        return False

    def get_profile_path(self, level: SandboxLevel) -> Path | None:
        """Return the static template path for *level*, or None for NONE/FULL.

        The file returned for RESTRICTED and NETWORKED still contains the
        ``PROJECT_ROOT_PLACEHOLDER`` token; callers that need a ready-to-use
        profile should call :meth:`generate_profile` instead.
        """
        if level in (SandboxLevel.NONE, SandboxLevel.FULL):
            return None
        name = f"{level.value}.sb"
        path = self._profile_dir / name
        if path.exists():
            return path
        return None

    def generate_profile(self, level: SandboxLevel, project_root: Path) -> str:
        """Generate and return the sandbox profile text for *level*.

        For RESTRICTED and NETWORKED, replaces ``PROJECT_ROOT_PLACEHOLDER``
        with *project_root* so that file-write permissions are scoped to the
        project directory.

        Args:
            level: The desired sandbox security level.
            project_root: Absolute path to the agent's working project directory.

        Returns:
            The complete seatbelt profile text ready to be written to a file.

        Raises:
            ValueError: If *level* is NONE or FULL (no profile needed).
            FileNotFoundError: If the profile template is missing.
        """
        if level in (SandboxLevel.NONE, SandboxLevel.FULL):
            raise ValueError(f"Level {level.value!r} does not use a profile.")

        template_path = self.get_profile_path(level)
        if template_path is None:
            raise FileNotFoundError(
                f"Sandbox profile template not found for level {level.value!r} in {self._profile_dir}"
            )
        template = template_path.read_text(encoding="utf-8")

        if level in (SandboxLevel.RESTRICTED, SandboxLevel.NETWORKED):
            project_root_str = str(project_root.resolve())
            template = template.replace(_PROJECT_ROOT_PLACEHOLDER, project_root_str)

        return template

    def apply_to_command(
        self,
        cmd: list[str],
        level: SandboxLevel,
        project_root: Path | None = None,
    ) -> list[str]:
        """Wrap *cmd* with ``sandbox-exec`` for the given *level*.

        For NONE and FULL, returns *cmd* unchanged.  For all other levels,
        writes a profile to a temporary file and prepends
        ``sandbox-exec -f <profile>`` to the command.

        The temporary profile file is written with a unique name derived from
        ``tempfile.mkstemp`` so that concurrent agents do not clobber each
        other's profiles.

        Args:
            cmd: The original subprocess command list.
            level: The sandbox security level to apply.
            project_root: Required for RESTRICTED and NETWORKED levels.
                          Defaults to ``Path.cwd()`` when not supplied.

        Returns:
            The wrapped command list.

        Raises:
            RuntimeError: If sandbox-exec is not available on this platform.
            FileNotFoundError: If the profile template is missing.
        """
        if level in (SandboxLevel.NONE, SandboxLevel.FULL):
            return list(cmd)

        if not self.is_sandbox_available():
            _log.warning(
                "sandbox-exec not available; skipping sandbox wrapping for level %r",
                level.value,
            )
            return list(cmd)

        root = project_root or Path.cwd()
        profile_text = self.generate_profile(level, root)

        # Write profile to a unique temp file so parallel agents don't collide
        fd, profile_path = tempfile.mkstemp(suffix=".sb", prefix="thegent-sandbox-")
        try:
            os.write(fd, profile_text.encode("utf-8"))
        finally:
            os.close(fd)

        _log.debug("Sandbox level %r: profile written to %s", level.value, profile_path)
        return ["sandbox-exec", "-f", profile_path, *cmd]

    @classmethod
    def from_env(cls) -> MacOSSandbox:
        """Construct a MacOSSandbox using defaults (profile_dir from package)."""
        return cls()

    @classmethod
    def level_from_settings(cls) -> SandboxLevel:
        """Read sandbox level from ThegentSettings."""
        from thegent_core.config import ThegentSettings

        settings = ThegentSettings()
        raw = settings.sandbox_level.strip().lower() if settings.sandbox_level else "none"
        if not raw or raw == "none":
            return SandboxLevel.NONE
        try:
            return SandboxLevel(raw)
        except ValueError:
            valid = [e.value for e in SandboxLevel]
            _log.warning(
                "Unknown sandbox_level value %r; valid values: %s. Defaulting to 'none'.",
                raw,
                valid,
            )
            return SandboxLevel.NONE

    @classmethod
    def level_from_env(cls) -> SandboxLevel:
        """Deprecated: Use level_from_settings() instead. Kept for backwards compatibility."""
        return cls.level_from_settings()
