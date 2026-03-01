"""Terminal keepalive for long-running agent tasks.

Prints periodic dots/messages to stdout so the user can see the process
is still alive. Output is suppressed when stdout is not a TTY (CI/pipe).

Usage::

    from thegent_cli.ux.keepalive import keepalive, KeepaliveConfig, TerminalKeepalive

    with keepalive(interval_s=30.0):
        long_running_operation()

    # Or with custom config:
    cfg = KeepaliveConfig(interval_s=10.0, message=".", newline_every=5)
    with TerminalKeepalive(cfg) as ka:
        long_running_operation()
"""

from __future__ import annotations

import sys
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class KeepaliveConfig:
    """Configuration for :class:`TerminalKeepalive`.

    Attributes:
        interval_s: Seconds between keepalive characters (default: 30.0).
        message: Character/string to print on each tick (default: ".").
        newline_every: Print a newline after this many ticks so the line
            doesn't grow forever (default: 10).
        enabled: When *False* the keepalive is a no-op even inside the
            context manager (default: True).
    """

    interval_s: float = 30.0
    message: str = "."
    newline_every: int = 10
    enabled: bool = True
    # Mutable default handled via field() to satisfy dataclass rules.
    _tick_count: int = field(default=0, init=False, repr=False, compare=False)


class TerminalKeepalive:
    """Prints periodic keepalive dots/messages to stdout.

    Only prints when ``sys.stdout.isatty()`` returns *True* so CI/pipe
    environments receive no spurious output.

    Thread safety: :meth:`start` and :meth:`stop` are safe to call from
    any thread.  The background printing thread is a daemon thread so the
    process will not be blocked from exiting.

    Example::

        with TerminalKeepalive() as ka:
            time.sleep(120)  # dots print every 30 s
    """

    def __init__(self, config: KeepaliveConfig | None = None) -> None:
        self._config: KeepaliveConfig = config if config is not None else KeepaliveConfig()
        self._stop_event: threading.Event = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock: threading.Lock = threading.Lock()
        self._tick_count: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the background keepalive thread.

        If keepalive is disabled (``config.enabled is False``) or stdout
        is not a TTY, this is a no-op.  Calling :meth:`start` when the
        thread is already running is safe — the existing thread continues.
        """
        if not self._config.enabled:
            return
        if not self._is_tty():
            return

        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._stop_event.clear()
            self._tick_count = 0
            self._thread = threading.Thread(
                target=self._run,
                daemon=True,
                name="TerminalKeepalive",
            )
            self._thread.start()

    def stop(self) -> None:
        """Stop the background keepalive thread and print a trailing newline.

        Safe to call multiple times.  Waits up to 1 second for the thread
        to exit cleanly before returning.
        """
        thread: threading.Thread | None = None
        printed: bool = False

        with self._lock:
            thread = self._thread
            printed = self._tick_count > 0
            if thread is None or not thread.is_alive():
                # Thread was never started or already stopped.
                if printed and self._is_tty():
                    self._write_newline()
                return
            self._stop_event.set()

        # Join outside the lock to avoid blocking the background thread.
        thread.join(timeout=1.0)

        # Print trailing newline if any dots were written.
        if printed and self._is_tty():
            self._write_newline()

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> TerminalKeepalive:
        self.start()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.stop()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_tty() -> bool:
        """Return *True* when stdout is an interactive terminal."""
        try:
            return bool(sys.stdout.isatty())
        except (AttributeError, OSError):
            return False

    @staticmethod
    def _write_newline() -> None:
        """Write a single newline to stdout, swallowing IO errors."""
        try:
            sys.stdout.write("\n")
            sys.stdout.flush()
        except (OSError, AttributeError):
            pass

    def _run(self) -> None:
        """Background thread: print a keepalive message on each interval tick."""
        while not self._stop_event.wait(timeout=self._config.interval_s):
            if self._stop_event.is_set():
                break
            self._print_tick()

    def _print_tick(self) -> None:
        """Print one keepalive character, flushing immediately."""
        with self._lock:
            self._tick_count += 1
            tick = self._tick_count

        try:
            sys.stdout.write(self._config.message)
            sys.stdout.flush()
        except (OSError, AttributeError):
            return

        if self._config.newline_every > 0 and tick % self._config.newline_every == 0:
            self._write_newline()


@contextmanager
def keepalive(
    interval_s: float = 30.0,
    message: str = ".",
) -> Generator[TerminalKeepalive]:
    """Context manager convenience wrapper for :class:`TerminalKeepalive`.

    Suppresses output when stdout is not a TTY (CI/pipe).

    Args:
        interval_s: Seconds between each printed character.
        message: Character/string printed on each tick.

    Yields:
        The running :class:`TerminalKeepalive` instance.

    Example::

        with keepalive(interval_s=30.0):
            run_agent(prompt)
    """
    config = KeepaliveConfig(interval_s=interval_s, message=message)
    ka = TerminalKeepalive(config)
    ka.start()
    try:
        yield ka
    finally:
        ka.stop()
