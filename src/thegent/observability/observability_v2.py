"""Phase 18: Observability v2 implementation.
Includes JSONL structured logging, advanced metrics, and mesh management CLI.
"""

import json
import importlib
import logging
import os
import time
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

logger = logging.getLogger(__name__)


class JSONLFormatter(logging.Formatter):
    """Formats log records as JSONL."""

    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "pid": os.getpid(),
        }
        if hasattr(record, "agent_id"):
            log_obj["agent_id"] = record.__dict__["agent_id"]
        return json.dumps(log_obj)


class AdvancedMetrics:
    """Aggregates advanced metrics per agent and command."""

    def __init__(self, metrics_file: Path) -> None:
        self.metrics_file = metrics_file
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

    def record(self, agent_id: str, command: str, duration: float, success: bool) -> None:
        if duration < 0:
            raise ValueError("duration must be >= 0")
        entry = {
            "timestamp": time.time(),
            "agent_id": agent_id,
            "command": command,
            "duration": duration,
            "success": success,
        }
        with open(self.metrics_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def aggregate(self, since_seconds: float | None = None) -> dict[str, Any]:
        """Aggregate metrics globally and by (agent, command)."""
        now = time.time()
        entries: list[dict[str, Any]] = []
        with open(self.metrics_file) as f:
            for idx, raw in enumerate(f, start=1):
                line = raw.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSONL metrics entry at line {idx}") from exc
                if since_seconds is not None and (now - float(entry["timestamp"])) > since_seconds:
                    continue
                entries.append(entry)

        grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for entry in entries:
            grouped[(str(entry["agent_id"]), str(entry["command"]))].append(entry)

        by_agent_command: dict[str, dict[str, Any]] = {}
        for (agent_id, command), rows in grouped.items():
            durations = [float(r["duration"]) for r in rows]
            success_count = sum(1 for r in rows if bool(r["success"]))
            error_count = len(rows) - success_count
            key = f"{agent_id}:{command}"
            by_agent_command[key] = {
                "agent_id": agent_id,
                "command": command,
                "count": len(rows),
                "success_count": success_count,
                "error_count": error_count,
                "success_rate": success_count / len(rows) if rows else 0.0,
                "duration_ms": {
                    "min": min(durations) if durations else 0.0,
                    "max": max(durations) if durations else 0.0,
                    "mean": mean(durations) if durations else 0.0,
                    "p95": _percentile(durations, 0.95),
                },
            }

        total_count = len(entries)
        total_success = sum(1 for e in entries if bool(e["success"]))
        durations = [float(e["duration"]) for e in entries]

        return {
            "total_count": total_count,
            "success_count": total_success,
            "error_count": total_count - total_success,
            "success_rate": total_success / total_count if total_count else 0.0,
            "duration_ms": {
                "min": min(durations) if durations else 0.0,
                "max": max(durations) if durations else 0.0,
                "mean": mean(durations) if durations else 0.0,
                "p95": _percentile(durations, 0.95),
            },
            "by_agent_command": by_agent_command,
        }


class MeshCLI:
    """CLI functions for mesh management."""

    @staticmethod
    def status(mesh_dir: Path) -> dict[str, Any]:
        """Show summary status of the agent mesh."""
        import yaml

        agents_dir = mesh_dir / "agents"
        if not agents_dir.exists():
            return {"mesh_dir": str(mesh_dir), "total_agents": 0, "alive_agents": 0, "agents": []}

        psutil_module = importlib.import_module("psutil")

        agents: list[dict[str, Any]] = []
        alive_agents = 0
        for manifest in sorted(agents_dir.glob("*.yaml")):
            with open(manifest) as f:
                data = yaml.safe_load(f) or {}

            pid = int(data.get("pid", 0) or 0)
            alive = False
            if pid > 0:
                try:
                    alive = bool(psutil_module.Process(pid).is_running())
                except Exception:
                    alive = False
            if alive:
                alive_agents += 1

            agents.append(
                {
                    "agent_id": manifest.stem,
                    "pid": pid,
                    "type": data.get("type") or data.get("name", "unknown"),
                    "status": "running" if alive else "offline",
                }
            )

        return {
            "mesh_dir": str(mesh_dir),
            "total_agents": len(agents),
            "alive_agents": alive_agents,
            "agents": agents,
        }

    @staticmethod
    def tasks(mesh_dir: Path) -> dict[str, Any]:
        """Show status of tasks in the mesh."""
        queue_root = mesh_dir / "queue"
        pending = list((queue_root / "new").iterdir()) if (queue_root / "new").exists() else []
        inflight = list((queue_root / "cur").iterdir()) if (queue_root / "cur").exists() else []
        failed = list((queue_root / "tmp").iterdir()) if (queue_root / "tmp").exists() else []
        return {
            "mesh_dir": str(mesh_dir),
            "pending_count": len(pending),
            "inflight_count": len(inflight),
            "failed_count": len(failed),
            "pending_ids": sorted(p.name for p in pending),
            "inflight_ids": sorted(p.name for p in inflight),
            "failed_ids": sorted(p.name for p in failed),
        }


def _percentile(values: list[float], q: float) -> float:
    """Return percentile in [0, 1] using nearest-rank semantics."""
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int((len(ordered) - 1) * q)))
    return ordered[index]
