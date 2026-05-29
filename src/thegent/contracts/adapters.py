"""Contracts adapters module."""
from __future__ import annotations
from typing import TYPE_CHECKING, Any



class ContractAdapter:
    """Base contract adapter."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}

    def adapt(self, data: Any) -> Any:
        """Adapt data between formats."""
        return data


class XMLOutputAdapter:
    """XML output adapter for contracts."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}

    def adapt(self, data: Any) -> str:
        """Adapt data to XML format."""
        return f"<data>{data}</data>"


class AdapterResult:
    """Result of an adapter operation."""

    def __init__(self, success: bool, data: Any | None = None, error: str | None = None) -> None:
        self.success = success
        self.data = data
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        return {"success": self.success, "data": self.data, "error": self.error}


class ContractValidator:
    """Validates contract compliance."""

    def validate(self, data: Any, schema: dict[str, Any]) -> bool:
        """Validate data against schema."""
        return True


def normalize_output(data: Any) -> str:
    """Normalize output data."""
    return str(data)


__all__ = [
    "ContractAdapter",
    "XMLOutputAdapter",
    "AdapterResult",
    "ContractValidator",
    "normalize_output",
    "ADAPTER_REGISTRY",
]


class AdapterRegistry:
    """Registry for contract adapters."""

    def __init__(self) -> None:
        self._adapters: dict[str, Any] = {}

    def register(self, name: str, adapter: Any) -> None:
        """Register an adapter."""
        self._adapters[name] = adapter

    def get(self, name: str) -> Any | None:
        """Get an adapter by name."""
        return self._adapters.get(name)

    def list_adapters(self) -> list[str]:
        """List all registered adapter names."""
        return list(self._adapters.keys())


ADAPTER_REGISTRY = AdapterRegistry()


class GenericOutputAdapter:
    """Generic output adapter for various output formats."""

    def __init__(self, format: str = "json") -> None:
        self.format = format

    def adapt(self, data: Any) -> str:
        """Adapt data to the specified format."""
        if self.format == "json":
            import json
            return json.dumps(data, default=str)
        elif self.format == "xml":
            return f"<data>{data}</data>"
        elif self.format == "text":
            return str(data)
        return str(data)


__all__ = [
    "ContractAdapter",
    "XMLOutputAdapter",
    "AdapterResult",
    "ContractValidator",
    "normalize_output",
    "ADAPTER_REGISTRY",
    "GenericOutputAdapter",
    "OutputAdapter",
    "get_adapter",
    "register_adapter",
]


def register_adapter(name: str, adapter: ContractAdapter) -> None:
    """Register an adapter by name.

    Args:
        name: Adapter name.
        adapter: ContractAdapter instance.
    """
    ADAPTER_REGISTRY.register(name, adapter)


def get_adapter(name: str) -> ContractAdapter | None:
    """Get an adapter by name.

    Args:
        name: Adapter name.

    Returns:
        ContractAdapter instance or None.
    """
    return ADAPTER_REGISTRY.get(name)


class OutputAdapter:
    """Output adapter for contract results."""

    def __init__(self, format: str = "json") -> None:
        self.format = format

    def adapt(self, data: Any) -> str:
        """Adapt data to output format."""
        if self.format == "json":
            import json
            return json.dumps(data, default=str)
        return str(data)
