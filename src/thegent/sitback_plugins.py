"""Sitback plugin API: dashboard widgets and startup steps.

Plugins are discovered from ~/.claude/sitback-plugins/ (JSON or Python).
Each plugin can register:
- dashboard_widgets: dict[str, callable] -> name -> fn() -> dict (title, content, border_style)
- startup_steps: list[str] -> extra lines for startup prompt
- harness_status: callable -> dict | None (for heliosShield/FUSE; returns None if unavailable)
"""

from __future__ import annotations

import orjson as json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

_log = logging.getLogger(__name__)

SITBACK_PLUGINS_DIR = Path.home() / ".claude" / "sitback-plugins"


class SitbackPluginRegistry:
    """Registry for sitback plugins: widgets, startup steps, harness status."""

    def __init__(self) -> None:
        self._widgets: dict[str, Callable[[], dict[str, Any]]] = {}
        self._startup_steps: list[str] = []
        self._harness_status_fn: Callable[[], dict[str, Any] | None] | None = None

    def register_widget(self, name: str, fn: Callable[[], dict[str, Any]]) -> None:
        """Register a dashboard widget. fn() returns {title, content, border_style}."""
        self._widgets[name] = fn

    def register_startup_step(self, step: str) -> None:
        """Register an extra startup step (appended to startup prompt)."""
        self._startup_steps.append(step)

    def register_harness_status(self, fn: Callable[[], dict[str, Any] | None]) -> None:
        """Register harness status provider (e.g. heliosShield). Returns None if unavailable."""
        self._harness_status_fn = fn

    def _run_widget(self, name: str, fn: Callable[[], Any]) -> dict[str, Any] | None:
        """Run a single widget, returning result or None on failure."""
        try:
            return fn()
        except Exception as e:
            _log.warning("sitback widget %s failed: %s", name, e)
            return None

    def get_widgets(self) -> dict[str, dict[str, Any]]:
        """Run all widgets, return {name: result}. Skips failures."""
        out: dict[str, dict[str, Any]] = {}
        for name, fn in self._widgets.items():
            result = self._run_widget(name, fn)
            if result is not None:
                out[name] = result
        return out

    def get_startup_steps(self) -> list[str]:
        """Return registered startup steps."""
        return list(self._startup_steps)

    def get_harness_status(self) -> dict[str, Any] | None:
        """Return harness status if provider available, else None."""
        if self._harness_status_fn is None:
            return None
        try:
            return self._harness_status_fn()
        except Exception as e:
            _log.debug("harness status unavailable: %s", e)
            return None


_registry: SitbackPluginRegistry | None = None


def get_registry() -> SitbackPluginRegistry:
    """Get or create the global plugin registry."""
    global _registry
    if _registry is None:
        _registry = SitbackPluginRegistry()
        _registry.register_harness_status(_probe_harness_status)
        _discover_plugins(_registry)
    return _registry


def _discover_plugins(registry: SitbackPluginRegistry) -> None:
    """Discover plugins from ~/.claude/sitback-plugins/."""
    if not SITBACK_PLUGINS_DIR.exists():
        return
    for path in SITBACK_PLUGINS_DIR.iterdir():
        if path.suffix == ".json":
            _load_json_plugin(path, registry)
        elif path.suffix == ".py" and path.name != "__init__.py":
            _load_py_plugin(path, registry)


def _load_json_plugin(path: Path, registry: SitbackPluginRegistry) -> None:
    """Load a JSON plugin: {startup_steps: [...], widgets: {name: {title, content}}}."""
    try:
        data = json.loads(path.read_text())
        for step in data.get("startup_steps", []):
            registry.register_startup_step(str(step))
        for name, w in data.get("widgets", {}).items():
            title = w.get("title", name)
            content = w.get("content", "")
            border_style = w.get("border_style", "dim")

            def _make_fn(t: str, c: str, b: str) -> Callable[[], dict[str, Any]]:
                return lambda: {"title": t, "content": c, "border_style": b}

            registry.register_widget(name, _make_fn(title, content, border_style))
    except Exception as e:
        _log.warning("sitback plugin %s failed: %s", path.name, e)


def _load_py_plugin(path: Path, registry: SitbackPluginRegistry) -> None:
    """Load a Python plugin: must define register_sitback(registry)."""
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(f"sitback_plugin_{path.stem}", path)
        if spec is None or spec.loader is None:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "register_sitback"):
            mod.register_sitback(registry)
    except Exception as e:
        _log.warning("sitback plugin %s failed: %s", path.name, e)


def _probe_harness_status() -> dict[str, Any]:
    """Probe heliosShield harness and classify availability outcomes."""
    from thegent.config import ThegentSettings

    if not ThegentSettings().sitback_harness:
        return {
            "status": "unavailable",
            "reason": "disabled_by_config",
            "message": "heliosShield harness probe disabled by configuration.",
        }

    try:
        from thegent.skills.terminal import heliosShield_status
    except ImportError as exc:
        return {
            "status": "unavailable",
            "reason": "dependency_missing",
            "message": "heliosShield harness dependency is not installed.",
            "error": str(exc),
        }

    try:
        status = heliosShield_status()
    except Exception as exc:
        return {
            "status": "error",
            "reason": "runtime_failure",
            "message": "heliosShield harness probe raised an exception.",
            "error": str(exc),
        }

    if "not found" in status.lower():
        return {
            "status": "unavailable",
            "reason": "dependency_missing",
            "message": "heliosShield harness requested but not found.",
            "raw": status,
        }
    return {
        "status": "available",
        "reason": "ok",
        "message": "heliosShield harness active.",
        "raw": status,
    }
