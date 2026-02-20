"""Never-idle loop engine for Sitback Agent.

Provides continuous resident loop with:
- Non-blocking background task completion detection
- Rotating gardening checks
- Wake-on-completion callbacks
"""

from __future__ import annotations

import asyncio
import logging
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional

from thegent.sitback.gardening import GardeningManager
from thegent.sitback.watchdog import BackgroundTaskWatcher

_log = logging.getLogger(__name__)

# Type alias for wake callback
WakeCallback = Callable[[list[tuple[str, int]]], None]


class NeverIdleLoop:
    """Resident never-idle loop for Sitback Agent.

    Runs continuously with configurable sleep interval between iterations.
    Checks for background task completions (non-blocking) and runs gardening steps.
    """

    # Gardening steps in rotation order
    GARDENING_STEPS = [
        "govern_health",  # thegent govern go health
        "backlog_check",  # Check pending backlog
        "test_failures",  # Check recent test failures
        "traceability",  # Check FR traceability
        "escalation",  # Check past-SLA escalations
        "session_discovery",  # Scan for new external agents
        "quality_check",  # task quality-a-r
        "dag_sync",  # thegent dag sync
        # "smart_prune",  # DISABLED: Intelligent resource reclamation - too aggressive, kills terminals
    ]

    def __init__(
        self,
        session_dir: Path | None = None,
        sleep_interval: int = 45,
        project_root: Path | None = None,
    ) -> None:
        """Initialize the never-idle loop.

        Args:
            session_dir: Path to session directory. Defaults to ~/.thegent/sessions/
            sleep_interval: Seconds to sleep between iterations. Default 45.
            project_root: Root directory for gardening. Defaults to cwd.
        """
        if session_dir is None:
            session_dir = Path.home() / ".thegent" / "sessions"
        self.session_dir = session_dir

        self.sleep_interval = sleep_interval
        self.project_root = project_root or Path.cwd()

        self._running = False
        self._current_step = 0
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

        # Initialize components
        self._watcher = BackgroundTaskWatcher(session_dir)
        self._gardening = GardeningManager(project_root)

        # Callbacks for background task completion
        self._wake_callbacks: list[WakeCallback] = []

        # State tracking
        self._findings: dict[str, Any] = {}
        self._last_completion: dict[str, Any | None] = None

    def register_wake_callback(self, callback: WakeCallback) -> None:
        """Register a callback to be called when background task completes.

        Args:
            callback: Function(list of (session_id, exit_code)) to call.
        """
        self._wake_callbacks.append(callback)

    def is_running(self) -> bool:
        """Return whether the loop is currently running."""
        with self._lock:
            return self._running

    @property
    def current_step(self) -> str:
        """Return the current gardening step name."""
        return self.GARDENING_STEPS[self._current_step]

    def get_findings(self) -> dict[str, Any]:
        """Return gardening findings that need attention."""
        return self._findings.copy()

    def get_last_completion(self) -> dict[str, Any | None]:
        """Return last background task completion info."""
        return self._last_completion

    def start(self) -> None:
        """Start the never-idle loop in a background thread."""
        with self._lock:
            if self._running:
                _log.warning("Never-idle loop already running")
                return

            self._running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            _log.info("Never-idle loop started with %ds interval", self.sleep_interval)

    def stop(self) -> None:
        """Stop the never-idle loop."""
        with self._lock:
            if not self._running:
                _log.warning("Never-idle loop not running")
                return

            self._running = False
            if self._thread:
                self._thread.join(timeout=5)
            _log.info("Never-idle loop stopped")

    def _run_loop(self) -> None:
        """Main loop runner (runs in background thread)."""
        while True:
            with self._lock:
                if not self._running:
                    break

            try:
                self._run_once()
            except Exception as e:
                _log.error("Error in never-idle loop: %s", e)

            # Sleep with early exit check
            for _ in range(self.sleep_interval):
                with self._lock:
                    if not self._running:
                        break
                threading.Event().wait(1)

    def _run_once(self) -> None:
        """Run one iteration of the never-idle loop."""
        # 1. Check background completions (non-blocking)
        completions = self._watcher.run_once()
        if completions:
            self._handle_wake(completions)

        # 2. Run next gardening step
        step = self.GARDENING_STEPS[self._current_step]
        result = asyncio.run(self._gardening.run_step(step))

        # Store findings for items needing attention
        if result.get("needs_attention"):
            self._findings[step] = result

        # 3. Rotate to next step
        self._current_step = (self._current_step + 1) % len(self.GARDENING_STEPS)

    def _handle_wake(self, completions: list[tuple[str, int]]) -> None:
        """Handle background task completion - notify callbacks.

        Args:
            completions: List of (session_id, exit_code) tuples.
        """
        for session_id, exit_code in completions:
            self._last_completion = {
                "session_id": session_id,
                "exit_code": exit_code,
            }

        # Notify callbacks
        for callback in self._wake_callbacks:
            try:
                callback(completions)
            except Exception as e:
                _log.warning("Wake callback error: %s", e)

    def get_status(self) -> dict[str, Any]:
        """Get current status of the never-idle loop."""
        return {
            "running": self.is_running(),
            "current_step": self.current_step,
            "step_index": self._current_step,
            "sleep_interval": self.sleep_interval,
            "findings_count": len(self._findings),
            "last_completion": self._last_completion,
            "gardening_summary": self._gardening.get_summary(),
        }


# Global instance for easy access
_never_idle_instance: NeverIdleLoop | None = None


def get_never_idle() -> NeverIdleLoop | None:
    """Get the global never-idle loop instance."""
    return _never_idle_instance


def start_never_idle(
    sleep_interval: int = 45,
    session_dir: Path | None = None,
    project_root: Path | None = None,
) -> NeverIdleLoop:
    """Start the global never-idle loop.

    Args:
        sleep_interval: Seconds between iterations.
        session_dir: Path to session directory.
        project_root: Root directory for gardening.

    Returns:
        The started NeverIdleLoop instance.
    """
    global _never_idle_instance

    if _never_idle_instance is not None and _never_idle_instance.is_running():
        _log.warning("Never-idle loop already running, returning existing instance")
        return _never_idle_instance

    _never_idle_instance = NeverIdleLoop(
        session_dir=session_dir,
        sleep_interval=sleep_interval,
        project_root=project_root,
    )
    _never_idle_instance.start()
    return _never_idle_instance


def stop_never_idle() -> None:
    """Stop the global never-idle loop."""
    global _never_idle_instance

    if _never_idle_instance is not None:
        _never_idle_instance.stop()
        _never_idle_instance = None


def get_never_idle_status() -> dict[str, Any]:
    """Get status of the global never-idle loop."""
    if _never_idle_instance is None:
        return {"running": False, "error": "Not started"}

    return _never_idle_instance.get_status()
