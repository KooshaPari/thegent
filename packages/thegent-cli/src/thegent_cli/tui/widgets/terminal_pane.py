"""Terminal pane widget for TUI compositor.

Provides a terminal emulator pane using Python's asyncio and pty modules.
Supports subprocess execution and output display.
"""

from __future__ import annotations

import asyncio
from asyncio import subprocess
import contextlib
import fcntl
import os
import pty
import struct
import termios
from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual.css.query import QueryError
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from textual.events import Resize


@dataclass
class TerminalSize:
    """Terminal dimensions in rows/cols."""

    rows: int = 24
    cols: int = 80


@dataclass
class TerminalConfig:
    """Configuration for terminal pane."""

    rows: int = 24
    cols: int = 80
    env: dict[str, str] | None = None
    cwd: Path | None = None
    shell: str = "/bin/zsh"


class TerminalPane(Widget):
    """Widget that displays terminal output and executes commands."""

    # Reactive state
    is_running: reactive[bool] = reactive[bool](False)
    last_exit_code: reactive[int | None] = reactive[int | None](None)

    DEFAULT_CSS = """
    TerminalPane {
        height: 100%;
        width: 100%;
        background: $background;
        color: $text;
    }

    TerminalPane .output {
        height: 100%;
        width: 100%;
        overflow: hidden;
    }

    TerminalPane .cursor {
        background: $accent;
        color: $background;
    }

    TerminalPane .status {
        height: 1;
        background: $surface;
        color: $text-muted;
    }
    """

    def __init__(
        self,
        *,
        config: TerminalConfig | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.config = config or TerminalConfig()
        self._master_fd: int | None = None
        self._process: subprocess.Process | None = None
        self._output_buffer: list[str] = []
        self._output_lines: list[str] = []
        self._max_lines: int = 1000
        self._command_task: asyncio.Task[None] | None = None
        self._reader_task: asyncio.Task[None] | None = None
        self._size = TerminalSize(rows=self.config.rows, cols=self.config.cols)

    async def _setup_pty(self) -> tuple[int, int]:
        """Set up PTY and return (master, slave) file descriptors."""
        master, slave = pty.openpty()
        # Set non-blocking
        flags = fcntl.fcntl(master, fcntl.F_GETFL)
        fcntl.fcntl(master, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        return master, slave

    async def _resize(self, rows: int, cols: int) -> None:
        """Resize the terminal."""
        self._size = TerminalSize(rows=rows, cols=cols)
        if self._master_fd is not None:
            try:
                winsize = struct.pack("HHHH", rows, cols, 0, 0)
                fcntl.ioctl(self._master_fd, termios.TIOCSWINSZ, winsize)
            except OSError:
                pass

    async def write(self, data: str) -> None:
        """Write data to the terminal."""
        if self._master_fd is not None:
            with contextlib.suppress(OSError):
                os.write(self._master_fd, data.encode())

    async def write_input(self, input_text: str) -> None:
        """Write keyboard input to the terminal."""
        await self.write(input_text)

    async def run_command(
        self,
        command: str,
        *,
        on_exit: Callable[[int], None] | None = None,
    ) -> int:
        """Run a command in the terminal.

        Args:
            command: Command to execute
            on_exit: Callback when command exits

        Returns:
            Exit code
        """
        self._output_buffer.clear()
        self._output_lines.clear()
        self.is_running = True

        try:
            master, slave = await self._setup_pty()
            self._master_fd = master

            # Create environment
            env = os.environ.copy()
            if self.config.env:
                env.update(self.config.env)

            # Start process
            self._process = await asyncio.create_subprocess_shell(
                command,
                stdin=slave,
                stdout=slave,
                stderr=slave,
                env=env,
                cwd=str(self.config.cwd) if self.config.cwd else None,
            )

            # Start output reader
            self._reader_task = asyncio.create_task(self._read_output())

            # Wait for completion
            exit_code = await self._process.wait()
            self.last_exit_code = exit_code

            if self._reader_task:
                self._reader_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._reader_task

            self.is_running = False

            if on_exit:
                on_exit(exit_code)

            return exit_code

        except Exception as e:
            self._output_buffer.append(f"Error: {e}")
            self.is_running = False
            return -1

    async def start_shell(self) -> None:
        """Start an interactive shell."""
        await self.run_command(
            f"{self.config.shell} -i",
            on_exit=self._on_shell_exit,
        )

    def _on_shell_exit(self, exit_code: int) -> None:
        """Handle shell exit."""
        self._output_buffer.append(f"\n[Shell exited with code {exit_code}]")

    async def _read_output(self) -> None:
        """Read output from the terminal."""
        if self._master_fd is None:
            return

        while True:
            try:
                data = os.read(self._master_fd, 4096)
                if not data:
                    break
                text = data.decode("utf-8", errors="replace")
                self._output_buffer.append(text)
                self._update_output_display()
            except OSError:
                break

    def _update_output_display(self) -> None:
        """Update the output display widget."""
        # Combine buffer and truncate
        full_output = "".join(self._output_buffer)
        lines = full_output.split("\n")

        # Keep last N lines
        if len(lines) > self._max_lines:
            lines = lines[-self._max_lines :]

        self._output_lines = lines

        # Update display
        try:
            output = self.query_one(".output", Static)
            output.update("\n".join(self._output_lines[-100:]))
        except QueryError:
            pass

    def clear(self) -> None:
        """Clear the terminal output."""
        self._output_buffer.clear()
        self._output_lines.clear()
        self._update_output_display()

    def get_output(self) -> str:
        """Get all output as a string."""
        return "".join(self._output_lines)

    def on_resize(self, event: Resize) -> None:
        """Handle terminal resize."""
        # Calculate new rows/cols based on size
        cols = max(40, event.size.width // 8)
        rows = max(10, event.size.height // 16)
        asyncio.create_task(self._resize(rows, cols))

    async def on_mount(self) -> None:
        """Initialize after mounting."""
        await self._resize(self._size.rows, self._size.cols)


class TerminalManager:
    """Manages multiple terminal panes."""

    def __init__(self) -> None:
        self._panes: dict[str, TerminalPane] = {}
        self._active: str | None = None

    def add_pane(self, pane_id: str, pane: TerminalPane) -> None:
        """Add a terminal pane."""
        self._panes[pane_id] = pane
        self._active = pane_id

    def get_pane(self, pane_id: str) -> TerminalPane | None:
        """Get a terminal pane by ID."""
        return self._panes.get(pane_id)

    def set_active(self, pane_id: str) -> bool:
        """Set the active pane."""
        if pane_id in self._panes:
            self._active = pane_id
            return True
        return False

    def list_panes(self) -> list[str]:
        """List all pane IDs."""
        return list(self._panes.keys())

    def get_active(self) -> TerminalPane | None:
        """Get the active pane."""
        if self._active:
            return self._panes.get(self._active)
        return None
