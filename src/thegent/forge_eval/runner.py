"""Deterministic runner for local ForgeEval fixture observations only."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from thegent.forge_eval.catalog import ForgeEvalCatalog
from thegent.forge_eval.contracts import ForgeEvalResult, LatencyProfile
from thegent.forge_eval.store import ForgeEvalResultStore

_SENSITIVE_MARKERS = ("api_key", "apikey", "bearer", "secret", "token", "sk-")


class OfflineRunError(ValueError):
    """Raised when a local observation packet cannot be evaluated safely."""


class OfflineCheck(BaseModel):
    """One explicitly named, boolean local observation for a fixture run."""

    model_config = ConfigDict(frozen=True)

    check_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{2,127}$")
    passed: bool


class OfflineRunRequest(BaseModel):
    """Validated input to the deterministic offline fixture runner."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = "forgeeval.offline-run-request.v1"
    run_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{2,127}$")
    task_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{2,127}$")
    harness: str = Field(min_length=1, max_length=200)
    candidate_model: str = Field(min_length=1, max_length=200)
    started_at: datetime
    completed_at: datetime
    latency: LatencyProfile
    checks: tuple[OfflineCheck, ...] = Field(min_length=1)

    @field_validator("checks")
    @classmethod
    def validate_unique_checks(cls, checks: tuple[OfflineCheck, ...]) -> tuple[OfflineCheck, ...]:
        """Keep each recorded observation unambiguous."""
        if len({check.check_id for check in checks}) != len(checks):
            raise ValueError("checks must have unique check_id values")
        return checks

    @field_validator("harness", "candidate_model")
    @classmethod
    def reject_sensitive_identifiers(cls, value: str) -> str:
        """Prevent accidental credential persistence in identifier-only fields."""
        if any(marker in value.lower() for marker in _SENSITIVE_MARKERS):
            raise ValueError("identifier fields must not contain credential-like values")
        return value

    @model_validator(mode="after")
    def validate_timestamps(self) -> OfflineRunRequest:
        """Reject impossible local observations before persistence."""
        if self.completed_at < self.started_at:
            raise ValueError("completed_at must not precede started_at")
        return self


class OfflineFixtureRunner:
    """Evaluate exact local assertion packets and persist unjudged results."""

    def __init__(self, catalog: ForgeEvalCatalog, store: ForgeEvalResultStore) -> None:
        self._catalog = catalog
        self._store = store

    def run(self, request: OfflineRunRequest) -> ForgeEvalResult:
        """Validate one fixture observation packet and record its unjudged result."""
        fixture = self._catalog.get(request.task_id)
        if fixture.task.requires_network:
            raise OfflineRunError("offline fixture runner rejects network-required tasks")
        self._validate_check_contract(fixture.required_checks, request.checks)
        failed_checks = tuple(check.check_id for check in request.checks if not check.passed)
        result = ForgeEvalResult(
            task=fixture.task,
            run_id=request.run_id,
            harness=request.harness,
            candidate_model=request.candidate_model,
            started_at=request.started_at,
            completed_at=request.completed_at,
            succeeded=not failed_checks,
            latency=request.latency,
            failure_reason=self._failure_reason(failed_checks),
        )
        self._store.append(result)
        return result

    @staticmethod
    def _validate_check_contract(required_checks: tuple[str, ...], checks: tuple[OfflineCheck, ...]) -> None:
        observed_ids = {check.check_id for check in checks}
        required_ids = set(required_checks)
        if observed_ids != required_ids:
            missing = sorted(required_ids - observed_ids)
            unexpected = sorted(observed_ids - required_ids)
            raise OfflineRunError(f"check contract mismatch: missing={missing}, unexpected={unexpected}")

    @staticmethod
    def _failure_reason(failed_checks: tuple[str, ...]) -> str | None:
        if not failed_checks:
            return None
        return f"failed required checks: {', '.join(failed_checks)}"
