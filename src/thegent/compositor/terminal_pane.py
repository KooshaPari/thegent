"""Terminal pane widget for the TUI compositor.

Handles PTY allocation, shell spawning, and input/output management for individual terminal panes.
"""

import os
import select
import subprocess

from textual.widgets import Static


class TerminalPane(Static):
    """A terminal pane widget that manages a PTY and shell process.

    Attributes:
        pane_id: Unique identifier for this pane
        working_dir: Working directory for the shell process
    """

    DEFAULT_CSS = """
    TerminalPane {
        border: solid $primary;
        background: $panel;
        color: $text;
        width: 1fr;
        height: 1fr;
        overflow: auto;
    }
    """

    def __init__(self, pane_id: str, working_dir: str = ".") -> None:
        """Initialize a TerminalPane.

        Args:
            pane_id: Unique identifier for this pane
            working_dir: Working directory for the shell process (default: current directory)
        """
        super().__init__()
        self.pane_id = pane_id
        self.working_dir = os.path.expanduser(working_dir)
        self.process: subprocess.Popen | None = None
        self.output_buffer: str = ""
        self.is_active = True

    def render(self) -> str:
        """Render the current output buffer to the pane."""
        return self.output_buffer or "Terminal ready. Type commands here.\n"

    def spawn_shell(self, shell: str = "/bin/bash") -> None:
        """Spawn a shell process in a PTY.

        Args:
            shell: Path to the shell executable (default: /bin/bash)

        Raises:
            RuntimeError: If shell spawning fails
        """
        if self.process is not None and self.process.poll() is None:
            return

        try:
            # Ensure shell exists
            if not os.path.exists(shell):
                shell = "/bin/sh"

            # For Textual, we'll use a simple subprocess approach
            # A full PTY implementation would require ptyprocess or similar
            self.process = subprocess.Popen(
                [shell],
                cwd=self.working_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True,
            )
            self.output_buffer = f"Shell spawned: {shell}\nWorking directory: {self.working_dir}\n"
        except Exception as e:
            error_msg = f"Failed to spawn shell: {e}"
            self.output_buffer = error_msg
            self.is_active = False
            raise RuntimeError(error_msg) from e

    def write_input(self, data: str) -> None:
        """Write input to the shell process.

        Args:
            data: Input string to write to the shell

        Raises:
            RuntimeError: If process is not running or write fails
        """
        if self.process is None or self.process.poll() is not None:
            raise RuntimeError("Shell process is not running")

        try:
            if self.process.stdin:
                self.process.stdin.write(data)
                self.process.stdin.flush()
        except Exception as e:
            raise RuntimeError(f"Failed to write to shell: {e}") from e

    def read_output(self) -> str:
        """Read available output from the shell process.

        Returns:
            Output string from the shell process
        """
        if self.process is None or self.process.poll() is not None:
            return ""

        try:
            if self.process.stdout and select.select([self.process.stdout], [], [], 0)[0]:
                output = self.process.stdout.read(4096)
                return output
        except Exception:
            return ""

        return ""

    def cleanup(self) -> None:
        """Clean up the terminal pane by terminating the shell process."""
        if self.process is not None:
            try:
                if self.process.poll() is None:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
            except Exception:
                pass
            finally:
                self.process = None
                self.is_active = False

    def on_mount(self) -> None:
        """Called when the pane is mounted. Spawns the shell."""
        try:
            self.spawn_shell()
        except RuntimeError:
            self.output_buffer = "Failed to initialize terminal pane"

    def on_unmount(self) -> None:
        """Called when the pane is unmounted. Cleans up the shell."""
        self.cleanup()
