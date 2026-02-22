"""Compatibility shim for ``thegent.mcp.server`` package exports."""

from thegent.mcp.server import *  # noqa: F401,F403 -- module re-exports 150+ public APIs for backward compatibility
from thegent.mcp.server import _get_event_store as _legacy_get_event_store

_get_event_store = _legacy_get_event_store
