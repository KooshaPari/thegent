"""Muxless zmx session persistence manager for thegent agent sessions.

Provides a high-level manager for creating and managing zmx virtual terminal
sessions, enabling agent sessions to persist without tmux/screen.

Integration model: subprocess calls only via shim_run (never os.system).
zmx not being installed degrades gracefully -- all methods return safe defaults.

FR-SES-001: Session backend must be pluggable and auto-detected.
FR-SES-002: Missing backend must not raise at import time.
FR-SES-003: All backend methods must return typed results, never raise on
            subprocess failure -- caller decides how to handle.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from thegent.infra.shim_subprocess import run as shim_run
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

_ZMX_BINARY_ENV_VAR = "THGENT_ZMX_BINARY"
_DEFAULT_ZMX_BINARY = "zmx"

_ZMX_NOT_INSTALLED_MSG = (
    "zmx is not installed or not on PATH. "
    "Install from https://github.com/ghostty-org/zmx or via your package manager. "
    "Muxless session persistence is unavailable."
)


@dataclass
class ZmxSessionConfig:
    """Configuration for ZmxSessionManager.

    Attributes:
        binary_path: Path (or name) of the zmx binary.
        max_sessions: Maximum number of concurrent sessions allowed.
        session_ttl_s: Default session time-to-live in seconds.

    # @trace FR-SES-001
    """

    binary_path: str = field(default_factory=lambda: _DEFAULT_ZMX_BINARY)
    max_sessions: int = 50
    session_ttl_s: int = 3600

    @classmethod
    def from_settings(cls) -> ZmxSessionConfig:
        """Build a ZmxSessionConfig reading values from settings."""
        from thegent.config import ThegentSettings

        settings = ThegentSettings()
        binary_path = getattr(settings, "zmx_binary", _DEFAULT_ZMX_BINARY) or _DEFAULT_ZMX_BINARY
        return cls(
            binary_path=binary_path,
            max_sessions=settings.zmx_max_sessions,
            session_ttl_s=settings.zmx_session_ttl,
        )

    @classmethod
    def from_env(cls) -> ZmxSessionConfig:
        """Deprecated: Use from_settings() instead."""
        return cls.from_settings()


class ZmxSessionManager:
    """High-level manager for zmx muxless virtual terminal sessions.

    All public methods are safe to call even when zmx is not installed --
    they log a warning and return a safe fallback value.

    Subprocess integration: all zmx calls go through shim_run().

    # @trace FR-SES-001, FR-SES-002, FR-SES-003
    """

    def __init__(self, config: ZmxSessionConfig | None = None) -> None:
        """Create a ZmxSessionManager.

        Args:
            config: Optional configuration. When None, defaults are used.
        """
        self._config = config or ZmxSessionConfig()
        self._available: bool | None = None

    def is_available(self) -> bool:
        """Return True if the zmx binary is present and functional.

        The result is cached after the first check.

        # @trace FR-SES-002
        """
        if self._available is None:
            self._available = self._probe()
        return self._available

    def create_session(self, session_id: str, command: list[str]) -> str:
        """Create a new zmx session running *command*.

        Calls: ``zmx new <session_id> -- <command...>``

        Args:
            session_id: Unique session identifier; becomes the zmx session name.
            command: Command and arguments to run inside the session.

        Returns:
            The session name (same as *session_id*) on success, or an empty
            string on failure (including when zmx is unavailable).

        # @trace FR-SES-001
        """
        if not self.is_available():
            logger.warning(_ZMX_NOT_INSTALLED_MSG)
            return ""
        if not session_id:
            logger.warning("create_session: session_id must be non-empty")
            return ""
        if not command:
            logger.warning("create_session: command must be non-empty")
            return ""
        args = [self._config.binary_path, "new", session_id, "--", *command]
        if self._run_bool(args):
            return session_id
        logger.debug("create_session: zmx new failed for session %r", session_id)
        return ""

    def attach_session(self, session_name: str) -> bool:
        """Attach (interactively) to an existing zmx session.

        Calls: ``zmx attach <session_name>``

        This call blocks until the user detaches from the session.

        Args:
            session_name: Name of the session to attach to.

        Returns:
            True on success, False when zmx is unavailable or the session
            does not exist.

        # @trace FR-SES-001
        """
        if not self.is_available():
            logger.warning(_ZMX_NOT_INSTALLED_MSG)
            return False
        args = [self._config.binary_path, "attach", session_name]
        return self._run_interactive(args)

    def capture_output(self, session_name: str, lines: int = 100) -> str:
        """Capture the last *lines* lines of output from a zmx session.

        Calls: ``zmx capture <session_name> --lines <lines>``

        Args:
            session_name: Name of the session to capture from.
            lines: Number of trailing lines to return (default 100).

        Returns:
            Captured output as a string, or empty string on failure.

        # @trace FR-SES-001
        """
        if not self.is_available():
            logger.warning(_ZMX_NOT_INSTALLED_MSG)
            return ""
        args = [self._config.binary_path, "capture", session_name, "--lines", str(lines)]
        ok, stdout, stderr = self._run_capture(args)
        if not ok:
            logger.debug("capture_output: zmx capture failed for %r: %s", session_name, stderr.strip())
            return ""
        return stdout

    def send_input(self, session_name: str, text: str) -> bool:
        """Send keystrokes (text) to a zmx session.

        Calls: ``zmx send-keys <session_name> <text>``

        Args:
            session_name: Target session name.
            text: Text to deliver as keystrokes.

        Returns:
            True on success, False on failure (including zmx unavailable).

        # @trace FR-SES-001
        """
        if not self.is_available():
            logger.warning(_ZMX_NOT_INSTALLED_MSG)
            return False
        args = [self._config.binary_path, "send-keys", session_name, text]
        return self._run_bool(args)

    def list_sessions(self) -> list[str]:
        """Return the names of all active zmx sessions.

        Calls: ``zmx list`` (or ``zmx list --format json`` if supported).

        Returns:
            Sorted list of session name strings, or empty list on failure.

        # @trace FR-SES-001
        """
        if not self.is_available():
            logger.warning(_ZMX_NOT_INSTALLED_MSG)
            return []
        return self._list_session_names()

    def destroy_session(self, session_name: str) -> bool:
        """Terminate and clean up a zmx session.

        Calls: ``zmx kill <session_name>``

        Args:
            session_name: Name of the session to destroy.

        Returns:
            True on success, False on failure.

        # @trace FR-SES-001
        """
        if not self.is_available():
            logger.warning(_ZMX_NOT_INSTALLED_MSG)
            return False
        args = [self._config.binary_path, "kill", session_name]
        return self._run_bool(args)

    def _probe(self) -> bool:
        """Check whether the zmx binary is on PATH and responds."""
        binary = self._config.binary_path
        if shutil.which(binary) is None:
            logger.debug("zmx binary not found on PATH (%s)", binary)
            return False
        try:
            result = shim_run(
                [binary, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0:
                logger.debug("zmx detected: %s", result.stdout.strip())
                return True
            result2 = shim_run(
                [binary, "list"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            return result2.returncode == 0
        except (OSError, subprocess.TimeoutExpired) as exc:
            logger.debug("zmx probe failed: %s", exc)
            return False

    def _run_bool(self, args: list[str]) -> bool:
        """Run a zmx command, return True iff exit code is 0."""
        try:
            result = shim_run(args, capture_output=True, text=True, timeout=30, check=False)
            if result.returncode != 0:
                logger.debug(
                    "zmx command %r exited %d: %s",
                    args,
                    result.returncode,
                    result.stderr.strip(),
                )
            return result.returncode == 0
        except (OSError, subprocess.TimeoutExpired) as exc:
            logger.debug("zmx command %r failed: %s", args, exc)
            return False

    def _run_interactive(self, args: list[str]) -> bool:
        """Run a zmx command interactively (no capture, inherit stdio)."""
        try:
            result = shim_run(args, timeout=None, check=False)
            return result.returncode == 0
        except (OSError, subprocess.TimeoutExpired) as exc:
            logger.debug("zmx interactive command %r failed: %s", args, exc)
            return False

    def _run_capture(self, args: list[str]) -> tuple[bool, str, str]:
        """Run a zmx command, returning (success, stdout, stderr)."""
        try:
            result = shim_run(args, capture_output=True, text=True, timeout=30, check=False)
            return result.returncode == 0, result.stdout, result.stderr
        except (OSError, subprocess.TimeoutExpired) as exc:
            logger.debug("zmx command %r failed: %s", args, exc)
            return False, "", str(exc)

    def _list_session_names(self) -> list[str]:
        """Return session names from ``zmx list``, trying JSON first."""
        names = self._list_names_json()
        if names is not None:
            return sorted(names)
        return sorted(self._list_names_text())

    def _list_names_json(self) -> list[str] | None:
        """Try ``zmx list --format json``. Returns None if flag unsupported."""
        import json as _json

        ok, stdout, stderr = self._run_capture([self._config.binary_path, "list", "--format", "json"])
        if not ok:
            if "unknown" in stderr.lower() or "unrecognized" in stderr.lower():
                return None
            return []
        try:
            data = _json.loads(stdout)
        except _json.JSONDecodeError:
            return None
        if not isinstance(data, list):
            return None
        names: list[str] = []
        for entry in data:
            if isinstance(entry, dict) and entry.get("name"):
                names.append(str(entry["name"]))
            elif isinstance(entry, str) and entry:
                names.append(entry)
        return names

    def _list_names_text(self) -> list[str]:
        """Parse plain-text ``zmx list`` output (best-effort)."""
        ok, stdout, _ = self._run_capture([self._config.binary_path, "list"])
        if not ok or not stdout.strip():
            return []
        names: list[str] = []
        for line in stdout.strip().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if parts:
                names.append(parts[0])
        return names


def make_zmx_session_manager(config: ZmxSessionConfig | None = None) -> ZmxSessionManager:
    """Create a ZmxSessionManager, reading config from environment if not provided.

    Reads ``THGENT_ZMX_BINARY`` to determine the zmx binary path.

    Args:
        config: Optional pre-built config. When None, config is built from
                environment variables via :meth:`ZmxSessionConfig.from_env`.

    Returns:
        A configured :class:`ZmxSessionManager` instance.

    # @trace FR-SES-001
    """
    if config is None:
        config = ZmxSessionConfig.from_settings()
    return ZmxSessionManager(config=config)
