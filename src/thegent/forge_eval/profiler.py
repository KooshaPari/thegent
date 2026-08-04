"""Deterministic, async-safe profiling for future ForgeEval execution adapters."""

from __future__ import annotations

import asyncio
import math
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from time import perf_counter

from pydantic import BaseModel, ConfigDict, Field, model_validator

from thegent.forge_eval.contracts import ForgeEvalTask

TaskExecutor = Callable[[ForgeEvalTask], Awaitable[object]]
Clock = Callable[[], float]


@dataclass
class _ConcurrencyState:
    """Mutable accounting scoped to one profiling invocation."""

    active: int = 0
    peak: int = 0


class ProfileStatus(StrEnum):
    """Terminal states recorded for each profiled task."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMED_OUT = "timed-out"


class ProfileLatencySummary(BaseModel):
    """Nearest-rank latency percentiles over completed task executions."""

    model_config = ConfigDict(frozen=True)

    p50_seconds: float = Field(ge=0)
    p90_seconds: float = Field(ge=0)
    p99_seconds: float = Field(ge=0)


class ProfiledTask(BaseModel):
    """A sanitized per-task observation from one profiled execution."""

    model_config = ConfigDict(frozen=True)

    task_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{2,127}$")
    status: ProfileStatus
    wall_time_seconds: float = Field(ge=0)
    error_type: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def validate_error_state(self) -> ProfiledTask:
        """Keep error metadata minimal, sanitized, and unambiguous."""
        if self.status is ProfileStatus.SUCCEEDED and self.error_type is not None:
            raise ValueError("successful tasks must not have an error_type")
        if self.status is not ProfileStatus.SUCCEEDED and self.error_type is None:
            raise ValueError("failed or timed-out tasks require an error_type")
        return self


class ForgeEvalProfile(BaseModel):
    """Stable structured evidence for one bounded concurrent profiling run."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = "forgeeval.profile.v1"
    requested_concurrency: int = Field(ge=1, le=128)
    peak_concurrency: int = Field(ge=0, le=128)
    elapsed_seconds: float = Field(ge=0)
    throughput_tasks_per_second: float = Field(ge=0)
    total_tasks: int = Field(ge=0)
    succeeded_tasks: int = Field(ge=0)
    failed_tasks: int = Field(ge=0)
    timed_out_tasks: int = Field(ge=0)
    latency: ProfileLatencySummary
    tasks: tuple[ProfiledTask, ...]

    @model_validator(mode="after")
    def validate_accounting(self) -> ForgeEvalProfile:
        """Ensure aggregate counts exactly represent stable per-task evidence."""
        if len(self.tasks) != self.total_tasks:
            raise ValueError("total_tasks must equal the number of task observations")
        if len({task.task_id for task in self.tasks}) != len(self.tasks):
            raise ValueError("profile task observations must have unique task_id values")
        succeeded = sum(task.status is ProfileStatus.SUCCEEDED for task in self.tasks)
        failed = sum(task.status is ProfileStatus.FAILED for task in self.tasks)
        timed_out = sum(task.status is ProfileStatus.TIMED_OUT for task in self.tasks)
        if (succeeded, failed, timed_out) != (self.succeeded_tasks, self.failed_tasks, self.timed_out_tasks):
            raise ValueError("aggregate task status counts do not match task observations")
        if self.peak_concurrency > self.requested_concurrency:
            raise ValueError("peak_concurrency must not exceed requested_concurrency")
        return self


def nearest_rank_percentile(samples: Sequence[float], percentile: float) -> float:
    """Return a deterministic nearest-rank percentile, or zero for no samples."""
    if not 0 < percentile <= 1:
        raise ValueError("percentile must be greater than zero and at most one")
    if not samples:
        return 0.0
    if any(sample < 0 for sample in samples):
        raise ValueError("latency samples must be non-negative")
    ordered = sorted(samples)
    return ordered[math.ceil(percentile * len(ordered)) - 1]


class ConcurrentProfiler:
    """Profile an async adapter with bounded concurrency and monotonic timing."""

    def __init__(self, concurrency: int, *, clock: Clock = perf_counter) -> None:
        if isinstance(concurrency, bool) or not 1 <= concurrency <= 128:
            raise ValueError("concurrency must be an integer from 1 through 128")
        self._concurrency = concurrency
        self._clock = clock

    async def profile(
        self,
        tasks: Sequence[ForgeEvalTask],
        executor: TaskExecutor,
    ) -> ForgeEvalProfile:
        """Run each task once, preserving input order while bounding active work."""
        self._validate_task_ids(tasks)
        started_at = self._clock()
        state = _ConcurrencyState()
        observations = await self._run_all(tasks, executor, state)
        elapsed_seconds = self._elapsed_since(started_at)
        return ForgeEvalProfile(
            requested_concurrency=self._concurrency,
            peak_concurrency=state.peak,
            elapsed_seconds=elapsed_seconds,
            throughput_tasks_per_second=self._throughput(len(observations), elapsed_seconds),
            total_tasks=len(observations),
            succeeded_tasks=sum(item.status is ProfileStatus.SUCCEEDED for item in observations),
            failed_tasks=sum(item.status is ProfileStatus.FAILED for item in observations),
            timed_out_tasks=sum(item.status is ProfileStatus.TIMED_OUT for item in observations),
            latency=self._latency_summary(observations),
            tasks=observations,
        )

    async def _run_all(
        self,
        tasks: Sequence[ForgeEvalTask],
        executor: TaskExecutor,
        state: _ConcurrencyState,
    ) -> tuple[ProfiledTask, ...]:
        semaphore = asyncio.Semaphore(self._concurrency)
        observations = await asyncio.gather(*(self._run_task(task, executor, semaphore, state) for task in tasks))
        return tuple(observations)

    async def _run_task(
        self,
        task: ForgeEvalTask,
        executor: TaskExecutor,
        semaphore: asyncio.Semaphore,
        state: _ConcurrencyState,
    ) -> ProfiledTask:
        async with semaphore:
            state.active += 1
            state.peak = max(state.peak, state.active)
            task_started_at = self._clock()
            try:
                await asyncio.wait_for(executor(task), timeout=task.timeout_seconds)
            except TimeoutError:
                status, error_type = ProfileStatus.TIMED_OUT, "TimeoutError"
            except Exception as exc:
                status, error_type = ProfileStatus.FAILED, type(exc).__name__
            else:
                status, error_type = ProfileStatus.SUCCEEDED, None
            finally:
                state.active -= 1
        return ProfiledTask(
            task_id=task.id,
            status=status,
            wall_time_seconds=self._elapsed_since(task_started_at),
            error_type=error_type,
        )

    def _elapsed_since(self, started_at: float) -> float:
        return max(0.0, self._clock() - started_at)

    @staticmethod
    def _throughput(total_tasks: int, elapsed_seconds: float) -> float:
        if not total_tasks or elapsed_seconds == 0:
            return 0.0
        return total_tasks / elapsed_seconds

    @staticmethod
    def _validate_task_ids(tasks: Sequence[ForgeEvalTask]) -> None:
        task_ids = tuple(task.id for task in tasks)
        if len(set(task_ids)) != len(task_ids):
            raise ValueError("profile tasks must have unique task ids")

    @staticmethod
    def _latency_summary(observations: Sequence[ProfiledTask]) -> ProfileLatencySummary:
        samples = tuple(observation.wall_time_seconds for observation in observations)
        return ProfileLatencySummary(
            p50_seconds=nearest_rank_percentile(samples, 0.50),
            p90_seconds=nearest_rank_percentile(samples, 0.90),
            p99_seconds=nearest_rank_percentile(samples, 0.99),
        )
