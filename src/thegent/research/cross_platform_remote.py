"""Research: Remote compute implementation."""

from typing import Any

from thegent.compute.offload import ComputeOffload


class CrossPlatformRemoteResearch:
    """Research for cross-platform remote compute."""

    def __init__(self) -> None:
        """Initialize cross-platform remote research."""
        self.offload = ComputeOffload()

    def test_remote_compute(self) -> dict[str, Any]:
        """Test remote compute.

        Returns:
            Test results
        """
        self.offload.register_target("test-host", "localhost", 22)
        result = self.offload.offload("test-host", "echo test")
        return result
