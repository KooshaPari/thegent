"""OrchestrationPlan: Extended PlanNode Metadata + Convenience Factory.

Provides an OrchestrationPlan subclass with extended metadata fields for each
PlanNode including agent_hint, model_hint, budget_tokens, budget_time_s,
sandbox, require_hitl, output_schema, and parent_run_id.

Also provides convenience factory methods:
- add_task(): Add a task with extended metadata
- from_goal(): Classmethod to create a plan from a goal string
- total_budget_used(): Calculate total budget tokens used across all nodes
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from thegent.agents.plangent import Plan, PlanNode

# Extended metadata keys for OrchestrationPlan
AGENT_HINT = "agent_hint"
MODEL_HINT = "model_hint"
BUDGET_TOKENS = "budget_tokens"
BUDGET_TIME_S = "budget_time_s"
SANDBOX = "sandbox"
REQUIRE_HITL = "require_hitl"
OUTPUT_SCHEMA = "output_schema"
PARENT_RUN_ID = "parent_run_id"


@dataclass
class OrchestrationPlan(Plan):
    """Extended Plan with Orchestration-specific metadata and convenience methods.

    Inherits all fields from Plan and adds orchestration-specific functionality
    for budget tracking, sandboxing, and HITL requirements.

    Attributes:
        id: Unique plan identifier.
        goal: High-level goal statement that was decomposed.
        nodes: Ordered list of :class:`PlanNode` objects.
        created_at: UTC timestamp when the plan was created.
        metadata: Arbitrary extra data attached to the plan.
    """

    def add_task(
        self,
        task: str,
        *,
        depends_on: list[str] | None = None,
        agent_hint: str | None = None,
        model_hint: str | None = None,
        budget_tokens: int | None = None,
        budget_time_s: float | None = None,
        sandbox: bool | None = None,
        require_hitl: bool | None = None,
        output_schema: dict[str, Any] | None = None,
        parent_run_id: str | None = None,
        **extra_metadata: Any,
    ) -> PlanNode:
        """Add a task node to the plan with extended orchestration metadata.

        Args:
            task: Natural-language description of the sub-task.
            depends_on: List of node IDs that must complete before this node runs.
            agent_hint: Suggested agent persona to execute this node.
            model_hint: Suggested model to use for this node.
            budget_tokens: Token budget allocated for this node.
            budget_time_s: Time budget in seconds for this node.
            sandbox: Whether to run this node in a sandboxed environment.
            require_hitl: Whether this node requires human-in-the-loop approval.
            output_schema: JSON schema for expected output from this node.
            parent_run_id: ID of the parent run this node belongs to.
            **extra_metadata: Additional metadata key-value pairs.

        Returns:
            The newly created PlanNode with extended metadata.
        """
        metadata: dict[str, Any] = dict(extra_metadata)

        if agent_hint is not None:
            metadata[AGENT_HINT] = agent_hint
        if model_hint is not None:
            metadata[MODEL_HINT] = model_hint
        if budget_tokens is not None:
            metadata[BUDGET_TOKENS] = budget_tokens
        if budget_time_s is not None:
            metadata[BUDGET_TIME_S] = budget_time_s
        if sandbox is not None:
            metadata[SANDBOX] = sandbox
        if require_hitl is not None:
            metadata[REQUIRE_HITL] = require_hitl
        if output_schema is not None:
            metadata[OUTPUT_SCHEMA] = output_schema
        if parent_run_id is not None:
            metadata[PARENT_RUN_ID] = parent_run_id

        node = PlanNode(
            task=task,
            depends_on=depends_on or [],
            metadata=metadata,
        )
        self.nodes.append(node)
        return node

    @classmethod
    def from_goal(
        cls,
        goal: str,
        *,
        agent_hint: str | None = None,
        model_hint: str | None = None,
        budget_tokens: int | None = None,
        budget_time_s: float | None = None,
        sandbox: bool | None = None,
        require_hitl: bool | None = None,
        output_schema: dict[str, Any] | None = None,
        parent_run_id: str | None = None,
    ) -> OrchestrationPlan:
        """Create an OrchestrationPlan from a goal string.

        Convenience factory that initializes a plan with a goal and optional
        default metadata applied to all nodes.

        Args:
            goal: High-level goal statement to create the plan for.
            agent_hint: Default agent persona for all nodes in the plan.
            model_hint: Default model for all nodes in the plan.
            budget_tokens: Default token budget for all nodes in the plan.
            budget_time_s: Default time budget in seconds for all nodes.
            sandbox: Default sandbox setting for all nodes.
            require_hitl: Default HITL requirement for all nodes.
            output_schema: Default output schema for all nodes.
            parent_run_id: ID of the parent run this plan belongs to.

        Returns:
            A new OrchestrationPlan instance with the goal set.
        """
        plan = cls(goal=goal)
        plan.metadata[AGENT_HINT] = agent_hint
        plan.metadata[MODEL_HINT] = model_hint
        plan.metadata[BUDGET_TOKENS] = budget_tokens
        plan.metadata[BUDGET_TIME_S] = budget_time_s
        plan.metadata[SANDBOX] = sandbox
        plan.metadata[REQUIRE_HITL] = require_hitl
        plan.metadata[OUTPUT_SCHEMA] = output_schema
        plan.metadata[PARENT_RUN_ID] = parent_run_id
        return plan

    def total_budget_used(self) -> dict[str, int | float]:
        """Calculate total budget used across all nodes in the plan.

        Sums the budget_tokens and budget_time_s metadata from every node,
        regardless of node status.

        Returns:
            Dict with keys ``"budget_tokens"`` (int) and ``"budget_time_s"``
            (float) representing the combined budgets allocated across all
            nodes.  Returns 0 / 0.0 for each dimension when no budget is set.
        """
        total_tokens: int = 0
        total_time: float = 0.0
        for node in self.nodes:
            tokens = node.metadata.get(BUDGET_TOKENS)
            if isinstance(tokens, int):
                total_tokens += tokens
            time_s = node.metadata.get(BUDGET_TIME_S)
            if isinstance(time_s, (int, float)):
                total_time += float(time_s)
        return {"budget_tokens": total_tokens, "budget_time_s": total_time}

    def get_nodes_by_agent(self, agent_hint: str) -> list[PlanNode]:
        """Get all nodes with a specific agent_hint.

        Args:
            agent_hint: The agent persona to filter by.

        Returns:
            List of PlanNodes that have the specified agent_hint.
        """
        return [node for node in self.nodes if node.metadata.get(AGENT_HINT) == agent_hint]

    def get_nodes_by_model(self, model_hint: str) -> list[PlanNode]:
        """Get all nodes with a specific model_hint.

        Args:
            model_hint: The model to filter by.

        Returns:
            List of PlanNodes that have the specified model_hint.
        """
        return [node for node in self.nodes if node.metadata.get(MODEL_HINT) == model_hint]

    def get_sandbox_nodes(self) -> list[PlanNode]:
        """Get all nodes that require sandboxing.

        Returns:
            List of PlanNodes where sandbox is True.
        """
        return [node for node in self.nodes if node.metadata.get(SANDBOX) is True]

    def get_hitl_nodes(self) -> list[PlanNode]:
        """Get all nodes that require human-in-the-loop approval.

        Returns:
            List of PlanNodes where require_hitl is True.
        """
        return [node for node in self.nodes if node.metadata.get(REQUIRE_HITL) is True]
