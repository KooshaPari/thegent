"""Tests for WL-176 Process-Compose Operational Hardening.

# @trace WL-176
"""

from __future__ import annotations

import pytest

from thegent.integrations.process_compose_ops import ProcessComposeOps, ServiceStatus


@pytest.mark.requirement("WL-176")
class TestServiceStatus:
    """Tests for ServiceStatus dataclass."""

    def test_service_status_creation(self) -> None:
        """ServiceStatus can be created with required fields."""
        status = ServiceStatus(name="api", running=True)
        assert status.name == "api"
        assert status.running is True
        assert status.exit_code is None

    def test_service_status_with_exit_code(self) -> None:
        """ServiceStatus can include exit code."""
        status = ServiceStatus(name="api", running=False, exit_code=1)
        assert status.name == "api"
        assert status.running is False
        assert status.exit_code == 1

    def test_service_status_exit_code_zero(self) -> None:
        """ServiceStatus can have exit code 0."""
        status = ServiceStatus(name="api", running=False, exit_code=0)
        assert status.exit_code == 0


@pytest.mark.requirement("WL-176")
class TestProcessComposeOps:
    """Tests for ProcessComposeOps class."""

    def test_register_service(self) -> None:
        """register() creates a service entry."""
        ops = ProcessComposeOps()
        ops.register("api")

        status = ops.get_status("api")
        assert status.name == "api"
        assert status.running is False
        assert status.exit_code is None

    def test_register_multiple_services(self) -> None:
        """register() can create multiple service entries."""
        ops = ProcessComposeOps()
        ops.register("api")
        ops.register("db")
        ops.register("cache")

        assert ops.get_status("api").name == "api"
        assert ops.get_status("db").name == "db"
        assert ops.get_status("cache").name == "cache"

    def test_register_idempotent(self) -> None:
        """register() is idempotent for the same service."""
        ops = ProcessComposeOps()
        ops.register("api")
        ops.mark_running("api")
        ops.register("api")  # Register again

        # Should still be marked as running
        assert ops.get_status("api").running is True

    def test_mark_running_success(self) -> None:
        """mark_running() sets service to running."""
        ops = ProcessComposeOps()
        ops.register("api")
        ops.mark_running("api")

        status = ops.get_status("api")
        assert status.running is True
        assert status.exit_code is None

    def test_mark_running_not_registered(self) -> None:
        """mark_running() raises KeyError for unregistered service."""
        ops = ProcessComposeOps()

        with pytest.raises(KeyError, match="Service not registered"):
            ops.mark_running("unknown")

    def test_mark_stopped_success(self) -> None:
        """mark_stopped() sets service to stopped."""
        ops = ProcessComposeOps()
        ops.register("api")
        ops.mark_stopped("api", exit_code=0)

        status = ops.get_status("api")
        assert status.running is False
        assert status.exit_code == 0

    def test_mark_stopped_default_exit_code(self) -> None:
        """mark_stopped() defaults exit_code to 0."""
        ops = ProcessComposeOps()
        ops.register("api")
        ops.mark_stopped("api")

        status = ops.get_status("api")
        assert status.exit_code == 0

    def test_mark_stopped_nonzero_exit_code(self) -> None:
        """mark_stopped() can set nonzero exit code."""
        ops = ProcessComposeOps()
        ops.register("api")
        ops.mark_stopped("api", exit_code=127)

        status = ops.get_status("api")
        assert status.exit_code == 127

    def test_mark_stopped_not_registered(self) -> None:
        """mark_stopped() raises KeyError for unregistered service."""
        ops = ProcessComposeOps()

        with pytest.raises(KeyError, match="Service not registered"):
            ops.mark_stopped("unknown")

    def test_get_status_success(self) -> None:
        """get_status() returns registered service."""
        ops = ProcessComposeOps()
        ops.register("api")
        ops.mark_running("api")

        status = ops.get_status("api")
        assert status.name == "api"
        assert status.running is True

    def test_get_status_not_found(self) -> None:
        """get_status() raises KeyError for unknown service."""
        ops = ProcessComposeOps()

        with pytest.raises(KeyError, match="Service not found"):
            ops.get_status("unknown")

    def test_all_running_empty(self) -> None:
        """all_running() returns empty list when no services registered."""
        ops = ProcessComposeOps()
        assert ops.all_running() == []

    def test_all_running_all_stopped(self) -> None:
        """all_running() returns empty list when all services are stopped."""
        ops = ProcessComposeOps()
        ops.register("api")
        ops.register("db")
        # Both remain stopped
        assert ops.all_running() == []

    def test_all_running_some_running(self) -> None:
        """all_running() returns only running services."""
        ops = ProcessComposeOps()
        ops.register("api")
        ops.register("db")
        ops.register("cache")

        ops.mark_running("api")
        ops.mark_running("cache")
        # db remains stopped

        running = ops.all_running()
        assert len(running) == 2
        assert "api" in running
        assert "cache" in running
        assert "db" not in running

    def test_all_running_sorted(self) -> None:
        """all_running() returns services in sorted order."""
        ops = ProcessComposeOps()
        ops.register("zebra")
        ops.register("alpha")
        ops.register("beta")

        ops.mark_running("zebra")
        ops.mark_running("alpha")
        ops.mark_running("beta")

        running = ops.all_running()
        assert running == ["alpha", "beta", "zebra"]

    def test_state_transitions(self) -> None:
        """Services can transition between running and stopped states."""
        ops = ProcessComposeOps()
        ops.register("api")

        # Start running
        ops.mark_running("api")
        assert ops.get_status("api").running is True

        # Stop with exit code
        ops.mark_stopped("api", exit_code=1)
        assert ops.get_status("api").running is False
        assert ops.get_status("api").exit_code == 1

        # Start again
        ops.mark_running("api")
        assert ops.get_status("api").running is True
        assert ops.get_status("api").exit_code is None
