"""Metrics collection and provider performance tracking.

This module provides the ProviderMetricsCollector for tracking execution
metrics across providers and the ExecutionResult data model.
"""

import asyncio
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


@dataclass
class ExecutionResult:
    """Represents a single execution result from a provider.

    Attributes:
        provider_id: Identifier of the provider that executed the task
        timestamp: When the execution occurred
        success: Whether the execution was successful
        latency_ms: Execution time in milliseconds
        tokens_input: Number of input tokens
        tokens_output: Number of output tokens
        error_msg: Error message if execution failed
        task_type: Optional task type for filtering
        cost_usd: Optional cost in USD
        quality_score: Optional quality score (0.0-1.0)
        metadata: Additional execution metadata
    """

    provider_id: str
    timestamp: datetime
    success: bool
    latency_ms: float
    tokens_input: int = 0
    tokens_output: int = 0
    error_msg: Optional[str] = None
    task_type: Optional[str] = None
    cost_usd: float = 0.0
    quality_score: Optional[float] = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate the execution result."""
        if self.latency_ms < 0:
            raise ValueError("latency_ms cannot be negative")
        if self.cost_usd < 0:
            raise ValueError("cost_usd cannot be negative")
        if self.quality_score is not None:
            if not 0.0 <= self.quality_score <= 1.0:
                raise ValueError("quality_score must be between 0.0 and 1.0")

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "provider_id": self.provider_id,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "latency_ms": self.latency_ms,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "error_msg": self.error_msg,
            "task_type": self.task_type,
            "cost_usd": self.cost_usd,
            "quality_score": self.quality_score,
            "metadata": self.metadata,
        }


@dataclass
class AggregatedMetrics:
    """Aggregated metrics for a provider over a time window.

    Attributes:
        provider_id: Identifier of the provider
        task_type: Type of task these metrics apply to
        latency_samples: List of latency measurements
        success_count: Number of successful executions
        failure_count: Number of failed executions
        window_hours: Time window in hours
    """

    provider_id: str
    task_type: Optional[str] = None
    latency_samples: list = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    window_hours: int = 24

    @property
    def total_count(self) -> int:
        """Total number of executions."""
        return self.success_count + self.failure_count

    @property
    def success_rate(self) -> float:
        """Success rate as a fraction (0.0-1.0)."""
        if self.total_count == 0:
            return 0.0
        return self.success_count / self.total_count

    @property
    def latency_p50(self) -> float:
        """50th percentile latency."""
        if not self.latency_samples:
            return 0.0
        sorted_samples = sorted(self.latency_samples)
        idx = int(len(sorted_samples) * 0.50)
        return sorted_samples[min(idx, len(sorted_samples) - 1)]

    @property
    def latency_p95(self) -> float:
        """95th percentile latency."""
        if not self.latency_samples:
            return 0.0
        sorted_samples = sorted(self.latency_samples)
        idx = int(len(sorted_samples) * 0.95)
        return sorted_samples[min(idx, len(sorted_samples) - 1)]

    @property
    def latency_p99(self) -> float:
        """99th percentile latency."""
        if not self.latency_samples:
            return 0.0
        sorted_samples = sorted(self.latency_samples)
        # p99 is at the 99th percentile position (using 0-based indexing)
        idx = int(len(sorted_samples) * 0.99) - 1
        return sorted_samples[max(0, min(idx, len(sorted_samples) - 1))]

    @property
    def avg_latency(self) -> float:
        """Average latency."""
        if not self.latency_samples:
            return 0.0
        return sum(self.latency_samples) / len(self.latency_samples)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "provider_id": self.provider_id,
            "task_type": self.task_type,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "latency_p50": self.latency_p50,
            "latency_p95": self.latency_p95,
            "latency_p99": self.latency_p99,
            "avg_latency": self.avg_latency,
            "window_hours": self.window_hours,
            "timestamp": datetime.now().isoformat(),
        }


class ProviderMetricsCollector:
    """Collects and aggregates metrics from provider executions.

    This collector maintains an in-memory store of execution results and
    provides methods to query aggregated metrics. It also persists
    metrics to local cache files.

    Attributes:
        storage_backend: Storage type ("local" for file-based)

    Example:
        >>> collector = ProviderMetricsCollector()
        >>> result = ExecutionResult(
        ...     provider_id="openai-gpt4",
        ...     timestamp=datetime.now(),
        ...     success=True,
        ...     latency_ms=150.5,
        ...     tokens_input=100,
        ...     tokens_output=50,
        ... )
        >>> await collector.record_execution(result)
        >>> metrics = collector.get_metrics("openai-gpt4")
        >>> print(metrics.latency_p99)
        150.5
    """

    CACHE_DIR = Path("~/.thegent/metrics").expanduser()

    def __init__(self, storage_backend: str = "local"):
        """Initialize the metrics collector.

        Args:
            storage_backend: Storage type ("local" for file-based persistence)
        """
        self.storage_backend = storage_backend
        self.results: dict[str, list[ExecutionResult]] = {}
        self._cache: dict[str, AggregatedMetrics] = {}
        self._cache_dir = self.CACHE_DIR
        if self.storage_backend == "local":
            self._cache_dir.mkdir(parents=True, exist_ok=True)

    async def record_execution(self, result: ExecutionResult) -> None:
        """Record an execution result.

        Args:
            result: The execution result to record.
        """
        provider_id = result.provider_id

        # Initialize provider list if needed
        if provider_id not in self.results:
            self.results[provider_id] = []

        self.results[provider_id].append(result)

        # Invalidate cache for this provider
        if provider_id in self._cache:
            del self._cache[provider_id]

        # Persist to local cache if enabled
        if self.storage_backend == "local":
            await self._persist_result(result)

    async def _persist_result(self, result: ExecutionResult) -> None:
        """Persist a single result to cache file."""
        try:
            today = result.timestamp.strftime("%Y-%m-%d")
            logfile = self._cache_dir / f"metrics_{today}.jsonl"

            async with asyncio.Lock():
                with open(logfile, "a") as f:
                    f.write(json.dumps(result.to_dict()) + "\n")
        except Exception:
            # Silently ignore persistence errors
            pass

    def get_metrics(
        self,
        provider_id: str,
        task_type: Optional[str] = None,
        window_hours: Optional[int] = None,
    ) -> AggregatedMetrics:
        """Get aggregated metrics for a provider.

        Args:
            provider_id: The provider to get metrics for
            task_type: Optional task type filter
            window_hours: Optional time window in hours

        Returns:
            Aggregated metrics for the provider
        """
        cache_key = f"{provider_id}:{task_type}:{window_hours}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Get results for this provider
        results = self.results.get(provider_id, [])

        # Filter by task type if specified
        if task_type is not None:
            results = [r for r in results if r.task_type == task_type]

        # Filter by time window if specified
        if window_hours is not None:
            cutoff = datetime.now() - timedelta(hours=window_hours)
            results = [r for r in results if r.timestamp >= cutoff]

        # Calculate aggregated metrics
        latency_samples = [r.latency_ms for r in results if r.success]
        success_count = sum(1 for r in results if r.success)
        failure_count = sum(1 for r in results if not r.success)

        metrics = AggregatedMetrics(
            provider_id=provider_id,
            task_type=task_type,
            latency_samples=latency_samples,
            success_count=success_count,
            failure_count=failure_count,
            window_hours=window_hours or 24,
        )

        self._cache[cache_key] = metrics
        return metrics

    def get_all_providers_metrics(
        self,
        task_type: Optional[str] = None,
        window_hours: Optional[int] = None,
    ) -> dict[str, AggregatedMetrics]:
        """Get metrics for all providers.

        Args:
            task_type: Optional task type filter
            window_hours: Optional time window in hours

        Returns:
            Dictionary mapping provider_id to their metrics
        """
        all_metrics = {}
        for provider_id in self.results.keys():
            all_metrics[provider_id] = self.get_metrics(
                provider_id, task_type, window_hours
            )
        return all_metrics

    def load_historical_metrics(self, date_str: str) -> dict[str, list[ExecutionResult]]:
        """Load metrics from a specific date's cache file.

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            Dictionary mapping provider_id to list of historical results
        """
        logfile = self._cache_dir / f"metrics_{date_str}.jsonl"
        if not logfile.exists():
            return {}

        historical: dict[str, list[ExecutionResult]] = {}

        try:
            with open(logfile) as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                        result = ExecutionResult(**data)
                        pid = result.provider_id
                        if pid not in historical:
                            historical[pid] = []
                        historical[pid].append(result)
        except Exception:
            pass

        return historical

    def clear(self) -> None:
        """Clear all stored results and cache."""
        self.results.clear()
        self._cache.clear()
