"""thegent SDK -- typed, stable public API surface.

This facade re-exports the most important types and functions from internal
modules under stable names.  Import from ``thegent.sdk`` for programmatic use.

# @trace FR-SDK-102
"""

from __future__ import annotations

import importlib.metadata

from thegent.agents.run_options import RunOptions
from thegent.core.worker_pool import AgentResult
from thegent.governance.providers import ProviderRegistry
from thegent.orchestration.protocol import SubAgentRequest, SubAgentResult
from thegent.session.manager import SessionState

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VERSION: str = importlib.metadata.version("thegent")

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


def get_version() -> str:
    """Return the installed thegent package version."""
    return VERSION


def list_providers() -> list[str]:
    """Return names of all registered providers."""
    return [p.provider_id for p in ProviderRegistry.list_providers()]


def run(task: str, **kwargs: object) -> AgentResult:
    """Execute *task* via the worker-pool runner and return an AgentResult.

    This is a thin convenience wrapper around the internal execution path.
    Keyword arguments are forwarded to the underlying runner.
    """
    import dataclasses

    from thegent.core.worker_pool import AgentTask
    from thegent.core.worker_pool import _run_task_in_process as _run

    agent_task = AgentTask(
        task_id=str(kwargs.get("task_id", "sdk-0")),
        prompt=task,
        cwd=str(kwargs.get("cwd", ".")),
        mode=str(kwargs.get("mode", "write")),
        timeout=int(kwargs.get("timeout", 600)),
        agent_name=str(kwargs.get("agent_name", "default")),
    )
    result_dict = _run(dataclasses.asdict(agent_task))
    return AgentResult(**result_dict)


# ---------------------------------------------------------------------------
# Public surface
# ---------------------------------------------------------------------------

__all__: list[str] = [
    "VERSION",
    "AgentResult",
    "RunOptions",
    "SessionState",
    "SubAgentRequest",
    "SubAgentResult",
    "get_version",
    "list_providers",
    "run",
]
