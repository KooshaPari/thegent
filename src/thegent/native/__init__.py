"""Compatibility facade for native platform helpers."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_MODULE = import_module("thegent_platform.native")


def __getattr__(name: str) -> Any:
    return getattr(_MODULE, name)
