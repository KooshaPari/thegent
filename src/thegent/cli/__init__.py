"""Compatibility facade for `thegent.cli` command surface."""

from __future__ import annotations

import json
import os
import signal
import sys
import time
from typing import Any

from thegent.cli.commands import cli as _cli_surface
from thegent.cli.commands import _cli_shared as _shared


def __getattr__(name: str) -> Any:
    """Load command surface symbols lazily from the re-export module."""
    if name == "AGENT_LABELS":
        from thegent.agents.registry import AGENT_LABELS

        globals()[name] = AGENT_LABELS
        return AGENT_LABELS
    if hasattr(_cli_surface, name):
        return getattr(_cli_surface, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


_surface_names = getattr(_cli_surface, "__all__", [])
for _name in _surface_names:
    globals()[_name] = getattr(_cli_surface, _name)

_patchable_names_list = [
    "resolve_agent",
    "list_agent_names",
    "list_droid_names",
    "run_login",
    "_normalize_output_format",
    "_find_session_meta",
    "_session_paths",
    "_read_session_meta",
    "_is_pid_running",
    "_resolve_session_status",
    "_resolve_cwd",
    "_resolve_droids_dir",
    "_resolve_run_id",
    "_safe_dict",
    "_safe_list",
    "RunRegistry",
    "ThegentSettings",
    "get_exit_message",
]
for _name in _patchable_names_list:
    if not hasattr(sys.modules[__name__], _name) and hasattr(_shared, _name):
        globals()[_name] = getattr(_shared, _name)

# Export all patchable names and agent labels (static literal for ruff compliance)
__all__ = [
    "AGENT_LABELS",
    "RunRegistry",
    "ThegentSettings",
    "_find_session_meta",
    "_is_pid_running",
    "_normalize_output_format",
    "_read_session_meta",
    "_resolve_cwd",
    "_resolve_droids_dir",
    "_resolve_run_id",
    "_resolve_session_status",
    "_safe_dict",
    "_safe_list",
    "_session_paths",
    "get_exit_message",
    "list_agent_names",
    "list_droid_names",
    "resolve_agent",
    "run_login",
]
