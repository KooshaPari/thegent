"""WL-277 artifact schema versioning tests."""

import pytest

from docs_engine.export.json_export import JsonExporter
from thegent.maif.artifacts import MAIF_ARTIFACT_SCHEMA_VERSION, require_supported_schema_version


def test_json_export_requires_schema_version() -> None:
    with pytest.raises(ValueError, match="missing required schema_version"):
        JsonExporter.validate_artifact_schema({"payload_type": "audit-log"})


def test_json_export_rejects_unknown_schema_version() -> None:
    with pytest.raises(ValueError, match="Unsupported artifact schema_version"):
        JsonExporter.validate_artifact_schema({"schema_version": "unknown.v9"})


def test_maif_requires_supported_schema_version() -> None:
    resolved = require_supported_schema_version({"schema_version": MAIF_ARTIFACT_SCHEMA_VERSION})
    assert resolved == MAIF_ARTIFACT_SCHEMA_VERSION
