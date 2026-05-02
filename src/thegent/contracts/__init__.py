"""STUB MODULE - thegent.contracts

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations

from typing import Any

# Re-export from submodules for backwards compatibility
from thegent.contracts.adapters import AdapterResult, normalize_output, OutputAdapter
from thegent.contracts.csm import CSMPhase, CanonicalStructuredMessage, CSMStatus

CONTRACT_SCHEMA_VERSION = "1.0.0"

def get_registry() -> ADAPTER_REGISTRY:
    """Get the global adapter registry instance.

    Returns:
        The global ADAPTER_REGISTRY instance.
    """
    return ADAPTER_REGISTRY


def get_adapter(name: str) -> Any | None:
    """Get an adapter by name from the registry.

    Args:
        name: The adapter name to look up.

    Returns:
        The adapter instance or None if not found.
    """
    return ADAPTER_REGISTRY.get(name)


__all__ = [
    "ADAPTER_REGISTRY",
    "AdapterResult",
    "CanonicalStructuredMessage",
    "CONTRACT_SCHEMA_VERSION",
    "CSMPhase",
    "CSMStatus",
    "get_adapter",
    "get_registry",
    "normalize_output",
    "OutputAdapter",
]


class ADAPTER_REGISTRY:
    """Adapter registry for contracts."""

    _adapters: dict[str, Any] = {}

    @classmethod
    def register(cls, name: str, adapter: Any) -> None:
        cls._adapters[name] = adapter

    @classmethod
    def get(cls, name: str) -> Any | None:
        return cls._adapters.get(name)

    @classmethod
    def keys(cls) -> list[str]:
        return list(cls._adapters.keys())


__all__ = [
    "ADAPTER_REGISTRY",
    "AdapterResult",
    "CanonicalStructuredMessage",
    "CONTRACT_SCHEMA_VERSION",
    "CSMStatus",
    "normalize_output",
    "OutputAdapter",
]
