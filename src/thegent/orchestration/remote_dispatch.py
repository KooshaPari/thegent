"""WL-089: RemoteDispatchBackend — ComputePoolManager integration for SubAgentDispatcher.

Wires ComputePoolManager.submit() into SubAgentDispatcher as an optional remote
dispatch backend. When agent_hint resolves to a compute node task, this backend
delegates to the Tailscale pool with optional workspace sync.

# @trace FR-ORC-089
# @trace WL-089
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from thegent.orchestration.protocol import (
    SubAgentRequest,
    SubAgentResult,
    SubAgentStatus,
)

if TYPE_CHECKING:
    from thegent.compute.offload import ComputePoolManager
    from thegent.core.worker_pool import AgentResult, AgentTask

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Adapter functions
# ---------------------------------------------------------------------------


def adapt_request_to_agent_task(request: SubAgentRequest) -> AgentTask:
    """Convert a SubAgentRequest to an AgentTask for ComputePoolManager.submit().

    Args:
        request: The sub-agent request to convert.

    Returns:
        AgentTask suitable for submission to ComputePoolManager.

    # @trace FR-ORC-089
    """
    from thegent.core.worker_pool import AgentTask

    cwd = request.context.get("cwd", ".")
    mode = request.context.get("mode", "write")
    env: dict[str, str] = request.metadata.get("env", {})

    return AgentTask(
        task_id=request.request_id,
        prompt=request.task,
        cwd=cwd,
        mode=mode,
        timeout=request.timeout_seconds,
        env=env,
        agent_name=request.agent_type,
    )


def adapt_result_to_sub_agent_result(
    request: SubAgentRequest,
    agent_result: AgentResult,
) -> SubAgentResult:
    """Convert an AgentResult from ComputePoolManager into a SubAgentResult.

    A task is considered successful iff exit_code == 0 and not timed_out.

    Args:
        request: The original SubAgentRequest (for correlation fields).
        agent_result: The AgentResult returned by ComputePoolManager.submit().

    Returns:
        SubAgentResult with status COMPLETED on success, FAILED otherwise.

    # @trace FR-ORC-089
    """
    failed = agent_result.exit_code != 0 or agent_result.timed_out
    status = SubAgentStatus.FAILED if failed else SubAgentStatus.COMPLETED

    metrics: dict[str, Any] = {
        "exit_code": agent_result.exit_code,
        "duration_ms": agent_result.duration_ms,
    }
    if agent_result.timed_out:
        metrics["timed_out"] = True

    return SubAgentResult(
        request_id=request.request_id,
        parent_id=request.parent_id,
        agent_type=request.agent_type,
        status=status,
        output={"stdout": agent_result.stdout, "stderr": agent_result.stderr},
        metrics=metrics,
    )


# ---------------------------------------------------------------------------
# RemoteDispatchConfig
# ---------------------------------------------------------------------------


@dataclass
class RemoteDispatchConfig:
    """Configuration for remote dispatch via ComputePoolManager.

    Attributes:
        enable_remote: Whether remote dispatch is active. Default False.
        fallback_to_local: Fall back to local dispatch when remote unavailable.
        sync_workspace: Whether to sync workspace via SyncthingWorkspaceSync.
        local_path: Optional workspace path to sync before remote dispatch.

    # @trace FR-ORC-089
    """

    enable_remote: bool = False
    fallback_to_local: bool = True
    sync_workspace: bool = False
    local_path: str | None = None


# ---------------------------------------------------------------------------
# RemoteDispatchBackend
# ---------------------------------------------------------------------------


class RemoteDispatchBackend:
    """Adapts ComputePoolManager.submit() for use by SubAgentDispatcher.

    Translates SubAgentRequest → AgentTask → ComputePoolManager.submit() →
    AgentResult → SubAgentResult, running the async submit() in a new event loop.

    Args:
        pool_manager: ComputePoolManager instance. When None, is_available()
            returns False and dispatch() raises RuntimeError.
        config: Optional RemoteDispatchConfig; defaults to RemoteDispatchConfig().

    Usage::

        mgr = ComputePoolManager()
        backend = RemoteDispatchBackend(pool_manager=mgr)
        dispatcher = SubAgentDispatcher(
            capability_index=index,
            remote_backend=backend,
        )

    # @trace FR-ORC-089
    """

    def __init__(
        self,
        pool_manager: ComputePoolManager | None = None,
        config: RemoteDispatchConfig | None = None,
    ) -> None:
        self._pool_manager = pool_manager
        self._config = config or RemoteDispatchConfig()

    def is_available(self) -> bool:
        """Return True iff a ComputePoolManager is configured.

        # @trace FR-ORC-089
        """
        return self._pool_manager is not None

    def dispatch(self, request: SubAgentRequest) -> SubAgentResult:
        """Dispatch a SubAgentRequest to the remote compute pool.

        Converts the request to an AgentTask, submits it via
        ComputePoolManager.submit(), and converts the result back to
        SubAgentResult.

        Args:
            request: The request to dispatch remotely.

        Returns:
            SubAgentResult from the remote execution.

        Raises:
            RuntimeError: When no ComputePoolManager is configured.

        # @trace FR-ORC-089
        """
        if self._pool_manager is None:
            raise RuntimeError(
                "RemoteDispatchBackend: no ComputePoolManager configured. "
                "Provide a pool_manager to enable remote dispatch."
            )

        agent_task = adapt_request_to_agent_task(request)
        local_path = self._config.local_path if self._config.sync_workspace else None

        _log.debug(
            "remote_dispatch.dispatch request_id=%s agent_type=%s",
            request.request_id,
            request.agent_type,
        )

        # Run the async submit() synchronously — create a fresh event loop
        # to avoid conflicts with any enclosing loop.
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(
                        asyncio.run,
                        self._pool_manager.submit(agent_task, local_path),
                    )
                    agent_result = future.result(timeout=request.timeout_seconds)
            else:
                agent_result = loop.run_until_complete(self._pool_manager.submit(agent_task, local_path))
        except Exception as exc:
            _log.error("remote_dispatch: pool_manager.submit failed: %s", exc)
            return SubAgentResult(
                request_id=request.request_id,
                parent_id=request.parent_id,
                agent_type=request.agent_type,
                status=SubAgentStatus.FAILED,
                output={},
                error=str(exc),
            )

        return adapt_result_to_sub_agent_result(request, agent_result)


__all__ = [
    "RemoteDispatchBackend",
    "RemoteDispatchConfig",
    "adapt_request_to_agent_task",
    "adapt_result_to_sub_agent_result",
]
