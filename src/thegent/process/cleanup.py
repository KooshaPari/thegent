"""
Process Cleanup

Tracks and cleans up child processes on interrupt.
"""

from typing import Any, Optional
import os
import signal
import atexit


class ProcessCleanup:
    """Tracks and cleans up child processes."""

    _instance: Optional["ProcessCleanup"] = None
    _processes: set[int]
    _registered: bool

    def __new__(cls) -> "ProcessCleanup":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._processes = set()
            cls._instance._registered = False
        return cls._instance

    def register(self, pid: int) -> None:
        """Register a process for cleanup."""
        self._processes.add(pid)
        self._ensure_registered()

    def unregister(self, pid: int) -> None:
        """Unregister a process."""
        self._processes.discard(pid)

    def _ensure_registered(self) -> None:
        """Ensure cleanup handlers are registered."""
        if self._registered:
            return

        atexit.register(self.cleanup_all)
        self._registered = True

    def cleanup_all(self) -> None:
        """Kill all registered processes."""
        for pid in list(self._processes):
            try:
                self._kill_process_tree(pid)
            except ProcessLookupError:
                pass
            self._processes.discard(pid)

    def _kill_process_tree(self, pid: int) -> None:
        """Kill a process and all its children."""
        try:
            # Try process group first
            pgid = os.getpgid(pid)
            os.killpg(pgid, signal.SIGTERM)

            # Wait briefly then force kill
            import time
            time.sleep(0.5)

            try:
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass

        except ProcessLookupError:
            # Process already gone
            pass
        except PermissionError:
            # Try direct kill
            try:
                os.kill(pid, signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                pass

    def cleanup_on_signal(self, signum: int, frame: Any) -> None:
        """Signal handler for cleanup."""
        self.cleanup_all()
        # Re-raise signal
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)


# Global instance
_cleanup = ProcessCleanup()


def register_cleanup(pid: int) -> None:
    """Register a process for cleanup on exit/interrupt."""
    _cleanup.register(pid)
