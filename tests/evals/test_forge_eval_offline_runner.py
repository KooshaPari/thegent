"""Deterministic, network-free tests for the ForgeEval fixture runner."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from thegent.forge_eval import (
    ForgeEvalCatalog,
    ForgeEvalResultStore,
    ForgeEvalTask,
    LatencyProfile,
    OfflineCheck,
    OfflineFixtureRunner,
    OfflineRunError,
    OfflineRunRequest,
    ResultStoreError,
    TaskFamily,
    load_bundled_catalog,
)
from thegent.forge_eval.catalog import FixtureProvenance, OfflineTaskFixture

pytestmark = pytest.mark.requirement("FR-FORGEEVAL-002")


def _request(*, run_id: str = "offline-tbench2-run-001", passed: bool = True) -> OfflineRunRequest:
    return OfflineRunRequest(
        run_id=run_id,
        task_id="tbench2-fixture-filesystem-contract",
        harness="offline-fixture-runner",
        candidate_model="observation-packet-v1",
        started_at=datetime(2026, 8, 4, tzinfo=UTC),
        completed_at=datetime(2026, 8, 4, 0, 0, 2, tzinfo=UTC),
        latency=LatencyProfile(wall_time_seconds=2.0, output_tokens=4),
        checks=(
            OfflineCheck(check_id="workspace-layout", passed=passed),
            OfflineCheck(check_id="expected-file-contents", passed=True),
            OfflineCheck(check_id="verification-recorded", passed=True),
        ),
    )


def test_bundled_catalog_has_one_synthetic_fixture_for_each_task_family() -> None:
    catalog = load_bundled_catalog()

    assert catalog.schema_version == "forgeeval.catalog.v1"
    assert {fixture.task.family for fixture in catalog.fixtures} == set(TaskFamily)
    assert all(fixture.provenance.source_kind == "synthetic-fixture" for fixture in catalog.fixtures)
    assert all(not fixture.provenance.is_upstream_task for fixture in catalog.fixtures)
    assert all(not fixture.task.requires_network for fixture in catalog.fixtures)


def test_runner_persists_a_successful_unjudged_offline_observation(tmp_path) -> None:
    store = ForgeEvalResultStore(tmp_path / "results.jsonl")
    runner = OfflineFixtureRunner(load_bundled_catalog(), store)

    result = runner.run(_request())

    assert result.succeeded is True
    assert result.judge is None
    assert result.judge_score is None
    assert result.failure_reason is None
    assert store.read_all() == (result,)


def test_runner_persists_failure_reason_from_false_required_check(tmp_path) -> None:
    store = ForgeEvalResultStore(tmp_path / "results.jsonl")
    runner = OfflineFixtureRunner(load_bundled_catalog(), store)

    result = runner.run(_request(passed=False))

    assert result.succeeded is False
    assert result.failure_reason == "failed required checks: workspace-layout"
    assert store.read_all()[0].run_id == result.run_id


def test_runner_rejects_missing_or_unexpected_fixture_checks(tmp_path) -> None:
    store = ForgeEvalResultStore(tmp_path / "results.jsonl")
    runner = OfflineFixtureRunner(load_bundled_catalog(), store)
    request = _request().model_copy(
        update={
            "checks": (
                OfflineCheck(check_id="workspace-layout", passed=True),
                OfflineCheck(check_id="unrecognized-check", passed=True),
            )
        }
    )

    with pytest.raises(OfflineRunError, match="check contract mismatch"):
        runner.run(request)

    assert store.read_all() == ()


def test_runner_rejects_duplicate_persisted_run_id(tmp_path) -> None:
    store = ForgeEvalResultStore(tmp_path / "results.jsonl")
    runner = OfflineFixtureRunner(load_bundled_catalog(), store)
    runner.run(_request())

    with pytest.raises(ResultStoreError, match="already exists"):
        runner.run(_request())


def test_request_rejects_duplicate_check_identifiers() -> None:
    request_data = _request().model_dump()
    request_data["checks"] = [
        {"check_id": "workspace-layout", "passed": True},
        {"check_id": "workspace-layout", "passed": False},
    ]

    with pytest.raises(ValidationError, match="unique check_id"):
        OfflineRunRequest.model_validate(request_data)


def test_request_rejects_credential_like_identifier_values() -> None:
    request_data = _request().model_dump()
    request_data["candidate_model"] = "sk-not-a-model"

    with pytest.raises(ValidationError, match="credential-like"):
        OfflineRunRequest.model_validate(request_data)


def test_runner_rejects_network_required_fixture(tmp_path) -> None:
    source_fixture = load_bundled_catalog().get("tbench2-fixture-filesystem-contract")
    network_task = ForgeEvalTask.model_validate(source_fixture.task.model_dump() | {"requires_network": True})
    catalog = ForgeEvalCatalog(
        catalog_id="network-fixture-catalog",
        fixtures=(
            OfflineTaskFixture(
                task=network_task,
                required_checks=source_fixture.required_checks,
                provenance=FixtureProvenance(
                    source_kind="synthetic-fixture",
                    source_reference="test/network",
                    license_spdx="CC0-1.0",
                ),
            ),
        ),
    )
    runner = OfflineFixtureRunner(catalog, ForgeEvalResultStore(tmp_path / "results.jsonl"))

    with pytest.raises(OfflineRunError, match="network-required"):
        runner.run(_request())


def test_result_store_rejects_invalid_jsonl_evidence(tmp_path) -> None:
    path = tmp_path / "results.jsonl"
    path.write_text("not-json\n", encoding="utf-8")

    with pytest.raises(ResultStoreError, match="invalid result"):
        ForgeEvalResultStore(path).read_all()
