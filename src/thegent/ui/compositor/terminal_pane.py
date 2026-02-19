"""TerminalPane - PTY-based terminal widget for the compositor."""

import logging
import os
import subprocess
from pathlib import Path

from textual.widgets import Static

logger = logging.getLogger(__name__)


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
        self.process: subprocess.Popen | None = None  # type: ignore
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
        """Called when widget is mounted."""
        logger.debug(f"TerminalPane {self.pane_id} mounted")
        self.render = self._render_placeholder

    def _render_placeholder(self) -> str:
        """Render placeholder content."""
        return f"Terminal Pane: {self.pane_id}\nWorking Directory: {self.working_dir}"

    def close(self) -> None:
        """Close this pane and cleanup resources."""
        logger.info(f"Closing TerminalPane {self.pane_id}")
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=1)
            except Exception as e:
                logger.error(f"Error terminating process: {e}")
                if self.process:
                    self.process.kill()

        if self.pty_master is not None:
            try:
                os.close(self.pty_master)
            except Exception as e:
                logger.error(f"Error closing PTY: {e}")

        self.process = None
        self.pty_master = None
