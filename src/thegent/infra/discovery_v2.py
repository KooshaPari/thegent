"""Phase 12: Process Discovery implementation (v2).
Includes /proc scanner with agent patterns, heartbeats, and cleanup.
"""

import os
import logging
import psutil
import yaml
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class AgentScanner:
    """Scans for agent processes using specific patterns."""
    
    AGENT_PATTERNS = {
        "claude": ["claude-code", "claude"],
        "aider": ["aider"],
        "cursor": ["cursor-agent"],
        "cline": ["cline"],
        "thegent": ["thegent", "harness"]
    }

    def scan(self) -> List[Dict[str, Any]]:
        """Scan process tree for agents."""
        discovered = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd', 'environ']):
            try:
                cmdline = " ".join(proc.info['cmdline'] or [])
                for agent_type, patterns in self.AGENT_PATTERNS.items():
                    if any(p in cmdline.lower() for p in patterns):
                        discovered.append({
                            "id": f"{agent_type}-{proc.info['pid']}",
                            "type": agent_type,
                            "pid": proc.info['pid'],
                            "cwd": proc.info['cwd'],
                            "status": "discovered",
                            "last_seen": time.time()
                        })
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return discovered

class HeartbeatMonitor:
    """Manages agent heartbeats and stale detection."""

    def __init__(self, heartbeat_dir: Path, failure_threshold: int = 15):
        self.heartbeat_dir = heartbeat_dir
        self.heartbeat_dir.mkdir(parents=True, exist_ok=True)
        self.failure_threshold = failure_threshold

    def beat(self, agent_id: str):
        """Register a heartbeat for an agent."""
        heartbeat_file = self.heartbeat_dir / f"{agent_id}.heartbeat"
        heartbeat_file.touch()

    def get_stale_agents(self) -> List[str]:
        """Find agents that haven't beaten within threshold."""
        stale = []
        now = time.time()
        for f in self.heartbeat_dir.glob("*.heartbeat"):
            if now - f.stat().st_mtime > self.failure_threshold:
                stale.append(f.stem)
        return stale

    def cleanup_stale(self, callback: Optional[callable] = None):
        """Cleanup stale agent records."""
        stale_ids = self.get_stale_agents()
        for agent_id in stale_ids:
            logger.warning(f"Agent {agent_id} heartbeat failure. Cleaning up.")
            if callback:
                callback(agent_id)
            (self.heartbeat_dir / f"{agent_id}.heartbeat").unlink()

class AgentManifest:
    """Manages agent manifest files."""
    
    @staticmethod
    def create(manifest_path: Path, agent_info: Dict[str, Any]):
        """Create or update agent manifest."""
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **agent_info
        }
        with open(manifest_path, "w") as f:
            yaml.dump(data, f)
