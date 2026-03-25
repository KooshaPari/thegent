"""Provider and Model Management - Backward compatibility shim.

This module provides backward compatibility by re-exporting the decomposed
functionality from use_cases and adapters. All business logic has been moved
to hexagonal architecture modules.

DEPRECATED: New code should import directly from:
  - thegent.use_cases.manage_providers
  - thegent.use_cases.manage_models
  - thegent.adapters.driven.provider_io
  - thegent.adapters.driven.cliproxy_provider
"""

import logging
import warnings
from pathlib import Path
from typing import Any

import httpx

from thegent.agents.cliproxy_manager import _ensure_config
from thegent.config import ThegentSettings
from thegent.provider_model_manager_cliproxy import get_api_key_from_compat
from thegent.provider_model_manager_io import load_yaml
from thegent.use_cases.manage_models import (
    add_common_alias as _add_common_alias,
    add_model_alias as _add_model_alias,
    list_models as _list_models,
    remove_common_alias as _remove_common_alias,
    remove_model_alias as _remove_model_alias,
)
from thegent.use_cases.manage_providers import (
    add_provider as _add_provider,
    delete_provider as _delete_provider,
    get_provider,
    list_providers as _list_providers,
    update_provider as _update_provider,
)

_LOG = logging.getLogger(__name__)

# Issue deprecation warning on import
warnings.warn(
    "Importing from thegent.provider_model_manager is deprecated. "
    "Please import from thegent.use_cases.manage_providers or thegent.use_cases.manage_models instead.",
    DeprecationWarning,
    stacklevel=2,
)


# ============ PROVIDER CRUD (re-exported from use_cases.manage_providers) ============


def list_providers(include_credentials: bool = False) -> list[dict[str, Any]]:
    """List all configured providers.

    DEPRECATED: Use thegent.use_cases.manage_providers.list_providers instead.
    """
    return _list_providers(include_credentials=include_credentials)


def add_provider(
    name: str,
    base_url: str,
    model: str,
    login_url: str | None = None,
    login_instructions: list[str] | None = None,
    display_name: str | None = None,
    extra_aliases: list[str] | None = None,
    api_key: str | None = None,
    base_url_env: str | None = None,
) -> tuple[bool, str]:
    """Add a new provider.

    DEPRECATED: Use thegent.use_cases.manage_providers.add_provider instead.
    """
    return _add_provider(
        name=name,
        base_url=base_url,
        model=model,
        login_url=login_url,
        login_instructions=login_instructions,
        display_name=display_name,
        extra_aliases=extra_aliases,
        api_key=api_key,
        base_url_env=base_url_env,
    )


def update_provider(
    name: str,
    base_url: str | None = None,
    model: str | None = None,
    login_url: str | None = None,
    login_instructions: list[str] | None = None,
    display_name: str | None = None,
    extra_aliases: list[str] | None = None,
    api_key: str | None = None,
    base_url_env: str | None = None,
) -> tuple[bool, str]:
    """Update an existing provider.

    DEPRECATED: Use thegent.use_cases.manage_providers.update_provider instead.
    """
    return _update_provider(
        name=name,
        base_url=base_url,
        model=model,
        login_url=login_url,
        login_instructions=login_instructions,
        display_name=display_name,
        extra_aliases=extra_aliases,
        api_key=api_key,
        base_url_env=base_url_env,
    )


def delete_provider(name: str, remove_credentials: bool = True) -> tuple[bool, str]:
    """Delete a provider.

    DEPRECATED: Use thegent.use_cases.manage_providers.delete_provider instead.
    """
    return _delete_provider(name=name, remove_credentials=remove_credentials)


# ============ MODEL CRUD (re-exported from use_cases.manage_models) ============


def list_models(provider: str | None = None) -> list[dict[str, Any]]:
    """List all models, optionally filtered by provider.

    DEPRECATED: Use thegent.use_cases.manage_models.list_models instead.
    """
    return _list_models(provider=provider)


def add_model_alias(provider: str, model: str, alias: str) -> tuple[bool, str]:
    """Add a model alias for a provider.

    DEPRECATED: Use thegent.use_cases.manage_models.add_model_alias instead.
    """
    return _add_model_alias(provider=provider, model=model, alias=alias)


def remove_model_alias(provider: str, alias: str) -> tuple[bool, str]:
    """Remove a model alias from a provider.

    DEPRECATED: Use thegent.use_cases.manage_models.remove_model_alias instead.
    """
    return _remove_model_alias(provider=provider, alias=alias)


def add_common_alias(alias: str) -> tuple[bool, str]:
    """Add a common model alias that works across providers.

    DEPRECATED: Use thegent.use_cases.manage_models.add_common_alias instead.
    """
    return _add_common_alias(alias=alias)


def remove_common_alias(alias: str) -> tuple[bool, str]:
    """Remove a common model alias.

    DEPRECATED: Use thegent.use_cases.manage_models.remove_common_alias instead.
    """
    return _remove_common_alias(alias=alias)


# ============ CREDENTIALS MANAGEMENT ============


def list_credentials() -> list[dict[str, Any]]:
    """List all configured credentials (without showing actual keys)."""
    settings = ThegentSettings()
    config_path = _ensure_config(settings)
    config = load_yaml(config_path)

    result = []

    # Check OAuth credentials
    auth_dir = Path(settings.cliproxy_auth_dir.expanduser())
    if auth_dir.exists():
        for json_file in auth_dir.glob("*.json"):
            # Skip merged config
            if json_file.name in ("merged-config.yaml", "merged-config.yml"):
                continue
            # Extract provider from filename
            provider = json_file.stem.split("-")[0]
            result.append(
                {
                    "type": "oauth",
                    "provider": provider,
                    "file": str(json_file),
                }
            )

    # Check openai-compatibility credentials
    compat = config.get("openai-compatibility", [])
    for entry in compat:
        result.append(
            {
                "type": "api_key",
                "provider": entry.get("name"),
                "base_url": entry.get("base-url"),
                "has_credentials": bool(entry.get("api-key-entries")),
            }
        )

    return result


def add_api_key(provider: str, api_key: str) -> tuple[bool, str]:
    """Add API key for a provider."""
    return _add_provider(
        name=provider,
        base_url="",
        model="",
        api_key=api_key,
    )


def remove_api_key(provider: str) -> tuple[bool, str]:
    """Remove API key for a provider."""
    return _delete_provider(name=provider, remove_credentials=True)


# ============ VALIDATION ============


def validate_provider(name: str) -> tuple[bool, str, dict[str, Any]]:
    """Validate a provider by testing connectivity."""
    provider = get_provider(name)
    if not provider:
        return False, f"Provider '{name}' not found", {}

    base_url = provider.get("base_url", "")
    model = provider.get("model", name)

    if not base_url:
        return False, "No base_url configured", {}

    # Check if credentials exist
    settings = ThegentSettings()
    config_path = _ensure_config(settings)
    config = load_yaml(config_path)

    compat = config.get("openai-compatibility", [])
    api_key = get_api_key_from_compat(compat, name)

    if not api_key:
        return False, "No API key configured", {"has_credentials": False}

    # Try a simple request
    try:
        resp = httpx.post(
            f"{base_url.rstrip('/')}/chat/completions",
            json={"model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0,
        )
        if resp.status_code == 200:
            return True, "Provider is accessible", {"has_credentials": True, "status_code": 200}
        return (
            False,
            f"HTTP {resp.status_code}: {resp.text[:100]}",
            {"has_credentials": True, "status_code": resp.status_code},
        )
    except httpx.TimeoutException as exc:
        _LOG.warning(
            "provider_probe_failed",
            extra={"provider": name, "failure_type": "timeout", "failure_detail": str(exc)},
        )
        return (
            False,
            f"Provider probe timed out: {exc}",
            {"has_credentials": True, "error": True, "failure_type": "timeout", "error_message": str(exc)},
        )
    except httpx.ConnectError as exc:
        _LOG.warning(
            "provider_probe_failed",
            extra={"provider": name, "failure_type": "connect_error", "failure_detail": str(exc)},
        )
        return (
            False,
            f"Provider probe failed to connect: {exc}",
            {
                "has_credentials": True,
                "error": True,
                "failure_type": "connect_error",
                "error_message": str(exc),
            },
        )
    except httpx.NetworkError as exc:
        _LOG.warning(
            "provider_probe_failed",
            extra={"provider": name, "failure_type": "network_error", "failure_detail": str(exc)},
        )
        return (
            False,
            f"Provider probe network error: {exc}",
            {
                "has_credentials": True,
                "error": True,
                "failure_type": "network_error",
                "error_message": str(exc),
            },
        )
    except httpx.HTTPError as exc:
        _LOG.warning(
            "provider_probe_failed",
            extra={"provider": name, "failure_type": "http_error", "failure_detail": str(exc)},
        )
        return (
            False,
            f"Provider probe failed: {exc}",
            {"has_credentials": True, "error": True, "failure_type": "http_error", "error_message": str(exc)},
        )


# ============ DISCOVERY ============


def discover_models(
    provider: str | None = None,
    *,
    include_status: bool = False,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Discover available models from provider APIs.

    When include_status=True, returns:
    {
      "models": [...],
      "discovery": {
          "status": "ok"|"error",
          "failure_class": "transport"|"protocol"|None,
          "failure_type": str|None,
          "error_message": str|None,
          "url": str,
          "malformed_count": int,
          "catalog_state": "empty"|"available"|"unknown",
          "provider": str|None,
      }
    }
    """

    def _mark_failure(*, failure_class: str, failure_type: str, error_message: str, event: str, **extra: Any) -> None:
        status.update(
            {
                "status": "error",
                "failure_class": failure_class,
                "failure_type": failure_type,
                "error_message": error_message,
            }
        )
        _LOG.warning(
            event, extra={"failure_class": failure_class, "failure_type": failure_type, **warning_extra, **extra}
        )

    results: list[dict[str, Any]] = []
    status: dict[str, Any] = {
        "status": "ok",
        "failure_class": None,
        "failure_type": None,
        "error_message": None,
        "url": "http://127.0.0.1:8317/v1/models",
        "malformed_count": 0,
        "catalog_state": "unknown",
        "provider": provider,
    }
    warning_extra = {"provider": provider}
    settings = ThegentSettings()
    config_path = _ensure_config(settings)
    load_yaml(config_path)

    # Check CLIProxy for available models
    try:
        resp = httpx.get(status["url"], timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            if not isinstance(data, dict):
                status["catalog_state"] = "empty"
                _mark_failure(
                    failure_class="protocol",
                    failure_type="payload_not_object",
                    error_message="top-level JSON is not an object",
                    event="cliproxy_model_discovery_invalid_payload",
                )
                payload = {"models": results, "discovery": status}
                return payload if include_status else results
            models = data.get("models", []) or data.get("data", [])
            if not isinstance(models, list):
                status["catalog_state"] = "empty"
                _mark_failure(
                    failure_class="protocol",
                    failure_type="models_not_list",
                    error_message="models/data field is not a list",
                    event="cliproxy_model_discovery_invalid_payload",
                )
                payload = {"models": results, "discovery": status}
                return payload if include_status else results

            for m in models:
                if not isinstance(m, dict):
                    status["malformed_count"] += 1
                    continue
                owned_by = m.get("owned_by", "unknown")
                if not isinstance(owned_by, str):
                    status["malformed_count"] += 1
                    continue
                if provider and owned_by.lower() != provider.lower():
                    continue
                results.append(
                    {
                        "id": m.get("id"),
                        "provider": owned_by,
                        "object": m.get("object"),
                        "created": m.get("created"),
                    }
                )
            if status["malformed_count"]:
                _LOG.warning(
                    "cliproxy_model_discovery_malformed_entries",
                    extra={"malformed_count": status["malformed_count"], **warning_extra},
                )
            status["catalog_state"] = "available" if results else "empty"
        else:
            _mark_failure(
                failure_class="protocol",
                failure_type="http_status",
                error_message=f"HTTP {resp.status_code}",
                event="cliproxy_model_discovery_http_error",
                status_code=resp.status_code,
            )
    except httpx.TimeoutException as exc:
        _mark_failure(
            failure_class="transport",
            failure_type="timeout",
            error_message=str(exc),
            event="cliproxy_model_discovery_timeout",
            failure_detail=str(exc),
        )
    except httpx.ConnectError as exc:
        _mark_failure(
            failure_class="transport",
            failure_type="connect_error",
            error_message=str(exc),
            event="cliproxy_model_discovery_connect_error",
            failure_detail=str(exc),
        )
    except httpx.NetworkError as exc:
        _mark_failure(
            failure_class="transport",
            failure_type="network_error",
            error_message=str(exc),
            event="cliproxy_model_discovery_network_error",
            failure_detail=str(exc),
        )
    except httpx.HTTPError as exc:
        _mark_failure(
            failure_class="transport",
            failure_type="http_error",
            error_message=str(exc),
            event="cliproxy_model_discovery_http_error",
            failure_detail=str(exc),
        )
    except ValueError as exc:
        _mark_failure(
            failure_class="protocol",
            failure_type="json_decode",
            error_message=str(exc),
            event="cliproxy_model_discovery_json_decode_error",
            failure_detail=str(exc),
        )

    payload = {"models": results, "discovery": status}
    return payload if include_status else results


# ============ BACKWARD COMPATIBILITY RE-EXPORTS ============

# Form functions moved to provider_forms.py
# Scoring functions moved to provider_model_scoring.py

# Re-export scoring functions for backward compatibility
from thegent.provider_model_scoring import (
    add_custom_benchmark,
    add_model_index,
    add_model_modality,
    calculate_composite_score,
    fuzzy_search_models,
    get_model_indices,
    get_model_modalities,
    list_available_modalities,
    list_model_indices,
    list_models_with_scores,
    remove_model_index,
    search_by_modalities,
    search_models_by_capability,
)

# Re-export form functions
from thegent.provider_forms import run_provider_form

__all__ = [
    # Provider CRUD
    "list_providers",
    "get_provider",
    "add_provider",
    "update_provider",
    "delete_provider",
    # Model CRUD
    "list_models",
    "add_model_alias",
    "remove_model_alias",
    "add_common_alias",
    "remove_common_alias",
    # Credentials
    "list_credentials",
    "add_api_key",
    "remove_api_key",
    # Validation
    "validate_provider",
    # Discovery
    "discover_models",
    # Model Indices (re-exported from provider_model_scoring)
    "get_model_indices",
    "list_model_indices",
    "add_model_index",
    "remove_model_index",
    # Scoring (re-exported from provider_model_scoring)
    "calculate_composite_score",
    "list_models_with_scores",
    "add_custom_benchmark",
    # Search (re-exported from provider_model_scoring)
    "fuzzy_search_models",
    "search_models_by_capability",
    # Modalities (re-exported from provider_model_scoring)
    "get_model_modalities",
    "add_model_modality",
    "list_available_modalities",
    "search_by_modalities",
    # Forms (re-exported from provider_forms)
    "run_provider_form",
]
