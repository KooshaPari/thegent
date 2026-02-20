"""Phase 1 & 2: Process Detection, Mesh Init, and IPC Primitives for Agent Mesh Coordination.
"""

import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
import yaml

_log = logging.getLogger(__name__)


class MeshManager:
    """Core mesh initialization and process detection for agent coordination."""

    def __init__(self, mesh_root: Path = Path("/tmp/agent-mesh")) -> None:
        self.mesh_root = mesh_root
        self.agents_dir = self.mesh_root / "agents"
        self.queue_dir = self.mesh_root / "queue"
        self.tasks_dir = self.mesh_root / "var" / "tasks"
        self.intents_dir = self.mesh_root / "var" / "intents"
        self.locks_dir = self.mesh_root / "locks"
        self._init_mesh()

    def _init_mesh(self) -> None:
        """Initialize mesh directories."""
        for d in [self.agents_dir, self.queue_dir, self.tasks_dir, self.intents_dir, self.locks_dir]:
            d.mkdir(parents=True, exist_ok=True, mode=0o1777)

    def discover_agents(self, patterns: list[str]) -> list[dict[str, Any]]:
        """Discover agents based on process patterns."""
        discovered = []
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = " ".join(proc.info["cmdline"] or [])
                if any(p in cmdline.lower() for p in patterns):
                    discovered.append(
                        {
                            "pid": proc.info["pid"],
                            "name": proc.info["name"],
                            "cmdline": cmdline,
                            "discovered_at": time.time(),
                        }
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return discovered

    def register_agent(self, agent_id: str, metadata: dict[str, Any]) -> None:
        """Create agent manifest in mesh."""
        manifest_path = self.agents_dir / f"{agent_id}.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump({"id": agent_id, "registered_at": time.time(), **metadata}, f)

    def heartbeat(self, agent_id: str) -> None:
        """Touch heartbeat file."""
        hb_file = self.agents_dir / f"{agent_id}.heartbeat"
        hb_file.touch()

    def cleanup_stale(self, threshold: int = 15) -> None:
        """Cleanup agents whose heartbeats are older than threshold."""
        now = time.time()
        for hb in self.agents_dir.glob("*.heartbeat"):
            if now - hb.stat().st_mtime > threshold:
                agent_id = hb.stem
                _log.info("Cleaning up stale agent %s", agent_id)
                hb.unlink()
                manifest = self.agents_dir / f"{agent_id}.yaml"
                if manifest.exists():
                    manifest.unlink()


class MeshIPC:
    """IPC primitives for agent mesh: mkdir locks and Maildir queue."""

    def __init__(self, mesh_root: Path) -> None:
        self.mesh_root = mesh_root
        self.locks_dir = mesh_root / "locks"
        self.queue_dir = mesh_root / "queue"

    def acquire_lock(self, name: str) -> bool:
        """Atomic mkdir lock."""
        lock_path = self.locks_dir / name
        try:
            lock_path.mkdir()
            return True
        except FileExistsError:
            return False

    def release_lock(self, name: str) -> None:
        """Release mkdir lock."""
        lock_path = self.locks_dir / name
        if lock_path.exists():
            os.rmdir(lock_path)

    def send_message(self, agent_id: str, message: dict[str, Any]) -> None:
        """Send message via Maildir-like queue."""
        agent_queue = self.queue_dir / agent_id
        for d in ["tmp", "new", "cur"]:
            (agent_queue / d).mkdir(parents=True, exist_ok=True)

        msg_id = str(uuid.uuid4())
        tmp_path = agent_queue / "tmp" / msg_id
        new_path = agent_queue / "new" / msg_id

        with open(tmp_path, "w") as f:
            json.dump(message, f)
        tmp_path.rename(new_path)
