"""Unit tests for sync decision journal primitives.

# @trace WL-203
"""

from __future__ import annotations

import pytest

from thegent.sync.journal import LocalDecisionJournal, SyncDecisionEntry


@pytest.mark.requirement("WL-203")
def test_journal_append_and_read_round_trip(tmp_path):
    journal = LocalDecisionJournal(tmp_path / "journal.jsonl")
    entry = SyncDecisionEntry.create(
        cycle_id="cycle-1",
        wl_id="WL-203",
        decision="status_changed",
        rationale="remote accepted",
        before_state={"status": "BACKLOG"},
        after_state={"status": "IN PROGRESS"},
    )
    journal.append(entry)

    rows = journal.read_all()
    assert len(rows) == 1
    assert rows[0].wl_id == "WL-203"
    assert rows[0].decision == "status_changed"


@pytest.mark.requirement("WL-203")
def test_journal_read_replayable_filters_false(tmp_path):
    journal = LocalDecisionJournal(tmp_path / "journal.jsonl")
    replayable = SyncDecisionEntry.create(
        cycle_id="cycle-1",
        wl_id="WL-203",
        decision="keep_local",
        rationale="manual override",
        before_state={},
        after_state={},
        replayable=True,
    )
    non_replayable = SyncDecisionEntry.create(
        cycle_id="cycle-2",
        wl_id="WL-203",
        decision="transient_observation",
        rationale="telemetry only",
        before_state={},
        after_state={},
        replayable=False,
    )
    journal.append(replayable)
    journal.append(non_replayable)

    rows = journal.read_replayable()
    assert [row.entry_id for row in rows] == [replayable.entry_id]


@pytest.mark.requirement("WL-203")
def test_journal_read_all_fails_loud_on_invalid_json(tmp_path):
    journal_path = tmp_path / "journal.jsonl"
    journal_path.write_text("{bad json}\n", encoding="utf-8")
    journal = LocalDecisionJournal(journal_path)

    with pytest.raises(ValueError, match="invalid journal line 1"):
        journal.read_all()

