"""Shared dynamic module loader for MCP server helper modules (WL-126)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def load_server_module(
    *,
    server_file: Path,
    module_filename: str,
    module_import_name: str,
    failure_message: str,
) -> Any:
    """Load a neighboring helper module from the `server/` package directory."""
    module_path = server_file.with_suffix("") / module_filename
    spec = importlib.util.spec_from_file_location(module_import_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"{failure_message} from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except FileNotFoundError as exc:
        raise RuntimeError(f"{failure_message} from: {module_path}") from exc
    return module


__all__ = ["load_server_module"]
