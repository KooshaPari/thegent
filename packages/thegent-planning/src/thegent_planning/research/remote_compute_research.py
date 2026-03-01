"""Research: Implement thegent run --remote."""

from typing import Any

from thegent.research.remote_compute import RemoteComputeClient


class RemoteComputeImplResearch:
    """Research for remote compute implementation."""

    def __init__(self) -> None:
        """Initialize remote compute research."""
        self.client = RemoteComputeClient("localhost")

    def test_remote_execution(self) -> dict[str, Any]:
        """Test remote execution.

        Returns:
            Test results
        """
        result = self.client.execute_remote("echo test")
        return {"status": "success", "result": result}
