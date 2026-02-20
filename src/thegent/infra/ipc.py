"""Phase 11: IPC Primitives implementation.
Includes tmpfs mesh directory, atomic mkdir locks, Maildir queue, and WAL.
"""

import fcntl
import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class IPCMesh:
    """Manages the IPC mesh directory and atomic primitives."""

    def __init__(self, mesh_root: Path = Path("/tmp/agent-mesh")) -> None:
        self.mesh_root = mesh_root
        self._init_mesh()

    def _init_mesh(self):
        """Initialize tmpfs-like mesh directory."""
        try:
            self.mesh_root.mkdir(parents=True, exist_ok=True, mode=0o1777)
        except PermissionError:
            logger.warning(f"Could not create mesh root at {self.mesh_root} with mode 1777")

    def acquire_atomic_lock(self, lock_name: str, ttl: int = 60) -> bool:
        """Atomic lock primitive using mkdir (EEXIST)."""
        lock_path = self.mesh_root / "locks" / lock_name
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            lock_path.mkdir()
            (lock_path / "metadata").write_text(f"{os.getpid()}|{time.time() + ttl}")
            return True
        except FileExistsError:
            meta_file = lock_path / "metadata"
            if meta_file.exists():
                try:
                    _pid, expiry = meta_file.read_text().split("|")
                    if time.time() > float(expiry):
                        self.release_atomic_lock(lock_name)
                        return self.acquire_atomic_lock(lock_name, ttl)
                except ValueError:
                    pass
            return False

    def release_atomic_lock(self, lock_name: str):
        """Release atomic lock."""
        lock_path = self.mesh_root / "locks" / lock_name
        if lock_path.exists():
            import shutil

            shutil.rmtree(lock_path, ignore_errors=True)


class MaildirQueue:
    """IPC message queue following Maildir-like tmp/new/cur lifecycle."""

    def __init__(self, queue_dir: Path) -> None:
        self.queue_dir = queue_dir
        for d in ["tmp", "new", "cur"]:
            (self.queue_dir / d).mkdir(parents=True, exist_ok=True)

    def send(self, message: dict[str, Any]):
        """Send message by placing it in 'new'."""
        msg_id = f"{int(time.time())}.{uuid.uuid4().hex}"
        tmp_path = self.queue_dir / "tmp" / msg_id
        new_path = self.queue_dir / "new" / msg_id

        tmp_path.write_text(json.dumps(message))
        tmp_path.rename(new_path)
        return msg_id

    def receive(self) -> tuple[str, dict[str, Any]] | None:
        """Receive message by moving it from 'new' to 'cur'."""
        new_msgs = sorted((self.queue_dir / "new").iterdir())
        if not new_msgs:
            return None

        msg_file = new_msgs[0]
        cur_path = self.queue_dir / "cur" / msg_file.name
        msg_file.rename(cur_path)

        try:
            return msg_file.name, json.loads(cur_path.read_text())
        except json.JSONDecodeError:
            return None


class SharedStateManager:
    """Manages high-frequency shared state (metrics, circuit breakers) in the mesh."""

    def __init__(self, mesh_root: Path) -> None:
        self.mesh_root = mesh_root
        self.metrics_dir = mesh_root / "metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        from .shm_manager import SHMManager

        self.shm = SHMManager(mesh_root / "state.shm")

    def update_provider_metrics(self, provider: str, metrics: dict[str, Any]):
        """Update metrics for a specific provider."""
        # Update SHM (High Performance)
        req_count = metrics.get("request_count", 0)
        succ_count = metrics.get("success_count", 0)
        lat_ms = int(metrics.get("latency_p50_ms", metrics.get("latency_ms", 0)))
        self.shm.update_provider_metrics(provider, req_count, succ_count, lat_ms)

        # Fallback to file-based (for observability/debugging)
        metric_file = self.metrics_dir / f"{provider}.json"
        tmp_file = metric_file.with_suffix(".tmp")
        tmp_file.write_text(json.dumps(metrics))
        tmp_file.replace(metric_file)

    def get_all_metrics(self) -> dict[str, Any]:
        """Read all provider metrics from the mesh."""
        all_metrics = {}
        # Try reading from SHM first
        # (Note: we need a way to list all providers in SHM,
        # for now we'll merge file-based listing with SHM data)
        for f in self.metrics_dir.glob("*.json"):
            provider = f.stem
            shm_data = self.shm.get_provider_metrics(provider)
            if shm_data:
                all_metrics[provider] = shm_data
            else:
                try:
                    all_metrics[provider] = json.loads(f.read_text())
                except Exception:
                    continue
        return all_metrics


class WriteAheadLog:
    """WAL implementation for crash recovery."""

    def __init__(self, wal_file: Path) -> None:
        self.wal_file = wal_file
        self.wal_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, operation: str, data: dict[str, Any]):
        """Append entry to WAL before execution."""
        entry = {"timestamp": time.time(), "op": operation, "data": data, "id": uuid.uuid4().hex}
        with open(self.wal_file, "a") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(json.dumps(entry) + "\n")
            f.flush()
            os.fsync(f.fileno())
            fcntl.flock(f, fcntl.LOCK_UN)

    def replay(self) -> list[dict[str, Any]]:
        """Read WAL entries for recovery."""
        if not self.wal_file.exists():
            return []

        entries = []
        with open(self.wal_file) as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
            fcntl.flock(f, fcntl.LOCK_UN)
        return entries
