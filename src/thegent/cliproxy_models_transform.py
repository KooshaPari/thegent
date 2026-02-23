# MIGRATION NOTE: Migrate to cliproxyapi-plusplus Go SDK
from __future__ import annotations

import hashlib
import orjson as json
import logging
import time
from typing import Any

_LOG = logging.getLogger(__name__)
_WARNING_LIMIT = 3
_warning_count = 0
_transform_diagnostics: dict[str, Any] = {
    "failure_count": 0,
    "last_failure_type": None,
    "last_error_type": None,
    "last_error_message": None,
}


def get_transform_models_diagnostics() -> dict[str, Any]:
    """Return diagnostics for transform_models_response failures."""
    return dict(_transform_diagnostics)


def reset_transform_models_diagnostics() -> None:
    """Reset transform diagnostics (test helper)."""
    global _warning_count
    _warning_count = 0
    _transform_diagnostics["failure_count"] = 0
    _transform_diagnostics["last_failure_type"] = None
    _transform_diagnostics["last_error_type"] = None
    _transform_diagnostics["last_error_message"] = None


def _record_transform_failure(failure_type: str, exc: Exception) -> None:
    global _warning_count
    _transform_diagnostics["failure_count"] = int(_transform_diagnostics["failure_count"]) + 1
    _transform_diagnostics["last_failure_type"] = failure_type
    _transform_diagnostics["last_error_type"] = type(exc).__name__
    _transform_diagnostics["last_error_message"] = str(exc)
    _warning_count += 1
    if _warning_count <= _WARNING_LIMIT:
        _LOG.warning("transform_models_response failed (%s): %s", failure_type, type(exc).__name__)


def _compute_models_etag(models: list[dict[str, Any]]) -> str:
    """Compute x-models-etag: SHA256 of sorted model IDs."""
    ids = sorted(m.get("id") or m.get("slug") or "" for m in models if isinstance(m, dict))
    return hashlib.sha256(",".join(ids).encode()).hexdigest()


# OR-15: OpenRouter proxy models to inject into /v1/models when they are absent from the
# backend's own list. These are models that OpenRouter supports and thegent exposes as
# first-class options, keyed by their canonical OpenRouter model ID.
_OPENROUTER_PROXY_MODELS: list[dict[str, Any]] = [
    {"id": "anthropic/claude-opus-4-6", "name": "Anthropic: Claude Opus 4.6 (OpenRouter)"},
    {"id": "anthropic/claude-sonnet-4-6", "name": "Anthropic: Claude Sonnet 4.6 (OpenRouter)"},
    {"id": "anthropic/claude-haiku-4-5-20251001", "name": "Anthropic: Claude Haiku 4.5 (OpenRouter)"},
    {"id": "openai/gpt-4o", "name": "OpenAI: GPT-4o (OpenRouter)"},
    {"id": "google/gemini-2.0-flash-001", "name": "Google: Gemini 2.0 Flash (OpenRouter)"},
]


def _inject_openrouter_proxy_models(models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """OR-15: Add OpenRouter proxy models that the backend may not list itself.

    Skips injection for any model ID already present in the list to avoid duplicates.
    """
    existing_ids = {m.get("id", "") for m in models if isinstance(m, dict)}
    for stub in _OPENROUTER_PROXY_MODELS:
        if stub["id"] not in existing_ids:
            models.append(dict(stub))
    return models


def transform_models_response(
    content: bytes | memoryview, *, inject_openrouter: bool = False
) -> tuple[bytes, str] | None:
    """Transform CLIProxy models response to Codex-compatible format.

    Codex 0.104.0 requires:
    - Top-level "models" key (Codex API format, NOT OpenAI "data" key)
    - Each model object with 20+ required fields (slug, shell_type, supported_reasoning_levels, etc.)
    - x-models-etag response header (SHA256 of sorted model IDs)

    OR-15: When inject_openrouter=True, known OpenRouter proxy models are merged into the
    list before enrichment so Codex sees them even if the CLIProxy backend omits them.

    Without the full schema, Codex shows "Model metadata for X not found" and won't connect.

    Returns (transformed_body, etag) or None on parse failure.
    """
    try:
        raw = bytes(content) if isinstance(content, memoryview) else content
        payload = json.loads(raw.decode(errors="replace"))
        if not isinstance(payload, dict):
            exc = TypeError(f"expected object payload, got {type(payload).__name__}")
            _record_transform_failure("payload_not_object", exc)
            return None
        # Extract model list from either "data" (OpenAI format) or "models" (Codex format)
        models = payload.get("data") or payload.get("models") or []
        if not isinstance(models, list):
            exc = TypeError(f"expected list models payload, got {type(models).__name__}")
            _record_transform_failure("models_not_list", exc)
            return None

        # OR-15: inject OpenRouter proxy models when requested
        if inject_openrouter:
            models = _inject_openrouter_proxy_models(models)

        # Enrich each model with the full Codex metadata schema.
        # Codex 0.104.0 removed the `remote_models` feature flag, so all metadata must come
        # from the /v1/models response — any missing field triggers "Model metadata not found."
        from thegent.utils.routing_impl.model_metadata import get_model_metadata

        for m in models:
            if not isinstance(m, dict):
                continue
            mid = m.get("id") or m.get("name") or ""
            if not mid:
                continue

            # Look up thegent's model metadata registry for context/token info
            meta = get_model_metadata(mid)
            if not meta and "/" in mid:
                meta = get_model_metadata(mid.split("/", 1)[1])

            ctx = (meta or {}).get("context_window", 128000)

            # --- Required Codex fields (see ~/.codex/models_cache.json for reference schema) ---
            m.setdefault("slug", mid)
            m.setdefault("display_name", m.get("slug", mid))
            m.setdefault("description", "")
            m.setdefault("shell_type", "shell_command")
            m.setdefault("visibility", "list")
            m.setdefault("supported_in_api", True)
            m.setdefault("priority", 0)
            m.setdefault("upgrade", None)
            m.setdefault("base_instructions", "")
            m.setdefault("model_messages", "[]")
            m.setdefault("supports_reasoning_summaries", False)
            m.setdefault("support_verbosity", False)
            m.setdefault("default_verbosity", "low")
            m.setdefault("apply_patch_tool_type", "freeform")
            m.setdefault("truncation_policy", {"mode": "tokens", "limit": 10000})
            m.setdefault("supports_parallel_tool_calls", True)
            m.setdefault("context_window", ctx)
            m.setdefault("context_length", ctx)
            m.setdefault("max_completion_tokens", min(ctx, 8192))
            m.setdefault("effective_context_window_percent", 95)
            m.setdefault("experimental_supported_tools", [])
            m.setdefault("input_modalities", ["text"])
            m.setdefault("prefer_websockets", False)
            m.setdefault("default_reasoning_level", "medium")
            m.setdefault(
                "supported_reasoning_levels",
                [
                    {"effort": "low", "description": "Fast, lower quality"},
                    {"effort": "medium", "description": "Balanced"},
                    {"effort": "high", "description": "Thorough, higher quality"},
                ],
            )

        # Codex format: top-level "models" key (not OpenAI "data")
        result = {
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "client_version": "proxy",
            "models": models,
        }
        body = json.dumps(result).decode().encode()
        etag = _compute_models_etag(models)
        return body, etag
    except json.JSONDecodeError as exc:
        _record_transform_failure("json_decode_error", exc)
    except TypeError as exc:
        _record_transform_failure("type_error", exc)
    return None
