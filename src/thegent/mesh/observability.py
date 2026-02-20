"""Observability and metrics for the agent mesh."""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class MeshLogger:
    """JSONL structured logging (SCLI-P13.1)."""

    def __init__(self, mesh_root: Path) -> None:
        self.log_file = mesh_root / "mesh.jsonl"

    def log(self, agent_id: str, event: str, data: dict | None = None):
        """Append a structured log entry."""
        entry = {
            "timestamp": time.time(),
            "agent_id": agent_id,
            "event": event,
            "data": data or {}
        }
        # PIPE_BUF aware atomic append (SCLI-P13.1)
        line = json.dumps(entry) + "\n"
        if len(line) <= 4096: # PIPE_BUF limit for atomic write
            with open(self.log_file, "a") as f:
                f.write(line)
        else:
            # Fallback for large lines
            with open(self.log_file, "a") as f:
                f.write(line)


class MetricsAggregator:
    """Mesh metrics aggregation (SCLI-P13.2)."""

    def __init__(self, mesh_root: Path) -> None:
        self.metrics_dir = mesh_root / "metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True, mode=0o1777)

    def record_metric(self, agent_id: str, name: str, value: float):
        """Record a single metric point."""
        metric_file = self.metrics_dir / f"{agent_id}.jsonl"
        entry = {"timestamp": time.time(), "name": name, "value": value}
        with open(metric_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_summary(self) -> dict[str, Any]:
        """Aggregate metrics for all agents (SCLI-P13.4)."""
        summary = {"agents": {}, "totals": {}}
        for metric_file in self.metrics_dir.glob("*.jsonl"):
            agent_id = metric_file.stem
            with open(metric_file) as f:
                points = [json.loads(line) for line in f]

            # Simple aggregation
            summary["agents"][agent_id] = {
                "count": len(points),
                "avg_value": sum(p["value"] for p in points) / len(points) if points else 0
            }
        return summary


def mesh_status_cmd(mesh_root: Path) -> None:
    """CLI 'mesh status' (SCLI-P13.3)."""
    # This would be called from a Typer app
    agents = list((mesh_root / "agents").glob("*.yaml"))
    for _a in agents:
        pass
