"""Process-Compose Operational Hardening.

WL-176: Process-Compose Operational Hardening
Provides service status tracking and operational monitoring for process-compose services.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ServiceStatus:
    """Status of a registered service."""

    name: str
    running: bool
    exit_code: int | None = None


class ProcessComposeOps:
    """Operations manager for process-compose services."""

    def __init__(self) -> None:
        """Initialize the process-compose operations manager."""
        self._services: dict[str, ServiceStatus] = {}

    def register(self, name: str) -> None:
        """Register a service.

        Args:
            name: Name of the service.
        """
        if name not in self._services:
            self._services[name] = ServiceStatus(name=name, running=False)

    def mark_running(self, name: str) -> None:
        """Mark a service as running.

        Args:
            name: Name of the service.

        Raises:
            KeyError: If service not registered.
        """
        if name not in self._services:
            raise KeyError(f"Service not registered: {name}")
        self._services[name].running = True
        self._services[name].exit_code = None

    def mark_stopped(self, name: str, exit_code: int = 0) -> None:
        """Mark a service as stopped.

        Args:
            name: Name of the service.
            exit_code: Exit code of the service (default 0).

        Raises:
            KeyError: If service not registered.
        """
        if name not in self._services:
            raise KeyError(f"Service not registered: {name}")
        self._services[name].running = False
        self._services[name].exit_code = exit_code

    def get_status(self, name: str) -> ServiceStatus:
        """Get the status of a service.

        Args:
            name: Name of the service.

        Returns:
            ServiceStatus for the service.

        Raises:
            KeyError: If service not found.
        """
        if name not in self._services:
            raise KeyError(f"Service not found: {name}")
        return self._services[name]

    def all_running(self) -> list[str]:
        """Get list of all running services.

        Returns:
            Sorted list of names of all running services.
        """
        return sorted(name for name, status in self._services.items() if status.running)
