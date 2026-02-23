"""Thegent CLI - re-exports from thegent-cli package."""

import sys
from typing import Any

# Lazy import pattern to avoid circular dependencies
# The thegent-cli package is the source of truth

_cli_module = None


def __getattr__(name: str) -> Any:
    """Lazy load attributes from thegent_cli package."""
    global _cli_module

    if _cli_module is None:
        try:
            import thegent_cli as cli
            _cli_module = cli
        except ImportError:
            # Fall back to loading from commands if package not installed
            # This maintains backward compatibility with existing code
            from thegent.cli import commands
            _cli_module = commands

    if hasattr(_cli_module, name):
        return getattr(_cli_module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "RunRegistry",
    "ThegentSettings",
    "console",
    "list_agent_names",
    "resolve_agent",
]
