"""Phase 18: Observability v2 implementation.
Includes JSONL structured logging, advanced metrics, and mesh management CLI.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import os

logger = logging.getLogger(__name__)

class JSONLFormatter(logging.Formatter):
    """Formats log records as JSONL."""
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "pid": os.getpid()
        }
        if hasattr(record, "agent_id"):
            log_obj["agent_id"] = record.agent_id
        return json.dumps(log_obj)

class AdvancedMetrics:
    """Aggregates advanced metrics per agent and command."""
    
    def __init__(self, metrics_file: Path):
        self.metrics_file = metrics_file
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

    def record(self, agent_id: str, command: str, duration: float, success: bool):
        entry = {
            "timestamp": time.time(),
            "agent_id": agent_id,
            "command": command,
            "duration": duration,
            "success": success
        }
        with open(self.metrics_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

class MeshCLI:
    """CLI functions for mesh management."""

    @staticmethod
    def status(mesh_dir: Path):
        """Show summary status of the agent mesh."""
        print(f"MESH STATUS: {mesh_dir}")
        agents_dir = mesh_dir / "agents"
        if not agents_dir.exists():
            print("No active mesh found.")
            return

        active_agents = list(agents_dir.glob("*.yaml"))
        print(f"Active Agents: {len(active_agents)}")
        for a in active_agents:
            print(f" - {a.stem}")

    @staticmethod
    def tasks(mesh_dir: Path):
        """Show status of tasks in the mesh."""
        queue_dir = mesh_dir / "queue" / "new"
        if queue_dir.exists():
            pending = list(queue_dir.iterdir())
            print(f"Pending Tasks: {len(pending)}")
