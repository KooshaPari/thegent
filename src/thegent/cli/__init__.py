"""Compatibility facade for `thegent.cli` command surface."""

from __future__ import annotations

import os
import signal
import sys
import time
from typing import Any

from thegent.cli.commands import cli as _cli_surface
from thegent.cli.commands import _cli_shared as _shared

# Backward compatibility - expose commonly used modules for test mocking
Columns = getattr(_cli_surface, "Columns", None)

# Stub for tests
def _resolve_cwd(cd=None):
    """Stub for backward compatibility."""
    return

def _parse_dag_session(dag_file, cwd=None):
    """Stub for tests."""
    return {}, []

def _parse_dag_full(dag_file, cwd=None):
    """Stub for tests."""
    return {}

def _serialize_dag(doc):
    """Stub for tests."""
    return ""

def _validate_dag(doc):
    """Stub for tests."""
    return []

def _check_dag_cycles(doc):
    """Stub for tests."""
    return []

def _dag_path(cd=None):
    """Stub for tests."""
    return

def _ensure_dag_file(path, content):
    """Stub for tests."""
    return

def _dag_update_task(task_id, field, value, session_dir):
    """Stub for tests."""
    return True


def __getattr__(name: str) -> Any:
    """Load command surface symbols lazily from the re-export module."""
    # Forward to _shared for CLI helper functions
    if hasattr(_shared, name):
        return getattr(_shared, name)
    
    # Forward dag_update_cmd to _cli_surface
    if name == "dag_update_cmd":
        from thegent.cli.commands import plan_dag_cmds
        return getattr(plan_dag_cmds, name)
    
    # Forward ThegentSettings to _shared
    if name == "ThegentSettings":
        from thegent.cli.commands._cli_shared import ThegentSettings
        globals()[name] = ThegentSettings
        return ThegentSettings
    
    if name == "AGENT_LABELS":
        from thegent.agents.registry import AGENT_LABELS

        globals()[name] = AGENT_LABELS
        return AGENT_LABELS
    
    # Lazy load model list commands
    _model_list_funcs = (
        "_list_minimax_models", "_list_glm_models", "_list_cursor_models",
        "_list_gemini_models", "_list_copilot_models", "_list_claude_models",
        "_list_codex_models", "_list_antigravity_models", "_list_kiro_models",
        "_list_copilot_models_fallback", "_list_codex_models_fallback",
    )
    if name in _model_list_funcs:
        from thegent.cli.commands import model_cmds_config
        func = getattr(model_cmds_config, name, None)
        if func:
            globals()[name] = func
            return func
        # Try model_cmds_rules
        from thegent.cli.commands import model_cmds_rules
        func = getattr(model_cmds_rules, name, None)
        if func:
            globals()[name] = func
            return func
    
    if hasattr(_cli_surface, name):
        return getattr(_cli_surface, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


_surface_names = getattr(_cli_surface, "__all__", [])
for _name in _surface_names:
    globals()[_name] = getattr(_cli_surface, _name)

# Patchable names - delegate to _cli_shared for test mocking
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
    "console",
]
for _name in _patchable_names_list:
    if not hasattr(sys.modules[__name__], _name) and hasattr(_shared, _name):
        globals()[_name] = getattr(_shared, _name)

# Export all patchable names and agent labels (static literal for ruff compliance)
__all__ = [
    "_resolve_cwd",
    "os",
    "signal",
    "sys",
    "time",
    # DAG helpers
    "_dag_path",
    "_parse_dag_full",
    "_parse_dag_session",
    "_serialize_dag",
    "_validate_dag",
    "_check_dag_cycles",
    "_ensure_dag_file",
    "_dag_update_task",
]
