"""Stub module."""
from typing import Any


def load_server_module(module_name: str) -> dict[str, Any]:
    """Load a server module by name."""
    return {"name": module_name, "loaded": True}


__all__ = ["load_server_module"]
