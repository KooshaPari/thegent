"""FederatedPolicyEngine: scope-aware policy registry for governance.

Traces to: FR-GOV-001 (policy federation), FR-GOV-002 (scope precedence)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class PolicyScope(Enum):
    """Hierarchy level of a policy rule. Higher numeric value = higher authority."""

    LOCAL = 1
    REGIONAL = 2
    GLOBAL = 3


@dataclass(order=True)
class PolicyRule:
    """A single governance rule with scope and evaluation metadata.

    Attributes:
        rule_id: Unique identifier for the rule.
        scope: Authority level (LOCAL < REGIONAL < GLOBAL).
        condition: Key expected in the evaluation context (e.g. "cost_exceeded").
        action: Action to take when condition matches (e.g. "deny", "alert").
        priority: Tie-breaker within the same scope; lower number = higher priority.
    """

    # priority is first so dataclass ordering uses it as the primary sort key
    priority: int
    rule_id: str = field(compare=False)
    scope: PolicyScope = field(compare=False)
    condition: str = field(compare=False)
    action: str = field(compare=False)

    @classmethod
    def create(
        cls,
        rule_id: str,
        scope: PolicyScope,
        condition: str,
        action: str,
        priority: int,
    ) -> PolicyRule:
        """Named constructor matching the canonical field order in the task spec."""
        return cls(
            priority=priority,
            rule_id=rule_id,
            scope=scope,
            condition=condition,
            action=action,
        )


class FederatedPolicyEngine:
    """Registry and evaluator for scoped governance policy rules.

    Rules are stored by rule_id.  On evaluate() the engine returns all rules
    whose ``condition`` key is present (and truthy) in *context*, sorted by
    ascending priority (lower number = checked/applied first).

    Scope precedence (GLOBAL > REGIONAL > LOCAL) is enforced during merge():
    when two engines have a rule with the same rule_id, the rule belonging to
    the higher scope wins.
    """

    def __init__(self) -> None:
        self._rules: dict[str, PolicyRule] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def register(self, rule: PolicyRule) -> None:
        """Add *rule* to the registry, replacing any existing rule with the same id."""
        self._rules[rule.rule_id] = rule

    def load_from_file(self, path: Path) -> None:
        """Load rules from a JSON file.

        Expected format::

            [
              {
                "rule_id": "deny-high-cost",
                "scope": "GLOBAL",
                "condition": "cost_exceeded",
                "action": "deny",
                "priority": 1
              },
              ...
            ]
        """
        raw: list[dict[str, object]] = json.loads(path.read_text(encoding="utf-8"))
        for item in raw:
            rule = PolicyRule.create(
                rule_id=str(item["rule_id"]),
                scope=PolicyScope[str(item["scope"]).upper()],
                condition=str(item["condition"]),
                action=str(item["action"]),
                priority=int(str(item["priority"])),
            )
            self.register(rule)

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(self, context: dict[str, object]) -> list[PolicyRule]:
        """Return matching rules sorted by ascending priority.

        A rule matches when its ``condition`` key exists and is truthy in *context*.
        """
        matched = [
            rule
            for rule in self._rules.values()
            if context.get(rule.condition)
        ]
        return sorted(matched, key=lambda r: r.priority)

    # ------------------------------------------------------------------
    # Federation
    # ------------------------------------------------------------------

    def merge(self, other: FederatedPolicyEngine) -> FederatedPolicyEngine:
        """Return a new engine combining rules from *self* and *other*.

        Conflict resolution: when both engines carry a rule with the same
        rule_id, the rule with the **higher** PolicyScope wins (GLOBAL beats
        REGIONAL beats LOCAL).  On a scope tie the rule from *self* is kept
        (self takes precedence).
        """
        merged = FederatedPolicyEngine()
        all_ids = set(self._rules) | set(other._rules)
        for rid in all_ids:
            self_rule = self._rules.get(rid)
            other_rule = other._rules.get(rid)
            if self_rule is None and other_rule is not None:
                merged.register(other_rule)
            elif self_rule is not None and other_rule is None:
                merged.register(self_rule)
            elif self_rule is not None and other_rule is not None:
                # Higher scope wins; tie goes to self
                if other_rule.scope.value > self_rule.scope.value:
                    merged.register(other_rule)
                else:
                    merged.register(self_rule)
        return merged

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._rules)

    def __repr__(self) -> str:
        return f"FederatedPolicyEngine(rules={len(self._rules)})"
