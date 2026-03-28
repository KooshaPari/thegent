"""SessionService: DI-ready wrapper for the session persistence backend.

Previously session backend selection was performed ad-hoc by calling
``resolve_session_backend()`` at each call site.  This module wraps that
logic in a ``SessionService`` class whose backend can be:

1. Resolved automatically at construction time (default behaviour).
2. Injected explicitly for testing or custom configurations.

A module-level ``_session_service`` singleton is provided for backward
compatibility.  New code should prefer injecting a ``SessionService``
instance via the DI container.

Phase 2C DI migration
---------------------
The formerly implicit module-level ``_backend`` pattern is replaced by an
explicit ``SessionService`` instance with a public ``backend`` property.
Callers that previously called ``resolve_session_backend()`` and stored the
result in a local variable can now use ``get_session_service().backend``
instead.
"""

from __future__ import annotations

import logging

from thegent_execution.session.zmx_backend import SessionBackend, ZmxBackend, resolve_session_backend

logger = logging.getLogger(__name__)


class SessionService:
    """Injectable service that manages the active session persistence backend.

    Attributes:
        _backend: The resolved backend, or None if no backend is available.
        _resolved: Whether the backend has been resolved yet.
        _backend_override: Optional string override for backend selection.
    """

    def __init__(
        self,
        backend: SessionBackend | None = None,
        *,
        backend_override: str | None = None,
    ) -> None:
        """Initialize the SessionService.

        Args:
            backend: Pre-resolved backend to use.  If None, the backend is
                resolved lazily on first access.
            backend_override: String override passed to ``resolve_session_backend``
                (e.g. "zmx", "tmux", "none", "auto").  Ignored if *backend* is
                provided.
        """
        self._backend: SessionBackend | None = backend
        self._resolved: bool = backend is not None
        self._backend_override: str | None = backend_override

    # ------------------------------------------------------------------ #
    # Backend access
    # ------------------------------------------------------------------ #

    @property
    def backend(self) -> SessionBackend | None:
        """Return the active session backend, resolving lazily if needed.

        Returns:
            A concrete SessionBackend (e.g. ZmxBackend), or None when no
            backend is available (zmx not installed, tmux mode, etc.).
        """
        if not self._resolved:
            self._backend = resolve_session_backend(self._backend_override)
            self._resolved = True
            if self._backend is not None:
                logger.debug("SessionService: resolved backend %r", self._backend.name)
            else:
                logger.debug("SessionService: no session backend available")
        return self._backend

    @backend.setter
    def backend(self, value: SessionBackend | None) -> None:
        """Override the active backend (e.g. for testing)."""
        self._backend = value
        self._resolved = True

    # ------------------------------------------------------------------ #
    # Convenience pass-through methods
    # ------------------------------------------------------------------ #

    @property
    def available(self) -> bool:
        """Return True if a usable backend is available."""
        b = self.backend
        return b is not None and b.available

    def create(self, session_name: str, cmd: list[str]) -> bool:
        """Create a new named session running *cmd*.

        Returns False (with a warning) if no backend is available.
        """
        b = self.backend
        if b is None:
            logger.warning("SessionService.create: no backend available for session %r", session_name)
            return False
        return b.create(session_name, cmd)

    def attach(self, session_name: str) -> bool:
        """Attach to an existing session.  Returns False if no backend."""
        b = self.backend
        if b is None:
            logger.warning("SessionService.attach: no backend available")
            return False
        return b.attach(session_name)

    def list(self) -> list:
        """Return all sessions.  Returns [] if no backend."""
        b = self.backend
        if b is None:
            return []
        return b.list()

    def kill(self, session_name: str) -> bool:
        """Kill a named session.  Returns False if no backend."""
        b = self.backend
        if b is None:
            return False
        return b.kill(session_name)

    def capture(self, session_name: str, last_lines: int = 50) -> str:
        """Capture output from a session.  Returns '' if no backend."""
        b = self.backend
        if b is None:
            return ""
        return b.capture(session_name, last_lines)

    # ------------------------------------------------------------------ #
    # Reset
    # ------------------------------------------------------------------ #

    def reset(self) -> None:
        """Clear the cached backend, forcing re-resolution on next access."""
        self._backend = None
        self._resolved = False

    def __repr__(self) -> str:
        if self._resolved:
            return f"SessionService(backend={self._backend!r})"
        return "SessionService(backend=<not yet resolved>)"


# ---------------------------------------------------------------------------
# Module-level singleton — backward-compat shim
# ---------------------------------------------------------------------------

#: Module-level SessionService instance.
#: Callers that cannot receive injection may use get_session_service().
_session_service: SessionService = SessionService()


def get_session_service() -> SessionService:
    """Return the module-level SessionService singleton.

    Backward-compatible helper.  Prefer injecting a SessionService via the
    DI container (thegent_core.container.global_container).
    """
    return _session_service


def set_session_service(service: SessionService) -> None:
    """Replace the module-level SessionService singleton.

    Args:
        service: New SessionService instance to use as the singleton.
    """
    global _session_service
    _session_service = service


__all__ = [
    "SessionService",
    "_session_service",
    "get_session_service",
    "set_session_service",
]
