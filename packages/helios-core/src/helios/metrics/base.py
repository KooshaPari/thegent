"""Metrics system - Speed, Quality, Cost metrics"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SpeedMetrics:
    """Speed-related metrics"""
    wall_time_sec: float
    time_to_first_token_ms: float | None = None
    total_latency_ms: float | None = None
    throughput_tasks_per_hour: float | None = None
    
    def to_dict(self) -> dict:
        return {
            "wall_time_sec": self.wall_time_sec,
            "time_to_first_token_ms": self.time_to_first_token_ms,
            "total_latency_ms": self.total_latency_ms,
            "throughput_tasks_per_hour": self.throughput_tasks_per_hour
        }


@dataclass
class QualityMetrics:
    """Quality-related metrics"""
    pass_rate: float  # 0.0 - 1.0
    accuracy: float | None = None
    task_completion_rate: float | None = None
    retries_required: int = 0
    
    # Detailed breakdown
    correct_outputs: int = 0
    incorrect_outputs: int = 0
    errors: int = 0
    timeouts: int = 0
    
    def to_dict(self) -> dict:
        return {
            "pass_rate": self.pass_rate,
            "accuracy": self.accuracy,
            "task_completion_rate": self.task_completion_rate,
            "retries_required": self.retries_required,
            "correct_outputs": self.correct_outputs,
            "incorrect_outputs": self.incorrect_outputs,
            "errors": self.errors,
            "timeouts": self.timeouts
        }


@dataclass
class CostMetrics:
    """Cost-related metrics"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
    # Pricing (can be looked up from provider)
    prompt_cost_per_1k: float = 0.0
    completion_cost_per_1k: float = 0.0
    
    @property
    def estimated_cost_usd(self) -> float:
        return (
            self.prompt_tokens * self.prompt_cost_per_1k / 1000 +
            self.completion_tokens * self.completion_cost_per_1k / 1000
        )
    
    # Resource usage
    memory_peak_mb: float | None = None
    compute_time_sec: float | None = None
    
    def to_dict(self) -> dict:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": self.estimated_cost_usd,
            "memory_peak_mb": self.memory_peak_mb,
            "compute_time_sec": self.compute_time_sec
        }


@dataclass
class TaskMetrics:
    """Complete metrics for a single task"""
    task_id: str
    agent_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    speed: SpeedMetrics | None = None
    quality: QualityMetrics | None = None
    cost: CostMetrics | None = None
    
    # Additional
    trajectory_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "timestamp": self.timestamp.isoformat(),
            "speed": self.speed.to_dict() if self.speed else None,
            "quality": self.quality.to_dict() if self.quality else None,
            "cost": self.cost.to_dict() if self.cost else None,
            "trajectory_path": self.trajectory_path,
            "metadata": self.metadata
        }


class MetricsAggregator:
    """Aggregate metrics across multiple tasks"""
    
    def __init__(self):
        self._metrics: list[TaskMetrics] = []
    
    def add(self, metrics: TaskMetrics):
        """Add a task's metrics"""
        self._metrics.append(metrics)
    
    def aggregate(self) -> dict[str, Any]:
        """Aggregate all metrics"""
        if not self._metrics:
            return {}
        
        total_tasks = len(self._metrics)
        successful = sum(
            1 for m in self._metrics 
            if m.quality and m.quality.pass_rate > 0
        )
        
        avg_speed = sum(
            m.speed.wall_time_sec for m in self._metrics 
            if m.speed
        ) / total_tasks
        
        total_cost = sum(
            m.cost.estimated_cost_usd for m in self._metrics 
            if m.cost
        )
        
        return {
            "total_tasks": total_tasks,
            "successful": successful,
            "pass_rate": successful / total_tasks,
            "avg_speed_sec": avg_speed,
            "total_cost_usd": total_cost,
            "avg_cost_per_task": total_cost / total_tasks,
            "tasks": [m.to_dict() for m in self._metrics]
        }
