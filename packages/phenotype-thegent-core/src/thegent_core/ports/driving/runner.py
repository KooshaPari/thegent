"""RunnerPort: Abstract protocol for executing agent runs.

This port breaks the circular dependency between thegent-agents and
thegent-cli: agents/loop_controller.py used to import run_impl directly from
thegent_cli.cli.commands.impl.  Now agents depend on this abstract protocol;
the concrete CLI implementation is injected at startup.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class RunnerPort(Protocol):
    """Port for executing an agent run.

    The concrete implementation is thegent_cli.cli.commands.impl.run_impl
    (or a compatible callable).  Agent code must not import from thegent_cli
    directly; instead, receive a RunnerPort-compatible callable.
    """

    def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute a run and return a result dict.

        Returns:
            Mapping with at least ``exit_code`` (int), ``stdout`` (str),
            ``stderr`` (str) keys.  Additional keys such as ``cost_usd`` may
            be present.
        """
        ...


@runtime_checkable
class DagStatusPort(Protocol):
    """Port for fetching DAG status.

    Mirrors dag_status_impl from thegent_cli without importing it.
    """

    def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Fetch and return DAG status information."""
        ...


class NullRunnerPort:
    """Null-object implementation of RunnerPort.

    Returns a synthetic failure result when no real runner is wired in.
    Useful in tests and environments where the CLI layer is absent.
    """

    def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Return a synthetic 'runner unavailable' result."""
        return {
            "exit_code": 1,
            "stdout": "",
            "stderr": "RunnerPort: no concrete runner has been registered.",
            "cost_usd": 0.0,
        }


__all__ = [
    "DagStatusPort",
    "NullRunnerPort",
    "RunnerPort",
]
