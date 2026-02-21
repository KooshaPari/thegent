"""WL-086: BudgetTracker — Per-Node Token Budget Enforcement.

Wraps JSONL output from CodexProxyRunner / DirectAgentRunner to parse token
usage and enforce ``budget_tokens`` per node.  Raises :class:`BudgetExceededError`
(fail-loud, no silent continuation) when the accumulated token count for a node
exceeds the budget declared in ``node.metadata["budget_tokens"]``.

Supports two constructor patterns:
1. BudgetTracker(budgets={"node_id": 1000}) - dict-based
2. BudgetTracker(plan) - OrchestrationPlan-based

# @trace FR-ORC-086
# @trace WL-086
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from thegent.orchestration.plan import OrchestrationPlan

_BUDGET_TOKENS_KEY = "budget_tokens"


class BudgetExceededError(RuntimeError):
    """Raised when a node's accumulated token usage exceeds its budget.

    Attributes:
        node_id: ID of the plan node that exceeded its budget.
        budget: The token budget allocated to the node.
        actual: The total tokens used (including the latest call).
        used: Alias for actual (for backward compatibility).

    # @trace FR-ORC-086
    # @trace WL-086
    """

    def __init__(self, node_id: str, budget: int, actual: int = 0, *, used: int = 0) -> None:
        # Accept either positional `actual` or keyword `used`; keyword wins
        resolved = used if used != 0 else actual
        self.node_id = node_id
        self.budget = budget
        self.actual = resolved
        self.used = resolved
        super().__init__(
            f"Node '{node_id}' exceeded token budget: used {resolved} tokens, budget {budget} tokens "
            f"(over by {resolved - budget})"
        )


class BudgetTracker:
    """Per-node token budget enforcement.

    Supports two constructor patterns:
    1. ``BudgetTracker(budgets={"node_id": 1000})`` - dict-based
    2. ``BudgetTracker(plan)`` - OrchestrationPlan-based

    Accumulates token usage per node and raises :class:`BudgetExceededError`
    immediately when a node's budget is exceeded.  There is no silent degradation
    or continuation — callers receive a hard exception.

    # @trace FR-ORC-086
    # @trace WL-086
    """

    def __init__(
        self,
        plan_or_budgets: "OrchestrationPlan | dict[str, int] | None" = None,
        *,
        budgets: "dict[str, int] | None" = None,
    ) -> None:
        # Support BudgetTracker(budgets={...}) keyword form
        if budgets is not None:
            if plan_or_budgets is not None:
                raise TypeError("Pass either plan_or_budgets or budgets=, not both")
            plan_or_budgets = budgets
        if plan_or_budgets is None:
            raise TypeError("BudgetTracker requires plan_or_budgets or budgets= argument")
        # Support both dict-based and OrchestrationPlan-based constructors
        if isinstance(plan_or_budgets, dict):
            self._budgets: dict[str, int] = dict(plan_or_budgets)
            self._plan = None
            self._usage: dict[str, int] = dict.fromkeys(plan_or_budgets, 0)
        else:
            # OrchestrationPlan-based
            self._plan = plan_or_budgets
            self._budgets = {}
            self._usage = {}
            # Extract budgets from nodes that have budget_tokens in metadata
            for node in plan_or_budgets.nodes:
                if _BUDGET_TOKENS_KEY in node.metadata:
                    budget = node.metadata[_BUDGET_TOKENS_KEY]
                    if not isinstance(budget, int):
                        raise TypeError(
                            f"Node '{node.id}' budget_tokens must be int, got {type(budget).__name__!r}"
                        )
                    self._budgets[node.id] = budget
                    self._usage[node.id] = 0

    def _get_budget(self, node_id: str) -> int:
        """Get budget for a node, checking both dict and plan modes."""
        if self._plan is not None:
            node = self._plan.get_node(node_id)
            if node is None:
                raise KeyError(f"Node '{node_id}' not found in plan '{self._plan.id}'")
            budget = node.metadata.get(_BUDGET_TOKENS_KEY)
            if budget is None:
                raise KeyError(f"Node '{node_id}' has no budget_tokens in plan '{self._plan.id}'")
            return budget
        # Dict mode
        return self._budgets[node_id]

    def check(self, node_id: str, tokens: int) -> None:
        """Check whether consuming tokens would exceed the node's budget.

        This is a point-in-time check against the budget only — it does NOT
        consider cumulative usage. Use record() to enforce cumulative limits.

        Args:
            node_id: ID of the plan node to check.
            tokens: The token count to check against the budget.

        Raises:
            KeyError: If node_id is not in the configured budgets.
            BudgetExceededError: If tokens > budget for node_id.

        # @trace FR-ORC-086
        """
        budget = self._get_budget(node_id)
        if tokens > budget:
            raise BudgetExceededError(node_id=node_id, budget=budget, actual=tokens)

    def record(self, node_id: str, tokens: int) -> None:
        """Record token usage for a node, raising if cumulative exceeds budget.

        Args:
            node_id: ID of the plan node to record usage for.
            tokens: Number of tokens consumed in this call.

        Raises:
            KeyError: If node_id is not in the configured budgets.
            BudgetExceededError: If cumulative usage after this call > budget.

        # @trace FR-ORC-086
        """
        budget = self._get_budget(node_id)

        # Ensure node is tracked
        if node_id not in self._usage:
            self._usage[node_id] = 0

        new_total = self._usage[node_id] + tokens
        if new_total > budget:
            raise BudgetExceededError(node_id=node_id, budget=budget, actual=new_total)
        self._usage[node_id] = new_total

    def usage(self, node_id: str) -> int:
        """Return cumulative token usage recorded for node_id.

        Args:
            node_id: ID of the plan node to query.

        Raises:
            KeyError: If node_id is not in the configured budgets.

        Returns:
            Total tokens recorded so far for the node.

        # @trace FR-ORC-086
        """
        if node_id not in self._usage:
            raise KeyError(node_id)
        return self._usage[node_id]

    def remaining(self, node_id: str) -> int:
        """Return tokens remaining in the budget for node_id.

        Args:
            node_id: ID of the plan node to query.

        Raises:
            KeyError: If node_id is not in the configured budgets.

        Returns:
            Budget minus cumulative usage for the node.

        # @trace FR-ORC-086
        """
        budget = self._get_budget(node_id)
        return budget - self._usage.get(node_id, 0)

    def reset(self, node_id: str) -> None:
        """Reset cumulative usage to zero for node_id.

        Args:
            node_id: ID of the plan node to reset.

        Raises:
            KeyError: If node_id is not in the configured budgets.

        # @trace FR-ORC-086
        """
        if node_id not in self._usage:
            raise KeyError(node_id)
        self._usage[node_id] = 0

    # --------------------------------------------------------------------------
    # WL-086 specific methods (also work in dict mode)
    # --------------------------------------------------------------------------

    def track(self, node_id: str, tokens_used: int) -> None:
        """Accumulate tokens_used for node_id and enforce the budget.

        Alias for record() - accumulates usage and raises if budget exceeded.

        Args:
            node_id: ID of the plan node to track usage for.
            tokens_used: Number of tokens consumed in this call.

        Raises:
            KeyError: If node_id does not exist in the configured budgets.
            BudgetExceededError: If the accumulated token usage exceeds the
                node's budget.

        # @trace WL-086
        """
        self.record(node_id, tokens_used)

    def get_usage(self, node_id: str) -> int:
        """Return accumulated tokens used for node_id.

        Alias for usage().

        Args:
            node_id: ID of the plan node to query.

        Raises:
            KeyError: If node_id does not exist in the configured budgets.

        # @trace WL-086
        """
        return self.usage(node_id)

    def reset_usage(self, node_id: str) -> None:
        """Reset accumulated usage for node_id to zero.

        Alias for reset().

        Args:
            node_id: ID of the plan node to reset.

        Raises:
            KeyError: If node_id does not exist in the configured budgets.

        # @trace WL-086
        """
        self.reset(node_id)

    @staticmethod
    def parse_tokens_from_result(stdout: str) -> int:
        """Parse total token count from agent JSONL stdout.

        Understands both OpenAI-style ``prompt_tokens + completion_tokens`` and
        the ``total_tokens`` fallback.  Non-JSON lines are silently skipped.

        Args:
            stdout: Raw JSONL output from an agent run.

        Returns:
            Total tokens parsed from all ``"usage"`` lines; ``0`` if none found.

        # @trace FR-ORC-086
        # @trace WL-086
        """
        total = 0
        for raw_line in stdout.splitlines():
            line = raw_line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            usage = obj.get("usage")
            if not isinstance(usage, dict):
                continue
            prompt = usage.get("prompt_tokens", 0)
            completion = usage.get("completion_tokens", 0)
            if isinstance(prompt, int) and isinstance(completion, int) and (prompt or completion):
                total += prompt + completion
            else:
                total_tok = usage.get("total_tokens", 0)
                if isinstance(total_tok, int):
                    total += total_tok
        return total

    def track_result_stdout(self, node_id: str, stdout: str) -> int:
        """Parse tokens from *stdout* and track them for *node_id*.

        Args:
            node_id: ID of the plan node to track.
            stdout: Raw JSONL stdout from an agent run.

        Returns:
            Number of tokens parsed from *stdout* in this call.

        Raises:
            KeyError: If *node_id* does not exist in the plan.
            BudgetExceededError: If the accumulated token usage exceeds the
                node's budget.

        # @trace FR-ORC-086
        # @trace WL-086
        """
        tokens = BudgetTracker.parse_tokens_from_result(stdout)
        self.track(node_id, tokens)
        return tokens

    @property
    def all_usage(self) -> dict[str, int]:
        """Snapshot of all accumulated usage as ``{node_id: tokens_used}``.

        # @trace FR-ORC-086
        # @trace WL-086
        """
        return dict(self._usage)


__all__ = [
    "BudgetExceededError",
    "BudgetTracker",
]
