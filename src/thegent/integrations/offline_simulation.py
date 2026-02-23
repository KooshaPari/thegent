"""Offline Simulation Mode (WL-252): Simulate API responses for testing without network.

Provides mock response registration and retrieval for testing and development
without making actual API calls. Useful for offline testing, CI/CD pipelines,
and scenarios where live APIs are unavailable.

# @trace WL-252
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Response Simulation
# ---------------------------------------------------------------------------


@dataclass
class SimulatedResponse:
    """A simulated API response for offline testing.

    Attributes:
        endpoint: The API endpoint being simulated (e.g., "/api/users").
        status_code: HTTP status code (e.g., 200, 404, 500).
        body: The response body as a dictionary.
    """

    endpoint: str
    """The API endpoint being simulated."""

    status_code: int
    """HTTP status code."""

    body: dict[str, Any]
    """The response body."""

    def __post_init__(self) -> None:
        """Validate response configuration."""
        if not self.endpoint:
            raise ValueError("endpoint cannot be empty")
        if not 100 <= self.status_code < 600:
            raise ValueError(f"status_code must be 100-599, got {self.status_code}")


# ---------------------------------------------------------------------------
# Offline Simulation Mode
# ---------------------------------------------------------------------------


class OfflineSimulationMode:
    """Manages offline API response simulation.

    Allows registration of mock responses for endpoints and retrieval of
    simulated responses without making actual network calls.

    Example:
        >>> sim = OfflineSimulationMode(enabled=True)
        >>> sim.register_response("/api/users", 200, {"id": 1, "name": "Alice"})
        >>> sim.get_response("/api/users")
        SimulatedResponse(endpoint="/api/users", status_code=200, body={"id": 1, "name": "Alice"})
        >>> sim.is_enabled()
        True
    """

    def __init__(self, enabled: bool = False) -> None:
        """Initialize offline simulation mode.

        Args:
            enabled: Whether simulation mode is enabled (default: False).
        """
        self._enabled = enabled
        self._responses: dict[str, SimulatedResponse] = {}
        logger.debug("OfflineSimulationMode initialized: enabled=%s", enabled)

    def register_response(
        self,
        endpoint: str,
        status_code: int,
        body: dict[str, Any],
    ) -> SimulatedResponse:
        """Register a simulated response for an endpoint.

        If an endpoint already has a response, it is overwritten.

        Args:
            endpoint: The API endpoint (e.g., "/api/users").
            status_code: HTTP status code.
            body: The response body as a dictionary.

        Returns:
            The registered SimulatedResponse.

        Raises:
            ValueError: If response is invalid.

        Example:
            >>> sim = OfflineSimulationMode()
            >>> sim.register_response("/api/users", 200, {"users": []})
            SimulatedResponse(endpoint="/api/users", status_code=200, body={"users": []})
        """
        response = SimulatedResponse(
            endpoint=endpoint,
            status_code=status_code,
            body=body,
        )
        self._responses[endpoint] = response
        logger.debug(
            "Registered simulated response: endpoint=%r, status_code=%d",
            endpoint,
            status_code,
        )
        return response

    def get_response(self, endpoint: str) -> SimulatedResponse | None:
        """Retrieve a simulated response for an endpoint.

        Args:
            endpoint: The API endpoint to retrieve.

        Returns:
            The SimulatedResponse if registered, None otherwise.

        Example:
            >>> sim = OfflineSimulationMode()
            >>> sim.register_response("/api/users", 200, {"users": []})
            >>> sim.get_response("/api/users") is not None
            True
            >>> sim.get_response("/api/nonexistent") is None
            True
        """
        return self._responses.get(endpoint)

    def is_enabled(self) -> bool:
        """Check if offline simulation mode is enabled.

        Returns:
            True if simulation mode is enabled, False otherwise.
        """
        return self._enabled

    def enable(self) -> None:
        """Enable offline simulation mode.

        Example:
            >>> sim = OfflineSimulationMode(enabled=False)
            >>> sim.is_enabled()
            False
            >>> sim.enable()
            >>> sim.is_enabled()
            True
        """
        self._enabled = True
        logger.debug("Offline simulation mode enabled")

    def disable(self) -> None:
        """Disable offline simulation mode.

        Example:
            >>> sim = OfflineSimulationMode(enabled=True)
            >>> sim.is_enabled()
            True
            >>> sim.disable()
            >>> sim.is_enabled()
            False
        """
        self._enabled = False
        logger.debug("Offline simulation mode disabled")
