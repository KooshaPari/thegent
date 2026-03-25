"""
Signal Handler

Registers handlers for graceful shutdown.
"""

from typing import Callable, Optional
from .cleanup import ProcessCleanup
import signal
import os


class SignalHandler:
    """Handles system signals for graceful shutdown."""

    def __init__(self):
        self._cleanup = ProcessCleanup()
        self._original_handlers: dict[int, callable] = {}
        self._callbacks: list[Callable] = []
        self._installed = False

    def install(self) -> None:
        """Install signal handlers."""
        if self._installed:
            return

        # Handle SIGINT (Ctrl+C)
        self._install_handler(signal.SIGINT)

        # Handle SIGTERM
        self._install_handler(signal.SIGTERM)

        self._installed = True

    def _install_handler(self, signum: int) -> None:
        """Install handler for a signal."""
        self._original_handlers[signum] = signal.signal(signum, self._handler)

    def _handler(self, signum: int, frame) -> None:
        """Signal handler."""
        # Run callbacks
        for callback in self._callbacks:
            try:
                callback()
            except Exception as e:
                # Signal handlers must not raise; log and continue so all callbacks run.
                import logging

                logging.getLogger(__name__).warning(
                    "signal_callback_error: callback=%r error_type=%s error=%s",
                    callback,
                    type(e).__name__,
                    e,
                )

        # Cleanup processes
        self._cleanup.cleanup_all()

        # Call original handler or re-raise
        original = self._original_handlers.get(signum)
        if original:
            original(signum, frame)
        else:
            signal.signal(signum, signal.SIG_DFL)
            os.kill(os.getpid(), signum)

    def on_shutdown(self, callback: Callable) -> None:
        """Register callback for shutdown."""
        self._callbacks.append(callback)

    def restore(self) -> None:
        """Restore original signal handlers."""
        for signum, handler in self._original_handlers.items():
            signal.signal(signum, handler)
        self._original_handlers.clear()
        self._installed = False


# Global handler
_handler: Optional[SignalHandler] = None


def install_signal_handlers() -> SignalHandler:
    """Install global signal handlers."""
    global _handler
    if _handler is None:
        _handler = SignalHandler()
        _handler.install()
    return _handler
