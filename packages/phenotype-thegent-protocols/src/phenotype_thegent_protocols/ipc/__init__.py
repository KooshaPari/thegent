"""thegent IPC: file-based inter-process communication for cross-project agents."""

from phenotype_thegent_protocols.ipc.cross_project import (
    BROADCAST_ADDR,
    IPC_DIR,
    CrossProjectIpc,
    CrossProjectIpcServer,
    IpcMessage,
)

__all__ = [
    "BROADCAST_ADDR",
    "IPC_DIR",
    "CrossProjectIpc",
    "CrossProjectIpcServer",
    "IpcMessage",
]
