"""Shared Memory system for orchestration state.

This module provides a shared memory system for fast inter-process
communication in the orchestration layer.
"""

from __future__ import annotations

from typing import Any


class SHMSystem:
    """Shared memory system for orchestration.
    
    This class manages shared memory regions for fast
    inter-process communication.
    """

    def __init__(self, size: int = 1024 * 1024) -> None:
        """Initialize the SHM system.
        
        Args:
            size: Size of the shared memory region in bytes.
        """
        self.size = size
        self._data: dict[str, Any] = {}

    def write(self, key: str, value: Any) -> None:
        """Write a value to shared memory.
        
        Args:
            key: The key to write.
            value: The value to store.
        """
        self._data[key] = value

    def read(self, key: str) -> Any | None:
        """Read a value from shared memory.
        
        Args:
            key: The key to read.
            
        Returns:
            The stored value or None if not found.
        """
        return self._data.get(key)

    def delete(self, key: str) -> None:
        """Delete a value from shared memory.
        
        Args:
            key: The key to delete.
        """
        self._data.pop(key, None)

    def clear(self) -> None:
        """Clear all shared memory."""
        self._data.clear()

    def keys(self) -> list[str]:
        """Get all keys in shared memory.
        
        Returns:
            List of keys.
        """
        return list(self._data.keys())


# Global SHM system instance
_shm_system: SHMSystem | None = None


def get_shm_system() -> SHMSystem:
    """Get the global SHM system instance.
    
    Returns:
        The global SHMSystem instance.
    """
    global _shm_system
    if _shm_system is None:
        _shm_system = SHMSystem()
    return _shm_system


__all__ = [
    "SHMSystem",
    "get_shm_system",
]
