"""cli_bridge: Lazy accessor for thegent_cli functions used by the MCP server.

This module breaks the CLI ↔ Protocols circular dependency.  Instead of
importing CLI symbols at module load time (which requires CLI to be fully
importable before protocols can be imported), all CLI functions are resolved
lazily on first access.

Usage inside protocols:
    from thegent_protocols.mcp.cli_bridge import cli
    result = cli.run_impl(...)

The ``cli`` proxy object resolves thegent_cli.cli.commands.impl and
related modules on first attribute access.
"""

from __future__ import annotations

import importlib
from typing import Any


class _CLIBridge:
    """Lazy proxy to thegent_cli.cli.commands.impl and related modules.

    Attribute access triggers a one-time import of the concrete CLI module.
    This keeps protocols importable even before the CLI package is fully
    installed.
    """

    _impl: Any = None
    _auto_init: Any = None
    _session_ops: Any = None
    _session_ctrl: Any = None

    # ------------------------------------------------------------------ #
    # Primary impl module proxy
    # ------------------------------------------------------------------ #

    def _get_impl(self) -> Any:
        if self._impl is None:
            self.__class__._impl = importlib.import_module("thegent_cli.cli.commands.impl")
        return self._impl

    def __getattr__(self, name: str) -> Any:
        """Resolve any attribute from thegent_cli.cli.commands.impl."""
        impl = self._get_impl()
        try:
            return getattr(impl, name)
        except AttributeError as exc:
            raise AttributeError(f"thegent_cli.cli.commands.impl has no attribute {name!r}") from exc

    # ------------------------------------------------------------------ #
    # Convenience accessors for sub-modules
    # ------------------------------------------------------------------ #

    @property
    def auto_init_on_startup(self) -> Any:
        """Lazy accessor for thegent_cli.ide.auto_init.auto_init_on_startup."""
        if self._auto_init is None:
            mod = importlib.import_module("thegent_cli.ide.auto_init")
            self.__class__._auto_init = mod.auto_init_on_startup
        return self._auto_init

    @property
    def ps_impl(self) -> Any:
        """Alias for cli.ps_impl (from session_ops module)."""
        if self._session_ops is None:
            self.__class__._session_ops = importlib.import_module("thegent_cli.cli.commands.session_ops_impl")
        return self._session_ops.ps_impl

    @property
    def logs_impl(self) -> Any:
        """Alias for cli.logs_impl (from session_ops module)."""
        if self._session_ops is None:
            self.__class__._session_ops = importlib.import_module("thegent_cli.cli.commands.session_ops_impl")
        return self._session_ops.logs_impl

    @property
    def session_send_impl_raw(self) -> Any:
        """Alias for raw session_send_impl (from session_control module)."""
        if self._session_ctrl is None:
            self.__class__._session_ctrl = importlib.import_module("thegent_cli.cli.commands.session_control_impl")
        return self._session_ctrl.session_send_impl


# Singleton bridge instance — import this and call attributes lazily.
cli = _CLIBridge()

__all__ = ["cli"]
