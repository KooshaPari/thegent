"""Simple Dependency Injection container for thegent.

Provides a lightweight, dict-backed DI container for registering and
resolving named services.  This replaces module-level singletons with
injectable classes that can be configured at startup and swapped out in
tests without monkey-patching.

Usage
-----
::

    from phenotype_thegent_core.container import Container

    container = Container()
    container.register("platform", PlatformService())
    container.register("plugins", PluginRegistry())

    svc = container.get("platform")

The module also exposes a ``global_container`` singleton for convenience,
though callers should prefer explicit injection where possible.

Design principles
-----------------
* Zero external dependencies — stdlib only.
* Thread-safe registration and lookup via a simple dict (GIL is sufficient
  for CPython; add a threading.Lock if needed for other implementations).
* Services are registered by string name.  Type-safe factories or Protocol
  checks can be layered on top if needed.
* Supports factory callables: if the registered value is callable and was
  registered with ``factory=True``, it will be called on each ``get``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Container:
    """Simple dependency injection container for thegent.

    Attributes:
        _services: Internal mapping of service name -> instance or factory.
        _factories: Set of names that should be called on each ``get``.
    """

    _services: dict[str, Any] = field(default_factory=dict)
    _factories: set[str] = field(default_factory=set)

    # ------------------------------------------------------------------ #
    # Core API
    # ------------------------------------------------------------------ #

    def register(self, name: str, service: Any, *, factory: bool = False) -> None:
        """Register a service under *name*.

        Args:
            name: Unique identifier for this service.
            service: The service instance or factory callable.
            factory: If True, *service* is treated as a zero-argument
                factory; it will be called on every ``get`` rather than
                returned directly.  Useful for creating per-request
                instances.
        """
        self._services[name] = service
        if factory:
            self._factories.add(name)
        elif name in self._factories:
            self._factories.discard(name)

    def get(self, name: str) -> Any:
        """Retrieve a registered service by *name*.

        Args:
            name: Service identifier previously passed to ``register``.

        Returns:
            The registered service instance.  If the service was registered
            as a factory, a new instance is created on every call.

        Raises:
            KeyError: If *name* has not been registered.
        """
        svc = self._services[name]  # raises KeyError if missing
        if name in self._factories:
            return svc()
        return svc

    def get_or_default(self, name: str, default: Any = None) -> Any:
        """Return the service for *name*, or *default* if not registered.

        Never raises; useful for optional dependencies.
        """
        if name not in self._services:
            return default
        return self.get(name)

    def has(self, name: str) -> bool:
        """Return True if *name* is registered in this container."""
        return name in self._services

    def remove(self, name: str) -> None:
        """Unregister the service at *name*.  No-op if not registered."""
        self._services.pop(name, None)
        self._factories.discard(name)

    def names(self) -> list[str]:
        """Return the list of all registered service names."""
        return list(self._services.keys())

    # ------------------------------------------------------------------ #
    # Child / scoped containers
    # ------------------------------------------------------------------ #

    def child(self) -> "Container":
        """Create a child container that inherits this container's services.

        The child starts with a *copy* of the parent's service registry.
        Registrations in the child do not affect the parent; registrations
        in the parent after the child is created are not visible to the child.

        Useful for scoped / per-request contexts in test scenarios.

        Returns:
            A new Container pre-populated with the parent's services.
        """
        c = Container(
            _services=dict(self._services),
            _factories=set(self._factories),
        )
        return c

    # ------------------------------------------------------------------ #
    # Dunder conveniences
    # ------------------------------------------------------------------ #

    def __contains__(self, name: str) -> bool:
        """Support ``'name' in container`` syntax."""
        return self.has(name)

    def __repr__(self) -> str:
        names = ", ".join(sorted(self._services))
        return f"Container([{names}])"


# ---------------------------------------------------------------------------
# Global / module-level singleton
# ---------------------------------------------------------------------------

#: Module-level container instance.  Components that cannot receive an
#: explicit Container via constructor injection may fall back to this.
#: Prefer explicit injection in production code; use this only for
#: backward-compat shims or top-level entry points.
global_container: Container = Container()


__all__ = [
    "Container",
    "global_container",
]
