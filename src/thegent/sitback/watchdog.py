"""Background task watcher for non-blocking completion detection.

Provides polling-based detection of background task completion without blocking.
Used by the never-idle loop to wake on task completion.
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable
from pathlib import Path

_log = logging.getLogger(__name__)

# Type alias for callback: (session_id, exit_code) -> None
CompletionCallback = Callable[[str, int], None]


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
                except Exception as e:
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
