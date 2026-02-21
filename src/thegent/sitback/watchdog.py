"""Background task watcher for non-blocking completion detection.

Provides polling-based detection of background task completion without blocking.
Used by the never-idle loop to wake on task completion.

Also provides :class:`WatcherDaemon` (WP-5003): auto-scaling coroutine that
reads queue depth from :class:`~thegent.orchestration.execution.priority_queue.RunPriorityQueue`
or :class:`~thegent.core.prompt_queue.PromptQueueManager` and calls
:class:`~thegent.compute.offload.ComputePoolManager` to expand / shrink the
remote compute pool when thresholds are crossed.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from thegent.compute.offload import ComputePoolManager
    from thegent.orchestration.execution.priority_queue import RunPriorityQueue

_log = logging.getLogger(__name__)

# Type alias for callback: (session_id, exit_code) -> None
CompletionCallback = Callable[[str, int], None]

# Default env-controlled thresholds
_DEFAULT_SCALE_THRESHOLD = int(os.environ.get("THGENT_SCALE_THRESHOLD", "10"))
_SCALE_DOWN_DEPTH = 2
_SCALE_DOWN_IDLE_S = 300.0  # 5 minutes
_SCALE_CHECK_INTERVAL_S = 30.0


class BackgroundTaskWatcher:
    """Non-blocking watcher for background task completion.

    Polls run_registry.jsonl for 'finish' events and checks session RC files.
    Supports callback registration for completion notifications.
    """

    def __init__(
        self,
        session_dir: Path | None = None,
        poll_interval: float = 2.0,
    ) -> None:
        """Initialize the watcher.

        Args:
            session_dir: Path to session directory. Defaults to ~/.thegent/sessions/
            poll_interval: Polling interval in seconds. Default 2.0
        """
        if session_dir is None:
            session_dir = Path.home() / ".thegent" / "sessions"
        self.session_dir = session_dir
        self.poll_interval = poll_interval
        self._callbacks: list[CompletionCallback] = []
        self._last_positions: dict[Path, int] = {}  # registry_path -> position
        self._known_sessions: set[str] = set()

        # Initialize position tracking
        self._init_positions()

    def _init_positions(self) -> None:
        """Initialize file positions for all registry files."""
        registry_path = self.session_dir / "run_registry.jsonl"
        if registry_path.exists():
            try:
                # Start from end of file
                with registry_path.open("rb") as f:
                    f.seek(0, 2)  # Seek to end
                    self._last_positions[registry_path] = f.tell()
                self._load_existing_sessions(registry_path)
            except Exception as e:
                _log.warning("Failed to init registry positions: %s", e)

    def _load_existing_sessions(self, registry_path: Path) -> None:
        """Load existing session IDs from registry."""
        try:
            with registry_path.open("r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        record = json.loads(line)
                        if record.get("event") == "start":
                            self._known_sessions.add(record.get("session_id", ""))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            _log.warning("Failed to load existing sessions: %s", e)

    def register_callback(self, callback: CompletionCallback) -> None:
        """Register a callback to be called on task completion.

        Args:
            callback: Function(session_id, exit_code) to call when task completes.
        """
        self._callbacks.append(callback)

    def check_completions(self) -> list[tuple[str, int]]:
        """Check for newly completed tasks.

        Polls run_registry.jsonl for 'finish' events and checks session RC files.

        Returns:
            List of (session_id, exit_code) tuples for newly completed tasks.
        """
        completions: list[tuple[str, int]] = []
        registry_path = self.session_dir / "run_registry.jsonl"

        if not registry_path.exists():
            return completions

        try:
            current_pos = registry_path.stat().st_size

            # If file was truncated/rotated, reset position
            last_pos = self._last_positions.get(registry_path, 0)
            if current_pos < last_pos:
                last_pos = 0

            if current_pos > last_pos:
                with registry_path.open("r", encoding="utf-8") as f:
                    f.seek(last_pos)
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            record = json.loads(line)
                            event = record.get("event", "")

                            if event == "finish":
                                session_id = record.get("session_id", "")
                                exit_code = record.get("exit_code", -1)
                                if session_id and session_id not in self._known_sessions:
                                    completions.append((session_id, exit_code))
                                    self._known_sessions.add(session_id)
                            elif event == "start":
                                session_id = record.get("session_id", "")
                                if session_id:
                                    self._known_sessions.add(session_id)
                        except json.JSONDecodeError:
                            continue

                self._last_positions[registry_path] = current_pos

        except Exception as e:
            _log.warning("Error checking completions: %s", e)

        # Also check for completed sessions via RC files
        completions.extend(self._check_rc_files())

        return completions

    def _check_rc_files(self) -> list[tuple[str, int]]:
        """Check session RC files for completion status.

        RC files contain the exit code when a session completes.
        """
        completions: list[tuple[str, int]] = []

        if not self.session_dir.exists():
            return completions

        try:
            for session_file in self.session_dir.glob("*.json"):
                if session_file.stem.startswith("."):
                    continue

                # Check for RC file (session_id + ".rc")
                rc_file = session_file.with_suffix(".rc")
                if rc_file.exists():
                    session_id = session_file.stem

                    # Only report if we haven't seen this session complete
                    if session_id in self._known_sessions:
                        continue

                    try:
                        exit_code = int(rc_file.read_text().strip())
                        completions.append((session_id, exit_code))
                        self._known_sessions.add(session_id)
                    except (OSError, ValueError) as e:
                        _log.debug("Could not read RC file %s: %s", rc_file, e)
        except Exception as e:
            _log.warning("Error checking RC files: %s", e)

        return completions

    def run_once(self) -> list[tuple[str, int]]:
        """Run one check cycle, trigger callbacks, return completions.

        Returns:
            List of (session_id, exit_code) tuples for completed tasks.
        """
        completions = self.check_completions()

        for session_id, exit_code in completions:
            for callback in self._callbacks:
                try:
                    callback(session_id, exit_code)
                except Exception as e:  # noqa: PERF203 - intentional per-item error handling
                    _log.warning("Callback error for %s: %s", session_id, e)

        return completions

    def wait_for_completion(
        self,
        timeout: float | None = None,
    ) -> list[tuple[str, int]]:
        """Wait for any task to complete.

        This is a blocking wait with timeout. For non-blocking use run_once().

        Args:
            timeout: Maximum seconds to wait. None = wait forever.

        Returns:
            List of (session_id, exit_code) tuples for completed tasks.
        """
        start_time = time.time()

        while True:
            completions = self.run_once()
            if completions:
                return completions

            if timeout is not None and (time.time() - start_time) >= timeout:
                return []

            time.sleep(self.poll_interval)

    def get_known_sessions(self) -> set[str]:
        """Return set of known session IDs."""
        return self._known_sessions.copy()

    def reset(self) -> None:
        """Reset state (for testing)."""
        self._known_sessions.clear()
        self._last_positions.clear()
        self._init_positions()


# ---------------------------------------------------------------------------
# WP-5003: Auto-scaling watchdog daemon
# ---------------------------------------------------------------------------


class WatcherDaemon:
    """Async daemon that auto-scales the compute pool based on queue depth (WP-5003).

    Runs two coroutines every ``check_interval_s`` seconds:

    * :meth:`_check_scale_trigger`: if queue depth > ``scale_threshold``,
      calls ``pool_manager.expand(2)`` to add two remote workers.
    * :meth:`_check_scale_down`: if queue depth < ``scale_down_depth`` and
      all remote workers have been idle for ``idle_threshold_s``, calls
      ``pool_manager.shrink()`` to release idle remote nodes.

    Args:
        pool_manager: The :class:`~thegent.compute.offload.ComputePoolManager`
            that manages remote node lifecycle.
        run_queue: Optional :class:`~thegent.orchestration.execution.priority_queue.RunPriorityQueue`
            to read queue depth from.  When ``None``, *prompt_queue* is used.
        prompt_queue: Optional queue-like object with a ``list_pending()`` or
            ``qsize()`` method.  Used when *run_queue* is ``None``.
        scale_threshold: Queue depth above which scale-up is triggered.
        scale_down_depth: Queue depth below which scale-down is considered.
        idle_threshold_s: Seconds a remote worker must be idle before
            scale-down is allowed.
        check_interval_s: Seconds between successive checks.
    """

    def __init__(
        self,
        pool_manager: ComputePoolManager,
        run_queue: RunPriorityQueue | None = None,
        prompt_queue: Any | None = None,
        scale_threshold: int = _DEFAULT_SCALE_THRESHOLD,
        scale_down_depth: int = _SCALE_DOWN_DEPTH,
        idle_threshold_s: float = _SCALE_DOWN_IDLE_S,
        check_interval_s: float = _SCALE_CHECK_INTERVAL_S,
    ) -> None:
        self._pool = pool_manager
        self._run_queue = run_queue
        self._prompt_queue = prompt_queue
        self._scale_threshold = scale_threshold
        self._scale_down_depth = scale_down_depth
        self._idle_threshold_s = idle_threshold_s
        self._check_interval_s = check_interval_s
        self._task: asyncio.Task[None] | None = None

    # ------------------------------------------------------------------
    # Queue depth helpers
    # ------------------------------------------------------------------

    def _queue_depth(self) -> int:
        """Return current queue depth from whichever queue is configured."""
        if self._run_queue is not None:
            return self._run_queue.qsize()
        if self._prompt_queue is not None:
            # PromptQueueManager exposes list_pending(); fallback to qsize()
            if hasattr(self._prompt_queue, "list_pending"):
                return len(self._prompt_queue.list_pending())
            if hasattr(self._prompt_queue, "qsize"):
                return self._prompt_queue.qsize()
        return 0

    # ------------------------------------------------------------------
    # Scale coroutines
    # ------------------------------------------------------------------

    async def _check_scale_trigger(self) -> None:
        """Scale up if queue depth exceeds threshold (WP-5003).

        Calls ``ComputePoolManager.expand(2)`` when depth > scale_threshold.
        """
        depth = self._queue_depth()
        if depth > self._scale_threshold:
            _log.info(
                "WatcherDaemon: queue depth %d > threshold %d, expanding pool by 2",
                depth,
                self._scale_threshold,
            )
            added = self._pool.expand(2)
            _log.info("WatcherDaemon: scale-up added %d node(s)", len(added))
        else:
            _log.debug("WatcherDaemon: queue depth %d, no scale-up needed", depth)

    async def _check_scale_down(self) -> None:
        """Scale down when queue is shallow and remote workers are idle (WP-5003).

        Calls ``ComputePoolManager.shrink()`` when all conditions are met.
        """
        depth = self._queue_depth()
        if depth >= self._scale_down_depth:
            _log.debug("WatcherDaemon: queue depth %d >= %d, no scale-down", depth, self._scale_down_depth)
            return

        # Check if any remote node has been idle long enough
        now = time.monotonic()
        idle_long_enough = {
            node_id: since
            for node_id, since in self._pool._remote_idle_since.items()  # noqa: SLF001
            if now - since >= self._idle_threshold_s
        }
        if not idle_long_enough:
            _log.debug("WatcherDaemon: no remote nodes idle >= %.0fs, deferring scale-down", self._idle_threshold_s)
            return

        _log.info(
            "WatcherDaemon: queue depth %d < %d and %d node(s) idle >= %.0fs, shrinking",
            depth,
            self._scale_down_depth,
            len(idle_long_enough),
            self._idle_threshold_s,
        )
        released = self._pool.shrink()
        _log.info("WatcherDaemon: scale-down released %d node(s): %s", len(released), released)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def _run_loop(self) -> None:
        """Internal loop: check scale triggers every ``check_interval_s`` seconds."""
        while True:
            await asyncio.sleep(self._check_interval_s)
            await self._check_scale_trigger()
            await self._check_scale_down()

    def start(self) -> asyncio.Task[None]:
        """Start the daemon loop as a background asyncio task.

        Returns:
            The :class:`asyncio.Task` running the loop.
        """
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run_loop(), name="watcher-daemon-scale")
            _log.info("WatcherDaemon started (interval=%.0fs)", self._check_interval_s)
        return self._task

    def stop(self) -> None:
        """Cancel the daemon loop task."""
        if self._task is not None and not self._task.done():
            self._task.cancel()
            _log.info("WatcherDaemon stopped")
