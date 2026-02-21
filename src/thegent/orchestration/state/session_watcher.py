"""Session event watcher for auto-launch system.

Watches session directories for completion events using FastFileWatcher.
Harmonized with BackgroundTaskWatcher and NeverIdleLoop.
"""

import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from thegent.infra.fast_file_watcher import FastFileWatcher

_log = logging.getLogger(__name__)


class SessionEventWatcher:
    """Watches session directories for completion events."""

    def __init__(self, session_dir: Path) -> None:
        """Initialize session event watcher.

        Args:
            session_dir: Path to session directory (~/.cache/thegent/sessions)
        """
        self.session_dir = Path(session_dir)
        self._completion_callbacks: list[Callable[[str, int], None]] = []
        self._watcher: FastFileWatcher | None = None

    def on_complete(self, callback: Callable[[str, int], None]) -> None:
        """Register a callback for session completion events.

        Args:
            callback: Function(session_id: str, exit_code: int) -> None
        """
        self._completion_callbacks.append(callback)

    def start(self) -> None:
        """Start watching for session completion events."""
        if self._watcher:
            return

        self._watcher = FastFileWatcher(self.session_dir, recursive=True)

        class CompletionHandler:
            def __init__(self, watcher: SessionEventWatcher) -> None:
                self.watcher = watcher

            def on_completion(self, session_id: str, exit_code: int) -> None:
                """Handle session completion."""
                for callback in self.watcher._completion_callbacks:
                    try:
                        callback(session_id, exit_code)
                    except Exception as e:  # noqa: PERF203 - intentional per-item error handling
                        _log.error(f"Error in completion callback: {e}", exc_info=True)

        handler = CompletionHandler(self)

        # Use watchfiles backend if available (5-10x faster)
        if hasattr(self._watcher, "watch"):
            # watchfiles backend
            import threading

            def watch_loop():
                self._watcher.watch(lambda changes: self._process_changes(changes, handler))

            thread = threading.Thread(target=watch_loop, daemon=True)
            thread.start()
        else:
            # watchdog backend fallback
            self._watcher.start(handler)

        _log.info(f"Started session event watcher on {self.session_dir}")

    def stop(self) -> None:
        """Stop watching for events."""
        if self._watcher:
            self._watcher.stop()
            self._watcher = None
            _log.info("Stopped session event watcher")

    def _process_changes(self, changes: list[tuple[Any, str]], handler: Any) -> None:
        """Process file system changes and detect completions."""
        for _change, path_str in changes:
            path = Path(path_str)

            # Look for metadata.json updates (session completion marker)
            if path.name == "metadata.json" and path.parent.parent == self.session_dir:
                session_id = path.parent.name
                try:
                    metadata = json.loads(path.read_text())
                    if metadata.get("status") == "exited":
                        exit_code = metadata.get("exit_code", 0)
                        handler.on_completion(session_id, exit_code)
                except Exception as e:
                    _log.debug(f"Error processing metadata.json: {e}")

            # Also check stdout.log for completion markers
            if path.name == "stdout.log":
                session_id = path.parent.name
                try:
                    from thegent.utils.helpers import read_file_optimized

                    # Check last few lines for completion markers
                    content = read_file_optimized(path, max_size_mb=1)
                    if content and ("Session completed" in content[-1000:] or "exit code" in content[-1000:].lower()):
                        # Try to extract exit code
                        exit_code = 0
                        for line in content.splitlines()[-10:]:
                            if "exit code" in line.lower():
                                try:
                                    exit_code = int(line.split()[-1])
                                    break
                                except ValueError:
                                    pass
                        handler.on_completion(session_id, exit_code)
                except Exception as e:
                    _log.debug(f"Error processing stdout.log: {e}")
