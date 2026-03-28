"""Research: Remote compute implementation."""

from phenotype_thegent_core.compute.offload import ComputeOffload
from phenotype_thegent_core.compute.remote_executor import RemoteResult


class CrossPlatformRemoteResearch:
    """Research for cross-platform remote compute."""

    def __init__(self) -> None:
        """Initialize cross-platform remote research."""
        self.offload = ComputeOffload()

    def test_remote_compute(self) -> RemoteResult:
        """Test remote compute.

        Returns:
            Test results
        """
        self.offload.register_target("test-host", "localhost", 22)
        result = self.offload.offload("test-host", "echo test")
        return result
