"""Compute Offloading Mac↔PC (WP-4001).

Implements compute offloading between Mac and PC using Tailscale/SSH nodes.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from thegent.compute.remote_executor import RemoteExecutor, RemoteResult, RemoteTask

_log = logging.getLogger(__name__)


class ComputeOffload:
    """Compute offloading between Mac and PC using Tailscale nodes (WP-4001)."""

    def __init__(self, nodes: list[str] | None = None, ssh_user: str | None = None) -> None:
        """Initialize compute offload with remote executor.

        Args:
            nodes: Optional list of node hostnames or IPs.
            ssh_user: Optional SSH login user.
        """
        self.executor = RemoteExecutor(nodes=nodes, ssh_user=ssh_user)
        self.targets: dict[str, dict[str, Any]] = {}

    def register_target(self, target_id: str, host: str, port: int = 22) -> None:
        """Register an offload target.

        Args:
            target_id: Target identifier
            host: Host address
            port: SSH port
        """
        self.targets[target_id] = {
            "host": host,
            "port": port,
        }
        _log.info("Registered offload target: %s (%s:%d)", target_id, host, port)

    def offload(self, target_id: str, command: str, timeout_s: float = 300.0) -> RemoteResult:
        """Offload computation to target node.

        Args:
            target_id: Target identifier (must be a registered host or in executor's node list)
            command: Shell command to execute on the remote host
            timeout_s: Execution timeout in seconds

        Returns:
            RemoteResult with exit code, stdout, and stderr.
        """
        _log.info("Offloading to %s: %s", target_id, command)

        task = RemoteTask(
            task_id=f"offload-{target_id}",
            command=command,
            timeout_s=timeout_s,
            node=target_id if target_id in self.executor._nodes else None,
        )

        return self.executor.execute(task)

    async def offload_async(self, target_id: str, command: str, timeout_s: float = 300.0) -> RemoteResult:
        """Asynchronously offload computation to target node."""
        _log.info("Offloading async to %s: %s", target_id, command)

        task = RemoteTask(
            task_id=f"offload-async-{target_id}",
            command=command,
            timeout_s=timeout_s,
            node=target_id if target_id in self.executor._nodes else None,
        )

        return await self.executor.execute_async(task)

    def available_targets(self) -> list[str]:
        """Return list of reachable targets."""
        return self.executor.available_nodes()
