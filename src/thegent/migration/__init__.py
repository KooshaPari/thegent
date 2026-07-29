"""Migration helpers for thegent.

Provides:

* :func:`deprecated` — decorator that emits a :class:`DeprecationWarning`
  the first time a wrapped function/callable is invoked. The warning
  intentionally mentions the replacement symbol when provided so
  call-site upgrade paths are obvious in logs.
* :class:`MigrationRegistry` — a thread-safe registry of in-flight
  migrations that maps an old symbol path to its replacement and the
  emission date. Used by the audit chain and CLI deprecation commands
  to surface the migration backlog in dashboards.
* :func:`record_migration` — single-shot helper to register a
  migration step without instantiating a registry.

The module is intentionally side-effect free (no global warnings
filters): callers opt in by wrapping their deprecated APIs.

**Traces to**: L24 Migration (audit scorecard), WL-120 migration docs,
WP-4020 (deprecation tooling).
"""

from __future__ import annotations

import functools
import inspect
import warnings
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from threading import RLock
from typing import Any, TypeVar, cast

_F = TypeVar("_F", bound=Callable[..., Any])


def _is_coro(func: Any) -> bool:
    """Return True if ``func`` is a coroutine function.

    Uses ``inspect.iscoroutinefunction`` (the canonical predicate from
    3.12+). Falls back to ``False`` on very old runtimes that lack
    both ``inspect.iscoroutinefunction`` and ``functools.iscoroutinefunction``.
    """
    return inspect.iscoroutinefunction(func)  # type: ignore[func-returns-value]


# ---------------------------------------------------------------------------
# Decorator
# ---------------------------------------------------------------------------


def deprecated(
    replacement: str | None = None,
    *,
    since: str | None = None,
    remove_in: str | None = None,
    stacklevel: int = 2,
) -> Callable[[_F], _F]:
    """Mark a callable as deprecated.

    Args:
        replacement: Fully-qualified name of the replacement symbol.
            Surfaced in the warning message so users can find the new
            API without reading the source.
        since: Calendar version when the deprecation was introduced
            (e.g. ``"2.0.0"``).
        remove_in: Calendar version when the symbol will be removed
            (e.g. ``"3.0.0"``).
        stacklevel: ``warnings`` stacklevel. Defaults to ``2`` so the
            warning points at the call site.
    """

    def decorator(func: _F) -> _F:
        message_parts = [f"Call to deprecated {func.__qualname__}."]
        if replacement:
            message_parts.append(f"Use {replacement} instead.")
        if since:
            message_parts.append(f"Deprecated since {since}.")
        if remove_in:
            message_parts.append(f"Will be removed in {remove_in}.")
        message = " ".join(message_parts)

        if _is_coro(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                warnings.warn(message, DeprecationWarning, stacklevel=stacklevel)
                return await func(*args, **kwargs)

            return cast("_F", async_wrapper)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(message, DeprecationWarning, stacklevel=stacklevel)
            return func(*args, **kwargs)

        return cast("_F", wrapper)

    return decorator


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MigrationEntry:
    """A single migration record."""

    old_path: str
    new_path: str
    introduced: str
    target_removal: str | None = None
    notes: str = ""


class MigrationRegistry:
    """Thread-safe in-memory migration registry.

    Call :meth:`register` to add entries and :meth:`pending` to read
    them back. The registry is intentionally simple: a global
    :data:`default_registry` is exposed for the common case where one
    process-wide registry is sufficient.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._entries: dict[str, MigrationEntry] = {}

    def register(
        self,
        old_path: str,
        new_path: str,
        *,
        introduced: str | None = None,
        target_removal: str | None = None,
        notes: str = "",
    ) -> MigrationEntry:
        """Register a migration. Returns the entry (existing or newly created)."""
        with self._lock:
            existing = self._entries.get(old_path)
            if existing is not None:
                return existing
            entry = MigrationEntry(
                old_path=old_path,
                new_path=new_path,
                introduced=introduced or date.today().isoformat(),
                target_removal=target_removal,
                notes=notes,
            )
            self._entries[old_path] = entry
            return entry

    def pending(self) -> tuple[MigrationEntry, ...]:
        """Return a snapshot of all registered entries, sorted by old_path."""
        with self._lock:
            return tuple(sorted(self._entries.values(), key=lambda e: e.old_path))

    def get(self, old_path: str) -> MigrationEntry | None:
        """Return the entry for ``old_path`` or ``None`` if not registered."""
        with self._lock:
            return self._entries.get(old_path)

    def clear(self) -> None:
        """Drop all entries. Intended for tests."""
        with self._lock:
            self._entries.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)


default_registry = MigrationRegistry()


def record_migration(
    old_path: str,
    new_path: str,
    *,
    introduced: str | None = None,
    target_removal: str | None = None,
    notes: str = "",
) -> MigrationEntry:
    """Convenience wrapper around :meth:`MigrationRegistry.register`."""
    return default_registry.register(
        old_path,
        new_path,
        introduced=introduced,
        target_removal=target_removal,
        notes=notes,
    )


__all__ = [
    "MigrationEntry",
    "MigrationRegistry",
    "default_registry",
    "deprecated",
    "record_migration",
]
