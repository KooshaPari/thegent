"""WL-276 artifact redaction pipeline tests."""

from docs_engine.export.json_export import ARTIFACT_SCHEMA_VERSION, JsonExporter
from thegent.integrations.confidential_report import ConfidentialReportFilter


def test_redacts_sensitive_keys_and_token_values() -> None:
    payload = {
        "api_key": "abc",
        "nested": {"notes": "Bearer secret-token-123456789"},
        "safe": "ok",
    }
    redacted = ConfidentialReportFilter.redact_artifact_payload(payload)
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["nested"]["notes"] == "[REDACTED]"
    assert redacted["safe"] == "ok"


def test_json_export_wraps_with_redacted_records() -> None:
    exporter = object.__new__(JsonExporter)
    exporter.schema_version = ARTIFACT_SCHEMA_VERSION
    payload = exporter._wrap_payload("audit-log", [{"token": "ghp_abcdef123456"}])
    assert payload["schema_version"] == ARTIFACT_SCHEMA_VERSION
    assert payload["records"][0]["token"] == "[REDACTED]"
