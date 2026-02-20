"""Research: Integrate escalation queue with DLQ."""

from typing import Any

from thegent.research.governance_dlq import EscalationQueueDLQ


class GovernanceEscalationDLQResearch:
    """Research for escalation queue DLQ integration."""

    def __init__(self) -> None:
        """Initialize escalation DLQ research."""
        self.queue = EscalationQueueDLQ()

    def test_integration(self) -> dict[str, Any]:
        """Test DLQ integration.

        Returns:
            Test results
        """
        # Test enqueue
        self.queue.enqueue({"id": "test-1", "data": "test"})

        # Test process
        item = self.queue.process()

        # Test DLQ
        if item:
            self.queue.move_to_dlq(item, "Test reason")

        return {
            "queue_size": len(self.queue.queue),
            "dlq_size": len(self.queue.dlq),
        }
