"""Sitback plugin registry for dashboard widget extensions.

The SitbackRegistry collects plugin widgets and harness-status callbacks
that are shown in the "full" Sitback dashboard profile.  Plugins can be
registered at startup or via the DI container.

Phase 2C DI migration
---------------------
The module-level ``_registry`` singleton replaces an implicit "look up
via dynamic import at call time" pattern.  New code should inject a
SitbackRegistry instance where possible; the module-level helpers
``get_registry()`` / ``set_registry()`` are provided for backward
compatibility with existing callers that do:

    from phenotype_thegent_agents.sitback_plugins import get_registry
    reg = get_registry()
"""

from __future__ import annotations

from typing import Any


class SitbackRegistry:
    """Registry for Sitback dashboard plugin widgets and harness status.

    Attributes:
        _widgets: Mapping of widget name → widget data dict.
        _harness_callback: Optional callable returning harness status dict.
    """

    def __init__(self) -> None:
        self._widgets: dict[str, Any] = {}
        self._harness_callback: Any | None = None

    # ------------------------------------------------------------------ #
    # Widget API
    # ------------------------------------------------------------------ #

    def register_widget(self, name: str, widget_data: Any) -> None:
        """Register a dashboard widget under *name*.

        Args:
            name: Unique widget identifier.
            widget_data: Dict or callable returning widget payload.
        """
        self._widgets[name] = widget_data

    def unregister_widget(self, name: str) -> None:
        """Remove a widget by name.  No-op if not registered."""
        self._widgets.pop(name, None)

    def get_widgets(self) -> dict[str, Any]:
        """Return a snapshot of all registered widgets.

        If a widget_data value is callable, it is called and its return
        value is used.  Exceptions are caught and replaced with an error dict.

        Returns:
            Mapping of widget name → widget payload.
        """
        result: dict[str, Any] = {}
        for name, data in self._widgets.items():
            if callable(data):
                try:
                    result[name] = data()
                except Exception as exc:
                    result[name] = {"error": str(exc)}
            else:
                result[name] = data
        return result

    # ------------------------------------------------------------------ #
    # Harness status API
    # ------------------------------------------------------------------ #

    def set_harness_callback(self, callback: Any) -> None:
        """Register a callable that returns the current harness status dict.

        Args:
            callback: Zero-argument callable returning a dict or None.
        """
        self._harness_callback = callback

    def get_harness_status(self) -> dict[str, Any] | None:
        """Return the current harness status, or None if unavailable.

        Returns:
            Dict from the harness callback, or None if no callback is set
            or the callback raises.
        """
        if self._harness_callback is None:
            return None
        try:
            return self._harness_callback()
        except Exception:
            return None

    # ------------------------------------------------------------------ #
    # Membership
    # ------------------------------------------------------------------ #

    def __contains__(self, name: str) -> bool:
        """Support ``'name' in registry`` syntax."""
        return name in self._widgets

    def __repr__(self) -> str:
        return f"SitbackRegistry(widgets={list(self._widgets)})"


# ---------------------------------------------------------------------------
# Module-level singleton — backward-compat shim
# ---------------------------------------------------------------------------

#: Module-level SitbackRegistry instance.
#: Callers that cannot accept injection may use get_registry() / set_registry().
_registry: SitbackRegistry = SitbackRegistry()


def get_registry() -> SitbackRegistry:
    """Return the module-level SitbackRegistry singleton.

    Backward-compatible helper matching the pattern expected by callers:
        from phenotype_thegent_agents.sitback_plugins import get_registry
        reg = get_registry()
    """
    return _registry


def set_registry(registry: SitbackRegistry) -> None:
    """Replace the module-level SitbackRegistry singleton.

    Useful in tests or when wiring up a custom registry via the DI container.

    Args:
        registry: The SitbackRegistry instance to use as the new singleton.
    """
    global _registry
    _registry = registry


__all__ = [
    "SitbackRegistry",
    "_registry",
    "get_registry",
    "set_registry",
]
