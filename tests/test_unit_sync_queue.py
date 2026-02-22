"""Unit tests for machine-readable sync conflict queue.

# @trace WL-205
"""

from __future__ import annotations

import pytest

from thegent.sync.conflicts import SyncConflict
from thegent.sync.queue import ConflictQueueStore


@pytest.mark.requirement("WL-205")
def test_queue_add_and_pending(tmp_path):
    store = ConflictQueueStore(tmp_path / "queue.json")
    entry = SyncConflict(
        conflict_id="c1",
        wl_id="WL-205",
        field="status",
        local_value="BACKLOG",
        remote_value="IN PROGRESS",
        connector="github",
    )
    store.add(entry)
    pending = store.pending()
    assert len(pending) == 1
    assert pending[0].conflict_id == "c1"


@pytest.mark.requirement("WL-205")
def test_queue_resolve_marks_entry_resolved(tmp_path):
    store = ConflictQueueStore(tmp_path / "queue.json")
    store.add(
        SyncConflict(
            conflict_id="c1",
            wl_id="WL-205",
            field="priority",
            local_value="P2",
            remote_value="P1",
            connector="linear",
        )
    )
    store.resolve("c1")
    assert store.pending() == []


@pytest.mark.requirement("WL-205")
def test_queue_rejects_duplicate_conflict_id(tmp_path):
    store = ConflictQueueStore(tmp_path / "queue.json")
    entry = SyncConflict(
        conflict_id="c1",
        wl_id="WL-205",
        field="priority",
        local_value="P2",
        remote_value="P1",
        connector="linear",
    )
    store.add(entry)
    with pytest.raises(ValueError, match="conflict already exists"):
        store.add(entry)
