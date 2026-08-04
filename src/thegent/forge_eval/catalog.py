"""Validated, offline ForgeEval task catalogs and fixture provenance."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from thegent.forge_eval.contracts import ForgeEvalTask


class CatalogError(ValueError):
    """Raised when an offline catalog cannot be loaded or queried safely."""


class FixtureProvenance(BaseModel):
    """Provenance for a fixture without claiming it is an upstream benchmark task."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = "forgeeval.fixture-provenance.v1"
    source_kind: str = Field(pattern=r"^synthetic-fixture$")
    source_reference: str = Field(min_length=1, max_length=200)
    license_spdx: str = Field(pattern=r"^[A-Za-z0-9.-]+$")
    is_upstream_task: bool = False

    @model_validator(mode="after")
    def reject_upstream_claims(self) -> FixtureProvenance:
        """Keep clean-room fixtures distinct from unverified benchmark corpora."""
        if self.is_upstream_task:
            raise ValueError("offline fixtures must not claim upstream task provenance")
        return self


class OfflineTaskFixture(BaseModel):
    """A deterministic local evaluation fixture and its required observations."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = "forgeeval.fixture.v1"
    task: ForgeEvalTask
    required_checks: tuple[str, ...] = Field(min_length=1)
    provenance: FixtureProvenance

    @field_validator("required_checks")
    @classmethod
    def validate_required_checks(cls, checks: tuple[str, ...]) -> tuple[str, ...]:
        """Require stable check identifiers with no duplicated evidence keys."""
        normalized = tuple(check.strip() for check in checks)
        if any(not check or not check.replace("-", "").isalnum() for check in normalized):
            raise ValueError("required_checks must contain lowercase hyphenated identifiers")
        if any(check != check.lower() for check in normalized):
            raise ValueError("required_checks must be lowercase")
        if len(set(normalized)) != len(normalized):
            raise ValueError("required_checks must be unique")
        return normalized


class ForgeEvalCatalog(BaseModel):
    """Versioned collection of offline fixtures keyed by stable task identifiers."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = "forgeeval.catalog.v1"
    catalog_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{2,127}$")
    fixtures: tuple[OfflineTaskFixture, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_task_ids(self) -> ForgeEvalCatalog:
        """Reject ambiguous fixtures before an evaluation can start."""
        task_ids = tuple(fixture.task.id for fixture in self.fixtures)
        if len(set(task_ids)) != len(task_ids):
            raise ValueError("catalog fixture task ids must be unique")
        return self

    def get(self, task_id: str) -> OfflineTaskFixture:
        """Return one fixture or raise a clear error for an unknown task."""
        for fixture in self.fixtures:
            if fixture.task.id == task_id:
                return fixture
        raise CatalogError(f"task {task_id!r} is not present in catalog {self.catalog_id!r}")


def bundled_catalog_path() -> Path:
    """Return the package-local, versioned catalog fixture path."""
    return Path(__file__).with_name("fixtures") / "offline-catalog.v1.json"


def load_catalog(path: Path) -> ForgeEvalCatalog:
    """Load one local JSON catalog without performing any network access."""
    try:
        raw_catalog = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CatalogError(f"cannot read catalog {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise CatalogError(f"catalog {path} is not valid JSON: {exc.msg}") from exc
    return ForgeEvalCatalog.model_validate(raw_catalog)


def load_bundled_catalog() -> ForgeEvalCatalog:
    """Load the explicit synthetic fixture catalog bundled with ForgeEval."""
    return load_catalog(bundled_catalog_path())
