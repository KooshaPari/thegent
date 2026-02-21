"""SubAgentDispatcher: CapabilityIndex-backed dispatch with budget enforcement.

Provides CapabilityIndex for mapping capability strings to agent names, and
SubAgentDispatcher for dispatching SubAgentRequest objects to sub-agents with
optional token budget enforcement and structured event logging.

Events are published to a SubAgentEventQueue so that real-time consumers
(MCP tool, UnifiedWorkerDaemon) can observe dispatch lifecycle transitions.

WL-089: When a ComputePoolManager is provided via the compute_pool parameter,
SubAgentDispatcher will delegate requests whose agent_type is NOT a recognized
CLI harness (e.g. "codex", "claude", "gemini") to the remote compute pool via
RemoteDispatchBackend. CLI harnesses are dispatched locally as before.

# @trace FR-ORC-082
# @trace WL-085
# @trace WL-089
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from thegent.compute.offload import ComputePoolManager
    from thegent.orchestration.budget_tracker import BudgetTracker
    from thegent.orchestration.remote_dispatch import RemoteDispatchBackend

from thegent.orchestration.event_queue import SubAgentEventQueue, get_global_event_queue
from thegent.orchestration.protocol import (
    SubAgentEvent,
    SubAgentEventType,
    SubAgentRequest,
    SubAgentResult,
    SubAgentStatus,
)

# ---------------------------------------------------------------------------
# WL-089: Recognized CLI agent harness names.
# When agent_type matches one of these, dispatch is handled locally (or via
# remote_backend if set). When it does NOT match and compute_pool is set,
# the request is delegated to the Tailscale compute pool.
# ---------------------------------------------------------------------------

_CLI_HARNESSES: frozenset[str] = frozenset(
    {
        "claude",
        "codex",
        "gemini",
        "opencode",
        "copilot",
        "droid",
        "antigravity",
        "kiro",
        "cursor",
        "flash",
        "default",
    }
)


def is_cli_harness(agent_type: str) -> bool:
    """Return True when agent_type names a recognized CLI agent harness.

    CLI harnesses (e.g. "codex", "claude", "gemini") are dispatched locally.
    Any other agent_type is treated as a compute node task and, when a
    compute_pool is configured, delegated to ComputePoolManager.submit().

    Args:
        agent_type: The agent_type field from a SubAgentRequest.

    Returns:
        True if agent_type is a known CLI harness name.

    # @trace WL-089
    """
    return agent_type.lower() in _CLI_HARNESSES


_log = logging.getLogger(__name__)

# Stub token cost used for budget check on each dispatch.
# The actual token count is unknown at dispatch time; 1 is the minimum
# required to check a budget of 0.
_DISPATCH_TOKEN_STUB = 1


class CapabilityIndex:
    """Maps capability strings to agent names.

    Usage::

        index = CapabilityIndex()
        index.register("code_review", "reviewer-agent")
        agent_name = index.lookup("code_review")

    # @trace FR-ORC-082
    """

    def __init__(self) -> None:
        self._index: dict[str, str] = {}

    def register(self, capability: str, agent_name: str) -> None:
        """Register an agent_name as the handler for capability.

        Args:
            capability: Capability identifier string.
            agent_name: Name of the agent that handles the capability.

        # @trace FR-ORC-082
        """
        self._index[capability] = agent_name

    def lookup(self, capability: str) -> str:
        """Return the agent_name registered for capability.

        Args:
            capability: Capability identifier string to look up.

        Raises:
            KeyError: If no agent is registered for the capability.

        Returns:
            The agent_name registered for the capability.

        # @trace FR-ORC-082
        """
        if capability not in self._index:
            raise KeyError(capability)
        return self._index[capability]


class SubAgentDispatcher:
    """Dispatches SubAgentRequest objects with optional budget enforcement.

    This is a synchronous dispatcher stub. The actual agent execution logic
    is out of scope; dispatch() returns a COMPLETED SubAgentResult modelling
    the correct interface. Budget checking, event emission, and concurrent
    dispatch logic are fully implemented.

    Events are published to the provided *event_queue* (or the process-global
    queue when none is supplied) after each dispatch lifecycle transition.

    WL-089: When *compute_pool* is provided, requests whose agent_type is NOT
    a recognized CLI harness are delegated to the remote Tailscale compute
    pool via a :class:`~thegent.orchestration.remote_dispatch.RemoteDispatchBackend`
    constructed automatically from *compute_pool*. CLI harness requests are
    dispatched locally (or via *remote_backend* if set explicitly).

    Args:
        capability_index: CapabilityIndex for resolving capability to agent.
        budget_tracker: Optional BudgetTracker for per-request budget checks.
        event_queue: Queue to publish SubAgentEvents to.  When None the
            process-global queue returned by get_global_event_queue() is used.
        remote_backend: Optional explicit RemoteDispatchBackend.  When set,
            any request that passes is_available() on the backend is routed
            through it (regardless of agent_type).
        compute_pool: Optional ComputePoolManager for WL-089 compute dispatch.
            When set, requests whose agent_type is NOT a CLI harness are
            automatically routed to the pool via an internal
            RemoteDispatchBackend.  Ignored when remote_backend is also set.

    # @trace FR-ORC-082
    # @trace WL-085
    # @trace WL-089
    """

    def __init__(
        self,
        capability_index: CapabilityIndex,
        budget_tracker: BudgetTracker | None = None,
        event_queue: SubAgentEventQueue | None = None,
        remote_backend: RemoteDispatchBackend | None = None,
        compute_pool: ComputePoolManager | None = None,
    ) -> None:
        self._capability_index = capability_index
        self._budget_tracker = budget_tracker
        self._event_queue: SubAgentEventQueue = (
            event_queue if event_queue is not None else get_global_event_queue()
        )
        self._remote_backend = remote_backend
        self._compute_pool = compute_pool

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def dispatch(self, request: SubAgentRequest) -> SubAgentResult:
        """Dispatch a single SubAgentRequest and return a SubAgentResult.

        Emits DISPATCH_STARTED and DISPATCH_COMPLETED SubAgentEvents to the
        event queue. Checks the budget_tracker before dispatching if one was
        provided.

        Args:
            request: The request to dispatch.

        Raises:
            BudgetExceededError: If budget_tracker is set and the request
                exceeds its node budget.

        Returns:
            SubAgentResult with status COMPLETED.

        # @trace FR-ORC-082
        # @trace WL-085
        """
        self._publish_event(request, SubAgentEventType.STARTED)

        if self._budget_tracker is not None:
            self._budget_tracker.check(request.request_id, _DISPATCH_TOKEN_STUB)

        # WL-089: delegate to remote backend when available (explicit backend wins)
        if self._remote_backend is not None and self._remote_backend.is_available():
            result = self._remote_backend.dispatch(request)
        elif self._compute_pool is not None and not is_cli_harness(request.agent_type):
            # WL-089: agent_hint is not a CLI harness — delegate to the compute pool
            result = self._dispatch_via_compute_pool(request)
        else:
            result = SubAgentResult(
                request_id=request.request_id,
                agent_type=request.agent_type,
                status=SubAgentStatus.COMPLETED,
                parent_id=request.parent_id,
            )

        self._publish_event(request, SubAgentEventType.COMPLETED)
        return result

    def dispatch_concurrent(self, requests: list[SubAgentRequest]) -> list[SubAgentResult]:
        """Dispatch multiple requests concurrently using asyncio.gather.

        Uses asyncio.run() to execute all requests concurrently. Results are
        returned in the same order as the input requests.

        Args:
            requests: List of SubAgentRequest objects to dispatch.

        Returns:
            List of SubAgentResult objects in the same order as requests.

        # @trace FR-ORC-082
        # @trace WL-085
        """
        if not requests:
            return []
        return asyncio.run(self._gather_dispatch(requests))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _gather_dispatch(self, requests: list[SubAgentRequest]) -> list[SubAgentResult]:
        """Async implementation of concurrent dispatch via asyncio.gather."""
        return list(await asyncio.gather(*[self._dispatch_async(r) for r in requests]))

    async def _dispatch_async(self, request: SubAgentRequest) -> SubAgentResult:
        """Async wrapper around dispatch() for use with asyncio.gather."""
        return self.dispatch(request)

    def _dispatch_via_compute_pool(self, request: SubAgentRequest) -> SubAgentResult:
        """Delegate *request* to the Tailscale compute pool via RemoteDispatchBackend.

        Called when compute_pool is set and agent_type is not a CLI harness.
        Constructs a :class:`~thegent.orchestration.remote_dispatch.RemoteDispatchBackend`
        wrapping self._compute_pool and delegates the request.

        Args:
            request: The request to dispatch to the remote compute pool.

        Returns:
            SubAgentResult from the remote compute node.

        # @trace WL-089
        """
        from thegent.orchestration.remote_dispatch import RemoteDispatchBackend

        backend = RemoteDispatchBackend(pool_manager=self._compute_pool)
        _log.info(
            "compute_pool_dispatch request_id=%s agent_type=%s",
            request.request_id,
            request.agent_type,
        )
        return backend.dispatch(request)

    def _publish_event(self, request: SubAgentRequest, event_type: SubAgentEventType) -> None:
        """Build a SubAgentEvent and publish it to the event queue and log.

        Args:
            request: The request the event relates to.
            event_type: STARTED or COMPLETED.

        # @trace WL-085
        """
        event = SubAgentEvent(
            request_id=request.request_id,
            parent_id=request.parent_id,
            event_type=event_type,
            payload={"agent_type": request.agent_type},
            message=f"Dispatch {event_type.value}: {request.request_id}",
        )
        _log.info(
            "sub_agent_event request_id=%s event_type=%s msg=%s",
            event.request_id,
            event.event_type,
            event.message,
        )
        self._event_queue.put(event)


__all__ = [
    "_CLI_HARNESSES",
    "CapabilityIndex",
    "SubAgentDispatcher",
    "is_cli_harness",
]
