"""
Unified SDK Facade

Provides a single entry point for all agent/SDK operations.
"""

from typing import Any

from thegent.adapters.ports import AdapterRegistry, AdapterPort


class UnifiedSDK:
    """Unified SDK facade for all agent operations."""
    
    def __init__(self):
        self._adapters = AdapterRegistry.all()
    
    def list_adapters(self) -> list[str]:
        """List all registered adapters"""
        return list(self._adapters.keys())
    
    def get_adapter(self, name: str) -> AdapterPort | None:
        """Get adapter by name"""
        return AdapterRegistry.get(name)
    
    def call(self, adapter_name: str, **kwargs) -> dict[str, Any]:
        """Call adapter by name"""
        adapter = self.get_adapter(adapter_name)
        if not adapter:
            return {"error": f"Adapter '{adapter_name}' not found"}
        return adapter.call(**kwargs)
    
    def register(self, name: str, adapter: AdapterPort):
        """Register a new adapter"""
        AdapterRegistry.register(name, adapter)


# Global SDK instance
_sdk = None


def get_sdk() -> UnifiedSDK:
    """Get global UnifiedSDK instance"""
    global _sdk
    if _sdk is None:
        _sdk = UnifiedSDK()
    return _sdk


# Convenience functions
def list_adapters() -> list[str]:
    """List all registered adapters"""
    return get_sdk().list_adapters()


def get_adapter(name: str) -> AdapterPort | None:
    """Get adapter by name"""
    return get_sdk().get_adapter(name)


def call_adapter(name: str, **kwargs) -> dict[str, Any]:
    """Call adapter by name"""
    return get_sdk().call(name, **kwargs)
