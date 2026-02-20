"""TerminalPane - PTY-based terminal widget for the compositor."""

import logging
import os
import subprocess
from pathlib import Path

from textual.message import Message
from textual.widgets import Static

logger = logging.getLogger(__name__)


class PanelMounted(Message):
    """Sent when a panel is mounted."""

    def __init__(self, pane_id: str) -> None:
        super().__init__()
        self.pane_id = pane_id


class PanelUnmounted(Message):
    """Sent when a panel is unmounted."""

    def __init__(self, pane_id: str) -> None:
        super().__init__()
        self.pane_id = pane_id


class TerminalPane(Static):
    """A terminal pane widget backed by a PTY."""

    DEFAULT_CSS = """
    TerminalPane {
        width: 1fr;
        height: 1fr;
        border: solid $primary;
        background: $surface;
    }
    """

    def __init__(
        self,
        pane_id: str,
        working_dir: str = ".",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize TerminalPane.

        Args:
            pane_id: Unique identifier for this pane
            working_dir: Working directory for shell
            name: Display name for pane
            id: Textual widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.pane_id = pane_id
        self.working_dir = working_dir
        self.process: subprocess.Popen | None = None
        self.pty_master: int | None = None
        logger.info(f"TerminalPane {pane_id} created with working_dir={working_dir}")

    def spawn_shell(self, shell: str = "/bin/bash") -> None:
        """Spawn a shell in this pane via PTY.

        Args:
            shell: Shell binary path (default: /bin/bash)

        Raises:
            OSError: If PTY allocation or shell spawn fails

        Note:
            Requires Unix/Linux/macOS. Windows may need alternative PTY implementation.
        """
        try:
            # Verify shell exists
            if not Path(shell).exists():
                logger.warning(f"Shell {shell} not found, using /bin/sh")
                shell = "/bin/sh"

            # Get working directory
            cwd = Path(self.working_dir).expanduser().resolve()
            if not cwd.exists():
                logger.warning(f"Working dir {cwd} does not exist, using home")
                cwd = Path.home()

            logger.info(f"Spawning shell {shell} in {cwd}")

            # Allocate PTY (Unix/Linux/macOS)
            try:
                import pty

                self.pty_master, pty_slave = pty.openpty()
                logger.debug(f"PTY allocated: master={self.pty_master}, slave={pty_slave}")
            except ImportError:
                logger.warning("PTY module not available, falling back to pipe mode")
                # Fallback: use pipes instead (non-interactive)
                self.process = subprocess.Popen(
                    [shell],
                    cwd=str(cwd),
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                logger.info(f"Shell spawned in pipe mode (PID: {self.process.pid})")
                return

            # Spawn shell with PTY
            self.process = subprocess.Popen(
                [shell],
                stdin=pty_slave,
                stdout=pty_slave,
                stderr=pty_slave,
                preexec_fn=os.setsid,  # Create new session
                cwd=str(cwd),
                start_new_session=False,
            )

            # Close slave in parent (only parent uses master)
            os.close(pty_slave)

            logger.info(f"Shell spawned with PTY (PID: {self.process.pid}, master_fd: {self.pty_master})")

        except Exception as e:
            logger.error(f"Failed to spawn shell: {e}", exc_info=True)
            self.process = None
            self.pty_master = None
            raise

    def on_mount(self) -> None:
        """Called when widget is mounted.

        Lifecycle hook that spawns the shell process on pane mount.
        This ensures the shell starts when the widget is actually displayed.
        """
        try:
            logger.debug(f"TerminalPane {self.pane_id} mounted")

            # Spawn shell process on mount
            self.spawn_shell()

            # Post mount message
            self.post_message(PanelMounted(self.pane_id))

            logger.info(f"Shell spawned for pane {self.pane_id}")

        except Exception as e:
            logger.error(f"Error spawning shell in on_mount for {self.pane_id}: {e}", exc_info=True)
            # Use a custom render method for error display
            self._error_msg = str(e)
            self.render = self._render_error

    def on_unmount(self) -> None:
        """Called when widget is unmounted."""
        logger.debug(f"TerminalPane {self.pane_id} unmounting")
        self.close()
        self.post_message(PanelUnmounted(self.pane_id))

    def _render_error(self) -> str:
        """Render error message."""
        return f"Terminal Pane: {self.pane_id}\n[red]ERROR[/red]: {self._error_msg}\n[dim]Check logs for details[/dim]"

    def _render_placeholder(self) -> str:
        """Render placeholder content."""
        status = "Ready"
        if self.process:
            status = f"Running (PID: {self.process.pid})"
        elif self.process is None and hasattr(self, "_spawn_attempted"):
            status = "Shell spawned via PTY"
        return f"Terminal Pane: {self.pane_id}\nStatus: {status}\nDirectory: {self.working_dir}"

    def close(self) -> None:
        """Close this pane and cleanup resources.

        Lifecycle hook that:
        - Gracefully terminates the shell process
        - Cleans up PTY file descriptors
        - Handles edge cases (already terminated, permission errors)
        """
        try:
            logger.info(f"Closing TerminalPane {self.pane_id}")

            # Terminate process if running
            if self.process:
                try:
                    # Try graceful termination first
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        logger.warning(f"Process {self.pane_id} did not terminate gracefully, killing")
                        self.process.kill()
                        self.process.wait()
                    logger.debug(f"Process {self.pane_id} terminated")

                except Exception as e:
                    logger.error(f"Error terminating process {self.pane_id}: {e}")

            # Close PTY master file descriptor
            if self.pty_master is not None:
                try:
                    os.close(self.pty_master)
                    logger.debug(f"PTY closed for {self.pane_id}")
                except Exception as e:
                    logger.error(f"Error closing PTY for {self.pane_id}: {e}")

            # Clear references
            self.process = None
            self.pty_master = None
            logger.info(f"TerminalPane {self.pane_id} closed successfully")

        except Exception as e:
            logger.error(f"Unexpected error during close: {e}", exc_info=True)
            # Still clear references even on error
            self.process = None
            self.pty_master = None
