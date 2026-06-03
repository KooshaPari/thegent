"""Install helpers."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path


def _fallback_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _get_thegent_root() -> Path:
    try:
        module = import_module("thegent")
        return Path(module.__file__).resolve().parent
    except Exception:
        return _fallback_root()


__all__ = ["Path", "_get_thegent_root", "import_module"]
