"""AUDIT-N+100: orchestration/omega_consensus hardening spec (SOTA pass-84).

15 invariants FR-ORC-OC-001..015 covering OmegaConsensus init validation,
propose_state default metadata, cast_vote idempotency, finalize_consensus
unknown proposal, get_final_state field verification, __all__ export.

Source: src/thegent/orchestration/consensus/omega_consensus/__init__.py

@trace AUDIT-N+100 FR-ORC-OC-001..015
"""

from __future__ import annotations

import pytest

from thegent.orchestration.consensus.omega_consensus import (
    FinalState,
    OmegaConsensus,
)


class TestInitValidation:
    def test_swarm_size_zero_raises(self):
        with pytest.raises(ValueError, match="swarm_size"):
            OmegaConsensus(swarm_size=0)

    def test_swarm_size_negative_raises(self):
        with pytest.raises(ValueError, match="swarm_size"):
            OmegaConsensus(swarm_size=-5)

    def test_threshold_below_zero_raises(self):
        with pytest.raises(ValueError, match="threshold"):
            OmegaConsensus(swarm_size=3, threshold=-0.1)

    def test_threshold_above_one_raises(self):
        with pytest.raises(ValueError, match="threshold"):
            OmegaConsensus(swarm_size=3, threshold=1.5)

    def test_valid_init(self):
        oc = OmegaConsensus(swarm_size=5, threshold=0.6)
        assert oc.swarm_size == 5
        assert oc.threshold == 0.6


class TestProposeState:
    def test_metadata_none_default_path(self):
        oc = OmegaConsensus(swarm_size=3)
        pid = oc.propose_state("proposer-1", {"key": "val"})
        assert isinstance(pid, str)
        assert len(pid) > 0
        assert oc._proposals[pid].metadata == {}

    def test_metadata_provided(self):
        oc = OmegaConsensus(swarm_size=3)
        pid = oc.propose_state("proposer-1", "state", metadata={"region": "us"})
        assert oc._proposals[pid].metadata == {"region": "us"}


class TestCastVote:
    def test_duplicate_vote_returns_true(self):
        oc = OmegaConsensus(swarm_size=3)
        pid = oc.propose_state("p", "s")
        first = oc.cast_vote(pid, "voter-1", True, "sig-a")
        second = oc.cast_vote(pid, "voter-1", False, "sig-b")
        assert first is True
        assert second is True
        vote, sig = oc._proposals[pid].votes["voter-1"]
        assert vote is True
        assert sig == "sig-a"

    def test_unknown_proposal_returns_false(self):
        oc = OmegaConsensus(swarm_size=3)
        assert oc.cast_vote("nonexistent", "voter-1", True, "sig") is False


class TestFinalizeConsensus:
    def test_unknown_proposal_returns_false(self):
        oc = OmegaConsensus(swarm_size=3)
        assert oc.finalize_consensus("nonexistent") is False
        assert oc.get_final_state() is None


class TestGetFinalState:
    def test_returns_finalstate_with_fields(self):
        oc = OmegaConsensus(swarm_size=2, threshold=0.5)
        pid = oc.propose_state("p", {"data": 42}, metadata={"ver": 1})
        oc.cast_vote(pid, "v1", True, "s1")
        oc.cast_vote(pid, "v2", True, "s2")
        assert oc.finalize_consensus(pid) is True

        fs = oc.get_final_state()
        assert isinstance(fs, FinalState)
        assert fs.proposal_id == pid
        assert fs.state == {"data": 42}
        assert fs.metadata == {"ver": 1}

    def test_no_consensus_returns_none(self):
        oc = OmegaConsensus(swarm_size=3)
        assert oc.get_final_state() is None


class TestFinalStateFrozen:
    def test_immutable(self):
        fs = FinalState(proposal_id="p1", state="s1")
        with pytest.raises(AttributeError):
            fs.proposal_id = "p2"


class TestCanonicalAll:
    def test_all_export(self):
        from thegent.orchestration.consensus.omega_consensus import __all__ as exported

        assert "FinalState" in exported
        assert "OmegaConsensus" in exported
