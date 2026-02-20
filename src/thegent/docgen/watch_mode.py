"""Implement watch mode for auto-regeneration of documentation."""

import logging
import threading
import time
from collections.abc import Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentationWatcher:
    """Watch documentation source files and auto-regenerate."""

    def __init__(self, source_dir: Path, output_dir: Path, build_func: Callable) -> None:
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.build_func = build_func
        self._watcher_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def _get_last_modified_times(self) -> dict[Path, float]:
        """Get last modified times of all files in source directory."""
        return {p: p.stat().st_mtime for p in self.source_dir.rglob("*") if p.is_file()}

    def _watch_loop(self, poll_interval: float = 1.0):
        """Internal watch loop."""
        last_modified = self._get_last_modified_times()

        while not self._stop_event.is_set():
            time.sleep(poll_interval)
            current_modified = self._get_last_modified_times()

            if current_modified != last_modified:
                logger.info("Changes detected in documentation sources. Regenerating...")
                try:
                    self.build_func()
                    logger.info("Documentation regenerated successfully.")
                except Exception as e:
                    logger.error(f"Error regenerating documentation: {e}")

                last_modified = current_modified

    def start(self, poll_interval: float = 1.0):
        """Start documentation watcher in a background thread."""
        self._stop_event.clear()
        self._watcher_thread = threading.Thread(target=self._watch_loop, args=(poll_interval,), daemon=True)
        self._watcher_thread.start()
        logger.info(f"Documentation watcher started for {self.source_dir}")

    def stop(self):
        """Stop documentation watcher."""
        self._stop_event.set()
        if self._watcher_thread:
            self._watcher_thread.join()
        logger.info("Documentation watcher stopped.")
