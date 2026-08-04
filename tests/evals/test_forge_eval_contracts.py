"""Offline contract tests for the ForgeEval reconstruction foundation."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from thegent.forge_eval import (
    ForgeEvalResult,
    ForgeEvalTask,
    JudgeSpec,
    LatencyProfile,
    TaskFamily,
)

pytestmark = pytest.mark.requirement("FR-FORGEEVAL-001")


def test_task_round_trips_with_versioned_schema() -> None:
    task = ForgeEvalTask(
        id="tbench-filesystem-001",
        family=TaskFamily.TERMINAL_BENCH_2,
        title="Repair a constrained filesystem workflow",
        instruction="Implement the requested behavior and verify it locally.",
        timeout_seconds=240,
        tags=("coding", "long-horizon"),
    )

    restored = ForgeEvalTask.model_validate_json(task.model_dump_json())

    assert restored == task
    assert task.schema_version == "forgeeval.task.v1"


def test_task_rejects_non_positive_timeout() -> None:
    with pytest.raises(ValidationError):
        ForgeEvalTask(
            id="deep-swe-001",
            family=TaskFamily.DEEP_SWE,
            title="Repair a defect",
            instruction="Repair it.",
            timeout_seconds=0,
        )


def test_judge_is_declared_but_never_contains_a_credential() -> None:
    judge = JudgeSpec(model="inclusionai/ling-2.6-flash")

    assert judge.schema_version == "forgeeval.judge.v1"
    assert judge.transport == "openrouter"
    assert "token" not in judge.model_dump()


def test_result_requires_task_and_profile_contracts() -> None:
    task = ForgeEvalTask(
        id="custom-contract-001",
        family=TaskFamily.CUSTOM,
        title="Validate a contract",
        instruction="Use local fixtures only.",
    )
    result = ForgeEvalResult(
        task=task,
        run_id="offline-smoke-001",
        harness="forgecode",
        candidate_model="offline-fixture",
        started_at=datetime(2026, 8, 4, tzinfo=UTC),
        completed_at=datetime(2026, 8, 4, 0, 0, 1, tzinfo=UTC),
        succeeded=True,
        latency=LatencyProfile(
            wall_time_seconds=1.0,
            time_to_first_token_seconds=0.2,
            output_tokens=42,
        ),
    )

    assert result.schema_version == "forgeeval.result.v1"
    assert result.latency.tokens_per_second == pytest.approx(42.0)


def test_result_rejects_completion_before_start() -> None:
    task = ForgeEvalTask(
        id="custom-contract-002",
        family=TaskFamily.CUSTOM,
        title="Validate ordering",
        instruction="Use local fixtures only.",
    )
    with pytest.raises(ValidationError, match="completed_at"):
        ForgeEvalResult(
            task=task,
            run_id="offline-smoke-002",
            harness="forgecode",
            candidate_model="offline-fixture",
            started_at=datetime(2026, 8, 4, 0, 0, 1, tzinfo=UTC),
            completed_at=datetime(2026, 8, 4, tzinfo=UTC),
            succeeded=False,
            latency=LatencyProfile(wall_time_seconds=1.0),
        )
