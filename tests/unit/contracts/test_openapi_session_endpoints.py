"""Contract tests for the L15 audit lane expansion — new session endpoints.

Adds pinning for the three endpoints added to ``openapi.yaml`` on
2026-07-29:

* ``GET /thegent_logs`` — fetch session logs.
* ``GET /thegent_ps`` — list sessions.
* ``POST /thegent_resume`` — resume a paused session.

These tests intentionally use :func:`thegent.contracts.openapi_surface`
helpers (``load_spec``, ``path_count``, ``endpoint_count``,
``find_endpoint``) so the same surface that the cockpit / status
commands see is what we exercise here.
"""

from __future__ import annotations

import pytest

from thegent.contracts.openapi_surface import (
    endpoint_count,
    find_endpoint,
    list_endpoint_paths,
    load_spec,
    path_count,
)


@pytest.fixture(scope="module")
def spec() -> dict:
    """Load the vendored spec once per module."""
    return load_spec()


def test_spec_path_count_grew_to_eight_plus(spec: dict) -> None:
    """Adding the three session endpoints grew the surface to >= 8 paths."""
    assert path_count(spec) >= 8, f"only {path_count(spec)} paths declared"


def test_spec_endpoint_count_grew_to_eight_plus(spec: dict) -> None:
    """Total HTTP operations should track path growth (>= 8)."""
    assert endpoint_count(spec) >= 8


def test_logs_endpoint_is_documented(spec: dict) -> None:
    """``GET /thegent_logs`` must be in the spec with query parameters."""
    endpoint = find_endpoint(spec, "/thegent_logs", "get")
    assert endpoint is not None
    params = endpoint.get("parameters") or []
    param_names = {p["name"] for p in params if isinstance(p, dict)}
    assert "session_id" in param_names
    assert "follow" in param_names
    assert "tail" in param_names


def test_logs_endpoint_requires_session_id(spec: dict) -> None:
    """``session_id`` must be a required query parameter on ``/thegent_logs``."""
    endpoint = find_endpoint(spec, "/thegent_logs", "get")
    params = endpoint.get("parameters") or []
    session_param = next(p for p in params if p.get("name") == "session_id")
    assert session_param.get("required") is True


def test_logs_endpoint_references_logs_response_schema(spec: dict) -> None:
    """``/thegent_logs`` 200 response must resolve to ``LogsResponse``."""
    endpoint = find_endpoint(spec, "/thegent_logs", "get")
    response_200 = (endpoint.get("responses") or {})["200"]
    schema_ref = response_200["content"]["application/json"]["schema"]["$ref"]
    assert schema_ref == "#/components/schemas/LogsResponse"


def test_logs_response_schema_exists(spec: dict) -> None:
    """``LogsResponse`` schema must be defined under ``components.schemas``."""
    schemas = (spec.get("components") or {}).get("schemas") or {}
    assert "LogsResponse" in schemas
    logs_schema = schemas["LogsResponse"]
    required = set(logs_schema.get("required") or [])
    assert "session_id" in required
    assert "lines" in required


def test_ps_endpoint_is_documented(spec: dict) -> None:
    """``GET /thegent_ps`` must exist with the full query filter set."""
    endpoint = find_endpoint(spec, "/thegent_ps", "get")
    assert endpoint is not None
    params = endpoint.get("parameters") or []
    param_names = {p["name"] for p in params if isinstance(p, dict)}
    for expected in ("all", "owner", "format", "include_contract"):
        assert expected in param_names


def test_ps_endpoint_format_enum_is_constrained(spec: dict) -> None:
    """``/thegent_ps`` format parameter must accept only text/json/yaml."""
    endpoint = find_endpoint(spec, "/thegent_ps", "get")
    params = endpoint.get("parameters") or []
    format_param = next(p for p in params if p.get("name") == "format")
    enum = (format_param.get("schema") or {}).get("enum")
    assert enum == ["text", "json", "yaml"]


def test_ps_endpoint_references_session_list_response(spec: dict) -> None:
    """``/thegent_ps`` 200 response must resolve to ``SessionListResponse``."""
    endpoint = find_endpoint(spec, "/thegent_ps", "get")
    response_200 = (endpoint.get("responses") or {})["200"]
    schema_ref = response_200["content"]["application/json"]["schema"]["$ref"]
    assert schema_ref == "#/components/schemas/SessionListResponse"


def test_session_list_entry_schema_exists(spec: dict) -> None:
    """``SessionListEntry`` schema must declare status enum including paused."""
    schemas = (spec.get("components") or {}).get("schemas") or {}
    assert "SessionListEntry" in schemas
    entry = schemas["SessionListEntry"]
    status = (entry.get("properties") or {}).get("status")
    enum = status.get("enum") if isinstance(status, dict) else None
    assert enum is not None
    assert "paused" in enum
    assert "running" in enum


def test_resume_endpoint_is_documented(spec: dict) -> None:
    """``POST /thegent_resume`` must declare an ``operationId`` and request body."""
    endpoint = find_endpoint(spec, "/thegent_resume", "post")
    assert endpoint is not None
    assert endpoint.get("operationId") == "thegentResume"
    body = (endpoint.get("requestBody") or {}).get("content") or {}
    assert "application/json" in body


def test_resume_endpoint_references_resume_request_schema(spec: dict) -> None:
    """``/thegent_resume`` request body must resolve to ``ResumeRequest``."""
    endpoint = find_endpoint(spec, "/thegent_resume", "post")
    body = (endpoint.get("requestBody") or {}).get("content") or {}
    schema_ref = body["application/json"]["schema"]["$ref"]
    assert schema_ref == "#/components/schemas/ResumeRequest"


def test_resume_request_schema_requires_session_id(spec: dict) -> None:
    """``ResumeRequest`` schema must require ``session_id``."""
    schemas = (spec.get("components") or {}).get("schemas") or {}
    required = set(schemas["ResumeRequest"].get("required") or [])
    assert "session_id" in required


def test_resume_response_schema_exists(spec: dict) -> None:
    """``ResumeResponse`` schema must require session_id and accepted."""
    schemas = (spec.get("components") or {}).get("schemas") or {}
    required = set(schemas["ResumeResponse"].get("required") or [])
    assert "session_id" in required
    assert "accepted" in required


def test_endpoint_inventory_lists_new_paths(spec: dict) -> None:
    """The new session endpoints must show up in the helper inventory."""
    paths = list_endpoint_paths(spec)
    for expected in ("/thegent_logs", "/thegent_ps", "/thegent_resume"):
        assert expected in paths, f"missing path: {expected}"


def test_validation_error_response_is_reused_by_new_endpoints(spec: dict) -> None:
    """``/thegent_logs`` and ``/thegent_resume`` must both surface 422 errors."""
    for path, verb in (("/thegent_logs", "get"), ("/thegent_resume", "post")):
        endpoint = find_endpoint(spec, path, verb)
        responses = endpoint.get("responses") or {}
        assert "422" in responses, f"{verb.upper()} {path} missing 422 response"


def test_new_endpoints_are_tagged_correctly(spec: dict) -> None:
    """The three new endpoints must belong to ``sessions`` (and ``mcp``)."""
    expected = (
        ("/thegent_logs", "get"),
        ("/thegent_ps", "get"),
        ("/thegent_resume", "post"),
    )
    for path, verb in expected:
        endpoint = find_endpoint(spec, path, verb)
        assert endpoint is not None, f"{verb.upper()} {path} missing"
        tags = set(endpoint.get("tags") or [])
        assert {"mcp", "sessions"}.issubset(tags), f"{verb.upper()} {path} tags {tags}"


def test_logs_endpoint_tail_minimum_is_one(spec: dict) -> None:
    """``/thegent_logs`` ``tail`` parameter must have minimum 1."""
    endpoint = find_endpoint(spec, "/thegent_logs", "get")
    params = endpoint.get("parameters") or []
    tail_param = next(p for p in params if p.get("name") == "tail")
    minimum = (tail_param.get("schema") or {}).get("minimum")
    assert minimum == 1
