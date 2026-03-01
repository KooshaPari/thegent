"""BKM-09: Multi-tenant file watcher daemon using the watchdog library.

This module provides ``WatcherDaemon``, a singleton daemon that manages multiple
independent watch specs concurrently via a single ``watchdog.observers.Observer``
thread.  Each spec targets a root directory with optional glob patterns, and
fires a typed ``WatchEvent`` callback in the watcher thread.

A ``CircuitBreakerShm`` integration is optionally available to track watcher
health: callback errors increment the breaker's failure counter.

Usage::

    from thegent.native.watcher_daemon import WatchEvent, WatchSpec, get_watcher_daemon

    daemon = get_watcher_daemon()
    daemon.start()

    def on_event(ev: WatchEvent) -> None:
        print(ev.event_type, ev.src_path)

    spec = WatchSpec(root=Path("."), patterns=["*.py"], recursive=True, callback=on_event)
    watch_id = daemon.add_watch(spec)

    # ... later ...
    daemon.remove_watch(watch_id)
    daemon.stop()

Thread-safety:
    ``add_watch``/``remove_watch``/``list_watches`` acquire an internal RLock.
    Callbacks fire in the watchdog observer thread; they must be fast and
    non-blocking.  Any exception in a callback is logged and, when the optional
    CircuitBreakerShm integration is enabled, recorded as a failure.

Environment variables:
    THGENT_WATCHER_USE_SHM=0   Disable the optional CircuitBreakerShm health
                                integration even if state_shm is available.

FR-trace: BKM-09 (PYTHON_FRONTMATTER_NATIVE_BACKMATTER_AUDIT_PLAN.md)
"""

from __future__ import annotations

import logging
import os
import tempfile
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

from watchdog.events import (
    DirCreatedEvent,
    DirDeletedEvent,
    DirModifiedEvent,
    DirMovedEvent,
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    PatternMatchingEventHandler,
)
from watchdog.observers import Observer

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional CircuitBreakerShm integration
# ---------------------------------------------------------------------------


def _is_shm_enabled() -> bool:
    """Check if watcher SHM is enabled via settings."""
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    return settings.watcher_use_shm


_SHM_ENABLED: bool = _is_shm_enabled()

_TARGET_KEY = "watcher_daemon"


def _try_get_breaker() -> Any:
    """Return a CircuitBreakerShm instance if available, else None."""
    if not _SHM_ENABLED:
        return None
    try:
        from thegent.config import ThegentSettings
        from thegent.native.state_shm import CircuitBreakerShm

        settings = ThegentSettings()
        shm_default = str(Path(tempfile.gettempdir()) / "thegent_watcher.shm")
        tmp_path = Path(settings.watcher_shm_path) if settings.watcher_shm_path else Path(shm_default)
        return CircuitBreakerShm(tmp_path)
    except Exception as exc:
        _log.debug("WatcherDaemon: CircuitBreakerShm not available: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Public data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WatchEvent:
    """Structured file-system event delivered to watch callbacks.

    Attributes:
        event_type: One of ``"created"``, ``"modified"``, ``"deleted"``, or
            ``"moved"``.
        src_path: Absolute path of the affected file or directory.
        dest_path: Destination path for ``"moved"`` events; ``None`` otherwise.
        is_directory: ``True`` when the event target is a directory.
    """

    event_type: str
    src_path: str
    dest_path: str | None
    is_directory: bool


@dataclass
class WatchSpec:
    """Configuration for a single watch registered with :class:`WatcherDaemon`.

    Attributes:
        root: Directory root to watch.
        patterns: Glob patterns to match (e.g. ``["*.py", "*.toml"]``).  An
            empty list means *all files*.
        recursive: Whether to watch sub-directories recursively.
        callback: Callable invoked with each :class:`WatchEvent`.  Must not
            block; runs in the observer thread.
    """

    root: Path
    patterns: list[str]
    recursive: bool
    callback: Callable[[WatchEvent], None]


# ---------------------------------------------------------------------------
# Internal event handler
# ---------------------------------------------------------------------------


class _SpecHandler(PatternMatchingEventHandler):
    """watchdog event handler for one WatchSpec.

    Converts raw watchdog events to :class:`WatchEvent` and dispatches them to
    the registered callback.  Callback exceptions are caught, logged, and
    forwarded to the optional health breaker.
    """

    def __init__(
        self,
        watch_id: str,
        spec: WatchSpec,
        breaker: Any,
    ) -> None:
        patterns = spec.patterns or ["*"]
        super().__init__(patterns=patterns, ignore_directories=False, case_sensitive=False)
        self._watch_id = watch_id
        self._spec = spec
        self._breaker = breaker

    # ------------------------------------------------------------------
    # watchdog dispatch (exact signatures match parent class)
    # ------------------------------------------------------------------

    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        self._dispatch(event.event_type, str(event.src_path), None, event.is_directory)

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        self._dispatch(event.event_type, str(event.src_path), None, event.is_directory)

    def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
        self._dispatch(event.event_type, str(event.src_path), None, event.is_directory)

    def on_moved(self, event: DirMovedEvent | FileMovedEvent) -> None:
        self._dispatch(event.event_type, str(event.src_path), str(event.dest_path), event.is_directory)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _dispatch(
        self,
        event_type: str,
        src_path: str,
        dest_path: str | None,
        is_directory: bool,
    ) -> None:
        watch_event = WatchEvent(
            event_type=event_type,
            src_path=src_path,
            dest_path=dest_path,
            is_directory=is_directory,
        )
        try:
            self._spec.callback(watch_event)
        except Exception as exc:
            _log.error(
                "WatcherDaemon[%s] callback error for %s: %s",
                self._watch_id,
                src_path,
                exc,
            )
            if self._breaker is not None:
                try:
                    self._breaker.record_failure(_TARGET_KEY, "tool")
                except Exception as inner_exc:
                    _log.debug("WatcherDaemon breaker record_failure error: %s", inner_exc)


# ---------------------------------------------------------------------------
# WatcherDaemon
# ---------------------------------------------------------------------------


class WatcherDaemon:
    """Multi-tenant file watcher daemon backed by a single watchdog Observer.

    One ``WatcherDaemon`` instance manages N independent :class:`WatchSpec`
    objects.  Each spec is scheduled on the shared Observer using a dedicated
    :class:`_SpecHandler`.  The Observer runs in a daemon thread; it is started
    via :meth:`start` and stopped via :meth:`stop`.

    Thread-safety:
        All public methods (except callbacks) acquire ``_lock`` (RLock) before
        mutating internal state.

    Example::

        daemon = WatcherDaemon()
        daemon.start()
        wid = daemon.add_watch(WatchSpec(Path("."), ["*.py"], True, my_cb))
        daemon.remove_watch(wid)
        daemon.stop()
    """

    def __init__(self) -> None:
        self._lock: threading.RLock = threading.RLock()
        self._observer: Any = Observer()
        self._running: bool = False
        cleanup_interval = os.getenv("THGENT_WATCHER_CLEANUP_INTERVAL_S", "3600")
        self._cleanup_interval_s = max(int(cleanup_interval), 300)
        self._cleanup_stop_event = threading.Event()
        self._cleanup_thread: threading.Thread | None = None

        # watch_id -> (WatchSpec, _SpecHandler, watchdog_watch)
        self._watches: dict[str, tuple[WatchSpec, _SpecHandler, Any]] = {}

        # Optional health breaker
        self._breaker: Any = _try_get_breaker()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the underlying watchdog Observer thread.

        Idempotent: calling ``start()`` on an already-running daemon is a
        no-op.

        Raises:
            RuntimeError: If the Observer fails to start.
        """
        with self._lock:
            if self._running:
                return
            try:
                self._observer.start()
                self._cleanup_stop_event.clear()
                self._cleanup_thread = threading.Thread(
                    target=self._storage_cleanup_loop,
                    name="thegent-watcher-cleanup",
                    daemon=True,
                )
                self._cleanup_thread.start()
                self._running = True
                _log.info("WatcherDaemon started")
            except Exception as exc:
                _log.error("WatcherDaemon failed to start observer: %s", exc)
                raise

    def stop(self) -> None:
        """Stop the watchdog Observer and wait for it to terminate.

        Idempotent: safe to call multiple times.  All registered watches are
        removed before stopping.
        """
        with self._lock:
            if not self._running:
                return
            watch_ids = list(self._watches.keys())

        for wid in watch_ids:
            self.remove_watch(wid)

        with self._lock:
            if not self._running:
                return
            try:
                self._observer.stop()
            except Exception as exc:
                _log.warning("WatcherDaemon observer stop error: %s", exc)
            self._running = False
            self._cleanup_stop_event.set()
            cleanup_thread = self._cleanup_thread
            self._cleanup_thread = None

        try:
            self._observer.join(timeout=5.0)
        except Exception as exc:
            _log.warning("WatcherDaemon observer join error: %s", exc)
        if cleanup_thread is not None:
            cleanup_thread.join(timeout=5.0)

        _log.info("WatcherDaemon stopped")

    def is_running(self) -> bool:
        """Return ``True`` if the Observer thread is active."""
        with self._lock:
            return self._running

    # ------------------------------------------------------------------
    # Watch management
    # ------------------------------------------------------------------

    def add_watch(self, spec: WatchSpec) -> str:
        """Register a new :class:`WatchSpec` and return its watch ID.

        If the daemon is not yet started, the watch is registered but events
        will not fire until :meth:`start` is called.

        Args:
            spec: The watch configuration.

        Returns:
            A unique string watch ID used for :meth:`remove_watch`.
        """
        watch_id = uuid.uuid4().hex
        handler = _SpecHandler(watch_id=watch_id, spec=spec, breaker=self._breaker)

        with self._lock:
            watchdog_watch = self._observer.schedule(
                handler,
                str(spec.root),
                recursive=spec.recursive,
            )
            self._watches[watch_id] = (spec, handler, watchdog_watch)
            _log.debug(
                "WatcherDaemon.add_watch id=%s root=%s patterns=%s recursive=%s",
                watch_id,
                spec.root,
                spec.patterns,
                spec.recursive,
            )

        return watch_id

    def remove_watch(self, watch_id: str) -> bool:
        """Remove a previously registered watch by ID.

        Args:
            watch_id: The ID returned by :meth:`add_watch`.

        Returns:
            ``True`` if the watch was found and removed; ``False`` otherwise.
        """
        with self._lock:
            entry = self._watches.pop(watch_id, None)
            if entry is None:
                _log.debug("WatcherDaemon.remove_watch: id=%s not found", watch_id)
                return False
            _, _, watchdog_watch = entry
            try:
                self._observer.unschedule(watchdog_watch)
            except Exception as exc:
                _log.warning("WatcherDaemon.remove_watch unschedule error id=%s: %s", watch_id, exc)

        _log.debug("WatcherDaemon.remove_watch id=%s removed", watch_id)
        return True

    def list_watches(self) -> list[dict[str, object]]:
        """Return a snapshot of currently registered watches.

        Returns:
            List of dicts with keys ``watch_id``, ``root``, ``patterns``,
            ``recursive``.
        """
        with self._lock:
            return [
                {
                    "watch_id": wid,
                    "root": str(spec.root),
                    "patterns": list(spec.patterns),
                    "recursive": spec.recursive,
                }
                for wid, (spec, _, _) in self._watches.items()
            ]

    def _storage_cleanup_loop(self) -> None:
        """Periodically prune stale quality shadow directories and logs."""
        from thegent.config import ThegentSettings
        from thegent.orchestration.pruning.prune import prune_stale_shadow_and_logs

        while not self._cleanup_stop_event.is_set():
            try:
                settings = ThegentSettings()
                shadow_pruned, logs_pruned = prune_stale_shadow_and_logs(
                    dry_run=False,
                    shadow_max_age_hours=settings.quality_shadow_cleanup_hours,
                    quality_log_max_age_days=settings.quality_log_retention_days,
                )
                if shadow_pruned or logs_pruned:
                    _log.info(
                        "WatcherDaemon storage cleanup removed %d stale shadow dirs and %d quality log files",
                        shadow_pruned,
                        logs_pruned,
                    )
            except Exception as exc:
                _log.warning("WatcherDaemon storage cleanup failed: %s", exc)
            self._cleanup_stop_event.wait(self._cleanup_interval_s)


# ---------------------------------------------------------------------------
# Singleton factory
# ---------------------------------------------------------------------------

_daemon_lock: threading.Lock = threading.Lock()
_daemon_instance: WatcherDaemon | None = None


def get_watcher_daemon() -> WatcherDaemon:
    """Return the process-level singleton :class:`WatcherDaemon`.

    The singleton is created lazily on first call.  Callers must still invoke
    :meth:`WatcherDaemon.start` before any events will fire.

    Returns:
        The shared :class:`WatcherDaemon` instance.
    """
    global _daemon_instance
    if _daemon_instance is None:
        with _daemon_lock:
            if _daemon_instance is None:
                _daemon_instance = WatcherDaemon()
    return _daemon_instance


def _reset_singleton() -> None:
    """Reset the singleton for testing purposes (internal use only)."""
    global _daemon_instance
    with _daemon_lock:
        _daemon_instance = None


__all__ = [
    "WatchEvent",
    "WatchSpec",
    "WatcherDaemon",
    "_reset_singleton",
    "get_watcher_daemon",
]
