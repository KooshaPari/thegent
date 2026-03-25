"""Agent execution interface. Breaks cli ↔ agents circular dependency.

This port allows agents to run agent code without importing from cli.commands.impl.
The concrete implementation (run_impl) lives in cli but is injected.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel


class RunResult(BaseModel):
    """Result of an agent run."""

    session_id: str | None = None
    status: str
    output: str | None = None
    error: str | None = None


class DagStatusInfo(BaseModel):
    """Status information for a DAG."""

    tasks: dict[str, Any] = {}
    error: str | None = None


class AgentExecutor(Protocol):
    """Execute an agent run and query DAG status.

    Implementations: impl_core_runners.run_impl, dag_impl_ops.dag_status_impl
    """

    def execute_agent(
        self,
        agent: str | None,
        prompt: str,
        cd: Path | None = None,
        mode: str = "write",
        timeout: int | None = None,
        full: bool = False,
        live: bool = True,
        model: str | None = None,
        provider: str | None = None,
        run_id: str | None = None,
        owner: str | None = None,
        include_contract: bool = False,
        route_contract: dict[str, Any] | None = None,
        route_request: dict[str, Any] | None = None,
        lane: str = "standard",
    ) -> RunResult:
        """Execute an agent run.

        Args:
            agent: Agent name
            prompt: Prompt to execute
            cd: Working directory
            mode: Execution mode (write, read, etc.)
            timeout: Timeout in seconds
            full: Whether to return full output
            live: Whether to stream live updates
            model: Model override
            provider: Provider override
            run_id: Custom run ID
            owner: Session owner
            include_contract: Include contract in result
            route_contract: Routing contract
            route_request: Routing request
            lane: Execution lane (standard, critical, etc.)

        Returns:
            RunResult with session_id and status
        """
        ...

    def get_dag_status(self, cd: Path | None = None) -> DagStatusInfo:
        """Get DAG execution status.

        Args:
            cd: Working directory

        Returns:
            DagStatusInfo with task statuses
        """
        ...


__all__ = ["AgentExecutor", "RunResult", "DagStatusInfo"]
