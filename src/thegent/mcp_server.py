"""Compatibility shim for ``thegent.mcp.server`` package exports."""

from thegent.mcp.server import *  # noqa: F401,F403 -- module re-exports 150+ public APIs for backward compatibility
from thegent.mcp.server import _get_event_store  # pyright: ignore[reportAttributeAccessIssue] -- private API re-export for backward compatibility
