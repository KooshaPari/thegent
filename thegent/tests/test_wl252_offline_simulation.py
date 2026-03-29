"""Tests for WL-252: Offline Simulation Mode.

Verifies offline API response simulation.

# @trace WL-252
"""

from __future__ import annotations

import pytest

from thegent.integrations.offline_simulation import (
    OfflineSimulationMode,
    SimulatedResponse,
)


@pytest.mark.requirement("WL-252")
class TestOfflineSimulationMode:
    """WL-252: Offline simulation mode."""

    def test_simulated_response_creation(self):
        """SimulatedResponse instantiation succeeds with valid inputs."""
        response = SimulatedResponse(
            endpoint="/api/users",
            status_code=200,
            body={"id": 1, "name": "Alice"},
        )
        assert response.endpoint == "/api/users"
        assert response.status_code == 200
        assert response.body == {"id": 1, "name": "Alice"}

    def test_simulated_response_validation_empty_endpoint(self):
        """SimulatedResponse rejects empty endpoint."""
        with pytest.raises(ValueError, match="endpoint cannot be empty"):
            SimulatedResponse(
                endpoint="",
                status_code=200,
                body={},
            )

    def test_simulated_response_validation_invalid_status_code(self):
        """SimulatedResponse rejects invalid status codes."""
        with pytest.raises(ValueError, match="status_code must be 100-599"):
            SimulatedResponse(
                endpoint="/api/users",
                status_code=99,
                body={},
            )

        with pytest.raises(ValueError, match="status_code must be 100-599"):
            SimulatedResponse(
                endpoint="/api/users",
                status_code=600,
                body={},
            )

    def test_offline_simulation_disabled_by_default(self):
        """OfflineSimulationMode is disabled by default."""
        sim = OfflineSimulationMode()
        assert not sim.is_enabled()

    def test_offline_simulation_enabled_on_init(self):
        """OfflineSimulationMode can be enabled on initialization."""
        sim = OfflineSimulationMode(enabled=True)
        assert sim.is_enabled()

    def test_register_response(self):
        """register_response() registers a response."""
        sim = OfflineSimulationMode()
        response = sim.register_response("/api/users", 200, {"users": []})

        assert response.endpoint == "/api/users"
        assert response.status_code == 200
        assert response.body == {"users": []}

    def test_get_response_found(self):
        """get_response() returns registered response."""
        sim = OfflineSimulationMode()
        sim.register_response("/api/users", 200, {"id": 1})
        response = sim.get_response("/api/users")

        assert response is not None
        assert response.status_code == 200
        assert response.body == {"id": 1}

    def test_get_response_not_found(self):
        """get_response() returns None for unregistered endpoint."""
        sim = OfflineSimulationMode()
        response = sim.get_response("/api/nonexistent")
        assert response is None

    def test_register_multiple_endpoints(self):
        """Multiple endpoints can be registered."""
        sim = OfflineSimulationMode()
        sim.register_response("/api/users", 200, {"users": []})
        sim.register_response("/api/posts", 200, {"posts": []})
        sim.register_response("/api/comments", 404, {"error": "not found"})

        assert sim.get_response("/api/users").status_code == 200
        assert sim.get_response("/api/posts").status_code == 200
        assert sim.get_response("/api/comments").status_code == 404

    def test_register_overwrites_existing(self):
        """Registering same endpoint overwrites previous response."""
        sim = OfflineSimulationMode()
        sim.register_response("/api/users", 200, {"version": 1})
        sim.register_response("/api/users", 201, {"version": 2})

        response = sim.get_response("/api/users")
        assert response.status_code == 201
        assert response.body == {"version": 2}

    def test_enable_simulation_mode(self):
        """enable() sets enabled flag to True."""
        sim = OfflineSimulationMode(enabled=False)
        assert not sim.is_enabled()
        sim.enable()
        assert sim.is_enabled()

    def test_disable_simulation_mode(self):
        """disable() sets enabled flag to False."""
        sim = OfflineSimulationMode(enabled=True)
        assert sim.is_enabled()
        sim.disable()
        assert not sim.is_enabled()

    def test_response_with_complex_body(self):
        """register_response() handles complex nested dictionaries."""
        complex_body = {
            "data": [
                {"id": 1, "name": "Alice", "tags": ["admin", "user"]},
                {"id": 2, "name": "Bob", "tags": ["user"]},
            ],
            "pagination": {"page": 1, "total": 2},
            "metadata": {"timestamp": "2026-02-22T00:00:00Z"},
        }
        sim = OfflineSimulationMode()
        sim.register_response("/api/users", 200, complex_body)

        response = sim.get_response("/api/users")
        assert response.body == complex_body
        assert len(response.body["data"]) == 2

    def test_response_with_error_status_codes(self):
        """register_response() handles error status codes."""
        sim = OfflineSimulationMode()
        sim.register_response("/api/users", 400, {"error": "Bad request"})
        sim.register_response("/api/posts", 401, {"error": "Unauthorized"})
        sim.register_response("/api/comments", 500, {"error": "Server error"})

        assert sim.get_response("/api/users").status_code == 400
        assert sim.get_response("/api/posts").status_code == 401
        assert sim.get_response("/api/comments").status_code == 500

    def test_empty_response_body(self):
        """register_response() handles empty response bodies."""
        sim = OfflineSimulationMode()
        sim.register_response("/api/delete", 204, {})

        response = sim.get_response("/api/delete")
        assert response.body == {}
        assert response.status_code == 204

    def test_get_response_case_sensitive_endpoints(self):
        """get_response() matches endpoints case-sensitively."""
        sim = OfflineSimulationMode()
        sim.register_response("/api/Users", 200, {"data": "upper"})

        assert sim.get_response("/api/Users") is not None
        assert sim.get_response("/api/users") is None

    def test_enable_disable_toggle(self):
        """enable/disable can be toggled multiple times."""
        sim = OfflineSimulationMode(enabled=False)
        assert not sim.is_enabled()

        sim.enable()
        assert sim.is_enabled()

        sim.disable()
        assert not sim.is_enabled()

        sim.enable()
        assert sim.is_enabled()
