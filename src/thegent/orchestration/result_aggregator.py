"""ResultAggregator: Merge sub-agent outputs with cost and token tracking.

Aggregates SubAgentResult objects produced by sub-agents and produces an
AggregatedResult summary with total cost, token usage, success/failure
counts, and collected error messages.

# @trace FR-ORC-083
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from thegent.orchestration.protocol import SubAgentResult, SubAgentStatus


class AggregatedResult(BaseModel):
    """Merged summary of multiple SubAgentResult objects.

    Attributes:
        results: All SubAgentResult instances that were aggregated.
        total_cost_usd: Sum of cost_usd from all result metrics.
        total_tokens_used: Sum of tokens_used from all result metrics.
        success_count: Number of results with status COMPLETED.
        failure_count: Number of results with status other than COMPLETED.
        all_passed: True when every result has status COMPLETED.
        errors: Error messages collected from failed results.
    """

    results: list[SubAgentResult] = Field(default_factory=list)
    total_cost_usd: float = Field(default=0.0)
    total_tokens_used: int = Field(default=0)
    success_count: int = Field(default=0)
    failure_count: int = Field(default=0)
    all_passed: bool = Field(default=True)
    errors: list[str] = Field(default_factory=list)


class ResultAggregator:
    """Collect SubAgentResult objects and produce a merged AggregatedResult.

    Usage::

        agg = ResultAggregator()
        for result in sub_agent_results:
            agg.add(result)
        summary = agg.aggregate()

    # @trace FR-ORC-083
    """

    def __init__(self) -> None:
        self._results: list[SubAgentResult] = []

    def add(self, result: SubAgentResult) -> None:
        """Append a SubAgentResult for later aggregation.

        Args:
            result: A SubAgentResult instance from a completed sub-agent.

        # @trace FR-ORC-083
        """
        self._results.append(result)

    def aggregate(self) -> AggregatedResult:
        """Produce an AggregatedResult from all stored SubAgentResult objects.

        Computes totals for cost and tokens from the ``metrics`` dict of each
        result (keys: ``cost_usd``, ``tokens_used``). Missing metric keys
        default to zero without error.

        Returns:
            AggregatedResult summarising all stored results.

        # @trace FR-ORC-083
        """
        total_cost: float = 0.0
        total_tokens: int = 0
        success_count: int = 0
        failure_count: int = 0
        errors: list[str] = []

        for result in self._results:
            total_cost += float(result.metrics.get("cost_usd", 0.0))
            total_tokens += int(result.metrics.get("tokens_used", 0))

            if result.status == SubAgentStatus.COMPLETED:
                success_count += 1
            else:
                failure_count += 1
                if result.error is not None:
                    errors.append(result.error)

        return AggregatedResult(
            results=list(self._results),
            total_cost_usd=total_cost,
            total_tokens_used=total_tokens,
            success_count=success_count,
            failure_count=failure_count,
            all_passed=failure_count == 0,
            errors=errors,
        )


__all__ = [
    "AggregatedResult",
    "ResultAggregator",
]
