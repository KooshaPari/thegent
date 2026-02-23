"""Execution module - re-exports all symbols from execution.py for backward compatibility.

The flat execution.py file contains 35+ classes. This package __init__ forwards
all attribute lookups to that file via importlib so both
`from thegent.execution import X` and `import thegent.execution; thegent.execution.X`
continue to work.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any

# Load the flat execution.py file as a sibling module.
# It lives at src/thegent/execution.py which is shadowed by this package,
# so we load it explicitly by file path.
_EXECUTION_PY = Path(__file__).parent.parent / "execution.py"
_MODULE_NAME = "thegent._execution_flat"

if _MODULE_NAME not in sys.modules:
    _spec = importlib.util.spec_from_file_location(_MODULE_NAME, _EXECUTION_PY)
    if _spec is None or _spec.loader is None:
        raise ImportError(f"Cannot load {_EXECUTION_PY}")
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules[_MODULE_NAME] = _mod
    _spec.loader.exec_module(_mod)  # type: ignore[union-attr]

_flat = sys.modules[_MODULE_NAME]

# Re-export every public name from the flat module into this package namespace.
_PUBLIC = [name for name in dir(_flat) if not name.startswith("_")]
for _name in _PUBLIC:
    globals()[_name] = getattr(_flat, _name)

__all__ = _PUBLIC


def __getattr__(name: str) -> Any:
    try:
        return getattr(_flat, name)
    except AttributeError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
