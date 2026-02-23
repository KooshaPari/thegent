"""Compute Offloading Mac<->PC (WP-4001) + Adaptive Scale Pool (WP-5001/5004).

Implements:
  - ComputeOffload: original SSH-based offload (WP-4001)
  - RemoteNodeClient: thin httpx client for thegent worker-pool HTTP API (WP-5001)
  - TailscaleComputePool: discovers and manages remote nodes via Tailscale (WP-5001)
  - ComputePoolManager: orchestrates local + remote worker dispatch (WP-5001)
  - FederatedLoadBalancer: EMA-weighted round-robin across compute nodes (WP-5004)
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import httpx

from thegent.compute.remote_executor import RemoteExecutor, RemoteResult, RemoteTask
from thegent.compute.tailscale import TailscaleError, TailscaleManager, TailscaleNode

if TYPE_CHECKING:
    from thegent.compute.syncthing import SyncthingWorkspaceSync
    from thegent.core.worker_pool import AgentTask, AgentResult

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# WP-4001: Original SSH-based offload (unchanged public API)
# ---------------------------------------------------------------------------


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
            node=target_id if target_id in self.executor._nodes else None,  # noqa: SLF001 -- intentional internal access to RemoteExecutor node list
        )

        return self.executor.execute(task)

    async def offload_async(self, target_id: str, command: str, timeout_s: float = 300.0) -> RemoteResult:
        """Asynchronously offload computation to target node."""
        _log.info("Offloading async to %s: %s", target_id, command)

        task = RemoteTask(
            task_id=f"offload-async-{target_id}",
            command=command,
            timeout_s=timeout_s,
            node=target_id if target_id in self.executor._nodes else None,  # noqa: SLF001 -- intentional internal access to RemoteExecutor node list
        )

        return await self.executor.execute_async(task)

    def available_targets(self) -> list[str]:
        """Return list of reachable targets."""
        return self.executor.available_nodes()


# ---------------------------------------------------------------------------
# WP-5001: Remote node HTTP client
# ---------------------------------------------------------------------------


class RemoteNodeError(Exception):
    """Raised when an HTTP call to a remote compute node fails."""


@dataclass
class ComputeNode:
    """Represents a remote compute node available for task dispatch.

    Attributes:
        node_id: Unique identifier (hostname or Tailscale IP).
        base_url: HTTP base URL for the thegent worker-pool API.
        is_available: Whether the node is currently available.
        ema_latency_ms: Exponential moving average of recent task latencies (ms).
    """

    node_id: str
    base_url: str
    is_available: bool = True
    ema_latency_ms: float = 0.0

    # EMA smoothing factor (alpha). Lower = slower to adapt.
    _EMA_ALPHA: float = field(default=0.2, init=False, repr=False)

    def update_latency(self, latency_ms: float) -> None:
        """Update the EMA latency estimate with a new measurement.

        Args:
            latency_ms: Observed latency in milliseconds.
        """
        if self.ema_latency_ms == 0.0:
            self.ema_latency_ms = latency_ms
        else:
            self.ema_latency_ms = self._EMA_ALPHA * latency_ms + (1 - self._EMA_ALPHA) * self.ema_latency_ms


class RemoteNodeClient:
    """Thin httpx client for dispatching tasks to a thegent worker-pool HTTP API.

    The remote worker-pool exposes ``POST /execute`` accepting a JSON body
    with the AgentTask fields and returning a JSON AgentResult.

    Authentication uses a shared secret passed as the ``X-Compute-Token``
    header (set via ``THGENT_COMPUTE_SHARED_SECRET`` environment variable).

    Args:
        node: The :class:`ComputeNode` to communicate with.
        timeout_s: Per-request timeout in seconds.
    """

    _AUTH_HEADER = "X-Compute-Token"

    def __init__(self, node: ComputeNode, timeout_s: float = 30.0) -> None:
        self._node = node
        self._timeout_s = timeout_s
        self._secret = os.environ.get("THGENT_COMPUTE_SHARED_SECRET", "")
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers: dict[str, str] = {}
            if self._secret:
                headers[self._AUTH_HEADER] = self._secret
            self._client = httpx.AsyncClient(
                base_url=self._node.base_url,
                headers=headers,
                timeout=self._timeout_s,
            )
        return self._client

    async def execute(self, task: AgentTask) -> AgentResult:  # type: ignore[name-defined]
        """POST task to the remote node's ``/execute`` endpoint.

        Args:
            task: The :class:`~thegent.core.worker_pool.AgentTask` to dispatch.

        Returns:
            :class:`~thegent.core.worker_pool.AgentResult` with the outcome.

        Raises:
            RemoteNodeError: On HTTP error or connection failure.
        """
        import dataclasses

        from thegent.core.worker_pool import AgentResult

        client = self._get_client()
        payload = dataclasses.asdict(task)
        t0 = time.monotonic()
        try:
            resp = await asyncio.wait_for(
                client.post("/execute", json=payload),
                timeout=self._timeout_s,
            )
            resp.raise_for_status()
        except TimeoutError as exc:
            raise RemoteNodeError(f"Remote node {self._node.node_id} timed out after {self._timeout_s}s") from exc
        except httpx.HTTPStatusError as exc:
            raise RemoteNodeError(
                f"Remote node {self._node.node_id} returned HTTP {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise RemoteNodeError(f"Remote node {self._node.node_id} connection error: {exc}") from exc

        elapsed_ms = (time.monotonic() - t0) * 1000.0
        self._node.update_latency(elapsed_ms)

        data: dict[str, Any] = resp.json()
        return AgentResult(
            task_id=data.get("task_id", task.task_id),
            exit_code=data.get("exit_code", 1),
            stdout=data.get("stdout", ""),
            stderr=data.get("stderr", ""),
            timed_out=data.get("timed_out", False),
            duration_ms=data.get("duration_ms", elapsed_ms),
            worker_pid=data.get("worker_pid", 0),
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


# ---------------------------------------------------------------------------
# WP-5001: Tailscale compute pool
# ---------------------------------------------------------------------------


class TailscaleComputePool:
    """Discovers and manages remote compute nodes via Tailscale.

    Reads ``tailscale status --json`` to get the peer list, then filters
    by TailnetLockKey presence (trusted peers) or by hostname pattern.

    Args:
        tailscale_manager: Optional :class:`~thegent.compute.tailscale.TailscaleManager`.
            If None, a default one is created.
        hostname_pattern: If set, only peers whose hostname contains this
            string are considered. Ignored when ``None``.
        worker_port: HTTP port where the remote thegent worker-pool listens.
        scheme: URL scheme (``http`` or ``https``).
    """

    def __init__(
        self,
        tailscale_manager: TailscaleManager | None = None,
        hostname_pattern: str | None = None,
        worker_port: int = 9001,
        scheme: str = "http",
    ) -> None:
        self._ts = tailscale_manager or TailscaleManager()
        self._hostname_pattern = hostname_pattern
        self._worker_port = worker_port
        self._scheme = scheme
        # node_id -> ComputeNode
        self._nodes: dict[str, ComputeNode] = {}

    def _tailscale_enabled(self) -> bool:
        """Return True when THGENT_TAILSCALE_ENABLED=1 is set."""
        return os.environ.get("THGENT_TAILSCALE_ENABLED", "0") == "1"

    def _require_tailscale(self) -> None:
        """Raise TailscaleError if Tailscale is enabled but unavailable."""
        if self._tailscale_enabled() and not self._ts.is_available():
            raise TailscaleError(
                "THGENT_TAILSCALE_ENABLED=1 but the tailscale binary is not on PATH. "
                "Install Tailscale or unset THGENT_TAILSCALE_ENABLED."
            )

    def _filter_peers(self, peers: list[TailscaleNode]) -> list[TailscaleNode]:
        """Filter peers to only trusted / matching ones.

        Args:
            peers: Raw peer list from Tailscale.

        Returns:
            Filtered list of online peers, optionally matching hostname pattern.
        """
        result = [p for p in peers if p.is_online]
        if self._hostname_pattern:
            result = [p for p in result if self._hostname_pattern in p.hostname]
        return result

    def _make_compute_node(self, peer: TailscaleNode) -> ComputeNode:
        """Build a :class:`ComputeNode` from a Tailscale peer.

        Args:
            peer: The Tailscale peer descriptor.

        Returns:
            A :class:`ComputeNode` pointing at the peer's worker HTTP API.
        """
        addr = peer.ip or peer.hostname
        base_url = f"{self._scheme}://{addr}:{self._worker_port}"
        return ComputeNode(node_id=peer.hostname, base_url=base_url)

    def refresh(self) -> list[ComputeNode]:
        """Re-discover remote nodes from Tailscale.

        When ``THGENT_TAILSCALE_ENABLED=1`` and the binary is unavailable,
        this raises :class:`~thegent.compute.tailscale.TailscaleError` loudly
        rather than silently returning an empty list.

        Returns:
            Current list of available :class:`ComputeNode` objects.

        Raises:
            TailscaleError: When Tailscale is required but unavailable.
        """
        self._require_tailscale()

        if not self._ts.is_available():
            _log.info("TailscaleComputePool: tailscale not available, returning empty pool")
            return []

        peers = self._ts.get_online_nodes()
        filtered = self._filter_peers(peers)

        updated: dict[str, ComputeNode] = {}
        for peer in filtered:
            existing = self._nodes.get(peer.hostname)
            if existing is not None:
                existing.is_available = True
                updated[peer.hostname] = existing
            else:
                updated[peer.hostname] = self._make_compute_node(peer)
                _log.info("TailscaleComputePool: discovered new node %s", peer.hostname)

        self._nodes = updated
        return list(self._nodes.values())

    def get_nodes(self) -> list[ComputeNode]:
        """Return the current list of known compute nodes (no refresh)."""
        return list(self._nodes.values())

    def add_node(self, node: ComputeNode) -> None:
        """Manually register a compute node.

        Args:
            node: The :class:`ComputeNode` to register.
        """
        self._nodes[node.node_id] = node
        _log.debug("TailscaleComputePool: manually added node %s", node.node_id)

    def remove_node(self, node_id: str) -> None:
        """Remove a compute node from the pool.

        Args:
            node_id: The node identifier to remove.
        """
        self._nodes.pop(node_id, None)
        _log.debug("TailscaleComputePool: removed node %s", node_id)


# ---------------------------------------------------------------------------
# WP-5004: Federated load balancer
# ---------------------------------------------------------------------------


class FederatedLoadBalancer:
    """Round-robin load balancer with EMA-latency weights.

    Selects among available :class:`ComputeNode` instances by round-robin,
    favouring nodes with lower EMA latency.  When all nodes have equal or
    zero latency, pure round-robin applies.

    Args:
        nodes: Initial list of compute nodes.
    """

    def __init__(self, nodes: list[ComputeNode] | None = None) -> None:
        self._nodes: list[ComputeNode] = list(nodes or [])
        self._rr_index: int = 0

    def set_nodes(self, nodes: list[ComputeNode]) -> None:
        """Replace the full node list.

        Args:
            nodes: New list of compute nodes.
        """
        self._nodes = list(nodes)
        self._rr_index = 0

    def add_node(self, node: ComputeNode) -> None:
        """Add a compute node to the balancer.

        Args:
            node: The :class:`ComputeNode` to add.
        """
        self._nodes.append(node)

    def remove_node(self, node_id: str) -> None:
        """Remove a node by ID.

        Args:
            node_id: The node ID to remove.
        """
        self._nodes = [n for n in self._nodes if n.node_id != node_id]
        self._rr_index = 0

    def select_node(self, task: Any = None) -> ComputeNode:  # noqa: ANN401 -- generic task type
        """Select the best available node for a task.

        Uses round-robin as the base strategy.  When EMA latency data is
        available, the node with the globally lowest EMA is preferred for
        the current slot unless it is unavailable.

        Args:
            task: The task to dispatch (currently unused for selection logic
                but included for future extension).

        Returns:
            The selected :class:`ComputeNode`.

        Raises:
            RuntimeError: When no nodes are available.
        """
        available = [n for n in self._nodes if n.is_available]
        if not available:
            raise RuntimeError("FederatedLoadBalancer: no available compute nodes")

        # If any node has real latency data, prefer the lowest-latency node.
        with_latency = [n for n in available if n.ema_latency_ms > 0.0]
        if with_latency:
            return min(with_latency, key=lambda n: n.ema_latency_ms)

        # Pure round-robin
        idx = self._rr_index % len(available)
        self._rr_index += 1
        return available[idx]


# ---------------------------------------------------------------------------
# WP-5001: Compute pool manager
# ---------------------------------------------------------------------------


class ComputePoolManager:
    """Orchestrates local worker pool + remote Tailscale compute nodes.

    When the local :class:`~thegent.core.worker_pool.PersistentWorkerPool`
    is saturated, overflow tasks are delegated to remote nodes discovered
    via :class:`TailscaleComputePool`.

    Workspace synchronisation (WP-5002) is handled by injecting an optional
    :class:`~thegent.compute.syncthing.SyncthingWorkspaceSync` instance.

    Args:
        compute_pool: The Tailscale-backed remote node pool.
        workspace_sync: Optional Syncthing sync helper.
        local_worker_pool: The local :class:`~thegent.core.worker_pool.PersistentWorkerPool`.
            When ``None``, tasks always go to remote nodes.
    """

    def __init__(
        self,
        compute_pool: TailscaleComputePool | None = None,
        workspace_sync: SyncthingWorkspaceSync | None = None,
        local_worker_pool: Any | None = None,
    ) -> None:
        self._compute_pool = compute_pool or TailscaleComputePool()
        self._workspace_sync = workspace_sync
        self._local_pool = local_worker_pool
        self._load_balancer = FederatedLoadBalancer()
        self._remote_clients: dict[str, RemoteNodeClient] = {}
        # Track when remote workers became idle for scale-down (node_id -> monotonic)
        self._remote_idle_since: dict[str, float] = {}

    # ------------------------------------------------------------------
    # Public scaling API
    # ------------------------------------------------------------------

    def expand(self, n_nodes: int) -> list[ComputeNode]:
        """Add up to *n_nodes* remote nodes to the active pool.

        Refreshes the Tailscale peer list and selects the first *n_nodes*
        currently-undiscovered available nodes.

        Args:
            n_nodes: Number of remote nodes to add.

        Returns:
            List of newly-added :class:`ComputeNode` instances.
        """
        available = self._compute_pool.refresh()
        current_ids = {n.node_id for n in self._load_balancer._nodes}  # noqa: SLF001
        new_nodes: list[ComputeNode] = []
        for node in available:
            if node.node_id not in current_ids and len(new_nodes) < n_nodes:
                self._load_balancer.add_node(node)
                self._remote_clients[node.node_id] = RemoteNodeClient(node)
                self._remote_idle_since.pop(node.node_id, None)
                new_nodes.append(node)
                _log.info("ComputePoolManager.expand: added remote node %s", node.node_id)
        return new_nodes

    def shrink(self) -> list[str]:
        """Release idle remote nodes.

        A remote node is eligible for release when it has been continuously
        idle for at least 5 minutes (300 s).

        Returns:
            List of node IDs that were released.
        """
        _IDLE_THRESHOLD_S = 300.0  # noqa: N806 -- local constant
        now = time.monotonic()
        released: list[str] = []
        for node_id, idle_since in list(self._remote_idle_since.items()):
            if now - idle_since >= _IDLE_THRESHOLD_S:
                self._load_balancer.remove_node(node_id)
                self._compute_pool.remove_node(node_id)
                client = self._remote_clients.pop(node_id, None)
                if client is not None:
                    asyncio.get_event_loop().create_task(client.close())
                del self._remote_idle_since[node_id]
                released.append(node_id)
                _log.info("ComputePoolManager.shrink: released idle node %s", node_id)
        return released

    def mark_remote_idle(self, node_id: str) -> None:
        """Mark a remote node as idle (no active tasks).

        Args:
            node_id: The node that became idle.
        """
        self._remote_idle_since.setdefault(node_id, time.monotonic())

    def mark_remote_busy(self, node_id: str) -> None:
        """Clear idle tracking for a remote node that received a task.

        Args:
            node_id: The node that is now busy.
        """
        self._remote_idle_since.pop(node_id, None)

    # ------------------------------------------------------------------
    # Task dispatch
    # ------------------------------------------------------------------

    async def submit(self, task: AgentTask, local_path: str | None = None) -> AgentResult:  # type: ignore[name-defined]
        """Submit a task, delegating to local pool or remote nodes.

        If a local worker pool is configured and has an idle worker, the task
        runs locally.  Otherwise it is forwarded to the best remote node via
        :class:`FederatedLoadBalancer`, with workspace sync if configured.

        Args:
            task: The :class:`~thegent.core.worker_pool.AgentTask` to run.
            local_path: Optional workspace path to sync before remote dispatch.

        Returns:
            :class:`~thegent.core.worker_pool.AgentResult` with the outcome.

        Raises:
            RuntimeError: When no local or remote workers are available.
        """
        # Try local pool first
        if self._local_pool is not None:
            try:
                return await self._local_pool.submit(task)
            except Exception:  # noqa: BLE001 -- local pool saturation: delegate to remote
                _log.debug("ComputePoolManager: local pool saturated, delegating to remote")

        # Select remote node
        if not self._load_balancer._nodes:  # noqa: SLF001
            raise RuntimeError("ComputePoolManager: no remote compute nodes available for overflow")

        node = self._load_balancer.select_node(task)

        # Sync workspace before dispatch (WP-5002)
        if self._workspace_sync is not None and local_path is not None:
            peer_ids = [n.node_id for n in self._load_balancer._nodes]  # noqa: SLF001
            await self._workspace_sync.push(local_path, peer_ids)

        client = self._remote_clients.get(node.node_id)
        if client is None:
            client = RemoteNodeClient(node)
            self._remote_clients[node.node_id] = client

        self.mark_remote_busy(node.node_id)
        try:
            result = await client.execute(task)
        finally:
            self.mark_remote_idle(node.node_id)

        return result

    def get_remote_nodes(self) -> list[ComputeNode]:
        """Return the currently active remote node list."""
        return self._load_balancer._nodes[:]  # noqa: SLF001

    def get_load_balancer(self) -> FederatedLoadBalancer:
        """Return the underlying :class:`FederatedLoadBalancer`."""
        return self._load_balancer
