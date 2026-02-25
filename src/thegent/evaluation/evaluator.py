"""
Agent Evaluator

Evaluates agent performance on tasks.
"""

from dataclasses import dataclass
from typing import Optional, Any
from .metrics import MetricsCollector
import time


@dataclass
class EvaluationResult:
    """Result of agent evaluation."""
    agent_id: str
    task_type: str
    success: bool
    score: float
    duration: float
    tokens_used: int
    error: Optional[str] = None
    details: Optional[dict] = None


class AgentEvaluator:
    """Evaluates agent performance."""

    def __init__(self, metrics: Optional[MetricsCollector] = None):
        self.metrics = metrics or MetricsCollector()
        self._results: list[EvaluationResult] = []

    def evaluate(
        self,
        agent_id: str,
        task_type: str,
        task_fn: callable,
        timeout: float = 300.0
    ) -> EvaluationResult:
        """Evaluate agent on a task."""
        start_time = time.time()
        success = False
        score = 0.0
        tokens_used = 0
        error = None
        details = {}

        try:
            with self.metrics.timer(f"task.{task_type}"):
                result = task_fn()

            success = True
            if isinstance(result, dict):
                score = result.get("score", 1.0 if success else 0.0)
                tokens_used = result.get("tokens", 0)
                details = result.get("details", {})
            else:
                score = 1.0 if result else 0.0

        except Exception as e:
            error = str(e)
            success = False
            score = 0.0

        duration = time.time() - start_time

        result = EvaluationResult(
            agent_id=agent_id,
            task_type=task_type,
            success=success,
            score=score,
            duration=duration,
            tokens_used=tokens_used,
            error=error,
            details=details
        )

        self._results.append(result)
        self._record_metrics(result)

        return result

    def _record_metrics(self, result: EvaluationResult) -> None:
        """Record metrics for result."""
        self.metrics.record("evaluation.success", 1 if result.success else 0)
        self.metrics.record("evaluation.score", result.score)
        self.metrics.record("evaluation.duration", result.duration)
        self.metrics.record("evaluation.tokens", result.tokens_used)

    def benchmark(
        self,
        agent_id: str,
        tasks: list[dict]
    ) -> dict:
        """Run benchmark suite."""
        results = []

        for task in tasks:
            task_type = task.get("type", "unknown")
            task_fn = task.get("fn")

            if task_fn:
                result = self.evaluate(agent_id, task_type, task_fn)
                results.append(result)

        return self._summarize_benchmark(results)

    def _summarize_benchmark(self, results: list[EvaluationResult]) -> dict:
        """Summarize benchmark results."""
        if not results:
            return {}

        success_rate = sum(1 for r in results if r.success) / len(results)
        avg_score = sum(r.score for r in results) / len(results)
        avg_duration = sum(r.duration for r in results) / len(results)
        total_tokens = sum(r.tokens_used for r in results)

        return {
            "total_tasks": len(results),
            "success_rate": success_rate,
            "average_score": avg_score,
            "average_duration": avg_duration,
            "total_tokens": total_tokens,
            "results": [
                {
                    "task_type": r.task_type,
                    "success": r.success,
                    "score": r.score,
                    "duration": r.duration
                }
                for r in results
            ]
        }

    def compare(self, agent_ids: list[str], tasks: list[dict]) -> dict:
        """Compare multiple agents on same tasks."""
        comparison = {}

        for agent_id in agent_ids:
            summary = self.benchmark(agent_id, tasks)
            comparison[agent_id] = summary

        return comparison
