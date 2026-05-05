"""Tests for governance task classifier loader and rules."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="Module not implemented")

from pathlib import Path

from thegent.governance.task_classifier import (
    TaskClassifierError,
    classify,
    load_schema,
    validate_classification_payload,
)


def test_schema_loads_and_is_strict() -> None:
    schema = load_schema()
    assert schema.fields, "missing fields"
    assert schema.outputs


def test_validate_payload_accepts_required_fields() -> None:
    schema = load_schema()
    payload = {
        "task_id": "W78-A01",
        "title": "Add worktree job",
        "domain": "infra",
        "scale": "XS",
        "risk": "low",
        "coupling": "isolated",
        "runtime_profile": "interactive",
        "validation_depth": ["lint", "unit"],
        "overlap_risk": 12,
    }
    validate_classification_payload(payload, schema)


def test_validate_payload_rejects_invalid_enum() -> None:
    schema = load_schema()
    payload = {
        "task_id": "W78-A02",
        "title": "Bad enum",
        "domain": "infra",
        "scale": "BLAH",
        "risk": "low",
        "coupling": "isolated",
        "runtime_profile": "interactive",
        "validation_depth": ["lint"],
        "overlap_risk": 20,
    }

    with pytest.raises(TaskClassifierError):
        validate_classification_payload(payload, schema)


def test_validate_payload_rejects_range_violation() -> None:
    schema = load_schema()
    payload = {
        "task_id": "W78-A03",
        "title": "Range violation",
        "domain": "infra",
        "scale": "XS",
        "risk": "low",
        "coupling": "isolated",
        "runtime_profile": "interactive",
        "validation_depth": ["lint"],
        "overlap_risk": 120,
    }

    with pytest.raises(TaskClassifierError):
        validate_classification_payload(payload, schema)


def test_classify_adds_required_gates_for_high_risk() -> None:
    payload = {
        "task_id": "W78-B01",
        "title": "High-risk control surface",
        "domain": "security",
        "scale": "M",
        "risk": "high",
        "coupling": "cross_module",
        "runtime_profile": "mixed",
        "validation_depth": ["lint", "unit", "security", "integration"],
        "overlap_risk": 55,
    }
    metadata, result = classify(payload)

    assert metadata.risk == "high"
    assert result.delegation_tier == "L3_specialist"
    assert "security" in result.required_gates
    assert result.worker_count >= 3


def test_classify_applies_escalation_worktree_mode() -> None:
    payload = {
        "task_id": "W78-B02",
        "title": "Cross-repo concurrency",
        "domain": "infra",
        "scale": "XL",
        "risk": "medium",
        "coupling": "cross_repo",
        "runtime_profile": "io_heavy",
        "validation_depth": ["lint", "unit"],
        "overlap_risk": 80,
    }

    _, result = classify(payload)
    assert result.worktree_mode == "burst_isolated"


def test_classify_rejects_invalid_scale_definition() -> None:
    with pytest.raises(TaskClassifierError):
        load_schema(schema_path=Path("/tmp/does-not-exist.yaml"))


def test_load_schema_required_identifiers() -> None:
    schema = load_schema()
    assert schema.payload.get("version") is not None
    assert schema.payload.get("name") is not None


def test_validate_payload_missing_required_field() -> None:
    schema = load_schema()
    payload = {
        "task_id": "W78-B03",
        "title": "Missing field",
        "domain": "infra",
        # scale intentionally missing
        "risk": "low",
        "coupling": "isolated",
        "runtime_profile": "interactive",
        "validation_depth": ["lint"],
        "overlap_risk": 5,
    }

    with pytest.raises(TaskClassifierError):
        validate_classification_payload(payload, schema)
