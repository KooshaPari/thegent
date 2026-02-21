"""WL-083: ResultAggregator — Aggregate inter-agent messages with cost tracking.

Aggregates InterAgentMessage objects produced by agents and produces an
AggregationResult summary with total count, type breakdown, success/failure
tracking, token sum per wave, global budget overrun detection, and structured
output dict keyed by node_id.

# @trace WL-083
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AggregationResult(BaseModel):
    """Structured result from aggregating inter-agent messages.

    Attributes:
        total: Total count of all messages.
        by_type: Dictionary mapping message_type to count.
        results: List of result messages (message_type == "result").
        errors: List of error messages (message_type == "error").
        passed: True when no error messages present.
        by_node: Dictionary mapping node_id to aggregated results.
        tokens_by_wave: Dictionary mapping wave_id to total token count.
        budget_overrun: True if global budget was exceeded.
        total_tokens: Total tokens across all waves.
    """

    total: int = Field(default=0)
    by_type: dict[str, int] = Field(default_factory=dict)
    results: list[Any] = Field(default_factory=list)
    errors: list[Any] = Field(default_factory=list)
    passed: bool = Field(default=True)
    by_node: dict[str, dict[str, Any]] = Field(default_factory=dict)
    tokens_by_wave: dict[str, int] = Field(default_factory=dict)
    budget_overrun: bool = Field(default=False)
    total_tokens: int = Field(default=0)


class GlobalBudgetExceededError(RuntimeError):
    """Raised when total token usage exceeds the global budget.

    Attributes:
        budget: The configured global token budget.
        used: The total token count that triggered the error.
        wave_id: The wave in which the budget was exceeded.
    """

    def __init__(self, *, budget: int, used: int, wave_id: str | None = None) -> None:
        self.budget = budget
        self.used = used
        self.wave_id = wave_id
        msg = f"Global budget exceeded: used={used}, budget={budget}"
        if wave_id:
            msg += f" (wave: {wave_id})"
        super().__init__(msg)


class ResultAggregator:
    """Collect InterAgentMessage objects and produce aggregated results.

    Supports:
    - Token sum across waves
    - Partial failure tracking
    - Global budget overrun detection
    - Structured output dict keyed by node_id

    Usage::

        agg = ResultAggregator(global_budget=100000)
        for msg in messages:
            agg.add(msg, wave_id="wave-1", node_id=msg.sender_id)
        result = agg.aggregate()

    # @trace WL-083
    """

    def __init__(
        self,
        global_budget: int | None = None,
        tokens_per_message: int = 0,
    ) -> None:
        """Initialize the ResultAggregator.

        Args:
            global_budget: Optional global token budget. If provided and total
                tokens exceed this, GlobalBudgetExceededError is raised on aggregate().
            tokens_per_message: Default tokens to count per message for budget tracking.
        """
        self._messages: list[Any] = []
        self._global_budget = global_budget
        self._tokens_per_message = tokens_per_message

    def add(
        self,
        message: Any,
        wave_id: str | None = None,
        node_id: str | None = None,
        tokens: int | None = None,
    ) -> None:
        """Append an InterAgentMessage for later aggregation.

        Args:
            message: An InterAgentMessage instance.
            wave_id: Optional wave identifier for token tracking.
            node_id: Optional node identifier for by-node aggregation.
            tokens: Optional token count for this message. Defaults to tokens_per_message.

        # @trace WL-083
        """
        self._messages.append(
            {
                "message": message,
                "wave_id": wave_id,
                "node_id": node_id,
                "tokens": tokens if tokens is not None else self._tokens_per_message,
            }
        )

    def aggregate(self) -> dict[str, Any]:
        """Produce an AggregationResult from all stored messages.

        Returns:
            Dictionary with total, by_type, results, errors, passed, by_node,
            tokens_by_wave, budget_overrun, and total_tokens.

        Raises:
            GlobalBudgetExceededError: If global_budget was set and total tokens exceed it.

        # @trace WL-083
        """
        total = len(self._messages)
        by_type: dict[str, int] = {}
        results: list[Any] = []
        errors: list[Any] = []
        by_node: dict[str, dict[str, Any]] = {}
        tokens_by_wave: dict[str, int] = {}
        total_tokens = 0
        has_errors = False

        for item in self._messages:
            msg = item["message"]
            wave_id = item["wave_id"]
            node_id = item["node_id"]
            tokens = item["tokens"]

            # Count by type
            msg_type = msg.message_type
            by_type[msg_type] = by_type.get(msg_type, 0) + 1

            # Collect results and errors
            if msg_type == "result":
                results.append(msg)
            elif msg_type == "error":
                errors.append(msg)
                has_errors = True

            # Track by node_id
            if node_id:
                if node_id not in by_node:
                    by_node[node_id] = {
                        "total": 0,
                        "results": [],
                        "errors": [],
                        "passed": True,
                    }
                by_node[node_id]["total"] += 1
                if msg_type == "result":
                    by_node[node_id]["results"].append(msg)
                elif msg_type == "error":
                    by_node[node_id]["errors"].append(msg)
                    by_node[node_id]["passed"] = False

            # Track tokens by wave
            if wave_id and tokens:
                tokens_by_wave[wave_id] = tokens_by_wave.get(wave_id, 0) + tokens
                total_tokens += tokens

        # Check global budget
        budget_overrun = False
        if self._global_budget is not None and total_tokens > self._global_budget:
            budget_overrun = True
            # Find the wave that pushed us over
            exceeded_wave: str | None = None
            running_total = 0
            for wave, tokens in tokens_by_wave.items():
                running_total += tokens
                if running_total > self._global_budget:
                    exceeded_wave = wave
                    break
            raise GlobalBudgetExceededError(
                budget=self._global_budget,
                used=total_tokens,
                wave_id=exceeded_wave,
            )

        return {
            "total": total,
            "by_type": by_type,
            "results": results,
            "errors": errors,
            "passed": not has_errors,
            "by_node": by_node,
            "tokens_by_wave": tokens_by_wave,
            "budget_overrun": budget_overrun,
            "total_tokens": total_tokens,
        }

    def clear(self) -> None:
        """Reset all internal state.

        # @trace WL-083
        """
        self._messages.clear()

    def summary(self) -> str:
        """Return a human-readable summary string.

        # @trace WL-083
        """
        if not self._messages:
            return "ResultAggregator: 0 messages, passed=True"

        result = self.aggregate()
        total = result["total"]
        passed = result["passed"]
        by_type = result["by_type"]
        total_tokens = result["total_tokens"]

        status = "passed" if passed else "failed"
        type_summary = ", ".join(f"{k}={v}" for k, v in by_type.items())
        tokens_summary = f", tokens={total_tokens}" if total_tokens > 0 else ""

        return f"ResultAggregator: {total} messages ({type_summary}), {status}{tokens_summary}"


__all__ = [
    "AggregationResult",
    "GlobalBudgetExceededError",
    "ResultAggregator",
]
