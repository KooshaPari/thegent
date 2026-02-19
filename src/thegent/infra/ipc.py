"""Phase 11: IPC Primitives implementation.
Includes tmpfs mesh directory, atomic mkdir locks, Maildir queue, and WAL.
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import time
import json
import fcntl
import uuid

logger = logging.getLogger(__name__)

class IPCMesh:
    """Manages the IPC mesh directory and atomic primitives."""

    def __init__(self, mesh_root: Path = Path("/tmp/agent-mesh")):
        self.mesh_root = mesh_root
        self._init_mesh()

    def _init_mesh(self):
        """Initialize tmpfs-like mesh directory."""
        try:
            self.mesh_root.mkdir(parents=True, exist_ok=True, mode=0o1777)
            # On Linux, we could try mounting tmpfs here if privileged, 
            # but usually /tmp is already tmpfs.
        except PermissionError:
            logger.warning(f"Could not create mesh root at {self.mesh_root} with mode 1777")

    def acquire_atomic_lock(self, lock_name: str, ttl: int = 60) -> bool:
        """Atomic lock primitive using mkdir (EEXIST)."""
        lock_path = self.mesh_root / "locks" / lock_name
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            lock_path.mkdir()
            # Write metadata
            (lock_path / "metadata").write_text(f"{os.getpid()}|{time.time() + ttl}")
            return True
        except FileExistsError:
            # Check if expired
            meta_file = lock_path / "metadata"
            if meta_file.exists():
                try:
                    pid, expiry = meta_file.read_text().split("|")
                    if time.time() > float(expiry):
                        logger.info(f"Lock {lock_name} expired, breaking.")
                        self.release_atomic_lock(lock_name)
                        return self.acquire_atomic_lock(lock_name, ttl)
                except ValueError:
                    pass
            return False

    def release_atomic_lock(self, lock_name: str):
        """Release atomic lock."""
        lock_path = self.mesh_root / "locks" / lock_name
        if lock_path.exists():
            # In a real implementation, should check if we own it
            import shutil
            shutil.rmtree(lock_path, ignore_errors=True)

class MaildirQueue:
    """IPC message queue following Maildir-like tmp/new/cur lifecycle."""

    def __init__(self, queue_dir: Path):
        self.queue_dir = queue_dir
        for d in ["tmp", "new", "cur"]:
            (self.queue_dir / d).mkdir(parents=True, exist_ok=True)

    def send(self, message: Dict[str, Any]):
        """Send message by placing it in 'new'."""
        msg_id = f"{int(time.time())}.{uuid.uuid4().hex}"
        tmp_path = self.queue_dir / "tmp" / msg_id
        new_path = self.queue_dir / "new" / msg_id
        
        tmp_path.write_text(json.dumps(message))
        tmp_path.rename(new_path) # Atomic move
        return msg_id

    def receive(self) -> Optional[tuple[str, Dict[str, Any]]]:
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

class WriteAheadLog:
    """WAL implementation for crash recovery."""

    def __init__(self, wal_file: Path):
        self.wal_file = wal_file
        self.wal_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, operation: str, data: Dict[str, Any]):
        """Append entry to WAL before execution."""
        entry = {
            "timestamp": time.time(),
            "op": operation,
            "data": data,
            "id": uuid.uuid4().hex
        }
        with open(self.wal_file, "a") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(json.dumps(entry) + "\n")
            f.flush()
            os.fsync(f.fileno())
            fcntl.flock(f, fcntl.LOCK_UN)

    def replay(self) -> List[Dict[str, Any]]:
        """Read WAL entries for recovery."""
        if not self.wal_file.exists():
            return []
        
        entries = []
        with open(self.wal_file, "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
            fcntl.flock(f, fcntl.LOCK_UN)
        return entries
