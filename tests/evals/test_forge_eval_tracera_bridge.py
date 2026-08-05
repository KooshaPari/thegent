"""Mocked, opt-in tests for the ForgeEval-to-Tracera evidence bridge."""

from __future__ import annotations

from datetime import UTC, datetime
import json

import httpx
import pytest
from pydantic import ValidationError

from thegent.forge_eval import ForgeEvalResult, LatencyProfile, load_bundled_catalog
from thegent.forge_eval.tracera import (
    TraceraBridgeStatus,
    TraceraEnvelope,
    TraceraTransport,
    TraceraTransportConfig,
    TraceraTransportError,
)

pytestmark = pytest.mark.requirement("FR-FORGEEVAL-004")


def _hex(character: str) -> str:
    return character * 64


def _result() -> ForgeEvalResult:
    return ForgeEvalResult(
        task=load_bundled_catalog().fixtures[0].task,
        run_id="offline-bridge-run-001",
        harness="offline-fixture-runner",
        candidate_model="fixture-model-v1",
        started_at=datetime(2026, 8, 5, tzinfo=UTC),
        completed_at=datetime(2026, 8, 5, 0, 0, 1, tzinfo=UTC),
        succeeded=True,
        latency=LatencyProfile(wall_time_seconds=1.0),
    )


def _envelope() -> TraceraEnvelope:
    return TraceraEnvelope(
        run_id=_hex("A"),
        session_id=_hex("b"),
        attempt_id=_hex("c"),
        replay_hash=_hex("d"),
        status=TraceraBridgeStatus.SUCCEEDED,
        forgeeval_result=_result(),
    )


def _config() -> TraceraTransportConfig:
    return TraceraTransportConfig.model_validate(
        {"endpoint": "https://tracera.invalid/evidence", "token": "explicit-test-token"}
    )


def test_envelope_preserves_supplied_causal_identifiers_verbatim() -> None:
    envelope = _envelope()

    assert envelope.schema_version == "forgeeval.tracera-envelope.v1"
    assert envelope.run_id == _hex("A")
    assert envelope.session_id == _hex("b")
    assert envelope.attempt_id == _hex("c")
    assert envelope.replay_hash == _hex("d")
    assert envelope.forgeeval_result == _result()


@pytest.mark.parametrize("field", ["run_id", "session_id", "attempt_id", "replay_hash"])
def test_envelope_rejects_non_64_hex_causal_identifiers(field: str) -> None:
    payload = _envelope().model_dump()
    payload[field] = "not-a-valid-64-hex-id"

    with pytest.raises(ValidationError):
        TraceraEnvelope.model_validate(payload)


def test_envelope_requires_known_status_and_additive_provenance() -> None:
    payload = _envelope().model_dump()
    payload["status"] = "unknown"
    with pytest.raises(ValidationError):
        TraceraEnvelope.model_validate(payload)

    payload = _envelope().model_dump()
    payload["forgeeval_result"] = None
    with pytest.raises(ValidationError, match="at least one ForgeEval"):
        TraceraEnvelope.model_validate(payload)


@pytest.mark.asyncio
async def test_transport_posts_only_when_explicitly_constructed_with_endpoint_and_token() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(202, json={"accepted": True})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        receipt = await TraceraTransport(_config(), client).send(_envelope())

    assert receipt.status_code == 202
    assert receipt.response == {"accepted": True}
    assert len(requests) == 1
    assert str(requests[0].url) == "https://tracera.invalid/evidence"
    assert requests[0].headers["Authorization"] == "Bearer explicit-test-token"
    assert json.loads(requests[0].content)["run_id"] == _hex("A")


@pytest.mark.asyncio
async def test_transport_converts_timeout_and_non_2xx_to_sanitized_errors() -> None:
    def timeout_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("network unavailable", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(timeout_handler)) as client:
        with pytest.raises(TraceraTransportError, match="timed out"):
            await TraceraTransport(_config(), client).send(_envelope())

    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(503))) as client:
        with pytest.raises(TraceraTransportError, match="HTTP 503"):
            await TraceraTransport(_config(), client).send(_envelope())


@pytest.mark.asyncio
async def test_transport_rejects_malformed_success_responses() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(201, content=b"not-json"))
    ) as client:
        with pytest.raises(TraceraTransportError, match="malformed JSON"):
            await TraceraTransport(_config(), client).send(_envelope())

    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=[]))) as client:
        with pytest.raises(TraceraTransportError, match="JSON object"):
            await TraceraTransport(_config(), client).send(_envelope())


def test_transport_configuration_requires_explicit_nonempty_token() -> None:
    with pytest.raises(ValidationError, match="token"):
        TraceraTransportConfig.model_validate({"endpoint": "https://tracera.invalid/evidence", "token": "   "})
