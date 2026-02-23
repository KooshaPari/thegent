"""Doctor module - re-exports symbols from doctor.py (flat file) for backward compat."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

_DOCTOR_PY = Path(__file__).parent.parent / "doctor.py"
_MODULE_NAME = "thegent._doctor_flat"

if _MODULE_NAME not in sys.modules:
    _spec = importlib.util.spec_from_file_location(_MODULE_NAME, _DOCTOR_PY)
    if _spec is None or _spec.loader is None:
        raise ImportError(f"Cannot load {_DOCTOR_PY}")
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules[_MODULE_NAME] = _mod
    _spec.loader.exec_module(_mod)  # type: ignore[union-attr]

_flat = sys.modules[_MODULE_NAME]

_PUBLIC = [name for name in dir(_flat) if not name.startswith("_")]
for _name in _PUBLIC:
    globals()[_name] = getattr(_flat, _name)

__all__ = _PUBLIC


def __getattr__(name: str) -> Any:
    try:
        return getattr(_flat, name)
    except AttributeError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
