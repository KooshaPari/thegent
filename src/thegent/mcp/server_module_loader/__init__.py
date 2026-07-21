"""WL-126 server module loader.

Provides ``load_server_module`` which can be called with either the
WL-126 keyword-argument signature (``server_file``, ``module_filename``,
``module_import_name``, ``failure_message``) or the legacy positional
form (``module_name``).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def load_server_module(
    module_name: str | None = None,
    *,
    server_file: Path | None = None,
    module_filename: str | None = None,
    module_import_name: str | None = None,
    failure_message: str | None = None,
) -> Any:
    """Load a server module by name or by WL-126 keyword arguments.

    When ``module_name`` is provided (legacy form), loads the module from
    ``server_file``.  When ``server_file`` + ``module_filename`` +
    ``module_import_name`` are provided (WL-126 form), loads the module
    checking ``server_file.parent / 'server' / module_filename`` first
    (neighbor server package), then ``server_file.parent / module_filename``.
    Raises ``RuntimeError`` with ``failure_message`` when the module
    cannot be found or loaded.
    """
    if module_name is None and module_import_name is not None:
        module_name = module_import_name

    if module_name is None:
        raise RuntimeError(failure_message or "No module name provided")

    # Determine the file to load
    target_file: Path | None = None
    if server_file is not None and module_filename is not None:
        # WL-126: check neighbor ``server/`` subdirectory first, then parent.
        candidate_in_server_dir = server_file.parent / "server" / module_filename
        candidate_in_parent = server_file.parent / module_filename
        if candidate_in_server_dir.exists():
            target_file = candidate_in_server_dir
        elif candidate_in_parent.exists():
            target_file = candidate_in_parent
    elif server_file is not None:
        target_file = server_file

    if target_file is None or not target_file.exists():
        msg = failure_message or f"Module not found: {module_name}"
        if module_filename:
            msg = f"{msg}\n  Module file: {module_filename}"
        raise RuntimeError(msg)

    try:
        spec = importlib.util.spec_from_file_location(module_name, target_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot create spec for {module_name}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as exc:
        msg = failure_message or f"Failed to load module {module_name}"
        raise RuntimeError(f"{msg}\n  {exc}") from exc


__all__ = ["load_server_module"]
