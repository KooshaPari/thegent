"""Terminal pane process wrapper used by compositor tests."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import types
from pathlib import Path
from typing import ClassVar

try:
    import pty
except ImportError:  # Windows: pty imports termios.
    pty = types.ModuleType("pty")

    def _openpty_unavailable() -> tuple[int, int]:
        raise ImportError("pty not available")

    pty.openpty = _openpty_unavailable  # type: ignore[attr-defined]
    sys.modules.setdefault("pty", pty)


class TerminalPane:
    """Small terminal process lifecycle helper."""

    _ALLOWED_SHELLS: ClassVar[set[str]] = {
        "bash",
        "bash.exe",
        "cmd.exe",
        "fish",
        "fish.exe",
        "pwsh",
        "pwsh.exe",
        "powershell.exe",
        "sh",
        "sh.exe",
        "zsh",
        "zsh.exe",
    }

    def __init__(self, pane_id: str = "pane", working_dir: str = ".", name: str | None = None) -> None:
        self.pane_id = pane_id
        self.working_dir = working_dir
        self.name = name or pane_id
        self.process: subprocess.Popen[str] | None = None
        self.pty_master: int | None = None
        self.is_active = False
        self.last_cleanup_diagnostic: dict[str, object] | None = None

    def _render_placeholder(self) -> str:
        return f"TerminalPane {self.pane_id} ({self.working_dir})"

    def render(self) -> str:
        return self._render_placeholder()

    def _fallback_shell(self) -> str:
        if os.name == "nt":
            return os.environ.get("COMSPEC") or "cmd.exe"
        return shutil.which("sh") or "/bin/sh"

    def _resolve_shell(self, shell: str | None) -> str:
        if not shell:
            return self._fallback_shell()
        shell_path = Path(shell).expanduser()
        if not shell_path.exists() or shell_path.name.lower() not in self._ALLOWED_SHELLS:
            return self._fallback_shell()
        return str(shell_path.resolve())

    def spawn_shell(self, shell: str | None = None) -> None:
        """Spawn a shell process, falling back when path/cwd are invalid."""
        command = self._resolve_shell(shell)
        cwd = self.working_dir if Path(self.working_dir).exists() else str(Path.home())
        self.close()
        try:
            self.pty_master, pty_slave = pty.openpty()
        except (ImportError, OSError):
            self.pty_master = None
            pty_slave = None
        self.process = subprocess.Popen(
            [command],
            cwd=cwd,
            stdin=pty_slave if pty_slave is not None else subprocess.DEVNULL,
            stdout=pty_slave if pty_slave is not None else subprocess.DEVNULL,
            stderr=pty_slave if pty_slave is not None else subprocess.DEVNULL,
            text=True,
        )
        if self.pty_master is None:
            self.pty_master = -1
        if pty_slave is not None:
            try:
                os.close(pty_slave)
            except OSError:
                pass
        self.is_active = True
        self.last_cleanup_diagnostic = None

    def cleanup(self) -> None:
        """Terminate the child process and clear pane resources."""
        proc = self.process
        self.last_cleanup_diagnostic = None
        if proc is not None:
            try:
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait(timeout=1)
            except BaseException as exc:  # noqa: BLE001 - diagnostics are part of the API.
                self.last_cleanup_diagnostic = {
                    "failure_type": "terminate_failed",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
        if self.pty_master is not None:
            try:
                os.close(self.pty_master)
            except OSError:
                pass
        self.process = None
        self.pty_master = None
        self.is_active = False

    def close(self) -> None:
        self.cleanup()


__all__ = ["TerminalPane"]
