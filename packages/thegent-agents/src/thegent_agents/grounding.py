"""Google Search Grounding support for Gemini API passthrough.

# @trace WL-119
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

from thegent_agents.base import RunResult

_log = logging.getLogger(__name__)

# Agents that are Gemini-backed and eligible for Google Search Grounding.
GEMINI_GROUNDING_AGENTS: frozenset[str] = frozenset({"gemini", "antigravity"})


@dataclass
class GroundingSource:
    """A single grounding source returned by the Gemini API."""

    url: str
    title: str | None = None


def build_grounding_tools_arg() -> list[dict[str, Any]]:
    """Return the Gemini grounding tools argument for Google Search.

    Pass the result as the ``tools`` kwarg to a LiteLLM or Gemini API call.

    # @trace WL-119
    """
    return [{"google_search": {}}]


def extract_grounding_metadata_sources(response: dict[str, Any]) -> list[str]:
    """Extract grounding source URLs from a Gemini API response ``groundingMetadata``.

    Handles the standard Gemini grounding payload shape::

        {
            "groundingMetadata": {
                "groundingChunks": [
                    {"web": {"uri": "https://example.com", "title": "..."}},
                    ...
                ]
            }
        }

    Returns a deduplicated, ordered list of URL strings.

    # @trace WL-119
    """
    grounding_meta = response.get("groundingMetadata", {})
    if not isinstance(grounding_meta, dict):
        return []
    chunks = grounding_meta.get("groundingChunks", [])
    if not isinstance(chunks, list):
        return []

    seen: set[str] = set()
    urls: list[str] = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        web = chunk.get("web", {})
        if not isinstance(web, dict):
            continue
        uri = web.get("uri", "")
        if isinstance(uri, str) and uri and uri not in seen:
            seen.add(uri)
            urls.append(uri)
    return urls


def _resolve_gemini_api_key() -> str:
    """Resolve the Gemini API key from the environment.

    Checks GEMINI_API_KEY then GOOGLE_API_KEY.
    Raises ValueError if neither is set.

    # @trace WL-119
    """
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    if not key:
        raise ValueError(
            "Google Search Grounding requires a Gemini API key. "
            "Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable."
        )
    return key


def _resolve_gemini_model(model: str | None) -> str:
    """Resolve the Gemini model to use for grounding requests.

    # @trace WL-119
    """
    if model:
        return model
    return "gemini/gemini-2.0-flash"


def run_gemini_with_grounding(
    prompt: str,
    *,
    model: str | None = None,
    api_key: str | None = None,
    timeout: int = 120,
) -> RunResult:
    """Run a prompt against the Gemini API with Google Search Grounding enabled.

    Makes a direct LiteLLM completion call using ``tools=[{"google_search": {}}]``.
    Extracts ``groundingMetadata`` from the response and populates
    ``RunResult.grounding_sources``.

    Only call this function for Gemini-backed agents.  For non-Gemini agents,
    use the standard runner path; this function will raise ValueError if the
    model does not belong to the Gemini provider namespace.

    # @trace WL-119

    Args:
        prompt:  The user prompt to send.
        model:   Gemini model identifier (e.g. ``"gemini/gemini-2.0-flash"``).
                 Defaults to ``"gemini/gemini-2.0-flash"``.
        api_key: Gemini API key.  If None, resolved from environment.
        timeout: Request timeout in seconds.

    Returns:
        RunResult with ``stdout`` set to the assistant response text and
        ``grounding_sources`` populated from ``groundingMetadata``.

    Raises:
        ValueError: When the API key is missing or the model is not Gemini-backed.
        RuntimeError: When the LiteLLM completion fails.
    """
    import litellm  # noqa: PLC0415 -- deferred to avoid top-level side effects

    effective_model = _resolve_gemini_model(model)
    if not effective_model.startswith("gemini/") and not effective_model.startswith("google/"):
        raise ValueError(
            f"run_gemini_with_grounding requires a Gemini model (prefix 'gemini/' or 'google/'). "
            f"Got: '{effective_model}'. Use a non-grounding runner for non-Gemini models."
        )

    effective_key = api_key or _resolve_gemini_api_key()

    tools = build_grounding_tools_arg()
    messages = [{"role": "user", "content": prompt}]

    _log.info(
        "WL-119: Gemini grounding call model=%s tools=%s",
        effective_model,
        tools,
    )

    try:
        response = litellm.completion(
            model=effective_model,
            messages=messages,
            tools=tools,
            api_key=effective_key,
            timeout=timeout,
        )
    except Exception as exc:
        raise RuntimeError(f"Gemini grounding API call failed: {exc}") from exc

    # Extract text content from response
    content = ""
    choices = getattr(response, "choices", None) or []
    if choices:
        msg = getattr(choices[0], "message", None)
        if msg:
            content = getattr(msg, "content", None) or ""

    # Extract groundingMetadata from response metadata / _hidden_params
    grounding_sources: list[str] = []
    raw_response = getattr(response, "_hidden_params", {}) or {}
    # LiteLLM may surface the raw provider response under various attributes
    for candidate_key in ("groundingMetadata", "grounding_metadata"):
        meta = raw_response.get(candidate_key)
        if meta:
            synthetic = {"groundingMetadata": meta}
            grounding_sources = extract_grounding_metadata_sources(synthetic)
            break

    # Also check model_extra / additional_kwargs
    if not grounding_sources:
        for attr in ("model_extra", "additional_kwargs"):
            extra = getattr(response, attr, None) or {}
            if isinstance(extra, dict):
                for candidate_key in ("groundingMetadata", "grounding_metadata"):
                    meta = extra.get(candidate_key)
                    if meta:
                        synthetic = {"groundingMetadata": meta}
                        grounding_sources = extract_grounding_metadata_sources(synthetic)
                        break
            if grounding_sources:
                break

    if grounding_sources:
        _log.info("WL-119: Extracted %d grounding source(s)", len(grounding_sources))

    return RunResult(
        exit_code=0,
        stdout=content or "",
        stderr="",
        grounding_sources=grounding_sources or None,
    )
