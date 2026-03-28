"""zmx session persistence backend for thegent agent sessions.

zmx is a Zig-based muxless terminal session persistence tool (libghostty-vt).
It allows agent sessions to survive terminal detachment without tmux/screen.

Integration model: subprocess calls only (no C-ABI linking).
zmx not being installed degrades gracefully to tmux or none.

FR-SES-001: Session backend must be pluggable and auto-detected.
FR-SES-002: Missing backend must not raise at import time.
FR-SES-003: All backend methods must return typed results, never raise on
            subprocess failure — caller decides how to handle.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from thegent_core.infra.shim_subprocess import run as shim_run
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class ZmxSession:
    """Metadata for a single zmx-managed session."""

    name: str
    pid: int | None = None
    state: str = "unknown"  # running | detached | exited | unknown
    cmd: str = ""
    extra: dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Protocol — SessionBackend
# ---------------------------------------------------------------------------


@runtime_checkable
class SessionBackend(Protocol):
    """Minimal protocol that all session backends must implement.

    # @trace FR-SES-001
    """

    @property
    def name(self) -> str:
        """Human-readable backend identifier."""
        ...

    @property
    def available(self) -> bool:
        """Return True if the underlying tool is installed and functional."""
        ...

    def create(self, session_name: str, cmd: list[str]) -> bool:
        """Create and start a new named session running *cmd*.

        Returns True on success, False on failure.
        """
        ...

    def attach(self, session_name: str) -> bool:
        """Attach to an existing session (interactive; blocks until detach).

        Returns True on success, False if session does not exist or zmx failed.
        """
        ...

    def list(self) -> list[ZmxSession]:
        """Return all sessions known to this backend."""
        ...

    def kill(self, session_name: str) -> bool:
        """Terminate a named session.

        Returns True on success, False if session was not found or kill failed.
        """
        ...

    def capture(self, session_name: str, last_lines: int = 50) -> str:
        """Return the last *last_lines* lines of session output.

        Returns an empty string if the session is unknown or capture fails.
        """
        ...


# ---------------------------------------------------------------------------
# ZmxBackend — wraps `zmx` CLI via subprocess
# ---------------------------------------------------------------------------

_ZMX_NOT_INSTALLED_MSG = (
    "zmx is not installed or not on PATH. "
    "Install from https://github.com/ghostty-org/zmx or via your package manager. "
    "Session persistence is unavailable for this backend."
)


class ZmxBackend:
    """Session backend that delegates to the `zmx` CLI.

    All public methods are safe to call even when zmx is not installed —
    they log a warning and return a safe fallback value.

    # @trace FR-SES-001, FR-SES-002, FR-SES-003
    """

    _name = "zmx"

    def __init__(self, zmx_bin: str = "zmx") -> None:
        self._zmx_bin = zmx_bin
        self._available: bool | None = None  # lazily resolved

    # ------------------------------------------------------------------
    # Protocol properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        """Return True if zmx binary is present and responds.

        Result is cached after first check.
        # @trace FR-SES-002
        """
        if self._available is None:
            self._available = self._probe()
        return self._available

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create(self, session_name: str, cmd: list[str]) -> bool:
        """Start a new zmx session running *cmd*.

        Calls: ``zmx new <session_name> -- <cmd...>``

        Returns True on success, False on failure (including zmx not installed).
        # @trace FR-SES-001
        """
        if not self.available:
            logger.warning(_ZMX_NOT_INSTALLED_MSG)
            return False
        args = [self._zmx_bin, "new", session_name, "--", *cmd]
        return self._run(args)

    def attach(self, session_name: str) -> bool:
        """Attach (interactively) to a running zmx session.

        Calls: ``zmx attach <session_name>``

        This call blocks until the user detaches. Returns False when zmx is
        unavailable or the session does not exist.
        # @trace FR-SES-001
        """
        if not self.available:
            logger.warning(_ZMX_NOT_INSTALLED_MSG)
            return False
        args = [self._zmx_bin, "attach", session_name]
        return self._run(args, capture=False)

    def list(self) -> list[ZmxSession]:
        """Return all zmx sessions.

        Calls: ``zmx list --format json`` (falling back to plain text parsing
        if --format is unsupported in the installed version).

        Returns an empty list when zmx is unavailable.
        # @trace FR-SES-001
        """
        if not self.available:
            logger.warning(_ZMX_NOT_INSTALLED_MSG)
            return []
        return self._list_sessions()

    def kill(self, session_name: str) -> bool:
        """Terminate a zmx session.

        Calls: ``zmx kill <session_name>``

        Returns True on success, False on failure.
        # @trace FR-SES-001
        """
        if not self.available:
            logger.warning(_ZMX_NOT_INSTALLED_MSG)
            return False
        args = [self._zmx_bin, "kill", session_name]
        return self._run(args)

    def capture(self, session_name: str, last_lines: int = 50) -> str:
        """Capture the last *last_lines* lines of a session's scrollback.

        Calls: ``zmx capture <session_name> --lines <last_lines>``

        Returns an empty string when zmx is unavailable or capture fails.
        # @trace FR-SES-001
        """
        if not self.available:
            logger.warning(_ZMX_NOT_INSTALLED_MSG)
            return ""
        args = [self._zmx_bin, "capture", session_name, "--lines", str(last_lines)]
        ok, stdout, stderr = self._run_capture(args)
        if not ok:
            logger.debug("zmx capture failed for %r: %s", session_name, stderr.strip())
            return ""
        return stdout

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _probe(self) -> bool:
        """Check whether zmx is on PATH and responds to --version."""
        if shutil.which(self._zmx_bin) is None:
            logger.debug("zmx binary not found on PATH (%s)", self._zmx_bin)
            return False
        try:
            result = shim_run(
                [self._zmx_bin, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0:
                logger.debug("zmx detected: %s", result.stdout.strip())
                return True
            # Some zmx versions exit non-zero for --version; try `list` as fallback probe
            result2 = shim_run(
                [self._zmx_bin, "list"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            return result2.returncode == 0
        except (OSError, subprocess.TimeoutExpired) as exc:
            logger.debug("zmx probe failed: %s", exc)
            return False

    def _run(self, args: list[str], capture: bool = True) -> bool:
        """Run a zmx command, returning True on returncode==0."""
        try:
            if capture:
                result = shim_run(args, capture_output=True, text=True, timeout=30, check=False)
            else:
                # Interactive attach — no capture, inherit stdio
                result = shim_run(args, timeout=None, check=False)
            if result.returncode != 0 and capture:
                logger.debug(
                    "zmx command %r exited %d: %s",
                    args,
                    result.returncode,
                    getattr(result, "stderr", "").strip(),
                )
            return result.returncode == 0
        except (OSError, subprocess.TimeoutExpired) as exc:
            logger.debug("zmx command %r failed: %s", args, exc)
            return False

    def _run_capture(self, args: list[str]) -> tuple[bool, str, str]:
        """Run a zmx command, returning (success, stdout, stderr)."""
        try:
            result = shim_run(args, capture_output=True, text=True, timeout=30, check=False)
            return result.returncode == 0, result.stdout, result.stderr
        except (OSError, subprocess.TimeoutExpired) as exc:
            logger.debug("zmx command %r failed: %s", args, exc)
            return False, "", str(exc)

    def _list_sessions(self) -> list[ZmxSession]:
        """Parse output of ``zmx list`` into ZmxSession objects.

        zmx list output format (as of known versions) is one session per line:
            <name>  <state>  <pid>  [<cmd>]

        A JSON format flag (--format json) is attempted first; if the flag is
        not supported the plain text is parsed as a best-effort fallback.
        """
        # Attempt JSON first
        sessions = self._list_json()
        if sessions is not None:
            return sessions

        # Plain text fallback
        ok, stdout, _ = self._run_capture([self._zmx_bin, "list"])
        if not ok or not stdout.strip():
            return []
        return self._parse_list_text(stdout)

    def _list_json(self) -> list[ZmxSession] | None:
        """Try ``zmx list --format json``.  Returns None if flag unsupported."""
        import json as _json

        ok, stdout, stderr = self._run_capture([self._zmx_bin, "list", "--format", "json"])
        if not ok:
            # If the error mentions unknown flag, return None to fall through
            if "unknown" in stderr.lower() or "unrecognized" in stderr.lower():
                return None
            return []
        try:
            data = _json.loads(stdout)
        except _json.JSONDecodeError:
            return None
        if not isinstance(data, list):
            return None

        sessions: list[ZmxSession] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            sessions.append(
                ZmxSession(
                    name=str(entry.get("name", "")),
                    pid=entry.get("pid"),
                    state=str(entry.get("state", "unknown")),
                    cmd=str(entry.get("cmd", "")),
                    extra={k: str(v) for k, v in entry.items() if k not in {"name", "pid", "state", "cmd"}},
                )
            )
        return sessions

    @staticmethod
    def _parse_list_text(text: str) -> list[ZmxSession]:
        """Parse plain-text ``zmx list`` output (best-effort)."""
        sessions: list[ZmxSession] = []
        for line in text.strip().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if not parts:
                continue
            name = parts[0]
            state = parts[1] if len(parts) > 1 else "unknown"
            pid_str = parts[2] if len(parts) > 2 else ""
            cmd = " ".join(parts[3:]) if len(parts) > 3 else ""
            try:
                pid: int | None = int(pid_str)
            except ValueError:
                pid = None
            sessions.append(ZmxSession(name=name, state=state, pid=pid, cmd=cmd))
        return sessions


# ---------------------------------------------------------------------------
# Backend auto-detection / factory
# ---------------------------------------------------------------------------

_BACKEND_ENV_VAR = "THGENT_SESSION_BACKEND"


def resolve_session_backend(
    backend_override: str | None = None,
) -> ZmxBackend | None:
    """Return the appropriate session backend based on configuration.

    Selection order:
    1. *backend_override* argument (highest priority).
    2. ``THGENT_SESSION_BACKEND`` environment variable.
    3. Auto-detect: try zmx, then tmux sentinel, then none.

    Currently only ``zmx`` and ``none`` are implemented.  ``tmux`` is
    acknowledged (returns None) so callers can fall back to the existing
    tmux tooling in ``thegent.tools.terminal``.

    Returns a ``ZmxBackend`` when backend is ``zmx``, or ``None`` when
    the backend is ``tmux`` or ``none`` (caller uses legacy path).

    # @trace FR-SES-001
    """
    import os

    choice = (backend_override or os.environ.get(_BACKEND_ENV_VAR, "auto")).strip().lower()

    if choice == "zmx":
        backend = ZmxBackend()
        if not backend.available:
            logger.warning(
                "THGENT_SESSION_BACKEND=zmx but zmx is not installed. "
                "Falling back to none. Install zmx to enable muxless session persistence."
            )
            return None
        return backend

    if choice == "tmux":
        # Caller handles tmux via thegent.tools.terminal
        return None

    if choice == "none":
        return None

    if choice == "auto":
        backend = ZmxBackend()
        if backend.available:
            logger.debug("Auto-detected zmx; using ZmxBackend for session persistence.")
            return backend
        # Fall through to tmux/none — caller decides
        logger.debug("zmx not available; session persistence will use tmux or none.")
        return None

    logger.warning(
        "Unknown THGENT_SESSION_BACKEND value %r. Valid values: zmx, tmux, none, auto. Defaulting to none.",
        choice,
    )
    return None
