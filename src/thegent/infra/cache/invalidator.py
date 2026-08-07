"""TGNT-P9.2 — watchdog / inotify cache invalidation primitive.

This module is the canonical home for :class:`CacheInvalidator` and the
``HAS_WATCHDOG`` feature flag. ``CacheInvalidator.watch(directory)``
subscribes a ``cache.clear`` callback to a watchdog ``Observer`` so that
file modifications trigger cache invalidation.

If the optional ``watchdog`` dependency is not installed, ``watch()`` is
a silent no-op (and ``HAS_WATCHDOG`` is ``False``).

It is part of the WL706 L1 Architecture hardening pass that splits the
legacy single-file ``infra/cache_v2.py`` (419 LOC) into focused
single-responsibility sub-modules.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:
    import watchdog.events
    import watchdog.observers

    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False


class CacheInvalidator:
    """inotify-based cache invalidation."""

    def __init__(self, cache: Any) -> None:
        self.cache = cache
        if HAS_WATCHDOG:
            self.observer = watchdog.observers.Observer()
        else:
            self.observer = None

    def watch(self, directory: Path):
        if not self.observer:
            logger.warning("watchdog not installed, inotify invalidation disabled")
            return

        class Handler(watchdog.events.FileSystemEventHandler):
            def __init__(self, cache) -> None:
                self.cache = cache

            def on_modified(self, event):
                if not event.is_directory:
                    logger.info(f"Invalidating cache for {event.src_path}")
                    # In a real implementation, we'd map path to cache keys
                    # For now, clear all or match specifically if keys are paths
                    if hasattr(self.cache, "clear"):
                        self.cache.clear()

        self.observer.schedule(Handler(self.cache), str(directory), recursive=True)
        self.observer.start()

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()


__all__ = ["CacheInvalidator", "HAS_WATCHDOG"]
