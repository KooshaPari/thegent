"""WL-082: Async SubAgentDispatcher — capability-resolved parallel dispatch.

Provides async dispatch of PlanNode tasks with:
- CapabilityIndex.recommend() for runner selection
- asyncio.gather with semaphore for concurrency (default max 7)
- asyncio.wait_for for per-node timeouts
- PolicyEngine.await_approval() for HITL gates

# @trace WL-082
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from thegent.agents.capability_index import AgentRecommendation, CapabilityIndex

# Runtime imports needed for isinstance checks and runtime type usage
from thegent.agents.plangent import Plan, PlanNode  # noqa: TC001
from thegent.governance.hitl import PolicyEngine  # noqa: TC001


_log = logging.getLogger(__name__)

# Default max concurrency for parallel dispatch
DEFAULT_MAX_CONCURRENCY = 7

# Default timeout per node in seconds
DEFAULT_NODE_TIMEOUT = 120.0


@dataclass
class DispatchConfig:
    """Configuration for SubAgentDispatcher.

    Attributes:
        max_concurrency: Maximum number of concurrent task dispatches.
        default_timeout: Default timeout per node in seconds.
        hitl_enabled: Whether HITL approval gates are enabled.
    """

    max_concurrency: int = DEFAULT_MAX_CONCURRENCY
    default_timeout: float = DEFAULT_NODE_TIMEOUT
    hitl_enabled: bool = False


@dataclass
class DispatchResult:
    """Result from dispatching a single PlanNode.

    Attributes:
        node_id: ID of the dispatched PlanNode.
        output: Task output string.
        success: Whether the task completed successfully.
        error: Error message if success is False.
        runner: Runner name used for execution.
        elapsed_s: Time taken in seconds.
        metadata: Additional metadata from execution.
    """

    node_id: str
    output: str
    success: bool
    error: str | None = None
    runner: str | None = None
    elapsed_s: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class RunnerNotFoundError(LookupError):
    """Raised when no runner can be resolved for a capability.

    # @trace WL-082
    """


class DispatchTimeoutError(TimeoutError):
    """Raised when a node dispatch exceeds its timeout.

    # @trace WL-082
    """


class SubAgentDispatcher:
    """Async dispatcher for PlanNode tasks with capability-based runner selection.

    This dispatcher resolves runner capabilities via CapabilityIndex.recommend(),
    executes tasks concurrently with a semaphore, applies per-node timeouts
    via asyncio.wait_for, and optionally gates execution via HITL approval.

    Attributes:
        capability_index: CapabilityIndex instance for runner resolution.
        policy_engine: Optional PolicyEngine for HITL approval gates.
        config: Dispatch configuration.

    Usage:
        index = CapabilityIndex.get()
        dispatcher = SubAgentDispatcher(capability_index=index)
        results = await dispatcher.dispatch_plan(plan)
        for node_id, result in results.items():
            print(f"{node_id}: {result.success}")

    # @trace WL-082
    """

    def __init__(
        self,
        capability_index: CapabilityIndex,
        policy_engine: PolicyEngine | None = None,
        config: DispatchConfig | None = None,
    ) -> None:
        """Initialize the dispatcher.

        Args:
            capability_index: CapabilityIndex for resolving runner capabilities.
            policy_engine: Optional PolicyEngine for HITL approval gates.
            config: Optional dispatch configuration.
        """
        self._capability_index = capability_index
        self._policy_engine = policy_engine
        self._config = config or DispatchConfig()
        self._semaphore: asyncio.Semaphore | None = None

    @property
    def capability_index(self) -> CapabilityIndex:
        """Return the capability index."""
        return self._capability_index

    @property
    def policy_engine(self) -> PolicyEngine | None:
        """Return the policy engine (may be None)."""
        return self._policy_engine

    @property
    def config(self) -> DispatchConfig:
        """Return the dispatch configuration."""
        return self._config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def dispatch_plan(
        self,
        plan: Plan,
    ) -> dict[str, DispatchResult]:
        """Dispatch all nodes in a plan concurrently with dependency ordering.

        Uses asyncio.gather with a semaphore for concurrency control.
        Respects dependencies by ensuring parent nodes complete before
        children are dispatched.

        Args:
            plan: The Plan with nodes to dispatch.

        Returns:
            Dictionary mapping node_id -> DispatchResult for each dispatched node.

        # @trace WL-082
        """
        if not plan.nodes:
            return {}

        # Build dependency graph
        node_by_id: dict[str, PlanNode] = {n.id: n for n in plan.nodes}
        dependents: dict[str, list[str]] = {n.id: [] for n in plan.nodes}
        in_degree: dict[str, int] = {n.id: 0 for n in plan.nodes}

        for node in plan.nodes:
            for dep_id in node.depends_on:
                in_degree[node.id] += 1
                dependents[dep_id].append(node.id)

        # Track completed node IDs
        done_ids: set[str] = set()
        results: dict[str, DispatchResult] = {}

        # Initialize semaphore
        self._semaphore = asyncio.Semaphore(self._config.max_concurrency)

        # Kahn's algorithm with async dispatch
        ready_queue: list[str] = [nid for nid, deg in in_degree.items() if deg == 0]

        async def dispatch_node(node_id: str) -> DispatchResult:
            """Dispatch a single node with timeout and HITL gates."""
            node = node_by_id[node_id]
            timeout = node.metadata.get("timeout_seconds", self._config.default_timeout)

            try:
                result = await asyncio.wait_for(
                    self._dispatch_node(node),
                    timeout=timeout,
                )
                return result
            except TimeoutError:
                _log.error("Node %s timed out after %.1fs", node_id, timeout)
                return DispatchResult(
                    node_id=node_id,
                    output="",
                    success=False,
                    error=f"Timeout after {timeout}s",
                )

        while ready_queue:
            # Dispatch all ready nodes concurrently
            batch = ready_queue.copy()
            ready_queue.clear()

            # Run batch concurrently with semaphore
            async with self._semaphore:
                dispatch_tasks = [dispatch_node(nid) for nid in batch]
                batch_results = await asyncio.gather(*dispatch_tasks, return_exceptions=True)

            # Process results
            for node_id, outcome in zip(batch, batch_results):
                if isinstance(outcome, DispatchResult):
                    results[node_id] = outcome
                    done_ids.add(node_id)

                    # Add dependents to ready queue if all dependencies satisfied
                    for child_id in dependents[node_id]:
                        in_degree[child_id] -= 1
                        if in_degree[child_id] == 0 and child_id not in done_ids:
                            ready_queue.append(child_id)
                else:
                    # Exception occurred
                    _log.exception("Dispatch failed for node %s", node_id)
                    results[node_id] = DispatchResult(
                        node_id=node_id,
                        output="",
                        success=False,
                        error=f"{type(outcome).__name__}: {outcome}",
                    )
                    done_ids.add(node_id)

        return results

    async def dispatch_node_sync(
        self,
        node: PlanNode,
    ) -> DispatchResult:
        """Dispatch a single node synchronously (convenience method).

        Args:
            node: The PlanNode to dispatch.

        Returns:
            DispatchResult for the dispatched node.

        # @trace WL-082
        """
        return await self._dispatch_node(node)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _dispatch_node(self, node: PlanNode) -> DispatchResult:
        """Internal node dispatch with capability resolution and HITL gates.

        Args:
            node: The PlanNode to dispatch.

        Returns:
            DispatchResult for the dispatched node.

        # @trace WL-082
        """
        import time

        start_time = time.monotonic()

        # Resolve capability and select runner via recommend()
        recommendation = self._resolve_runner(node)
        runner_name = recommendation.runner if recommendation else None

        # Check HITL gate if enabled
        if self._config.hitl_enabled and self._policy_engine is not None:
            await self._check_hitl_gate(node, recommendation)

        # Execute the task (placeholder - integrate with actual runner)
        output, success, error = await self._execute_task(
            node=node,
            runner_name=runner_name,
            recommendation=recommendation,
        )

        elapsed = time.monotonic() - start_time

        return DispatchResult(
            node_id=node.id,
            output=output,
            success=success,
            error=error,
            runner=runner_name,
            elapsed_s=elapsed,
            metadata={"recommendation": recommendation.to_dict() if recommendation else {}},
        )

    def _resolve_runner(self, node: PlanNode) -> AgentRecommendation | None:
        """Resolve runner capability via CapabilityIndex.recommend().

        Args:
            node: The PlanNode to resolve runner for.

        Returns:
            Top AgentRecommendation or None if no match.

        # @trace WL-082
        """
        # Use agent_hint from metadata, fallback to task description
        agent_hint = node.metadata.get("agent_hint")
        task_description = node.task

        if agent_hint:
            # Use agent_hint for targeted lookup
            recommendations = self._capability_index.recommend(agent_hint, top_n=1)
        else:
            # Use task description for capability matching
            recommendations = self._capability_index.recommend(task_description, top_n=1)

        if not recommendations:
            _log.warning("No runner recommendation for node %s", node.id)
            return None

        return recommendations[0]

    async def _check_hitl_gate(
        self,
        node: PlanNode,
        recommendation: AgentRecommendation | None,
    ) -> None:
        """Check HITL approval gate via PolicyEngine.await_approval().

        Args:
            node: The PlanNode requiring approval.
            recommendation: Resolved runner recommendation.

        Raises:
            RuntimeError: When HITL approval is required but not granted.

        # @trace WL-082
        """
        if self._policy_engine is None:
            return

        # Check if this node requires approval
        require_approval = node.metadata.get("require_approval", False)

        # Auto-trigger for high-risk operations
        if recommendation and "critical" in recommendation.capabilities:
            require_approval = True

        if not require_approval:
            return

        run_id = f"hitl_{uuid.uuid4().hex[:8]}"
        agent_name = recommendation.name if recommendation else "unknown"
        policy = "require_human_approval.auto_critical"
        reason = f"Node {node.id} requires approval for capability: {agent_name}"

        _log.info("HITL gate: run_id=%s node_id=%s", run_id, node.id)

        # Emit await_approval event
        self._policy_engine.await_approval(
            run_id=run_id,
            policy=policy,
            reason=reason,
            agent=agent_name,
            lane=node.metadata.get("lane", "standard"),
            checkpoint="pre_execution",
        )

        if not bool(node.metadata.get("approval_granted", False)):
            raise RuntimeError(f"HITL approval blocked execution for node {node.id}")

        _log.debug("HITL approval granted for run_id=%s", run_id)

    async def _execute_task(
        self,
        node: PlanNode,
        runner_name: str | None,
        recommendation: AgentRecommendation | None = None,
    ) -> tuple[str, bool, str | None]:
        """Execute the task via the selected runner.

        Args:
            node: The PlanNode to execute.
            runner_name: Selected runner name.

        Returns:
            Tuple of (output, success, error).

        # @trace WL-082
        """
        if self._config.hitl_enabled and self._policy_engine is not None:
            await self._check_hitl_gate(node, recommendation)

        resolved_runner_name = runner_name
        if resolved_runner_name is None and recommendation is not None:
            resolved_runner_name = recommendation.runner

        if not resolved_runner_name:
            return "", False, f"No runner resolved for node {node.id}"

        from thegent.agents.registry import get_runner

        runner = get_runner(resolved_runner_name)
        if runner is None:
            return "", False, f"Runner '{resolved_runner_name}' not found"

        timeout = int(node.metadata.get("timeout_seconds", self._config.default_timeout))
        cwd_raw = node.metadata.get("cwd")
        cwd = Path(cwd_raw).expanduser().resolve() if isinstance(cwd_raw, str) and cwd_raw else Path.cwd()
        mode = str(node.metadata.get("mode", "write"))

        def _run_once() -> Any:
            return runner.run(prompt=node.task, cwd=cwd, mode=mode, timeout=timeout)

        try:
            result = await asyncio.to_thread(_run_once)
        except Exception as exc:
            return "", False, f"{type(exc).__name__}: {exc}"

        if hasattr(result, "exit_code"):
            exit_code = int(getattr(result, "exit_code", 1))
            stdout = str(getattr(result, "stdout", "") or "")
            stderr = str(getattr(result, "stderr", "") or "")
            if exit_code == 0:
                return stdout, True, None
            return stdout, False, stderr or f"Runner exited with code {exit_code}"

        if isinstance(result, dict):
            status = str(result.get("status", "")).lower()
            success = bool(result.get("success", status in {"ok", "success", "completed"}))
            output = str(result.get("stdout", result.get("output", "")) or "")
            error = result.get("error")
            return output, success, str(error) if error else (None if success else "Runner reported failure")

        return str(result), True, None


# ------------------------------------------------------------------
# Convenience factory
# ------------------------------------------------------------------


def create_dispatcher(
    capability_index: CapabilityIndex | None = None,
    policy_engine: PolicyEngine | None = None,
    max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    default_timeout: float = DEFAULT_NODE_TIMEOUT,
    hitl_enabled: bool = False,
) -> SubAgentDispatcher:
    """Factory function to create a SubAgentDispatcher.

    Args:
        capability_index: Optional CapabilityIndex (builds new if None).
        policy_engine: Optional PolicyEngine for HITL gates.
        max_concurrency: Max concurrent dispatches (default 7).
        default_timeout: Default timeout per node in seconds.
        hitl_enabled: Whether HITL gates are enabled.

    Returns:
        Configured SubAgentDispatcher instance.

    # @trace WL-082
    """
    index = capability_index or CapabilityIndex.get()

    config = DispatchConfig(
        max_concurrency=max_concurrency,
        default_timeout=default_timeout,
        hitl_enabled=hitl_enabled,
    )

    return SubAgentDispatcher(
        capability_index=index,
        policy_engine=policy_engine,
        config=config,
    )
