"""Deterministic, network-free tests for concurrent ForgeEval profiling."""

from __future__ import annotations

import asyncio

import pytest

from thegent.forge_eval import ForgeEvalTask, load_bundled_catalog
from thegent.forge_eval.profiler import ConcurrentProfiler, ProfileStatus, nearest_rank_percentile

pytestmark = pytest.mark.requirement("FR-FORGEEVAL-003")


@pytest.mark.asyncio
async def test_profiler_returns_a_stable_empty_profile() -> None:
    async def executor(task: ForgeEvalTask) -> None:
        raise AssertionError("an empty profile must not invoke the executor")

    profile = await ConcurrentProfiler(concurrency=2).profile((), executor)

    assert profile.schema_version == "forgeeval.profile.v1"
    assert profile.requested_concurrency == 2
    assert profile.peak_concurrency == 0
    assert profile.total_tasks == 0
    assert profile.throughput_tasks_per_second == 0.0
    assert profile.latency.p50_seconds == 0.0


def test_nearest_rank_percentiles_are_deterministic_for_unsorted_samples() -> None:
    samples = (5.0, 1.0, 3.0, 2.0, 4.0)

    assert nearest_rank_percentile(samples, 0.50) == 3.0
    assert nearest_rank_percentile(samples, 0.90) == 5.0
    assert nearest_rank_percentile(samples, 0.99) == 5.0
    assert nearest_rank_percentile((), 0.50) == 0.0


@pytest.mark.asyncio
async def test_profiler_bounds_concurrency_and_preserves_input_order() -> None:
    tasks = tuple(fixture.task for fixture in load_bundled_catalog().fixtures)
    two_tasks_started = asyncio.Event()
    release = asyncio.Event()
    active = 0
    maximum_active = 0

    async def executor(task: ForgeEvalTask) -> None:
        nonlocal active, maximum_active
        active += 1
        maximum_active = max(maximum_active, active)
        if active == 2:
            two_tasks_started.set()
        await release.wait()
        active -= 1

    profiler = ConcurrentProfiler(concurrency=2)
    profile_task = asyncio.create_task(profiler.profile(tasks, executor))
    await asyncio.wait_for(two_tasks_started.wait(), timeout=1)
    assert active == 2
    release.set()
    profile = await profile_task

    assert maximum_active == 2
    assert profile.peak_concurrency == 2
    assert tuple(item.task_id for item in profile.tasks) == tuple(task.id for task in tasks)
    assert [item.status for item in profile.tasks] == [ProfileStatus.SUCCEEDED] * 3
    assert profile.model_dump(mode="json")["tasks"][0]["task_id"] == tasks[0].id


@pytest.mark.asyncio
async def test_profiler_accounts_for_success_failure_and_timeout_per_task() -> None:
    fixture_tasks = tuple(fixture.task for fixture in load_bundled_catalog().fixtures)
    fast_task, failing_task, slow_task = fixture_tasks
    slow_task = slow_task.model_copy(update={"timeout_seconds": 1})

    async def executor(task: ForgeEvalTask) -> None:
        if task.id == failing_task.id:
            raise RuntimeError("sensitive detail must not enter profile evidence")
        if task.id == slow_task.id:
            await asyncio.sleep(2)

    profile = await ConcurrentProfiler(concurrency=3).profile((fast_task, failing_task, slow_task), executor)

    assert (profile.succeeded_tasks, profile.failed_tasks, profile.timed_out_tasks) == (1, 1, 1)
    assert [item.status for item in profile.tasks] == [
        ProfileStatus.SUCCEEDED,
        ProfileStatus.FAILED,
        ProfileStatus.TIMED_OUT,
    ]
    assert profile.tasks[1].error_type == "RuntimeError"
    assert profile.tasks[2].error_type == "TimeoutError"
    assert "sensitive detail" not in profile.model_dump_json()
    assert profile.latency.p50_seconds <= profile.latency.p90_seconds <= profile.latency.p99_seconds


@pytest.mark.asyncio
async def test_profiler_rejects_ambiguous_duplicate_task_ids_before_execution() -> None:
    source_task = load_bundled_catalog().fixtures[0].task
    calls = 0

    async def executor(task: ForgeEvalTask) -> None:
        nonlocal calls
        calls += 1

    with pytest.raises(ValueError, match="unique task ids"):
        await ConcurrentProfiler(concurrency=1).profile((source_task, source_task), executor)

    assert calls == 0


def test_profiler_rejects_invalid_concurrency_and_percentiles() -> None:
    with pytest.raises(ValueError, match="concurrency"):
        ConcurrentProfiler(concurrency=0)
    with pytest.raises(ValueError, match="concurrency"):
        ConcurrentProfiler(concurrency=True)
    with pytest.raises(ValueError, match="percentile"):
        nearest_rank_percentile((1.0,), 0.0)
    with pytest.raises(ValueError, match="non-negative"):
        nearest_rank_percentile((-1.0,), 0.5)
