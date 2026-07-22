"""Sub-agent dispatcher — plan-node → ``InterAgentMessage`` → ``MessageBus``.

The :class:`SubAgentDispatcher` is the canonical entry point for routing
:class:`PlanNode` work to the correct agent queue.  It publishes an
:class:`InterAgentMessage` of ``message_type="task_request"`` carrying the
node's task, id, and (optional) ``agent_hint`` routing metadata, and
returns the assigned message id so the caller can correlate later
:class:`InterAgentMessage` results.

Hardening (AUDIT-N+33)
----------------------
- Constructor validates ``bus`` is a :class:`MessageBus` and ``plan`` (when
  supplied) is an :class:`OrchestrationPlan`.  Older kwargs (``registry``,
  ``runner``, ``policy_engine``) are tolerated for backwards compatibility
  but do not influence dispatch behaviour — the dispatcher is now
  *message-bus-only*.
- :meth:`dispatch` auto-subscribes the recipient on the bus before
  publishing, so callers do not have to pre-register agents.
- :meth:`dispatch_all` performs a deterministic topological sort so that
  parents are always dispatched before their children.  Cycles raise
  :class:`ValueError` (no silent deadlock).
- :meth:`collect_results` auto-subscribes the agent on demand and forwards
  to :meth:`MessageBus.drain`.
- :attr:`sender_id` is stable per dispatcher instance (UUID4) so that
  downstream agents can identify the originator.

# @trace WL-082
# @trace AUDIT-N+33
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable
from typing import Any

from thegent.orchestration.inter_agent_protocol import (
    InterAgentMessage,
    MessageBus,
)
from thegent.orchestration.plan import (
    AGENT_HINT,
    OrchestrationPlan,
)
from thegent.agents.plangent import PlanNode

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DISPATCHER_SENDER_PREFIX = "dispatcher"


# ---------------------------------------------------------------------------
# DispatchResult — carried back from a runner to the executor.
# ---------------------------------------------------------------------------


class DispatchResult:
    """Result of dispatching a single :class:`PlanNode`.

    Constructed by :class:`SubAgentDispatcher.dispatch_plan` consumers or by
    the legacy :class:`SubAgentDispatcher.execute_task` path.  Fields are
    positional but most callers use keyword arguments for clarity.
    """

    __slots__ = ("error", "node_id", "output", "success")

    def __hash__(self) -> int:  # noqa: PLW1641 — explicit eq/hash pair
        return hash((self.node_id, self.output, self.success, self.error))

    def __init__(
        self,
        node_id: str,
        output: str = "",
        success: bool = True,
        error: str = "",
    ) -> None:
        if not isinstance(node_id, str) or not node_id:
            raise ValueError("node_id must be a non-empty string")
        if not isinstance(output, str):
            raise TypeError(f"output must be str, got {type(output).__name__}")
        if not isinstance(success, bool):
            raise TypeError(f"success must be bool, got {type(success).__name__}")
        if not isinstance(error, str):
            raise TypeError(f"error must be str, got {type(error).__name__}")
        self.node_id = node_id
        self.output = output
        self.success = success
        self.error = error

    def __repr__(self) -> str:
        return (
            f"DispatchResult(node_id={self.node_id!r}, "
            f"output={self.output!r}, success={self.success!r}, "
            f"error={self.error!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DispatchResult):
            return NotImplemented
        return (
            self.node_id == other.node_id
            and self.output == other.output
            and self.success == other.success
            and self.error == other.error
        )


# ---------------------------------------------------------------------------
# SubAgentDispatcher — canonical (bus + plan) implementation
# ---------------------------------------------------------------------------


class SubAgentDispatcher:
    """Publishes :class:`PlanNode` work to a :class:`MessageBus`.

    Parameters
    ----------
    bus
        The :class:`MessageBus` used to deliver :class:`InterAgentMessage`
        instances to subscribed agents.
    plan
        Optional :class:`OrchestrationPlan` the dispatcher is bound to.
        When set, ``self.plan`` exposes it; ``dispatch_all(plan)`` is the
        canonical bulk path.
    sender_id
        Override the auto-generated sender id (default: a deterministic
        UUID4 string prefixed ``"dispatcher-"``).
    registry / runner / policy_engine / config
        Legacy kwargs kept for backwards compatibility with the
        pre-WL-082 stub.  They are tolerated but not consulted by the
        current dispatch path.
    """

    def __init__(
        self,
        bus: MessageBus | None = None,
        plan: OrchestrationPlan | None = None,
        *,
        sender_id: str | None = None,
        registry: Any = None,
        runner: Any = None,
        policy_engine: Any = None,
        config: Any = None,
        capability_index: Any = None,
        **_: Any,
    ) -> None:
        if bus is not None and not isinstance(bus, MessageBus):
            raise TypeError(f"bus must be MessageBus, got {type(bus).__name__}")
        if plan is not None and not isinstance(plan, OrchestrationPlan):
            raise TypeError(f"plan must be OrchestrationPlan, got {type(plan).__name__}")
        # Backwards-compat: the legacy stub accepted `registry` /
        # `runner` / `policy_engine` / `config` and stored them as
        # attributes.  We keep the attributes so old callers can still
        # introspect them but the canonical dispatch path no longer
        # consults them.
        self.bus = bus if bus is not None else MessageBus()
        self.plan = plan
        self.registry = registry
        self.runner = runner
        self.policy_engine = policy_engine
        self.config = config
        self.capability_index = capability_index
        self.sender_id = (
            sender_id if isinstance(sender_id, str) and sender_id else f"{_DISPATCHER_SENDER_PREFIX}-{uuid.uuid4()}"
        )

    # ------------------------------------------------------------------
    # Single-node dispatch
    # ------------------------------------------------------------------

    def dispatch(self, node: PlanNode) -> str:
        """Publish a ``task_request`` message for ``node`` and return its id.

        The recipient id is derived from the node's ``agent_hint``
        metadata when present, otherwise it falls back to ``node.id`` so
        the dispatch always lands on a queue the bus can deliver to.

        The bus is auto-subscribed for the recipient (idempotent) before
        publishing, so callers do not have to pre-register agents.
        """
        if not isinstance(node, PlanNode):
            raise TypeError(f"node must be PlanNode, got {type(node).__name__}")
        recipient = self._recipient_for(node)
        self.bus.subscribe(recipient)
        message = InterAgentMessage(
            sender_id=self.sender_id,
            recipient_id=recipient,
            message_type="task_request",
            payload={
                "task": node.task,
                "node_id": node.id,
            },
            correlation_id=self.plan.id if self.plan is not None else None,
        )
        self.bus.publish(message)
        return message.id

    # ------------------------------------------------------------------
    # Bulk dispatch with topological ordering
    # ------------------------------------------------------------------

    def dispatch_all(self, plan: OrchestrationPlan | None = None) -> list[str]:
        """Dispatch every node in *plan* (or ``self.plan`` if ``None``).

        Returns the list of message ids in dispatch order, which is a
        topological ordering (parents before children).  Cycles raise
        :class:`ValueError`.
        """
        target = plan if plan is not None else self.plan
        if target is None:
            raise ValueError("dispatch_all requires a plan argument when no plan is bound to the dispatcher")
        ordered = _topological_order(target)
        return [self.dispatch(node) for node in ordered]

    # ------------------------------------------------------------------
    # Result collection (drain the bus for an agent)
    # ------------------------------------------------------------------

    def collect_results(self, agent_id: str, timeout_s: float = 0.0) -> list[InterAgentMessage]:
        """Drain queued messages for ``agent_id``.

        Auto-subscribes ``agent_id`` on the bus if it is not already
        registered.  ``timeout_s`` is forwarded to
        :meth:`MessageBus.drain`.
        """
        if not isinstance(agent_id, str) or not agent_id:
            raise ValueError("agent_id must be a non-empty string")
        self.bus.subscribe(agent_id)
        return self.bus.drain(agent_id, timeout_s=timeout_s)

    # ------------------------------------------------------------------
    # Async dispatch — WL-084 contract (returns Dict[node_id, DispatchResult])
    # ------------------------------------------------------------------

    async def dispatch_plan(self, plan: OrchestrationPlan) -> dict[str, DispatchResult]:
        """Async dispatch path used by :class:`PlangentExecutor`.

        Walks the plan in topological order, publishes a message for each
        node, and returns a mapping ``node_id → DispatchResult``.  No
        agent actually executes anything — the dispatcher is purely a
        message-router; :class:`PlangentExecutor` collects the
        :class:`DispatchResult` objects from elsewhere (legacy
        ``execute_task`` path or a real runner wired through
        ``self.runner``).
        """
        if not isinstance(plan, OrchestrationPlan):
            raise TypeError(f"plan must be OrchestrationPlan, got {type(plan).__name__}")
        ordered = _topological_order(plan)
        results: dict[str, DispatchResult] = {}
        for node in ordered:
            self.dispatch(node)
            if self.runner is not None:
                outcome = await self._invoke_runner(node)
                results[node.id] = outcome
            else:
                # No runner — we still produce a placeholder so the
                # executor can record the dispatch.
                results[node.id] = DispatchResult(node_id=node.id, output="", success=True)
        return results

    async def _invoke_runner(self, node: PlanNode) -> DispatchResult:
        """Run ``self.runner`` against ``node`` and capture the outcome."""
        runner = self.runner
        try:
            if hasattr(runner, "run"):
                result = runner.run(task=node.task, **node.metadata)
            else:
                result = runner(node.task)
            # Coerce coroutine to a value if needed.
            import asyncio as _asyncio

            if _asyncio.iscoroutine(result):
                result = await result
            if hasattr(result, "exit_code"):
                if result.exit_code == 0:
                    return DispatchResult(
                        node_id=node.id,
                        output=getattr(result, "stdout", "") or "",
                        success=True,
                    )
                return DispatchResult(
                    node_id=node.id,
                    output="",
                    success=False,
                    error=getattr(result, "stderr", "") or "runner exited non-zero",
                )
            return DispatchResult(
                node_id=node.id,
                output=str(result),
                success=True,
            )
        except Exception as exc:  # noqa: BLE001 — capture any failure
            return DispatchResult(
                node_id=node.id,
                output="",
                success=False,
                error=f"{type(exc).__name__}: {exc}",
            )

    # ------------------------------------------------------------------
    # Legacy compat: pre-WL-082 sync/async task APIs
    # ------------------------------------------------------------------

    def start(self) -> None:
        """No-op retained for backwards compatibility."""
        return

    def stop(self) -> None:
        """No-op retained for backwards compatibility."""
        return

    def dispatch_task(self, task: str, context: dict | None = None) -> DispatchResult:
        """Legacy sync dispatch entry point.

        Publishes a message with ``recipient_id="default"`` and returns a
        successful :class:`DispatchResult` immediately (no actual
        execution).  Retained so older tests / callers that import the
        pre-WL-082 surface keep working.
        """
        recipient = (context or {}).get("agent_id", "default")
        self.bus.subscribe(recipient)
        message = InterAgentMessage(
            sender_id=self.sender_id,
            recipient_id=recipient,
            message_type="task_request",
            payload={"task": task},
        )
        self.bus.publish(message)
        return DispatchResult(node_id="", output=task, success=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _recipient_for(self, node: PlanNode) -> str:
        agent_hint = node.metadata.get(AGENT_HINT)
        if isinstance(agent_hint, str) and agent_hint:
            return agent_hint
        return node.id


# ---------------------------------------------------------------------------
# Topological sort helpers
# ---------------------------------------------------------------------------


def _topological_order(plan: OrchestrationPlan) -> list[PlanNode]:
    """Return *plan.nodes* in deterministic topological order.

    Cycles raise :class:`ValueError` so callers cannot accidentally
    deadlock.  ``depends_on`` may reference unknown node ids — those
    references are dropped defensively (silent cycle prevention).
    """
    nodes_by_id: dict[str, PlanNode] = {n.id: n for n in plan.nodes}
    in_degree: dict[str, int] = {n.id: 0 for n in plan.nodes}
    children: dict[str, list[str]] = {n.id: [] for n in plan.nodes}

    for node in plan.nodes:
        for dep in node.depends_on:
            if dep not in nodes_by_id:
                continue
            in_degree[node.id] += 1
            children[dep].append(node.id)

    # Kahn's algorithm with a stable ordering by node position.
    ready: list[PlanNode] = [n for n in plan.nodes if in_degree[n.id] == 0]
    ordered: list[PlanNode] = []
    while ready:
        # Pop the earliest-positioned ready node for determinism.
        node = ready.pop(0)
        ordered.append(node)
        for child_id in children[node.id]:
            in_degree[child_id] -= 1
            if in_degree[child_id] == 0 and child_id in nodes_by_id:
                # Append to ``ready`` preserving original order.
                ready.append(nodes_by_id[child_id])

    if len(ordered) != len(plan.nodes):
        raise ValueError(f"plan {plan.id!r} contains a cycle — cannot topologically sort nodes")
    return ordered


__all__ = [
    "DispatchResult",
    "SubAgentDispatcher",
    "is_cli_harness",
    "_CLI_HARNESSES",
    "CapabilityIndex",
]


# ---------------------------------------------------------------------------
# Backwards-compat surface (CLI harness detection, capability index)
# ---------------------------------------------------------------------------


def is_cli_harness(path: str) -> bool:
    """Check if ``path`` points at an executable CLI binary."""
    import os

    return os.path.exists(path) and os.access(path, os.X_OK)


_CLI_HARNESSES = {
    "bash": "/usr/bin/bash",
    "zsh": "/bin/zsh",
    "sh": "/bin/sh",
}


class CapabilityIndex:
    """Index for agent capabilities (legacy stub)."""

    def __init__(self) -> None:
        self.capabilities: dict[str, list[str]] = {}

    def register(self, agent_id: str, capabilities: list[str]) -> None:
        """Register ``capabilities`` for ``agent_id``."""
        self.capabilities[agent_id] = list(capabilities)

    def get(self, agent_id: str) -> list[str]:
        """Return the capabilities registered for ``agent_id``."""
        return list(self.capabilities.get(agent_id, []))

    @classmethod
    def get_default(cls) -> "CapabilityIndex":
        """Return a process-wide default :class:`CapabilityIndex`."""
        global _DEFAULT_CAPABILITY_INDEX
        try:
            return _DEFAULT_CAPABILITY_INDEX  # type: ignore[name-defined]
        except NameError:
            _DEFAULT_CAPABILITY_INDEX = cls()
            return _DEFAULT_CAPABILITY_INDEX


_DEFAULT_CAPABILITY_INDEX: CapabilityIndex | None = None
