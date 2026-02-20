"""Compute offloading implementations."""

from thegent.compute.offload import ComputeOffload
from thegent.compute.remote_executor import (
    RemoteExecutor,
    RemoteExecutorError,
    RemoteResult,
    RemoteTask,
)
from thegent.compute.syncthing import (
    SyncthingConfig,
    SyncthingDevice,
    SyncthingError,
    SyncthingFolder,
    SyncthingManager,
)
from thegent.compute.tailscale import TailscaleConfig, TailscaleManager, TailscaleNode

__all__ = [
    "ComputeOffload",
    "RemoteExecutor",
    "RemoteExecutorError",
    "RemoteResult",
    "RemoteTask",
    "SyncthingConfig",
    "SyncthingDevice",
    "SyncthingError",
    "SyncthingFolder",
    "SyncthingManager",
    "TailscaleConfig",
    "TailscaleManager",
    "TailscaleNode",
]
