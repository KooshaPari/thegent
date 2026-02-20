"""Compositor - Panel lifecycle management with mount/unmount hooks and error boundaries.

Provides:
- Panel: Dataclass representing a named content panel with lifecycle callbacks
  and an isolated error boundary (error_fallback, last_error, recover()).
- Compositor: Manages a collection of panels, firing on_mount/on_unmount hooks
  and rendering each panel behind its own error boundary so a failing panel
  cannot crash the compositor.
- Render caching: TTLCache-backed render cache keyed by (panel_name,
  content_hash). Cache hits skip content_fn calls entirely. Error states are
  cached with a shorter TTL (5 s) to avoid hammering a broken content_fn.
- Render profiling: CompositorProfiler records per-panel render timing so
  agents can detect slow renders, inspect averages, and generate summaries.
"""

from __future__ import annotations

import hashlib
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

from cachetools import TTLCache

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_TTL: float = 60.0
"""Default cache TTL in seconds for successful renders."""

_ERROR_TTL: float = 5.0
"""Short TTL in seconds used when the content_fn raises an exception."""

_DEFAULT_MAXSIZE: int = 256
"""Default maximum number of entries in the render cache."""

_PROFILER_MAXLEN: int = 100
"""Maximum number of render profiles retained by CompositorProfiler."""


# ---------------------------------------------------------------------------
# Render profiling
# ---------------------------------------------------------------------------


@dataclass
class RenderProfile:
    """Timing record for a single panel render.

    Attributes:
        panel_id: Name/identifier of the panel that was rendered.
        render_time_ms: Wall-clock time taken for the render in milliseconds.
        timestamp: Unix timestamp (``time.time()``) at the moment of recording.
        cache_hit: ``True`` when the result was served from the render cache
            without invoking the panel's ``content_fn``; ``False`` on a cache
            miss (i.e. content_fn was called).
    """

    panel_id: str
    render_time_ms: float
    timestamp: float
    cache_hit: bool = False


class CompositorProfiler:
    """Collects and reports render timing data for Compositor panels.

    Stores up to ``_PROFILER_MAXLEN`` (100) most-recent :class:`RenderProfile`
    records in a bounded :class:`collections.deque`.  All methods are
    synchronous and safe to call from the main thread; they do **not** mutate
    the profiles while iterating (a snapshot copy is taken where necessary).

    Typical usage::

        profiler = CompositorProfiler()
        profiler.record(RenderProfile("my-panel", render_time_ms=12.3, timestamp=time.time()))
        slow = profiler.get_slowest(n=3)
        avg = profiler.get_average("my-panel")
        print(profiler.report())
        profiler.clear()
    """

    def __init__(self) -> None:
        self._records: deque[RenderProfile] = deque(maxlen=_PROFILER_MAXLEN)

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def record(self, profile: RenderProfile) -> None:
        """Store a render profile record.

        If the deque is already at capacity the oldest entry is automatically
        evicted (standard :class:`deque` ``maxlen`` behaviour).

        Args:
            profile: The :class:`RenderProfile` to store.
        """
        self._records.append(profile)

    def get_slowest(self, n: int = 5) -> list[RenderProfile]:
        """Return the top-*n* profiles sorted by render time, slowest first.

        If fewer than *n* records exist all records are returned.

        Args:
            n: Maximum number of profiles to return.  Defaults to 5.

        Returns:
            List of :class:`RenderProfile` instances in descending
            ``render_time_ms`` order.
        """
        snapshot = list(self._records)
        return sorted(snapshot, key=lambda p: p.render_time_ms, reverse=True)[:n]

    def get_average(self, panel_id: str | None = None) -> float:
        """Return the mean render time in milliseconds.

        Args:
            panel_id: When given, only records for this panel are considered.
                When *None*, all records are used.

        Returns:
            Average ``render_time_ms`` across matching records, or ``0.0``
            when there are no matching records.
        """
        snapshot = list(self._records)
        if panel_id is not None:
            snapshot = [p for p in snapshot if p.panel_id == panel_id]
        if not snapshot:
            return 0.0
        return sum(p.render_time_ms for p in snapshot) / len(snapshot)

    def report(self) -> str:
        """Return a human-readable summary of recorded render profiles.

        The report includes:
        - Total number of records.
        - Overall average render time.
        - The top-5 slowest renders with panel id, time, cache-hit status,
          and ISO-formatted timestamp.

        Returns:
            Multi-line formatted string report.
        """
        snapshot = list(self._records)
        total = len(snapshot)
        if total == 0:
            return "CompositorProfiler: no render records collected."

        overall_avg = self.get_average()
        slowest = self.get_slowest(5)

        lines: list[str] = [
            f"CompositorProfiler — {total} record(s), avg {overall_avg:.2f} ms",
            "Top slowest renders:",
        ]
        for rank, profile in enumerate(slowest, start=1):
            cache_label = "HIT" if profile.cache_hit else "MISS"
            lines.append(
                f"  {rank}. [{profile.panel_id}] {profile.render_time_ms:.2f} ms"
                f" cache={cache_label} ts={profile.timestamp:.3f}"
            )
        return "\n".join(lines)

    def clear(self) -> None:
        """Remove all stored render profiles."""
        self._records.clear()

    @property
    def record_count(self) -> int:
        """Return the number of profiles currently stored."""
        return len(self._records)


@dataclass
class Panel:
    """A named content panel with optional lifecycle hooks and an error boundary.

    Attributes:
        name: Unique identifier for the panel.
        content_fn: Callable that returns the panel's rendered string content.
            Called with no arguments.
        on_mount: Optional callback fired when the panel is added/activated.
            Receives the Panel instance as its sole argument.
        on_unmount: Optional callback fired when the panel is removed/deactivated.
            Receives the Panel instance as its sole argument.
        error_fallback: Optional custom fallback when content_fn raises.
            May be a plain string OR a ``Callable[[Exception], str]``.
            When *None* the default placeholder is used:
            ``"[Panel error: {name} — {ExcType}]"``.
        last_error: The most recent unrecovered exception, or *None* if the
            panel has not failed or has been recovered.  Set automatically by
            the error boundary; do not write directly.
    """

    name: str
    content_fn: Callable[[], str]
    on_mount: Callable[[Panel], None] | None = field(default=None)
    on_unmount: Callable[[Panel], None] | None = field(default=None)
    error_fallback: str | Callable[[Exception], str] | None = field(default=None)
    last_error: Exception | None = field(default=None, init=False, repr=False)

    # ------------------------------------------------------------------
    # Error boundary API
    # ------------------------------------------------------------------

    def render(self) -> str:
        """Render this panel, catching any exception raised by content_fn.

        On success the last_error is cleared (so a recovered panel that later
        succeeds reflects healthy state).  On failure last_error is recorded
        and the configured error_fallback (string, callable, or default) is
        returned without re-raising.

        Returns:
            Rendered string content, or fallback string on error.
        """
        try:
            result = self.content_fn()
            self.last_error = None  # Clear previous error on success
            return result
        except Exception as exc:  # noqa: BLE001 — intentional error boundary
            self.last_error = exc
            logger.error(
                "Panel %r raised %s during render: %s",
                self.name,
                type(exc).__name__,
                exc,
                exc_info=True,
            )
            return self._build_fallback(exc)

    def recover(self) -> None:
        """Clear the error state so the next render() retries content_fn.

        After calling recover() the panel is treated as if it never failed:
        ``last_error`` is reset to *None*.  The next call to render() will
        invoke content_fn again and re-evaluate whether it succeeds or fails.
        """
        self.last_error = None
        logger.info("Panel %r error state cleared (recovered)", self.name)

    @property
    def has_error(self) -> bool:
        """True when the panel is in an error state (last render failed)."""
        return self.last_error is not None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_fallback(self, exc: Exception) -> str:
        """Construct the fallback string for an exception.

        Args:
            exc: The exception raised by content_fn.

        Returns:
            The fallback string to display in place of panel content.
        """
        if self.error_fallback is None:
            return f"[Panel error: {self.name} — {type(exc).__name__}]"
        if callable(self.error_fallback):
            try:
                return self.error_fallback(exc)
            except Exception as fallback_exc:  # noqa: BLE001
                logger.error(
                    "Panel %r error_fallback callable raised %s: %s",
                    self.name,
                    type(fallback_exc).__name__,
                    fallback_exc,
                )
                return f"[Panel error: {self.name} — {type(exc).__name__}] (fallback also failed)"
        # Plain string fallback.
        return self.error_fallback


class CacheStats(TypedDict):
    """Statistics snapshot returned by :meth:`Compositor.cache_stats`."""

    hits: int
    misses: int
    size: int


class Compositor:
    """Manages a collection of named panels with lifecycle hook support.

    Panels are stored in insertion order. Adding a panel fires its ``on_mount``
    hook; removing a panel fires its ``on_unmount`` hook. Hook exceptions are
    caught, logged, and do not propagate so that a misbehaving hook cannot crash
    the compositor.

    Each panel's render() call is wrapped by Panel's own error boundary so a
    failing panel produces a fallback string without crashing the compositor or
    affecting sibling panels.

    Render results are cached in a :class:`cachetools.TTLCache` keyed by
    ``(panel_name, content_hash)`` where *content_hash* is an MD5 hex digest
    of the string returned by calling ``content_fn()``.  On a cache *hit* the
    stored string is returned immediately without invoking ``content_fn`` again.
    On a cache *miss* the panel is rendered via the normal error-boundary path
    and the result is stored.  Error fallback strings are cached with a shorter
    TTL (``error_ttl``) so that a recovered panel is retried promptly.

    Attributes:
        _panels: Ordered mapping of panel name to Panel instance.
        _cache: TTLCache storing rendered strings keyed by
            ``(panel_name, content_hash)``.
        _error_cache: TTLCache for error-state fallback strings, keyed by
            ``panel_name``.  Uses a shorter ``error_ttl``.
        _hits: Running count of cache hits.
        _misses: Running count of cache misses.
        profiler: :class:`CompositorProfiler` that records timing for every
            render call (both cache hits and misses).
    """

    def __init__(
        self,
        ttl: float = _DEFAULT_TTL,
        error_ttl: float = _ERROR_TTL,
        maxsize: int = _DEFAULT_MAXSIZE,
    ) -> None:
        """Initialise an empty compositor with an optional render cache.

        Args:
            ttl: Time-to-live in seconds for successful render entries.
                Defaults to 60 s.
            error_ttl: Time-to-live in seconds for error-state fallback entries.
                Defaults to 5 s.
            maxsize: Maximum number of entries in the render cache.
                Defaults to 256.
        """
        self._panels: dict[str, Panel] = {}
        self._cache: TTLCache[tuple[str, str], str] = TTLCache(maxsize=maxsize, ttl=ttl)
        self._error_cache: TTLCache[str, str] = TTLCache(maxsize=maxsize, ttl=error_ttl)
        self._hits: int = 0
        self._misses: int = 0
        self.profiler: CompositorProfiler = CompositorProfiler()
        logger.debug("Compositor initialised (ttl=%.1fs, error_ttl=%.1fs)", ttl, error_ttl)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_panel(self, panel: Panel) -> None:
        """Add a panel and fire its on_mount hook.

        If a panel with the same name already exists it is replaced. The
        on_unmount hook of the *existing* panel is fired before the new panel's
        on_mount hook.  Any cached render output for the panel name is
        invalidated automatically.

        Args:
            panel: The panel to add.
        """
        if panel.name in self._panels:
            logger.debug("Replacing existing panel '%s'", panel.name)
            self._fire_unmount(self._panels[panel.name])
            self.invalidate(panel.name)

        self._panels[panel.name] = panel
        logger.debug("Panel '%s' added", panel.name)
        self._fire_mount(panel)

    def remove_panel(self, name: str) -> bool:
        """Remove a panel by name and fire its on_unmount hook.

        Cache entries for the removed panel are invalidated automatically.

        Args:
            name: The name of the panel to remove.

        Returns:
            ``True`` if the panel existed and was removed, ``False`` otherwise.
        """
        panel = self._panels.pop(name, None)
        if panel is None:
            logger.warning("remove_panel: no panel named '%s'", name)
            return False

        logger.debug("Panel '%s' removed", name)
        self._fire_unmount(panel)
        self.invalidate(name)
        return True

    def get_panel(self, name: str) -> Panel | None:
        """Return a panel by name, or None if not found.

        Args:
            name: Panel name.

        Returns:
            Panel instance or None.
        """
        return self._panels.get(name)

    def render(self) -> list[str]:
        """Render all panels in insertion order using per-panel error boundaries.

        Each panel's error boundary (Panel.render()) is invoked independently.
        A failing panel returns a fallback string; other panels are unaffected.
        Results are served from the render cache where possible.

        Returns:
            A list of rendered strings, one per panel in insertion order.
        """
        return [self._render_cached(panel) for panel in self._panels.values()]

    def render_all(self) -> dict[str, str]:
        """Render all panels and return a name -> content mapping.

        Results are served from the render cache where possible.

        Returns:
            Dictionary mapping each panel name to its rendered string.
        """
        return {name: self._render_cached(panel) for name, panel in self._panels.items()}

    def render_panel(self, name: str) -> str | None:
        """Render a single panel by name.

        The result is served from the render cache if available.

        Args:
            name: Panel name.

        Returns:
            Rendered string, or *None* if the panel does not exist.
        """
        panel = self._panels.get(name)
        if panel is None:
            logger.warning("Compositor.render_panel: panel %r not found", name)
            return None
        return self._render_cached(panel)

    # ------------------------------------------------------------------
    # Cache management API
    # ------------------------------------------------------------------

    def invalidate(self, panel_name: str | None = None) -> None:
        """Invalidate cached render output.

        Args:
            panel_name: If given, only entries for this panel are evicted.
                If *None*, the entire cache is cleared (all panels).
        """
        if panel_name is None:
            self._cache.clear()
            self._error_cache.clear()
            logger.debug("Compositor render cache cleared (all panels)")
        else:
            # Evict all entries whose key starts with the given panel_name.
            keys_to_drop = [k for k in list(self._cache) if k[0] == panel_name]
            for key in keys_to_drop:
                self._cache.pop(key, None)
            self._error_cache.pop(panel_name, None)
            logger.debug("Compositor render cache invalidated for panel '%s'", panel_name)

    def cache_stats(self) -> CacheStats:
        """Return a snapshot of cache performance counters.

        Returns:
            A :class:`CacheStats` mapping with keys ``hits``, ``misses``,
            and ``size`` (current number of entries across both caches).
        """
        return CacheStats(
            hits=self._hits,
            misses=self._misses,
            size=len(self._cache) + len(self._error_cache),
        )

    @property
    def panel_names(self) -> list[str]:
        """Return an ordered list of current panel names."""
        return list(self._panels)

    # ------------------------------------------------------------------
    # Error-state helpers
    # ------------------------------------------------------------------

    def errored_panels(self) -> list[str]:
        """Return names of panels currently in an error state."""
        return [name for name, panel in self._panels.items() if panel.has_error]

    def recover_panel(self, name: str) -> bool:
        """Clear error state for a single panel.

        Args:
            name: Panel name.

        Returns:
            True if panel was found and recovered, False otherwise.
        """
        panel = self._panels.get(name)
        if panel is None:
            return False
        panel.recover()
        return True

    def recover_all(self) -> None:
        """Clear error state for all panels."""
        for panel in self._panels.values():
            panel.recover()
        logger.info("Compositor: all panel error states cleared")

    def __len__(self) -> int:
        """Return the number of currently registered panels."""
        return len(self._panels)

    def __contains__(self, name: object) -> bool:
        """Return True if a panel with ``name`` is registered."""
        return name in self._panels

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _content_hash(content: str) -> str:
        """Return an MD5 hex digest of *content* for use as a cache key.

        Args:
            content: The rendered string to hash.

        Returns:
            32-character lowercase hex string.
        """
        return hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()  # noqa: S324 -- cache key only, not security-critical

    def _render_cached(self, panel: Panel) -> str:
        """Render *panel* with cache lookup and render-time profiling.

        Strategy:
        1. Attempt to call ``content_fn()`` to obtain the raw content string.
        2. Hash the content and look it up in ``_cache[(panel.name, hash)]``.
        3. On hit: increment ``_hits`` and return the cached string.
        4. On miss: render via ``Panel.render()`` (error boundary), store in
           cache (using the short ``_error_cache`` TTL if the panel is in an
           error state), increment ``_misses``, and return.

        If ``content_fn()`` raises before we can compute the hash we fall back
        to the error-state cache keyed only by ``panel.name``.

        Timing is measured with :func:`time.perf_counter` and recorded via
        :attr:`profiler` regardless of whether the result was a cache hit or
        miss.

        Args:
            panel: The panel to render.

        Returns:
            Rendered string (possibly a fallback on error).
        """
        t0 = time.perf_counter()
        cache_hit = False

        # --- Try to obtain a stable content hash ---
        try:
            raw_content = panel.content_fn()
        except Exception:  # noqa: BLE001 — hash probe; full error boundary below
            # content_fn raised; check the error cache first.
            cached_error = self._error_cache.get(panel.name)
            if cached_error is not None:
                self._hits += 1
                cache_hit = True
                result = cached_error
            else:
                # Cache miss: let Panel.render() handle the error boundary.
                self._misses += 1
                result = panel.render()  # records last_error; returns fallback
                self._error_cache[panel.name] = result
            self.profiler.record(
                RenderProfile(
                    panel_id=panel.name,
                    render_time_ms=(time.perf_counter() - t0) * 1000.0,
                    timestamp=time.time(),
                    cache_hit=cache_hit,
                )
            )
            return result

        # --- content_fn succeeded: check the main cache ---
        content_hash = self._content_hash(raw_content)
        cache_key: tuple[str, str] = (panel.name, content_hash)

        cached = self._cache.get(cache_key)
        if cached is not None:
            self._hits += 1
            cache_hit = True
            result = cached
        else:
            # Cache miss: perform a full render via the error boundary.
            self._misses += 1
            result = panel.render()
            if panel.has_error:
                # Something went wrong between our probe and the real render —
                # store in the short-TTL error cache.
                self._error_cache[panel.name] = result
            else:
                self._cache[cache_key] = result

        self.profiler.record(
            RenderProfile(
                panel_id=panel.name,
                render_time_ms=(time.perf_counter() - t0) * 1000.0,
                timestamp=time.time(),
                cache_hit=cache_hit,
            )
        )
        return result

    def _fire_mount(self, panel: Panel) -> None:
        """Fire *panel.on_mount* if set, swallowing any exception."""
        if panel.on_mount is None:
            return
        try:
            panel.on_mount(panel)
        except Exception:
            logger.exception(
                "Exception in on_mount hook for panel '%s' (ignored)",
                panel.name,
            )

    def _fire_unmount(self, panel: Panel) -> None:
        """Fire *panel.on_unmount* if set, swallowing any exception."""
        if panel.on_unmount is None:
            return
        try:
            panel.on_unmount(panel)
        except Exception:
            logger.exception(
                "Exception in on_unmount hook for panel '%s' (ignored)",
                panel.name,
            )
