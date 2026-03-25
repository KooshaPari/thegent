"""Remote execution of agent tasks on Tailscale nodes via SSH."""

from __future__ import annotations

import asyncio
import itertools
import logging
import os
import subprocess
from thegent.infra.shim_subprocess import run as shim_run
import time
from dataclasses import dataclass, field
from typing import ClassVar

logger = logging.getLogger(__name__)


class RemoteExecutorError(Exception):
    """Raised when a remote execution operation fails."""


@dataclass
class RemoteTask:
    """Describes a task to be executed on a remote node.

    Attributes:
        task_id: Caller-assigned identifier for correlation.
        command: Shell command string to run on the remote host.
        env: Extra environment variables forwarded to the SSH session.
        timeout_s: Maximum wall-clock seconds before the task is aborted.
        node: Explicit target hostname/IP.  If *None*, the executor
            selects a node via round-robin.
    """

    task_id: str
    command: str
    env: dict[str, str] = field(default_factory=dict)
    timeout_s: float = 300.0
    node: str | None = None


@dataclass
class RemoteResult:
    """The outcome of a remote task execution.

    Attributes:
        task_id: Matches :attr:`RemoteTask.task_id`.
        exit_code: Process exit code returned by the remote command.
        stdout: Combined standard output captured from the remote process.
        stderr: Combined standard error captured from the remote process.
        node: Hostname/IP of the node that ran the task.
        elapsed_s: Wall-clock seconds from dispatch to completion.
    """

    task_id: str
    exit_code: int
    stdout: str
    stderr: str
    node: str
    elapsed_s: float


def _load_nodes_from_settings() -> list[str]:
    """Parse remote nodes from settings into a list of node addresses.

    Returns:
        Non-empty stripped tokens from the comma-separated setting, or an
        empty list when unset or blank.
    """
    raw = os.environ.get("THGENT_REMOTE_NODES", "")
    return [n.strip() for n in raw.split(",") if n.strip()]


def _load_ssh_user_from_settings() -> str | None:
    """Return remote SSH user from settings or None if unset."""
    raw = os.environ.get("THGENT_REMOTE_SSH_USER", "").strip()
    return raw or None


# Aliases expected by tests
_load_nodes_from_env = _load_nodes_from_settings
_load_ssh_user_from_env = _load_ssh_user_from_settings


class RemoteExecutor:
    """Executes tasks on remote Tailscale nodes via SSH.

    Node selection uses a simple round-robin strategy when the caller does
    not specify an explicit target node on the :class:`RemoteTask`.

    Environment variable configuration (read at construction time):

    * ``THGENT_REMOTE_NODES`` — comma-separated list of hostnames/IPs.
    * ``THGENT_REMOTE_SSH_USER`` — SSH login user (optional; defaults to
      the current OS user when omitted).

    Args:
        nodes: List of node hostnames or IP addresses.  When *None* the
            value is read from settings.remote_nodes.
        ssh_user: SSH username for all nodes.  When *None* the value is
            read from settings.remote_ssh_user (may remain *None*,
            meaning SSH picks up the OS user).
    """

    _SSH_OPTS: ClassVar[list[str]] = ["-o", "StrictHostKeyChecking=no"]

    def __init__(
        self,
        nodes: list[str] | None = None,
        ssh_user: str | None = None,
    ) -> None:
        self._nodes: list[str] = nodes if nodes is not None else _load_nodes_from_settings()
        self._ssh_user: str | None = ssh_user if ssh_user is not None else _load_ssh_user_from_settings()
        # Infinite round-robin iterator; created lazily when nodes exist.
        self._rr: itertools.cycle[str] | None = itertools.cycle(self._nodes) if self._nodes else None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute(self, task: RemoteTask) -> RemoteResult:
        """Execute *task* on a remote node via SSH.

        Args:
            task: The task specification to run.

        Returns:
            A :class:`RemoteResult` with the outcome.

        Raises:
            RemoteExecutorError: If no nodes are configured, node selection
                fails, or the SSH process cannot be spawned.
        """
        node = self._resolve_node(task)
        destination = self._destination(node)
        cmd = ["ssh", *self._SSH_OPTS, destination, task.command]

        env = self._build_env(task.env)

        logger.debug("Executing task %s on %s: %s", task.task_id, node, task.command)
        start = time.monotonic()
        try:
            result = shim_run(
                cmd,
                capture_output=True,
                text=True,
                timeout=task.timeout_s,
                env=env,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RemoteExecutorError(f"Task {task.task_id} timed out after {task.timeout_s}s on {node}") from exc
        except OSError as exc:
            raise RemoteExecutorError(f"Task {task.task_id} failed to spawn SSH process: {exc}") from exc

        elapsed = time.monotonic() - start
        logger.debug(
            "Task %s finished on %s in %.2fs (exit=%d)",
            task.task_id,
            node,
            elapsed,
            result.returncode,
        )
        return RemoteResult(
            task_id=task.task_id,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            node=node,
            elapsed_s=elapsed,
        )

    async def execute_async(self, task: RemoteTask) -> RemoteResult:
        """Execute *task* asynchronously on a remote node via SSH.

        Runs :meth:`execute` in the default thread-pool executor so
        blocking SSH I/O does not stall the event loop.

        Args:
            task: The task specification to run.

        Returns:
            A :class:`RemoteResult` with the outcome.

        Raises:
            RemoteExecutorError: Propagated from :meth:`execute`.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute, task)

    def available_nodes(self) -> list[str]:
        """Return the subset of configured nodes reachable via ``ping``.

        Each node is tested with a single ICMP packet (``ping -c 1 -W 2``).
        Unreachable nodes are logged at DEBUG level and omitted from the
        result.

        Returns:
            List of reachable node addresses in the order they were
            originally configured.
        """
        reachable: list[str] = []
        for node in self._nodes:
            if self._ping(node):
                reachable.append(node)
            else:
                logger.debug("Node %s is not reachable", node)
        return reachable

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _resolve_node(self, task: RemoteTask) -> str:
        """Return the target node for *task*.

        If :attr:`RemoteTask.node` is set, that value is used directly.
        Otherwise the internal round-robin iterator selects the next node.

        Args:
            task: The task whose target node should be resolved.

        Returns:
            The hostname or IP address of the selected node.

        Raises:
            RemoteExecutorError: If no nodes are configured and no explicit
                node is provided.
        """
        if task.node is not None:
            return task.node
        if self._rr is None:
            raise RemoteExecutorError(
                f"Task {task.task_id}: no remote nodes configured and no explicit node given. "
                "Set THGENT_REMOTE_NODES or pass nodes= to RemoteExecutor."
            )
        return next(self._rr)

    def _destination(self, node: str) -> str:
        """Build the SSH destination string (``[user@]node``).

        Args:
            node: The target hostname or IP.

        Returns:
            SSH destination formatted as ``user@node`` when a user is
            configured, or simply ``node`` otherwise.
        """
        if self._ssh_user:
            return f"{self._ssh_user}@{node}"
        return node

    @staticmethod
    def _build_env(extra: dict[str, str]) -> dict[str, str] | None:
        """Merge *extra* into the current process environment.

        Args:
            extra: Additional environment variables to layer on top.

        Returns:
            A merged environment dict, or *None* when *extra* is empty
            (so subprocess inherits the process environment without copy).
        """
        if not extra:
            return None
        merged = dict(os.environ)
        merged.update(extra)
        return merged

    @staticmethod
    def _ping(node: str) -> bool:
        """Send a single ICMP ping to *node*.

        Args:
            node: Hostname or IP to test.

        Returns:
            *True* if the node responds within 2 seconds, *False* otherwise.
        """
        try:
            result = shim_run(
                ["ping", "-c", "1", "-W", "2", node],
                capture_output=True,
                text=True,
                timeout=5.0,
                check=False,
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired, OSError:
            return False
