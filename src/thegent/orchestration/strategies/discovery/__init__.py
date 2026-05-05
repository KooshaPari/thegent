"""Stub module."""
from dataclasses import dataclass


@dataclass
class DiscoverySystem:
    """System for discovering resources and services."""

    def discover(self) -> list[str]:
        """Discover available resources."""
        return []


__all__ = ["DiscoverySystem", "get_discovery_system"]


def get_discovery_system() -> DiscoverySystem:
    """Get the global discovery system."""
    return DiscoverySystem()
