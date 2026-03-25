"""Terminal capture utilities for thegent.

Captures terminal output from various backends (tmux, zmx, /proc, termitty).
"""

from __future__ import annotations

import importlib
import os
import platform
import shutil
from thegent.infra.shim_subprocess import run as shim_run
import sys
from dataclasses import dataclass, field


@dataclass
class CaptureResult:
    """Result of a terminal capture operation."""

    lines: list[str] = field(default_factory=list)
    backend: str = "none"
    pane_id: str | None = None


def _is_tmux_available() -> bool:
    """Return True when tmux is available on PATH."""
    return shutil.which("tmux") is not None


def _trim_to_n(lines: list[str], n: int) -> list[str]:
    """Trim lines to the last n entries."""
    if n <= 0:
        return lines
    return lines[-n:]


def _capture_via_tmux(pane_id: str, n: int) -> CaptureResult | None:
    """Capture terminal output via tmux capture-pane.

    Returns None if tmux is unavailable, exits non-zero, or raises OSError.
    """
    if not _is_tmux_available():
        return None
    cmd = ["tmux", "capture-pane", "-p", "-S", f"-{n}", "-t", pane_id]
    try:
        result = shim_run(cmd, capture_output=True, text=True, timeout=5, check=False)
    except OSError:
        return None
    if result.returncode != 0:
        return None
    lines = result.stdout.splitlines()
    return CaptureResult(lines=_trim_to_n(lines, n), backend="tmux", pane_id=pane_id)


def _capture_via_zmx(session: str, n: int) -> CaptureResult | None:
    """Capture terminal output via zmx (Zellij multiplexer).

    Returns None if the zmx backend is unavailable or capture is empty.
    """
    try:
        zmx_mod = importlib.import_module("thegent.session.zmx_backend")
    except ImportError, ModuleNotFoundError:
        return None
    backend = zmx_mod.ZmxBackend()
    if not backend.available:
        return None
    text = backend.capture(session)
    if not text:
        return None
    lines = text.splitlines()
    return CaptureResult(lines=_trim_to_n(lines, n), backend="zmx", pane_id=session)


def _capture_via_proc(pid: int, n: int) -> CaptureResult | None:
    """Capture terminal output via /proc filesystem (Linux only).

    Returns None on non-Linux systems or on permission/IO errors.
    """
    if platform.system() != "Linux":
        return None
    try:
        with open(f"/proc/{pid}/fd/1", "rb") as fh:
            raw = fh.read()
    except OSError:
        return None
    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()
    return CaptureResult(lines=_trim_to_n(lines, n), backend="proc", pane_id=str(pid))


def _capture_via_termitty(raw_bytes: bytes, n: int) -> CaptureResult | None:
    """Process raw terminal bytes.

    Returns None when termitty is explicitly blocked in sys.modules or when
    the decoded output is empty. Strips trailing blank lines, trims to n.
    """
    if "termitty" in sys.modules and sys.modules["termitty"] is None:
        return None
    text = raw_bytes.decode("utf-8", errors="replace")
    lines = text.splitlines()
    # Strip trailing blank lines
    while lines and not lines[-1].strip():
        lines.pop()
    lines = _trim_to_n(lines, n)
    if not lines:
        return None
    return CaptureResult(lines=lines, backend="termitty", pane_id=None)


class TerminalCapture:
    """Captures terminal output using available backends."""

    @staticmethod
    def _read_current_tty_bytes() -> bytes:
        """Read bytes from the current TTY. Returns empty bytes on error."""
        try:
            tty_path = os.ttyname(sys.stdout.fileno())
            with open(tty_path, "rb") as fh:
                return fh.read()
        except OSError:
            return b""

    @staticmethod
    def _read_proc_bytes(pid: int) -> bytes:
        """Read bytes from /proc/<pid>/fd/1 (Linux only). Returns empty bytes on error."""
        if platform.system() != "Linux":
            return b""
        try:
            with open(f"/proc/{pid}/fd/1", "rb") as fh:
                return fh.read()
        except OSError:
            return b""

    def capture_last_n_lines(self, n: int = 50, pane_id: str | None = None) -> CaptureResult:
        """Capture the last n lines from the terminal.

        When pane_id is provided, tries tmux then zmx backends.
        Falls through to termitty using current TTY bytes.
        Returns CaptureResult with backend='none' when all backends fail.
        """
        if pane_id is not None:
            result = _capture_via_tmux(pane_id, n)
            if result is not None:
                return result
            result = _capture_via_zmx(pane_id, n)
            if result is not None:
                return result

        raw = self._read_current_tty_bytes()
        result = _capture_via_termitty(raw, n)
        if result is not None:
            return result
        return CaptureResult()

    def capture_by_pid(self, pid: int, n: int = 50) -> CaptureResult:
        """Capture terminal output for a specific PID.

        Tries /proc on Linux, falls through to termitty.
        Always sets pane_id=str(pid) in the returned result.
        """
        result = _capture_via_proc(pid, n)
        if result is not None:
            return result

        raw = self._read_proc_bytes(pid)
        result = _capture_via_termitty(raw, n)
        if result is not None:
            result.pane_id = str(pid)
            return result

        return CaptureResult(backend="none", pane_id=str(pid))
