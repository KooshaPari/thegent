"""Explicit, opt-in delivery of ForgeEval evidence to a Tracera endpoint.

The bridge deliberately has no environment configuration or implicit client.  A
caller must supply a concrete endpoint, bearer token, and HTTP client before any
network request is possible.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Annotated

import httpx
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, SecretStr, StringConstraints, model_validator

from thegent.forge_eval.contracts import ForgeEvalResult
from thegent.forge_eval.profiler import ForgeEvalProfile

_HEX_64 = Annotated[str, StringConstraints(pattern=r"^[0-9a-fA-F]{64}$", strict=True)]
_SUCCESS_STATUSES = frozenset((200, 201, 202))


class TraceraBridgeStatus(StrEnum):
    """Only terminal ForgeEval outcomes accepted by the bridge envelope."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMED_OUT = "timed-out"


class TraceraEnvelopeError(ValueError):
    """Raised when an envelope lacks required causal provenance."""


class TraceraTransportError(RuntimeError):
    """Raised for a bounded, explicit delivery failure without exposing a token."""


class TraceraEnvelope(BaseModel):
    """Versioned causal envelope with ForgeEval observations as additive provenance."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = "forgeeval.tracera-envelope.v1"
    run_id: _HEX_64
    session_id: _HEX_64
    attempt_id: _HEX_64
    replay_hash: _HEX_64
    status: TraceraBridgeStatus
    forgeeval_result: ForgeEvalResult | None = None
    forgeeval_profile: ForgeEvalProfile | None = None

    @model_validator(mode="after")
    def require_additive_forgeeval_provenance(self) -> TraceraEnvelope:
        """Reject a causally labelled envelope without a ForgeEval observation."""
        if self.forgeeval_result is None and self.forgeeval_profile is None:
            raise TraceraEnvelopeError("at least one ForgeEval result or profile is required")
        return self


class TraceraTransportConfig(BaseModel):
    """Explicit endpoint and bearer token required for opt-in delivery."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    endpoint: AnyHttpUrl
    token: SecretStr
    timeout_seconds: float = Field(default=10.0, gt=0, le=120)

    @model_validator(mode="after")
    def reject_empty_token(self) -> TraceraTransportConfig:
        """Fail before creating a request if the caller supplied no credential."""
        if not self.token.get_secret_value().strip():
            raise ValueError("token must not be empty")
        return self


class TraceraDeliveryReceipt(BaseModel):
    """Bounded response evidence for an explicitly requested delivery."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status_code: int = Field(ge=200, lt=300)
    response: Mapping[str, object]


class TraceraTransport:
    """Opt-in async transport that never discovers endpoint or token implicitly."""

    def __init__(self, config: TraceraTransportConfig, client: httpx.AsyncClient) -> None:
        self._config = config
        self._client = client

    async def send(self, envelope: TraceraEnvelope) -> TraceraDeliveryReceipt:
        """POST validated evidence and return a parsed successful response object."""
        try:
            response = await self._client.post(
                str(self._config.endpoint),
                json=envelope.model_dump(mode="json"),
                headers={"Authorization": f"Bearer {self._config.token.get_secret_value()}"},
                timeout=self._config.timeout_seconds,
            )
        except httpx.TimeoutException as exc:
            raise TraceraTransportError("Tracera delivery timed out") from exc
        except httpx.HTTPError as exc:
            raise TraceraTransportError(f"Tracera delivery failed: {type(exc).__name__}") from exc
        if response.status_code not in _SUCCESS_STATUSES:
            raise TraceraTransportError(f"Tracera returned HTTP {response.status_code}")
        return TraceraDeliveryReceipt(status_code=response.status_code, response=self._response_object(response))

    @staticmethod
    def _response_object(response: httpx.Response) -> Mapping[str, object]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise TraceraTransportError("Tracera returned malformed JSON") from exc
        if not isinstance(payload, dict):
            raise TraceraTransportError("Tracera response must be a JSON object")
        return payload
