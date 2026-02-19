"""Phase 9: Request Coalescing v2 implementation.
Includes Singleflight, inotify cache invalidation, and heat-based LRU.
"""

import time
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional
import threading
import collections
try:
    import watchdog.observers
    import watchdog.events
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False

logger = logging.getLogger(__name__)

class Singleflight:
    """Implementation of Singleflight pattern to prevent duplicate requests."""
    def __init__(self):
        self.calls: Dict[str, threading.Event] = {}
        self.results: Dict[str, Any] = {}
        self.lock = threading.Lock()

    def do(self, key: str, func: Callable[[], Any]) -> Any:
        """Execute func for key, coalescing concurrent calls."""
        with self.lock:
            if key in self.calls:
                event = self.calls[key]
                self.lock.release()
                event.wait()
                self.lock.acquire()
                return self.results.get(key)

            event = threading.Event()
            self.calls[key] = event

        try:
            result = func()
            with self.lock:
                self.results[key] = result
            return result
        finally:
            with self.lock:
                event.set()
                del self.calls[key]
                # Results are kept until someone reads them or we use a better cache

class HeatBasedLRU:
    """LRU cache with heat-based eviction (frequency + decay)."""
    def __init__(self, capacity: int = 100, decay_factor: float = 0.9):
        self.capacity = capacity
        self.decay_factor = decay_factor
        self.cache: Dict[str, Any] = {}
        self.heat: Dict[str, float] = collections.defaultdict(float)
        self.last_access: Dict[str, float] = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                self._update_heat(key)
                return self.cache[key]
            return None

    def put(self, key: str, value: Any):
        with self.lock:
            if len(self.cache) >= self.capacity and key not in self.cache:
                self._evict()
            self.cache[key] = value
            self._update_heat(key)

    def _update_heat(self, key: str):
        now = time.time()
        prev_time = self.last_access.get(key, now)
        elapsed = now - prev_time
        # Apply decay to existing heat
        self.heat[key] = self.heat[key] * (self.decay_factor ** elapsed) + 1.0
        self.last_access[key] = now

    def _evict(self):
        # Evict item with lowest heat
        if not self.heat:
            return
        
        # Recalculate heat for all items before eviction to apply decay
        now = time.time()
        for k in list(self.heat.keys()):
            elapsed = now - self.last_access[k]
            self.heat[k] *= (self.decay_factor ** elapsed)
            self.last_access[k] = now

        victim = min(self.heat, key=self.heat.get)
        del self.cache[victim]
        del self.heat[victim]
        del self.last_access[victim]
        logger.info(f"Evicted {victim} from cache based on heat")

class CacheInvalidator:
    """inotify-based cache invalidation."""
    def __init__(self, cache: Any):
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
            def __init__(self, cache):
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
