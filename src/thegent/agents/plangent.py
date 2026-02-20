"""Plangent-style planning sub-agents for thegent.

Provides DAG-based task decomposition and structured plan execution.
The PlangentPlanner decomposes a goal into a directed acyclic graph (DAG)
of sub-tasks, and the PlangentExecutor dispatches each ready node to a
caller-supplied runner (sync or async).

# @trace FR-AGT-020
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

NodeStatus = Literal["pending", "running", "done", "failed"]


@dataclass
class PlanNode:
    """A single task node within a Plan DAG.

    Attributes:
        id: Unique node identifier (auto-generated UUID if not set).
        task: Natural-language description of the sub-task.
        depends_on: List of node IDs that must be ``done`` before this node
            can run.
        status: Current lifecycle status of the node.
        result: Output string produced when the node completes successfully.
        error: Error string stored when the node transitions to ``failed``.
        metadata: Arbitrary extra data (e.g., model hints, routing tags).
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task: str = ""
    depends_on: list[str] = field(default_factory=list)
    status: NodeStatus = "pending"
    result: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_ready(self, done_ids: set[str]) -> bool:
        """Return True when all dependencies are satisfied."""
        return self.status == "pending" and all(dep in done_ids for dep in self.depends_on)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for JSON / JSONL serialisation."""
        return {
            "id": self.id,
            "task": self.task,
            "depends_on": list(self.depends_on),
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "metadata": dict(self.metadata),
        }


@dataclass
class Plan:
    """A complete execution plan composed of a DAG of PlanNodes.

    Attributes:
        id: Unique plan identifier.
        goal: High-level goal statement that was decomposed.
        nodes: Ordered list of :class:`PlanNode` objects.
        created_at: UTC timestamp when the plan was created.
        metadata: Arbitrary extra data attached to the plan.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    goal: str = ""
    nodes: list[PlanNode] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------

    def get_node(self, node_id: str) -> PlanNode | None:
        """Return the node with the given ID, or ``None``."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    @property
    def done_ids(self) -> set[str]:
        """Set of node IDs whose status is ``done``."""
        return {n.id for n in self.nodes if n.status == "done"}

    @property
    def failed_ids(self) -> set[str]:
        """Set of node IDs whose status is ``failed``."""
        return {n.id for n in self.nodes if n.status == "failed"}

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict."""
        return {
            "id": self.id,
            "goal": self.goal,
            "nodes": [n.to_dict() for n in self.nodes],
            "created_at": self.created_at.isoformat(),
            "metadata": dict(self.metadata),
        }


# ---------------------------------------------------------------------------
# PlangentPlanner
# ---------------------------------------------------------------------------


class PlangentPlanner:
    """Decomposes a goal into a DAG of sub-tasks.

    The default ``decompose`` implementation produces a simple deterministic
    breakdown that requires no LLM call.  Subclass and override
    ``_generate_sub_tasks`` to inject an LLM-backed decomposition strategy.
    """

    def __init__(self, *, separator: str = ".", max_nodes_per_level: int = 5) -> None:
        """Initialise the planner.

        Args:
            separator: Character used to split compound goal strings during
                heuristic decomposition.
            max_nodes_per_level: Maximum sub-tasks per depth level when
                decomposing a compound goal.
        """
        self._separator = separator
        self._max_nodes_per_level = max_nodes_per_level

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def decompose(self, goal: str, max_depth: int = 3) -> Plan:
        """Break *goal* into a :class:`Plan` with a DAG of :class:`PlanNode`.

        Each node inherits the previous node as a dependency, forming a
        simple linear chain by default.  Override ``_generate_sub_tasks`` to
        produce arbitrary DAG shapes.

        Args:
            goal: Natural-language goal to decompose.
            max_depth: Maximum depth of the resulting DAG.  Ignored by the
                default heuristic implementation but forwarded to
                ``_generate_sub_tasks``.

        Returns:
            A :class:`Plan` instance with all nodes in ``pending`` status.
        """
        if not goal or not goal.strip():
            raise ValueError("goal must be a non-empty string")

        sub_tasks = self._generate_sub_tasks(goal.strip(), max_depth)
        plan = Plan(goal=goal.strip())

        prev_id: str | None = None
        for task_text in sub_tasks[: self._max_nodes_per_level * max_depth]:
            node = PlanNode(task=task_text, depends_on=[prev_id] if prev_id else [])
            plan.nodes.append(node)
            prev_id = node.id

        _log.debug("Decomposed goal=%r into %d nodes", goal, len(plan.nodes))
        return plan

    def next_ready_tasks(self, plan: Plan) -> list[PlanNode]:
        """Return all nodes that are ready to execute.

        A node is *ready* when its status is ``pending`` and every dependency
        is ``done``.

        Args:
            plan: The plan to evaluate.

        Returns:
            List of nodes that can start immediately (may be empty).
        """
        done = plan.done_ids
        return [n for n in plan.nodes if n.is_ready(done)]

    def mark_done(self, plan: Plan, node_id: str, result: str) -> None:
        """Mark a node as successfully completed.

        Args:
            plan: The plan containing the node.
            node_id: ID of the node to update.
            result: Output produced by the node.

        Raises:
            ValueError: If ``node_id`` is not found in the plan.
        """
        node = plan.get_node(node_id)
        if node is None:
            raise ValueError(f"Node '{node_id}' not found in plan '{plan.id}'")
        node.status = "done"
        node.result = result
        _log.debug("Node %s marked done (plan %s)", node_id, plan.id)

    def mark_failed(self, plan: Plan, node_id: str, error: str) -> None:
        """Mark a node as failed.

        Args:
            plan: The plan containing the node.
            node_id: ID of the node to update.
            error: Error message explaining the failure.

        Raises:
            ValueError: If ``node_id`` is not found in the plan.
        """
        node = plan.get_node(node_id)
        if node is None:
            raise ValueError(f"Node '{node_id}' not found in plan '{plan.id}'")
        node.status = "failed"
        node.error = error
        _log.debug("Node %s marked failed (plan %s): %s", node_id, plan.id, error)

    def is_complete(self, plan: Plan) -> bool:
        """Return ``True`` when every node is ``done`` or ``failed``.

        Args:
            plan: The plan to evaluate.
        """
        return all(n.status in ("done", "failed") for n in plan.nodes)

    def to_work_stream_rows(self, plan: Plan) -> list[dict[str, Any]]:
        """Convert a Plan into WORK_STREAM-compatible row dicts.

        Each row has keys: ``id``, ``title``, ``source``, ``priority``,
        ``depends``, ``status``.

        Args:
            plan: The plan to convert.

        Returns:
            List of dicts, one per node.
        """
        rows: list[dict[str, Any]] = []
        for node in plan.nodes:
            rows.append(
                {
                    "id": node.id,
                    "title": node.task,
                    "source": f"plan:{plan.id}",
                    "priority": "P2",
                    "depends": ",".join(node.depends_on) if node.depends_on else "-",
                    "status": node.status,
                }
            )
        return rows

    # ------------------------------------------------------------------
    # Overridable hook
    # ------------------------------------------------------------------

    def _generate_sub_tasks(self, goal: str, max_depth: int) -> list[str]:
        """Produce sub-task descriptions for a goal.

        The default implementation performs a simple heuristic split:
        - If the goal contains the separator character, split on it.
        - Otherwise, produce a minimal 5-step breakdown.

        Override this method in a subclass to inject an LLM-powered
        decomposition strategy.

        Args:
            goal: The (stripped) goal string.
            max_depth: Hint for how deep the decomposition should go.

        Returns:
            Ordered list of sub-task strings.
        """
        # max_depth is intentionally unused in the heuristic; subclasses use it.
        _ = max_depth
        if self._separator in goal:
            parts = [p.strip() for p in goal.split(self._separator) if p.strip()]
            return parts or [goal]

        return [
            f"Analyse and understand the scope of: {goal}",
            f"Design the solution approach for: {goal}",
            f"Implement: {goal}",
            f"Test and validate: {goal}",
            f"Document and finalise: {goal}",
        ]


# ---------------------------------------------------------------------------
# PlangentExecutor
# ---------------------------------------------------------------------------

RunnerType = Callable[[PlanNode], str]


class PlangentExecutor:
    """Executes a Plan by dispatching sub-tasks to thegent agents.

    The executor iterates over ready nodes, invokes the caller-supplied
    *runner* callback, and updates node status (``done`` / ``failed``).
    It repeats until the plan is complete or a blocking failure is detected.

    Attributes:
        planner: The :class:`PlangentPlanner` used to query plan state.
        fail_fast: When ``True``, execution stops immediately on the first
            failed node.  When ``False``, execution continues, skipping nodes
            whose dependencies have failed.
    """

    def __init__(
        self,
        planner: PlangentPlanner | None = None,
        *,
        fail_fast: bool = False,
    ) -> None:
        """Initialise the executor.

        Args:
            planner: :class:`PlangentPlanner` instance used to inspect plan
                state.  A default ``PlangentPlanner()`` is created if not
                provided.
            fail_fast: Stop on first failure when ``True``.
        """
        self.planner = planner or PlangentPlanner()
        self.fail_fast = fail_fast

    # ------------------------------------------------------------------
    # Sync execution
    # ------------------------------------------------------------------

    def execute(self, plan: Plan, runner: RunnerType) -> Plan:
        """Execute *plan* synchronously by dispatching each ready node.

        The method loops until the plan is complete (all nodes done/failed)
        or until no progress can be made (deadlock — remaining pending nodes
        have unsatisfied dependencies due to failures).

        Args:
            plan: The :class:`Plan` to execute.
            runner: Callable ``(PlanNode) -> str`` invoked for each ready
                node.  Must return the result string on success or raise an
                exception on failure.

        Returns:
            The mutated *plan* with updated node statuses.
        """
        _log.info("Executing plan %s (%d nodes) goal=%r", plan.id, len(plan.nodes), plan.goal)

        while not self.planner.is_complete(plan):
            ready = self.planner.next_ready_tasks(plan)
            if not ready:
                _log.warning("No ready tasks; plan %s may be deadlocked", plan.id)
                break

            for node in ready:
                node.status = "running"
                try:
                    result = runner(node)
                    self.planner.mark_done(plan, node.id, result)
                except Exception as exc:
                    error_msg = str(exc)
                    _log.error("Node %s failed: %s", node.id, error_msg)
                    self.planner.mark_failed(plan, node.id, error_msg)
                    if self.fail_fast:
                        _log.info("fail_fast=True; stopping plan %s after node %s failure", plan.id, node.id)
                        return plan

        _log.info(
            "Plan %s complete: %d done, %d failed",
            plan.id,
            len(plan.done_ids),
            len(plan.failed_ids),
        )
        return plan

    # ------------------------------------------------------------------
    # Async execution
    # ------------------------------------------------------------------

    async def execute_async(self, plan: Plan, runner: Callable[[PlanNode], Any]) -> Plan:
        """Execute *plan* asynchronously.

        Ready tasks in each wave are dispatched concurrently via
        ``asyncio.gather``.  The runner may be a plain coroutine function
        or a synchronous callable (wrapped in ``asyncio.to_thread``).

        Args:
            plan: The :class:`Plan` to execute.
            runner: Async coroutine ``async (PlanNode) -> str`` or sync
                ``(PlanNode) -> str`` invoked for each ready node.

        Returns:
            The mutated *plan* with updated node statuses.
        """
        _log.info("Async-executing plan %s (%d nodes)", plan.id, len(plan.nodes))

        while not self.planner.is_complete(plan):
            ready = self.planner.next_ready_tasks(plan)
            if not ready:
                _log.warning("No ready tasks; plan %s may be deadlocked (async)", plan.id)
                break

            # Mark all ready nodes as running before dispatching
            for node in ready:
                node.status = "running"

            async def _run_node(n: PlanNode) -> tuple[str, str | Exception]:
                try:
                    if asyncio.iscoroutinefunction(runner):
                        res = await runner(n)
                    else:
                        res = await asyncio.to_thread(runner, n)
                    return n.id, res
                except Exception as exc:
                    return n.id, exc

            outcomes = await asyncio.gather(*[_run_node(n) for n in ready])

            for node_id, outcome in outcomes:
                if isinstance(outcome, Exception):
                    _log.error("Node %s failed (async): %s", node_id, outcome)
                    self.planner.mark_failed(plan, node_id, str(outcome))
                    if self.fail_fast:
                        _log.info("fail_fast=True; stopping plan %s", plan.id)
                        return plan
                else:
                    self.planner.mark_done(plan, node_id, outcome)

        _log.info(
            "Plan %s async-complete: %d done, %d failed",
            plan.id,
            len(plan.done_ids),
            len(plan.failed_ids),
        )
        return plan
