"""Tests for thegent.phenotype.cliproxy_models_check.

Traces to: FR-AGT-004, FR-AGT-006
"""

from __future__ import annotations

import json

import pytest

from thegent.phenotype.cliproxy_models_check import (
    extract_model_ids,
    models_url,
    run_check,
)


@pytest.mark.requirement("FR-AGT-004")
def test_extract_model_ids_openai_data_shape() -> None:
    payload = {
        "object": "list",
        "data": [{"id": "minimax-m2.7-highspeed", "object": "model"}],
    }
    assert extract_model_ids(payload) == ["minimax-m2.7-highspeed"]


@pytest.mark.requirement("FR-AGT-004")
def test_extract_model_ids_legacy_models_key() -> None:
    payload = {"object": "list", "models": [{"id": "a"}, {"id": "b"}]}
    assert extract_model_ids(payload) == ["a", "b"]


@pytest.mark.requirement("FR-AGT-004")
def test_extract_model_ids_prefers_data_over_models() -> None:
    payload = {"data": [{"id": "x"}], "models": [{"id": "y"}]}
    assert extract_model_ids(payload) == ["x"]


@pytest.mark.requirement("FR-AGT-006")
def test_models_url_with_v1_suffix() -> None:
    assert models_url("http://127.0.0.1:8317/v1") == "http://127.0.0.1:8317/v1/models"
    assert models_url("http://127.0.0.1:8317/v1/") == "http://127.0.0.1:8317/v1/models"


@pytest.mark.requirement("FR-AGT-006")
def test_models_url_host_only() -> None:
    assert models_url("http://127.0.0.1:8317") == "http://127.0.0.1:8317/v1/models"


@pytest.mark.requirement("FR-AGT-006")
def test_run_check_success(monkeypatch: pytest.MonkeyPatch) -> None:
    body = json.dumps(
        {"object": "list", "data": [{"id": "minimax-m2.7-highspeed"}]},
    ).encode()

    class _Resp:
        def read(self) -> bytes:
            return body

        def __enter__(self) -> _Resp:
            return self

        def __exit__(self, *a: object) -> None:
            return None

    monkeypatch.setattr(
        "thegent.phenotype.cliproxy_models_check.urllib.request.urlopen",
        lambda *a, **k: _Resp(),
    )
    code, msg = run_check("http://x/v1", ["minimax-m2.7-highspeed"], bearer=None, timeout=1.0)
    assert code == 0
    assert "OK" in msg


@pytest.mark.requirement("FR-AGT-006")
def test_run_check_missing_id(monkeypatch: pytest.MonkeyPatch) -> None:
    body = json.dumps({"object": "list", "data": [{"id": "other"}]}).encode()

    class _Resp:
        def read(self) -> bytes:
            return body

        def __enter__(self) -> _Resp:
            return self

        def __exit__(self, *a: object) -> None:
            return None

    monkeypatch.setattr(
        "thegent.phenotype.cliproxy_models_check.urllib.request.urlopen",
        lambda *a, **k: _Resp(),
    )
    code, msg = run_check("http://x/v1", ["minimax-m2.7-highspeed"], bearer=None, timeout=1.0)
    assert code == 1
    assert "Missing" in msg
