"""Phase 10: Resource Isolation implementation.
Includes per-agent TMPDIR, port allocation, and environment isolation.
"""

import contextlib
import logging
import os
import shutil
import socket
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ResourceIsolator:
    """Manages isolated resources for agents."""

    def __init__(self, base_tmp_dir: Path) -> None:
        self.base_tmp_dir = base_tmp_dir
        self.base_tmp_dir.mkdir(parents=True, exist_ok=True)
        self.allocated_ports: dict[str, list[int]] = {}
        self.agent_dirs: dict[str, Path] = {}

    def setup_agent_env(self, agent_id: str) -> dict[str, str]:
        """Set up isolated environment for an agent."""
        # 1. Isolated TMPDIR
        agent_tmp = self.base_tmp_dir / f"agent-{agent_id}"
        agent_tmp.mkdir(parents=True, exist_ok=True)
        self.agent_dirs[agent_id] = agent_tmp

        env = os.environ.copy()
        env["TMPDIR"] = str(agent_tmp)
        env["TEMP"] = str(agent_tmp)
        env["TMP"] = str(agent_tmp)
        env["AGENT_ID"] = agent_id

        return env

    def allocate_ports(self, agent_id: str, count: int = 1) -> list[int]:
        """Dynamically allocate available ports for an agent."""
        ports = []
        for _ in range(count):
            with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                s.bind(("", 0))
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                port = s.getsockname()[1]
                ports.append(port)

        if agent_id not in self.allocated_ports:
            self.allocated_ports[agent_id] = []
        self.allocated_ports[agent_id].extend(ports)
        return ports

    def cleanup_agent(self, agent_id: str):
        """Cleanup isolated resources for an agent."""
        # Cleanup TMPDIR
        if agent_id in self.agent_dirs:
            shutil.rmtree(self.agent_dirs[agent_id], ignore_errors=True)
            del self.agent_dirs[agent_id]

        # Ports are released by the OS when process exit, but we clear our registry
        if agent_id in self.allocated_ports:
            del self.allocated_ports[agent_id]

        logger.info(f"Cleaned up isolated resources for agent {agent_id}")


class EnvIsolator:
    """Helper to wrap execution with isolated environment variables."""

    @staticmethod
    def wrap_env(agent_id: str, custom_vars: dict[str, str]) -> dict[str, str]:
        env = os.environ.copy()
        # Remove potentially dangerous inherited vars
        for key in ["PYTHONPATH", "PYTHONHOME"]:
            if key in env:
                del env[key]

        env.update(custom_vars)
        return env
