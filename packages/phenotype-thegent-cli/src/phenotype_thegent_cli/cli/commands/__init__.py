"""Namespace package for CLI command modules."""

from __future__ import annotations

import importlib
from typing import Any


def __getattr__(name: str) -> Any:
    """Expose common submodules for patch paths like `thegent.cli.commands.impl`."""
    if name in {"impl", "cli", "run_cmds", "session_cmds", "model_cmds", "governance_cmds", "_cli_shared"}:
        module = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
