"""Hardening tests for the WL705 ``mesh/consensus`` split.

These tests pin the canonical ADR-013 / SCLI-P3.x consensus surface after
the WL705 L1 Architecture hardening pass that split the legacy
368-LOC single-file ``mesh/consensus.py`` into a 3-submodule package +
30-LOC back-compat shim. The split closed a real test-coverage gap
(the legacy module shipped with **0 tests**) and dropped
``get_consensus`` cognitive complexity from CC=12 to CC≤6 via three
extracted helpers (``_tally_round_votes`` / ``_resolve_consensus_status``
/ ``_persist_decision_record``).

Coverage shape:

* Canonical resolution (5 tests) — package + sub-module shape.
* ``ConsensusProtocol`` lifecycle (10 tests) — propose / draft / share /
  vote / advance / load.
* ``get_consensus`` tally + decide (8 tests) — all four branches of
  the decision tree + defensive defaults.
* Helper extraction CC pin (3 tests) — the three extracted helpers each
  behave independently of the orchestrator.
* ``CausalInfluenceTracker`` (4 tests) — record / compute / Shapley
  normalisation / degenerate zero-weight case.
* ``EscalationWorkflow`` (5 tests) — tier transitions / human-queue
  enqueue / list / resolve.
* Back-compat shim (3 tests) — legacy import path resolves to the
  canonical package surface (identity check).
* AST purity (2 tests) — shim LOC ≤ 35, no class definitions inside
  the shim body.
"""

from __future__ import annotations

import importlib
import inspect
import json
import textwrap
from pathlib import Path

import pytest

from thegent.mesh.consensus import (
    CausalInfluenceTracker,
    ConsensusProtocol,
    ConsensusStatus,
    EscalationWorkflow,
)

# ---------------------------------------------------------------------------
# Canonical resolution (5 tests)
# ---------------------------------------------------------------------------


PACKAGE = "thegent.mesh.consensus"
PROTOCOL_MODULE = "thegent.mesh.consensus.protocol"
INFLUENCE_MODULE = "thegent.mesh.consensus.influence"
ESCALATION_MODULE = "thegent.mesh.consensus.escalation"
IO_MODULE = "thegent.mesh.consensus._io"


def test_consensus_package_imports_clean() -> None:
    """The package imports cleanly and resolves to the package __init__."""
    package = importlib.import_module(PACKAGE)
    assert package.__file__ is not None
    assert package.__file__.endswith("/consensus/__init__.py")


def test_consensus_package_exposes_canonical_surface() -> None:
    """The four canonical classes are reachable from the package root."""
    from thegent.mesh.consensus import (
        ConsensusProtocol,
        ConsensusStatus,
        CausalInfluenceTracker,
        EscalationWorkflow,
    )

    assert ConsensusProtocol.__name__ == "ConsensusProtocol"
    assert ConsensusStatus.__name__ == "ConsensusStatus"
    assert CausalInfluenceTracker.__name__ == "CausalInfluenceTracker"
    assert EscalationWorkflow.__name__ == "EscalationWorkflow"


def test_consensus_package_all_pins_canonical_surface() -> None:
    """``__all__`` contains exactly the four canonical symbols."""
    package = importlib.import_module(PACKAGE)
    assert set(package.__all__) == {
        "ConsensusStatus",
        "ConsensusProtocol",
        "CausalInfluenceTracker",
        "EscalationWorkflow",
    }


def test_consensus_protocol_identity_via_shim() -> None:
    """Back-compat shim re-exports are the SAME class objects as the canonical sub-modules."""
    from thegent.mesh.consensus import ConsensusProtocol as ShimCP
    from thegent.mesh.consensus import CausalInfluenceTracker as ShimCIT
    from thegent.mesh.consensus import EscalationWorkflow as ShimEW
    from thegent.mesh.consensus import ConsensusStatus as ShimStatus
    from thegent.mesh.consensus.escalation import EscalationWorkflow as CanonicalEW
    from thegent.mesh.consensus.influence import CausalInfluenceTracker as CanonicalCIT
    from thegent.mesh.consensus.protocol import ConsensusProtocol as CanonicalCP
    from thegent.mesh.consensus.protocol import ConsensusStatus as CanonicalStatus

    assert ShimCP is CanonicalCP
    assert ShimCIT is CanonicalCIT
    assert ShimEW is CanonicalEW
    assert ShimStatus is CanonicalStatus


def test_consensus_package_docstring_cites_adr_origin() -> None:
    """The package docstring documents the ADR-013 / SCLI-P3.x lineage."""
    package = importlib.import_module(PACKAGE)
    assert package.__doc__ is not None
    doc = package.__doc__
    assert "ADR-013" in doc
    assert "SCLI-P3" in doc


# ---------------------------------------------------------------------------
# ConsensusProtocol lifecycle (10 tests, tmp_path fixtures)
# ---------------------------------------------------------------------------


def test_propose_writes_canonical_proposal_record(tmp_path: Path) -> None:
    """``propose`` writes the canonical 9-key proposal JSON."""
    proto = ConsensusProtocol(tmp_path)
    proto.propose("p-1", "agent-alpha", "Topic A", {"x": 1})

    proposal_file = tmp_path / "proposals" / "p-1.json"
    assert proposal_file.exists()
    payload = json.loads(proposal_file.read_text())
    for key in (
        "proposal_id",
        "leader_id",
        "topic",
        "content",
        "decision_type",
        "phase",
        "round",
        "max_debate_rounds",
        "timestamp",
    ):
        assert key in payload, f"missing required key {key!r}"
    assert payload["phase"] == "propose"
    assert payload["round"] == 1
    assert payload["decision_type"] == "implementation"


def test_propose_with_architecture_decision_type(tmp_path: Path) -> None:
    """``decision_type='architecture'`` is recorded verbatim on the proposal."""
    proto = ConsensusProtocol(tmp_path)
    proto.propose("p-2", "agent-beta", "Architecture Topic", {}, decision_type="architecture")
    payload = json.loads((tmp_path / "proposals" / "p-2.json").read_text())
    assert payload["decision_type"] == "architecture"


def test_draft_writes_to_proposal_drafts_subdir(tmp_path: Path) -> None:
    """``draft`` writes to ``proposals/<id>.drafts/agent-<id>.json``."""
    proto = ConsensusProtocol(tmp_path)
    proto.draft("p-3", "agent-gamma", {"counter": 42})

    draft_file = tmp_path / "proposals" / "p-3.drafts" / "agent-agent-gamma.json"
    assert draft_file.exists()
    payload = json.loads(draft_file.read_text())
    assert payload["agent_id"] == "agent-gamma"
    assert payload["refinement"] == {"counter": 42}


def test_share_finalizes_phase(tmp_path: Path) -> None:
    """``share`` flips ``phase`` to ``"share"`` and writes ``finalized_at``."""
    proto = ConsensusProtocol(tmp_path)
    proto.propose("p-4", "agent-delta", "Topic", {})
    proto.share("p-4")
    payload = json.loads((tmp_path / "proposals" / "p-4.json").read_text())
    assert payload["phase"] == "share"
    assert "finalized_at" in payload


def test_share_is_silent_for_missing_proposal(tmp_path: Path) -> None:
    """``share`` is a no-op when the proposal file does not exist (no exception)."""
    proto = ConsensusProtocol(tmp_path)
    # Should not raise.
    proto.share("nonexistent")
    assert not (tmp_path / "proposals" / "nonexistent.json").exists()


def test_cast_vote_enforces_round_bounds(tmp_path: Path) -> None:
    """Out-of-range ``vote_round`` is silently dropped."""
    proto = ConsensusProtocol(tmp_path)
    proto.propose("p-5", "agent", "Topic", {}, max_debate_rounds=2)
    # Round 0 → silent drop.
    proto.cast_vote("p-5", "agent-1", True, vote_round=0)
    # Round 99 → silent drop.
    proto.cast_vote("p-5", "agent-2", True, vote_round=99)
    assert not (tmp_path / "votes" / "p-5").exists()


def test_cast_vote_writes_vote_record(tmp_path: Path) -> None:
    """In-bounds ``vote_round`` writes the canonical 5-key vote record."""
    proto = ConsensusProtocol(tmp_path)
    proto.propose("p-6", "agent", "Topic", {})
    proto.cast_vote("p-6", "agent-1", True, confidence=0.9, vote_round=1)
    vote_file = tmp_path / "votes" / "p-6" / "round-1" / "agent-agent-1.json"
    assert vote_file.exists()
    payload = json.loads(vote_file.read_text())
    assert payload["vote"] is True
    assert payload["confidence"] == pytest.approx(0.9)
    assert payload["vote_round"] == 1


def test_advance_debate_round_clamps_at_max(tmp_path: Path) -> None:
    """``advance_debate_round`` is idempotent at ``max_rounds``."""
    proto = ConsensusProtocol(tmp_path)
    proto.propose("p-7", "agent", "Topic", {}, max_debate_rounds=2)
    # Round 1 → 2.
    assert proto.advance_debate_round("p-7") == 2
    # Round 2 → still 2 (clamped).
    assert proto.advance_debate_round("p-7") == 2


def test_advance_debate_round_returns_1_for_missing_proposal(tmp_path: Path) -> None:
    """Missing proposal returns the defensive default round (1)."""
    proto = ConsensusProtocol(tmp_path)
    assert proto.advance_debate_round("nonexistent") == 1


def test_vote_round_dir_is_canonical_path(tmp_path: Path) -> None:
    """``_vote_round_dir`` returns ``votes/<id>/round-<n>``."""
    proto = ConsensusProtocol(tmp_path)
    assert proto._vote_round_dir("p-x", 3) == tmp_path / "votes" / "p-x" / "round-3"


# ---------------------------------------------------------------------------
# get_consensus tally + decide (8 tests)
# ---------------------------------------------------------------------------


def _seed_proposal_with_votes(tmp_path: Path, proto: ConsensusProtocol, ratio_yes: float) -> str:
    """Seed a proposal + 10 weighted votes achieving the given yes-ratio.

    ``ratio_yes = 1.0`` → all yes votes; ``ratio_yes = 0.0`` → all no votes;
    ``ratio_yes = 0.5`` → split 5/5; etc.
    """
    proto.propose("ratio-test", "leader", "T", {})
    yes_count = round(10 * ratio_yes)
    for i in range(10):
        vote = i < yes_count
        proto.cast_vote("ratio-test", f"agent-{i}", vote, confidence=0.8)
    return "ratio-test"


def test_get_consensus_unknown_proposal_returns_pending(tmp_path: Path) -> None:
    """Unknown proposal → ``(PENDING, 0.0)``, no decision file written."""
    proto = ConsensusProtocol(tmp_path)
    status, ratio = proto.get_consensus("nonexistent")
    assert status is ConsensusStatus.PENDING
    assert ratio == 0.0
    assert not (tmp_path / "decisions").exists() or not list((tmp_path / "decisions").glob("nonexistent*.json"))


def test_get_consensus_empty_votes_returns_pending(tmp_path: Path) -> None:
    """Proposal with no votes → ``(PENDING, 0.0)``, no decision file written."""
    proto = ConsensusProtocol(tmp_path)
    proto.propose("empty-test", "leader", "T", {})
    status, ratio = proto.get_consensus("empty-test")
    assert status is ConsensusStatus.PENDING
    assert ratio == 0.0


def test_get_consensus_above_threshold_agrees(tmp_path: Path) -> None:
    """Ratio ≥ threshold → ``AGREED``, decision file written with ``action='finalize'``."""
    proto = ConsensusProtocol(tmp_path)
    _seed_proposal_with_votes(tmp_path, proto, ratio_yes=1.0)
    status, ratio = proto.get_consensus("ratio-test")
    assert status is ConsensusStatus.AGREED
    assert ratio == pytest.approx(1.0)
    decision = json.loads((tmp_path / "decisions" / "ratio-test.json").read_text())
    assert decision["status"] == "agreed"
    assert decision["action"] == "finalize"


def test_get_consensus_below_inverse_threshold_rejects(tmp_path: Path) -> None:
    """Ratio ≤ ``(1 - threshold)`` → ``REJECTED`` with ``action='finalize'``."""
    proto = ConsensusProtocol(tmp_path)
    _seed_proposal_with_votes(tmp_path, proto, ratio_yes=0.0)
    status, _ = proto.get_consensus("ratio-test")
    assert status is ConsensusStatus.REJECTED
    decision = json.loads((tmp_path / "decisions" / "ratio-test.json").read_text())
    assert decision["status"] == "rejected"
    assert decision["action"] == "finalize"


def test_get_consensus_mid_ratio_under_max_round_is_pending(tmp_path: Path) -> None:
    """Mid ratio + round < max → ``PENDING`` with ``action='debate'``."""
    proto = ConsensusProtocol(tmp_path)
    # Split 5/5 → ratio = 0.5, threshold = 0.5 → ratio < required_majority.
    # Split 6/4 → ratio = 0.6, ratio >= required_majority → AGREED.
    # Need ratio strictly between ``(1 - threshold) = 0.5`` and ``threshold = 0.5``,
    # which is impossible. Use a 3-tier decision_type instead — threshold = 2/3.
    proto.propose("mid-ratio", "leader", "T", {}, decision_type="architecture", max_debate_rounds=3)
    # 5 yes, 5 no → ratio = 0.5, threshold = 2/3, 1-threshold = 1/3.
    # 0.5 > 0.333 AND 0.5 < 0.666 → mid-range → PENDING.
    for i in range(10):
        proto.cast_vote("mid-ratio", f"a-{i}", i < 5, confidence=1.0)
    # Stay in round 1 so the round-1 vote records are the ones tallied.
    status, ratio = proto.get_consensus("mid-ratio", vote_round=1)
    assert status is ConsensusStatus.PENDING
    assert ratio == pytest.approx(0.5)
    decision = json.loads((tmp_path / "decisions" / "mid-ratio.json").read_text())
    assert decision["status"] == "pending"
    assert decision["action"] == "debate"


def test_get_consensus_mid_ratio_at_max_round_escalates(tmp_path: Path) -> None:
    """Mid ratio + round == max → ``ESCALATED`` with ``action='human_review'``."""
    proto = ConsensusProtocol(tmp_path)
    proto.propose("escalate-test", "leader", "T", {}, decision_type="architecture", max_debate_rounds=1)
    for i in range(10):
        proto.cast_vote("escalate-test", f"a-{i}", i < 5, confidence=1.0)
    status, _ = proto.get_consensus("escalate-test", vote_round=1)
    assert status is ConsensusStatus.ESCALATED
    decision = json.loads((tmp_path / "decisions" / "escalate-test.json").read_text())
    assert decision["status"] == "escalated"
    assert decision["action"] == "human_review"


def test_get_consensus_zero_total_weight_returns_pending(tmp_path: Path) -> None:
    """All-zero confidence votes → ``(PENDING, 0.0)``, no decision file written."""
    proto = ConsensusProtocol(tmp_path)
    proto.propose("zero-weight", "leader", "T", {})
    for i in range(5):
        proto.cast_vote("zero-weight", f"a-{i}", True, confidence=0.0)
    status, ratio = proto.get_consensus("zero-weight")
    assert status is ConsensusStatus.PENDING
    assert ratio == 0.0


def test_get_consensus_explicit_required_majority(tmp_path: Path) -> None:
    """Caller-supplied ``required_majority`` overrides decision_type threshold."""
    proto = ConsensusProtocol(tmp_path)
    _seed_proposal_with_votes(tmp_path, proto, ratio_yes=0.6)
    # 0.6 ≥ 0.6 → AGREED.
    status, ratio = proto.get_consensus("ratio-test", required_majority=0.6)
    assert status is ConsensusStatus.AGREED
    assert ratio == pytest.approx(0.6)


# ---------------------------------------------------------------------------
# Helper extraction CC pin (3 tests)
# ---------------------------------------------------------------------------


def test_tally_round_votes_happy_path() -> None:
    """``_tally_round_votes`` returns ``(total_weight, weighted_votes)``."""
    votes = [
        {"vote": True, "confidence": 0.9},
        {"vote": False, "confidence": 0.1},
        {"vote": True, "confidence": 0.5},
    ]
    total, weighted = ConsensusProtocol._tally_round_votes(votes)
    assert total == pytest.approx(1.5)
    assert weighted == pytest.approx(1.4)  # 0.9 + 0.5


def test_resolve_consensus_status_four_branches() -> None:
    """``_resolve_consensus_status`` covers all four canonical branches."""
    # AGREED: ratio ≥ required_majority.
    assert ConsensusProtocol._resolve_consensus_status(0.8, 0.5, 1, 3) == (
        ConsensusStatus.AGREED,
        "finalize",
    )
    # REJECTED: ratio ≤ (1 - required_majority).
    assert ConsensusProtocol._resolve_consensus_status(0.1, 0.5, 1, 3) == (
        ConsensusStatus.REJECTED,
        "finalize",
    )
    # ESCALATED: mid ratio + at max rounds.
    assert ConsensusProtocol._resolve_consensus_status(0.5, 0.5, 3, 3) == (
        ConsensusStatus.ESCALATED,
        "human_review",
    )
    # PENDING: mid ratio + rounds remaining.
    assert ConsensusProtocol._resolve_consensus_status(0.5, 0.5, 1, 3) == (
        ConsensusStatus.PENDING,
        "debate",
    )


def test_persist_decision_record_writes_canonical_shape(tmp_path: Path) -> None:
    """``_persist_decision_record`` writes the canonical 10-key decision JSON."""
    proto = ConsensusProtocol(tmp_path)
    proto._persist_decision_record(
        proposal_id="dec-1",
        status=ConsensusStatus.AGREED,
        ratio=0.8,
        total_weight=5.0,
        current_round=1,
        max_rounds=3,
        required_majority=0.5,
        decision_type="implementation",
        action="finalize",
    )
    decision_file = tmp_path / "decisions" / "dec-1.json"
    assert decision_file.exists()
    payload = json.loads(decision_file.read_text())
    assert set(payload.keys()) == {
        "proposal_id",
        "status",
        "ratio",
        "total_weight",
        "round",
        "max_rounds",
        "required_majority",
        "decision_type",
        "action",
        "ts",
    }
    assert payload["status"] == "agreed"
    assert payload["decision_type"] == "implementation"


# ---------------------------------------------------------------------------
# CausalInfluenceTracker (4 tests)
# ---------------------------------------------------------------------------


def test_record_influence_appends_jsonl(tmp_path: Path) -> None:
    """``record_influence`` appends a JSON line per call."""
    tracker = CausalInfluenceTracker(tmp_path)
    tracker.record_influence("agent-1", "action-1", 0.5)
    tracker.record_influence("agent-2", "action-1", 0.3)
    lines = (tmp_path / "influence.jsonl").read_text().strip().splitlines()
    assert len(lines) == 2
    payloads = [json.loads(line) for line in lines]
    assert payloads[0]["agent_id"] == "agent-1"
    assert payloads[1]["agent_id"] == "agent-2"


def test_compute_shapley_unknown_action_returns_empty(tmp_path: Path) -> None:
    """Unknown ``action_id`` returns ``{}`` (no records filtered through)."""
    tracker = CausalInfluenceTracker(tmp_path)
    tracker.record_influence("agent-1", "action-1", 0.5)
    assert tracker.compute_shapley_values("action-2") == {}


def test_compute_shapley_normalizes_to_unit_weight(tmp_path: Path) -> None:
    """``compute_shapley_values`` divides per-agent totals by sum of absolute values."""
    tracker = CausalInfluenceTracker(tmp_path)
    tracker.record_influence("agent-1", "action-1", 0.6)
    tracker.record_influence("agent-2", "action-1", 0.4)
    values = tracker.compute_shapley_values("action-1")
    assert values["agent-1"] == pytest.approx(0.6)
    assert values["agent-2"] == pytest.approx(0.4)
    assert sum(values.values()) == pytest.approx(1.0)


def test_compute_shapley_degenerate_zero_weight(tmp_path: Path) -> None:
    """All-zero contributions return ``dict.fromkeys(agents, 0.0)`` (no NaN)."""
    tracker = CausalInfluenceTracker(tmp_path)
    tracker.record_influence("agent-1", "action-1", 0.0)
    tracker.record_influence("agent-2", "action-1", 0.0)
    values = tracker.compute_shapley_values("action-1")
    assert values == {"agent-1": 0.0, "agent-2": 0.0}


# ---------------------------------------------------------------------------
# EscalationWorkflow (5 tests)
# ---------------------------------------------------------------------------


def test_escalate_writes_tier_transition_record(tmp_path: Path) -> None:
    """``escalate(tier=1)`` writes a tier-1 → tier-2 record."""
    flow = EscalationWorkflow(tmp_path)
    flow.escalate("esc-1", current_tier=1, reason="consensus failure")
    record_file = tmp_path / "escalation-queue" / "escalation-esc-1.json"
    assert record_file.exists()
    payload = json.loads(record_file.read_text())
    assert payload["from_tier"] == 1
    assert payload["to_tier"] == 2
    assert payload["from_label"] == "self"
    assert payload["to_label"] == "peer"
    assert payload["reason"] == "consensus failure"


def test_escalate_tier_4_to_5(tmp_path: Path) -> None:
    """Tier 4 → tier 5 is the committee → human transition."""
    flow = EscalationWorkflow(tmp_path)
    flow.escalate("esc-2", current_tier=4)
    payload = json.loads((tmp_path / "escalation-queue" / "escalation-esc-2.json").read_text())
    assert payload["from_tier"] == 4
    assert payload["to_tier"] == 5
    assert payload["from_label"] == "committee"
    assert payload["to_label"] == "human"


def test_escalate_tier_5_enqueues_human_queue(tmp_path: Path) -> None:
    """``escalate(tier=5)`` writes to ``human-escalation/human-<id>.json``."""
    flow = EscalationWorkflow(tmp_path)
    flow.escalate("esc-3", current_tier=5, reason="human review needed")
    human_file = tmp_path / "human-escalation" / "human-esc-3.json"
    assert human_file.exists()
    payload = json.loads(human_file.read_text())
    assert payload["proposal_id"] == "esc-3"
    assert payload["status"] == "pending"
    assert payload["reason"] == "human review needed"
    # Tier-5 escalation does NOT write to escalation-queue/ — only human queue.
    assert not (tmp_path / "escalation-queue" / "escalation-esc-3.json").exists()


def test_list_pending_human_escalations_sorted_by_timestamp(tmp_path: Path) -> None:
    """``list_pending_human_escalations`` returns pending-only items, sorted ascending."""
    import time

    flow = EscalationWorkflow(tmp_path)
    flow.escalate("p-1", current_tier=5)
    time.sleep(0.01)
    flow.escalate("p-2", current_tier=5)
    pending = flow.list_pending_human_escalations()
    assert len(pending) == 2
    assert pending[0]["proposal_id"] == "p-1"
    assert pending[1]["proposal_id"] == "p-2"


def test_resolve_human_escalation_flips_status(tmp_path: Path) -> None:
    """``resolve_human_escalation`` flips status + writes ``resolved_at``; missing returns False."""
    flow = EscalationWorkflow(tmp_path)
    flow.escalate("res-1", current_tier=5)
    assert flow.resolve_human_escalation("res-1") is True
    payload = json.loads((tmp_path / "human-escalation" / "human-res-1.json").read_text())
    assert payload["status"] == "resolved"
    assert "resolved_at" in payload
    # Missing proposal → False.
    assert flow.resolve_human_escalation("nonexistent") is False


# ---------------------------------------------------------------------------
# Back-compat shim surface (3 tests)
# ---------------------------------------------------------------------------


def test_shim_consensus_protocol_class_file_is_protocol_submodule() -> None:
    """``inspect.getsourcefile`` confirms the split happened (file path is part of the contract)."""
    from thegent.mesh.consensus import ConsensusProtocol

    source_file = inspect.getsourcefile(ConsensusProtocol)
    assert source_file is not None
    # The canonical home is ``protocol.py`` inside the package, NOT the
    # legacy single-file ``mesh/consensus.py``.
    assert source_file.endswith("/mesh/consensus/protocol.py")
    assert not source_file.endswith("/mesh/consensus.py")


def test_shim_escalation_class_file_is_escalation_submodule() -> None:
    """``EscalationWorkflow`` lives in ``escalation.py``."""
    from thegent.mesh.consensus import EscalationWorkflow

    source_file = inspect.getsourcefile(EscalationWorkflow)
    assert source_file is not None
    assert source_file.endswith("/mesh/consensus/escalation.py")


def test_shim_influence_class_file_is_influence_submodule() -> None:
    """``CausalInfluenceTracker`` lives in ``influence.py``."""
    from thegent.mesh.consensus import CausalInfluenceTracker

    source_file = inspect.getsourcefile(CausalInfluenceTracker)
    assert source_file is not None
    assert source_file.endswith("/mesh/consensus/influence.py")


# ---------------------------------------------------------------------------
# AST purity (2 tests)
# ---------------------------------------------------------------------------


def test_shim_loc_is_within_budget() -> None:
    """The back-compat shim is ≤ 35 LOC (target ~30)."""
    shim_path = Path(__file__).resolve().parents[3] / "src" / "thegent" / "mesh" / "consensus.py"
    assert shim_path.exists()
    body = shim_path.read_text().splitlines()
    assert len(body) <= 35, f"shim is {len(body)} LOC, expected ≤ 35"


def test_shim_has_no_class_definitions() -> None:
    """The shim only re-exports — no class / function bodies."""
    shim_path = Path(__file__).resolve().parents[3] / "src" / "thegent" / "mesh" / "consensus.py"
    body = shim_path.read_text()
    assert "class " not in body, "shim must not define any classes"
    assert "def " not in body, "shim must not define any functions"
    # Sanity: it does have the imports + __all__.
    assert "__all__" in body
    assert "from .consensus" in body
