"""Unit tests for PromptQueue (WP-7001)."""

from pathlib import Path

import pytest

from thegent.queue.storage import PromptQueue


@pytest.fixture
def queue_dir(tmp_path: Path) -> Path:
    return tmp_path / "sessions"


@pytest.fixture
def queue(queue_dir: Path) -> PromptQueue:
    return PromptQueue(queue_dir)


def test_append_and_list_pending(queue: PromptQueue) -> None:
    queue.append("First task", "proj1")
    queue.append("Second task", "proj1")
    pending = queue.list_pending()
    assert len(pending) == 2
    assert pending[0]["prompt"] == "First task"
    assert pending[1]["prompt"] == "Second task"


def test_list_all_includes_ids(queue: PromptQueue) -> None:
    queue.append("A", "p1")
    queue.append("B", "p1")
    items = queue.list_all(include_done=True)
    assert len(items) == 2
    assert items[0]["id"] == 0
    assert items[1]["id"] == 1


def test_claim_returns_first_pending(queue: PromptQueue) -> None:
    queue.append("Task 1", "proj")
    queue.append("Task 2", "proj")
    claimed = queue.claim("worker-1", project="proj")
    assert claimed is not None
    assert claimed["prompt"] == "Task 1"
    assert claimed["claimed_by"] == "worker-1"
    assert claimed["status"] == "claimed"
    assert claimed["id"] == 0


def test_claim_filters_by_project(queue: PromptQueue) -> None:
    queue.append("P1 task", "proj1")
    queue.append("P2 task", "proj2")
    claimed = queue.claim("w", project="proj2")
    assert claimed is not None
    assert claimed["prompt"] == "P2 task"


def test_claim_empty_returns_none(queue: PromptQueue) -> None:
    assert queue.claim("w") is None


def test_done_marks_item(queue: PromptQueue) -> None:
    queue.append("X", "p")
    claimed = queue.claim("w")
    assert claimed is not None
    assert queue.done(claimed["id"]) is True
    items = queue.list_all(include_done=True)
    assert items[0]["status"] == "done"


def test_release_returns_to_pending(queue: PromptQueue) -> None:
    queue.append("Y", "p")
    claimed = queue.claim("w")
    assert claimed is not None
    assert queue.release(claimed["id"]) is True
    pending = queue.list_pending()
    assert len(pending) == 1
    assert pending[0]["prompt"] == "Y"


def test_extend_lease(queue: PromptQueue) -> None:
    queue.append("Z", "p")
    claimed = queue.claim("w", lease_seconds=60)
    assert claimed is not None
    assert queue.extend_lease(claimed["id"], lease_seconds=120) is True
    items = queue.list_all(include_done=True)
    assert "lease_expires_at" in items[0]


def test_edit_pending(queue: PromptQueue) -> None:
    queue.append("Original", "p")
    assert queue.edit(0, "Updated") is True
    pending = queue.list_pending()
    assert pending[0]["prompt"] == "Updated"


def test_edit_claimed(queue: PromptQueue) -> None:
    queue.append("Original", "p")
    queue.claim("w")
    assert queue.edit(0, "Updated") is True
    items = queue.list_all(include_done=True)
    assert items[0]["prompt"] == "Updated"


def test_edit_done_fails(queue: PromptQueue) -> None:
    queue.append("X", "p")
    queue.claim("w")
    queue.done(0)
    assert queue.edit(0, "Y") is False


def test_get_pending_count(queue: PromptQueue) -> None:
    assert queue.get_pending_count() == 0
    queue.append("A", "p")
    assert queue.get_pending_count() == 1
    queue.claim("w")
    assert queue.get_pending_count() == 0
