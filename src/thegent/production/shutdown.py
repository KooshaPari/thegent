"""
Graceful Shutdown

Handles graceful shutdown with cleanup.
"""

from typing import Callable, Optional
import signal
import sys
import time
import threading


class GracefulShutdown:
    """Manages graceful shutdown."""

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self._shutdown_handlers: list[Callable] = []
        self._shutting_down = False
        self._lock = threading.Lock()
        self._original_handlers: dict = {}

    def register(self, handler: Callable) -> None:
        """Register a shutdown handler."""
        self._shutdown_handlers.append(handler)

    def install(self) -> None:
        """Install signal handlers."""
        self._original_handlers[signal.SIGINT] = signal.signal(signal.SIGINT, self._handler)
        self._original_handlers[signal.SIGTERM] = signal.signal(signal.SIGTERM, self._handler)

    def uninstall(self) -> None:
        """Restore original signal handlers."""
        for sig, handler in self._original_handlers.items():
            if handler is not None:
                signal.signal(sig, handler)
        self._original_handlers.clear()

    def _handler(self, signum: int, frame) -> None:
        """Signal handler."""
        with self._lock:
            if self._shutting_down:
                # Force exit on second signal
                sys.exit(1)
            self._shutting_down = True

        print(f"\nReceived signal {signum}, shutting down gracefully...")

        # Run shutdown handlers with timeout
        self._run_handlers()

        sys.exit(0)

    def _run_handlers(self) -> None:
        """Run all shutdown handlers."""
        start = time.time()
        remaining = self.timeout

        for handler in self._shutdown_handlers:
            if remaining <= 0:
                break

            try:
                handler_start = time.time()
                handler()
                elapsed = time.time() - handler_start
                remaining -= elapsed
            except Exception as e:
                print(f"Shutdown handler error: {e}")

        total = time.time() - start
        print(f"Shutdown completed in {total:.2f}s")

    def shutdown(self) -> None:
        """Trigger shutdown programmatically."""
        self._handler(signal.SIGTERM, None)

    @property
    def is_shutting_down(self) -> bool:
        """Check if shutting down."""
        return self._shutting_down

    def __enter__(self):
        self.install()
        return self

    def __exit__(self, *args):
        self.uninstall()


class ShutdownContext:
    """Context manager for shutdown-aware operations."""

    def __init__(self, shutdown: GracefulShutdown):
        self.shutdown = shutdown

    def check(self) -> bool:
        """Check if should continue."""
        return not self.shutdown.is_shutting_down

    def __bool__(self) -> bool:
        return self.check()
