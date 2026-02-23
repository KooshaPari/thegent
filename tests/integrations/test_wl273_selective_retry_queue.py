"""Tests for thegent.integrations.selective_retry_queue — Attempt-limited retry queue.

@trace WL-273
"""

from __future__ import annotations

import pytest

from thegent.integrations.selective_retry_queue import (
    RetryItem,
    SelectiveRetryQueue,
)


class TestRetryItem:
    """Test RetryItem dataclass. @trace WL-273"""

    @pytest.mark.requirement("WL-273")
    def test_create_default(self) -> None:
        """Can create RetryItem with default attempt=0."""
        item = RetryItem(item_id="task1", payload={"data": "value"})

        assert item.item_id == "task1"
        assert item.payload == {"data": "value"}
        assert item.attempt == 0

    @pytest.mark.requirement("WL-273")
    def test_create_with_attempt(self) -> None:
        """Can create RetryItem with custom attempt."""
        item = RetryItem(item_id="task1", payload={"data": "value"}, attempt=2)

        assert item.item_id == "task1"
        assert item.attempt == 2

    @pytest.mark.requirement("WL-273")
    def test_payload_mutation(self) -> None:
        """RetryItem payload can be mutated."""
        payload = {"data": "value"}
        item = RetryItem(item_id="task1", payload=payload)

        payload["data"] = "modified"
        assert item.payload["data"] == "modified"


class TestSelectiveRetryQueue:
    """Test SelectiveRetryQueue operations. @trace WL-273"""

    @pytest.mark.requirement("WL-273")
    def test_init_default(self) -> None:
        """Can initialize with default max_attempts=3."""
        queue = SelectiveRetryQueue()
        assert queue._max_attempts == 3

    @pytest.mark.requirement("WL-273")
    def test_init_custom_max(self) -> None:
        """Can initialize with custom max_attempts."""
        queue = SelectiveRetryQueue(max_attempts=5)
        assert queue._max_attempts == 5

    @pytest.mark.requirement("WL-273")
    def test_init_invalid_max(self) -> None:
        """Raises ValueError for invalid max_attempts."""
        with pytest.raises(ValueError, match="max_attempts must be >= 1"):
            SelectiveRetryQueue(max_attempts=0)

    @pytest.mark.requirement("WL-273")
    def test_enqueue_single_item(self) -> None:
        """Can enqueue a single item."""
        queue = SelectiveRetryQueue()
        item = queue.enqueue("id1", {"data": "payload"})

        assert item.item_id == "id1"
        assert item.payload == {"data": "payload"}
        assert item.attempt == 0

    @pytest.mark.requirement("WL-273")
    def test_enqueue_multiple_items(self) -> None:
        """Can enqueue multiple items."""
        queue = SelectiveRetryQueue()
        queue.enqueue("id1", {"data": "1"})
        queue.enqueue("id2", {"data": "2"})
        queue.enqueue("id3", {"data": "3"})

        pending = queue.pending()
        assert len(pending) == 3

    @pytest.mark.requirement("WL-273")
    def test_retry_increments_attempt(self) -> None:
        """retry() increments attempt counter."""
        queue = SelectiveRetryQueue(max_attempts=5)
        queue.enqueue("id1", {"data": "value"})

        result = queue.retry("id1")
        assert result is not None
        assert result.attempt == 1

    @pytest.mark.requirement("WL-273")
    def test_retry_multiple_times(self) -> None:
        """Can retry item multiple times until max reached."""
        queue = SelectiveRetryQueue(max_attempts=3)
        queue.enqueue("id1", {"data": "value"})

        assert queue.retry("id1") is not None  # attempt 1
        assert queue.retry("id1") is not None  # attempt 2
        assert queue.retry("id1") is None  # attempt 3, max reached

    @pytest.mark.requirement("WL-273")
    def test_retry_nonexistent_item(self) -> None:
        """retry() on non-existent item returns None."""
        queue = SelectiveRetryQueue()
        result = queue.retry("nonexistent")
        assert result is None

    @pytest.mark.requirement("WL-273")
    def test_failed_when_max_reached(self) -> None:
        """Item moves to failed when max_attempts reached."""
        queue = SelectiveRetryQueue(max_attempts=2)
        queue.enqueue("id1", {"data": "value"})

        queue.retry("id1")
        queue.retry("id1")  # This should fail

        failed = queue.failed()
        assert len(failed) == 1
        assert failed[0].item_id == "id1"
        assert failed[0].attempt == 2

    @pytest.mark.requirement("WL-273")
    def test_failed_items_removed_from_pending(self) -> None:
        """Failed items are removed from pending queue."""
        queue = SelectiveRetryQueue(max_attempts=1)
        queue.enqueue("id1", {"data": "value"})

        queue.retry("id1")  # Hits max

        assert len(queue.pending()) == 0
        assert len(queue.failed()) == 1

    @pytest.mark.requirement("WL-273")
    def test_pending_list(self) -> None:
        """pending() returns all items not yet failed."""
        queue = SelectiveRetryQueue(max_attempts=3)
        queue.enqueue("id1", {"data": "1"})
        queue.enqueue("id2", {"data": "2"})

        queue.retry("id1")
        queue.retry("id1")
        queue.retry("id1")  # id1 now failed

        pending = queue.pending()
        assert len(pending) == 1
        assert pending[0].item_id == "id2"

    @pytest.mark.requirement("WL-273")
    def test_failed_list(self) -> None:
        """failed() returns all items exceeding max_attempts."""
        queue = SelectiveRetryQueue(max_attempts=1)
        queue.enqueue("id1", {"data": "1"})
        queue.enqueue("id2", {"data": "2"})
        queue.enqueue("id3", {"data": "3"})

        queue.retry("id1")
        queue.retry("id2")

        failed = queue.failed()
        assert len(failed) == 2
        failed_ids = {item.item_id for item in failed}
        assert failed_ids == {"id1", "id2"}

    @pytest.mark.requirement("WL-273")
    def test_empty_queues_initially(self) -> None:
        """Newly created queue has empty pending and failed."""
        queue = SelectiveRetryQueue()
        assert len(queue.pending()) == 0
        assert len(queue.failed()) == 0

    @pytest.mark.requirement("WL-273")
    def test_enqueue_overwrites_pending(self) -> None:
        """Enqueueing same ID again overwrites previous item."""
        queue = SelectiveRetryQueue()
        queue.enqueue("id1", {"data": "old"})
        queue.enqueue("id1", {"data": "new"})

        pending = queue.pending()
        assert len(pending) == 1
        assert pending[0].payload == {"data": "new"}


class TestSelectiveRetryQueueIntegration:
    """Integration tests for SelectiveRetryQueue. @trace WL-273"""

    @pytest.mark.requirement("WL-273")
    def test_mixed_retry_workflow(self) -> None:
        """Complex workflow with multiple items at different stages."""
        queue = SelectiveRetryQueue(max_attempts=2)

        # Enqueue items
        queue.enqueue("task_a", {"type": "compute"})
        queue.enqueue("task_b", {"type": "network"})
        queue.enqueue("task_c", {"type": "storage"})

        # Retry some items
        queue.retry("task_a")  # attempt 1
        queue.retry("task_a")  # attempt 2, now failed
        queue.retry("task_b")  # attempt 1

        # Check state
        pending = queue.pending()
        assert len(pending) == 2  # task_b and task_c

        failed = queue.failed()
        assert len(failed) == 1
        assert failed[0].item_id == "task_a"

    @pytest.mark.requirement("WL-273")
    def test_attempt_counter_per_item(self) -> None:
        """Each item has independent attempt counter."""
        queue = SelectiveRetryQueue(max_attempts=3)
        queue.enqueue("id1", {"data": "1"})
        queue.enqueue("id2", {"data": "2"})

        queue.retry("id1")
        queue.retry("id1")
        queue.retry("id2")

        pending = queue.pending()
        item1 = next(i for i in pending if i.item_id == "id1")
        item2 = next(i for i in pending if i.item_id == "id2")

        assert item1.attempt == 2
        assert item2.attempt == 1

    @pytest.mark.requirement("WL-273")
    def test_payload_preservation(self) -> None:
        """Payload is preserved through retry operations."""
        queue = SelectiveRetryQueue(max_attempts=3)
        original_payload = {"key": "value", "nested": {"field": "data"}}
        queue.enqueue("id1", original_payload.copy())

        queue.retry("id1")
        queue.retry("id1")

        pending = queue.pending()
        assert pending[0].payload == original_payload

    @pytest.mark.requirement("WL-273")
    def test_max_attempts_boundary(self) -> None:
        """Boundary condition at max_attempts limit."""
        queue = SelectiveRetryQueue(max_attempts=1)
        queue.enqueue("id1", {"data": "value"})

        # First retry should hit max immediately
        result = queue.retry("id1")
        assert result is None

        # Should now be in failed
        assert len(queue.failed()) == 1
        assert len(queue.pending()) == 0
