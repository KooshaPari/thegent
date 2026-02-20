"""Tests for FederatedPolicyEngine.

Traces to: FR-GOV-001 (policy federation), FR-GOV-002 (scope precedence)
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from thegent.governance.federated_policy import (
    FederatedPolicyEngine,
    PolicyRule,
    PolicyScope,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _rule(
    rule_id: str = "r1",
    scope: PolicyScope = PolicyScope.LOCAL,
    condition: str = "flag",
    action: str = "deny",
    priority: int = 10,
) -> PolicyRule:
    return PolicyRule.create(
        rule_id=rule_id,
        scope=scope,
        condition=condition,
        action=action,
        priority=priority,
    )


# ---------------------------------------------------------------------------
# register
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_register_adds_rule() -> None:
    """FR-GOV-001: register() stores a rule retrievable via evaluate()."""
    engine = FederatedPolicyEngine()
    engine.register(_rule("r1", condition="active"))
    assert len(engine) == 1


@pytest.mark.unit
def test_register_replaces_existing_rule() -> None:
    """FR-GOV-001: registering same rule_id replaces the previous entry."""
    engine = FederatedPolicyEngine()
    engine.register(_rule("r1", action="deny"))
    engine.register(_rule("r1", action="alert"))
    assert len(engine) == 1
    results = engine.evaluate({"flag": True})
    assert results[0].action == "alert"


# ---------------------------------------------------------------------------
# evaluate
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_evaluate_returns_matching_rules() -> None:
    """FR-GOV-001: evaluate() returns only rules whose condition is truthy in context."""
    engine = FederatedPolicyEngine()
    engine.register(_rule("r1", condition="cost_exceeded"))
    engine.register(_rule("r2", condition="sla_breached"))
    matched = engine.evaluate({"cost_exceeded": True})
    assert len(matched) == 1
    assert matched[0].rule_id == "r1"


@pytest.mark.unit
def test_evaluate_returns_empty_when_no_match() -> None:
    """FR-GOV-001: evaluate() returns [] when no conditions are met."""
    engine = FederatedPolicyEngine()
    engine.register(_rule("r1", condition="cost_exceeded"))
    assert engine.evaluate({}) == []
    assert engine.evaluate({"cost_exceeded": False}) == []


@pytest.mark.unit
def test_evaluate_sorted_by_priority_ascending() -> None:
    """FR-GOV-001: evaluate() returns rules ordered by ascending priority."""
    engine = FederatedPolicyEngine()
    engine.register(_rule("r-high", condition="flag", priority=5))
    engine.register(_rule("r-low", condition="flag", priority=1))
    engine.register(_rule("r-mid", condition="flag", priority=3))
    result = engine.evaluate({"flag": True})
    priorities = [r.priority for r in result]
    assert priorities == sorted(priorities)
    assert result[0].rule_id == "r-low"


@pytest.mark.unit
def test_evaluate_multiple_conditions() -> None:
    """FR-GOV-001: evaluate() matches multiple rules when multiple conditions are met."""
    engine = FederatedPolicyEngine()
    engine.register(_rule("r1", condition="cost_exceeded", priority=1))
    engine.register(_rule("r2", condition="sla_breached", priority=2))
    engine.register(_rule("r3", condition="quota_exceeded", priority=3))
    ctx = {"cost_exceeded": True, "sla_breached": True}
    matched = engine.evaluate(ctx)
    assert len(matched) == 2
    assert {r.rule_id for r in matched} == {"r1", "r2"}


# ---------------------------------------------------------------------------
# merge — scope precedence
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_merge_non_conflicting_rules_are_unioned() -> None:
    """FR-GOV-002: merge() combines rules that do not share rule_ids."""
    e1 = FederatedPolicyEngine()
    e1.register(_rule("local-rule", scope=PolicyScope.LOCAL))
    e2 = FederatedPolicyEngine()
    e2.register(_rule("global-rule", scope=PolicyScope.GLOBAL))
    merged = e1.merge(e2)
    assert len(merged) == 2


@pytest.mark.unit
def test_merge_global_beats_local_on_conflict() -> None:
    """FR-GOV-002: GLOBAL scope wins over LOCAL when rule_ids conflict."""
    e1 = FederatedPolicyEngine()
    e1.register(_rule("r1", scope=PolicyScope.LOCAL, action="alert"))
    e2 = FederatedPolicyEngine()
    e2.register(_rule("r1", scope=PolicyScope.GLOBAL, action="deny"))
    merged = e1.merge(e2)
    result = merged.evaluate({"flag": True})
    assert len(result) == 1
    assert result[0].scope == PolicyScope.GLOBAL
    assert result[0].action == "deny"


@pytest.mark.unit
def test_merge_global_beats_regional_on_conflict() -> None:
    """FR-GOV-002: GLOBAL scope wins over REGIONAL when rule_ids conflict."""
    e1 = FederatedPolicyEngine()
    e1.register(_rule("r1", scope=PolicyScope.REGIONAL, action="alert"))
    e2 = FederatedPolicyEngine()
    e2.register(_rule("r1", scope=PolicyScope.GLOBAL, action="deny"))
    merged = e1.merge(e2)
    result = merged.evaluate({"flag": True})
    assert result[0].scope == PolicyScope.GLOBAL


@pytest.mark.unit
def test_merge_regional_beats_local_on_conflict() -> None:
    """FR-GOV-002: REGIONAL scope wins over LOCAL when rule_ids conflict."""
    e1 = FederatedPolicyEngine()
    e1.register(_rule("r1", scope=PolicyScope.LOCAL, action="allow"))
    e2 = FederatedPolicyEngine()
    e2.register(_rule("r1", scope=PolicyScope.REGIONAL, action="deny"))
    merged = e1.merge(e2)
    result = merged.evaluate({"flag": True})
    assert result[0].scope == PolicyScope.REGIONAL
    assert result[0].action == "deny"


@pytest.mark.unit
def test_merge_self_wins_on_scope_tie() -> None:
    """FR-GOV-002: on equal scope, self takes precedence over other."""
    e1 = FederatedPolicyEngine()
    e1.register(_rule("r1", scope=PolicyScope.REGIONAL, action="self-action"))
    e2 = FederatedPolicyEngine()
    e2.register(_rule("r1", scope=PolicyScope.REGIONAL, action="other-action"))
    merged = e1.merge(e2)
    result = merged.evaluate({"flag": True})
    assert result[0].action == "self-action"


@pytest.mark.unit
def test_merge_returns_new_engine_leaves_originals_intact() -> None:
    """FR-GOV-002: merge() is non-destructive; originals are unchanged."""
    e1 = FederatedPolicyEngine()
    e1.register(_rule("r1"))
    e2 = FederatedPolicyEngine()
    e2.register(_rule("r2"))
    merged = e1.merge(e2)
    assert len(e1) == 1
    assert len(e2) == 1
    assert len(merged) == 2


# ---------------------------------------------------------------------------
# load_from_file
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_load_from_file_registers_rules() -> None:
    """FR-GOV-001: load_from_file() populates engine from JSON."""
    data = [
        {
            "rule_id": "file-rule-1",
            "scope": "GLOBAL",
            "condition": "cost_exceeded",
            "action": "deny",
            "priority": 1,
        },
        {
            "rule_id": "file-rule-2",
            "scope": "LOCAL",
            "condition": "quota_exceeded",
            "action": "alert",
            "priority": 5,
        },
    ]
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as fh:
        json.dump(data, fh)
        tmp_path = Path(fh.name)

    try:
        engine = FederatedPolicyEngine()
        engine.load_from_file(tmp_path)
        assert len(engine) == 2
        matched = engine.evaluate({"cost_exceeded": True})
        assert len(matched) == 1
        assert matched[0].scope == PolicyScope.GLOBAL
    finally:
        tmp_path.unlink(missing_ok=True)


@pytest.mark.unit
def test_load_from_file_scope_case_insensitive() -> None:
    """FR-GOV-001: scope field in JSON is case-insensitive."""
    data = [{"rule_id": "r1", "scope": "global", "condition": "flag", "action": "deny", "priority": 1}]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as fh:
        json.dump(data, fh)
        tmp_path = Path(fh.name)
    try:
        engine = FederatedPolicyEngine()
        engine.load_from_file(tmp_path)
        result = engine.evaluate({"flag": True})
        assert result[0].scope == PolicyScope.GLOBAL
    finally:
        tmp_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# PolicyScope ordering
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_policy_scope_values_ordered_correctly() -> None:
    """FR-GOV-002: GLOBAL > REGIONAL > LOCAL by numeric value."""
    assert PolicyScope.GLOBAL.value > PolicyScope.REGIONAL.value
    assert PolicyScope.REGIONAL.value > PolicyScope.LOCAL.value
