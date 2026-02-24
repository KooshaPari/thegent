"""Provider and Model Management - CLI, MCP, and programmatic CRUD for providers and models."""

import logging
from pathlib import Path
from typing import Any, cast

import httpx
from rich.console import Console

# from rich.formatted_text import FormattedText
from rich.prompt import Confirm, Prompt
from rich.table import Table

from thegent.agents.cliproxy_manager import _OAUTH_ONLY_PROVIDERS, _ensure_config
from thegent.config import ThegentSettings
from thegent.provider_model_manager_cliproxy import (
    get_api_key_from_compat,
    remove_openai_compat_entry,
    upsert_openai_compat_entry,
)
from thegent.provider_model_manager_io import (
    MODEL_DEFINITIONS_PATH as _MODEL_DEFINITIONS_PATH,
    MODEL_INDICES_PATH as _MODEL_INDICES_PATH,
    PROVIDER_DEFINITIONS_PATH as _PROVIDER_DEFINITIONS_PATH,
    PROVIDER_MAPPING_PATH as _PROVIDER_MAPPING_PATH,
    load_json as _load_json,
    load_yaml as _load_yaml,
    save_json as _save_json,
    save_yaml as _save_yaml,
    update_provider_mapping as _update_provider_mapping_file,
)
from thegent.provider_model_manager_sorting import sort_model_rows

console = Console()
_LOG = logging.getLogger(__name__)


# ============ PROVIDER CRUD ============


def list_providers(include_credentials: bool = False) -> list[dict[str, Any]]:
    """List all configured providers."""
    providers = _load_json(_PROVIDER_DEFINITIONS_PATH)
    result = []
    for name, cfg in providers.items():
        entry = {"name": name, **cfg}
        if not include_credentials:
            # Remove sensitive info
            entry.pop("api_key", None)
            if "login" in entry:
                entry["login"] = {k: v for k, v in entry["login"].items() if k != "credentials"}
        result.append(entry)
    return result


def get_provider(name: str) -> dict[str, Any] | None:
    """Get a specific provider."""
    providers = _load_json(_PROVIDER_DEFINITIONS_PATH)
    return providers.get(name.lower())


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
    """Add a new provider."""
    name = name.lower().strip()
    if name in _OAUTH_ONLY_PROVIDERS:
        return False, f"Provider '{name}' uses OAuth only. Use: thegent cliproxy login {name}"
    providers = _load_json(_PROVIDER_DEFINITIONS_PATH)

    if name in providers:
        return False, f"Provider '{name}' already exists"

    provider_cfg: dict[str, Any] = {
        "base_url": base_url,
        "model": model,
    }

    if base_url_env:
        provider_cfg["base_url_env"] = base_url_env

    if extra_aliases:
        provider_cfg["extra_aliases"] = extra_aliases

    if login_url or login_instructions:
        provider_cfg["login"] = {
            "url": login_url or "",
            "display_name": display_name or name.title(),
            "instructions": login_instructions or [],
        }

    # Add API key to CLIProxy config if provided
    if api_key:
        settings = ThegentSettings()
        config_path = _ensure_config(settings)
        config = _load_yaml(config_path)

        # Add to openai-compatibility
        compat = config.get("openai-compatibility", [])
        if not isinstance(compat, list):
            compat = []

        upsert_openai_compat_entry(
            compat,
            name=name,
            base_url=base_url,
            model=model,
            api_key=api_key,
        )

        config["openai-compatibility"] = compat
        _save_yaml(config_path, config)

    providers[name] = provider_cfg
    _save_json(_PROVIDER_DEFINITIONS_PATH, providers)

    # Update provider_mapping.json
    _update_provider_mapping(name, is_openai_compat=True)

    return True, f"Provider '{name}' added successfully"


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
    """Update an existing provider."""
    name = name.lower().strip()
    if name in _OAUTH_ONLY_PROVIDERS:
        return False, f"Provider '{name}' uses OAuth only. Use: thegent cliproxy login {name}"
    providers = _load_json(_PROVIDER_DEFINITIONS_PATH)

    if name not in providers:
        return False, f"Provider '{name}' not found"

    if base_url:
        providers[name]["base_url"] = base_url
    if model:
        providers[name]["model"] = model
    if base_url_env:
        providers[name]["base_url_env"] = base_url_env
    if extra_aliases is not None:
        providers[name]["extra_aliases"] = extra_aliases

    if login_url or login_instructions or display_name:
        login = providers[name].get("login", {})
        if login_url:
            login["url"] = login_url
        if display_name:
            login["display_name"] = display_name
        if login_instructions:
            login["instructions"] = login_instructions
        providers[name]["login"] = login

    # Update API key if provided
    if api_key:
        settings = ThegentSettings()
        config_path = _ensure_config(settings)
        config = _load_yaml(config_path)

        compat = config.get("openai-compatibility", [])
        upsert_openai_compat_entry(
            compat,
            name=name,
            base_url=base_url or providers[name].get("base_url", ""),
            model=model or providers[name].get("model", ""),
            api_key=api_key,
        )

        config["openai-compatibility"] = compat
        _save_yaml(config_path, config)

    _save_json(_PROVIDER_DEFINITIONS_PATH, providers)
    return True, f"Provider '{name}' updated successfully"


def delete_provider(name: str, remove_credentials: bool = True) -> tuple[bool, str]:
    """Delete a provider."""
    name = name.lower().strip()
    providers = _load_json(_PROVIDER_DEFINITIONS_PATH)

    if name not in providers:
        return False, f"Provider '{name}' not found"

    del providers[name]
    _save_json(_PROVIDER_DEFINITIONS_PATH, providers)

    # Update provider_mapping.json
    _update_provider_mapping(name, remove=True)

    # Remove from CLIProxy config if requested
    if remove_credentials:
        settings = ThegentSettings()
        config_path = _ensure_config(settings)
        config = _load_yaml(config_path)

        compat = config.get("openai-compatibility", [])
        config["openai-compatibility"] = remove_openai_compat_entry(compat, name)
        _save_yaml(config_path, config)

    return True, f"Provider '{name}' deleted successfully"


def _update_provider_mapping(name: str, is_openai_compat: bool = False, remove: bool = False) -> None:
    """Update provider_mapping.json."""
    _update_provider_mapping_file(
        _PROVIDER_MAPPING_PATH,
        name,
        is_openai_compat=is_openai_compat,
        remove=remove,
    )


# ============ MODEL CRUD ============


def list_models(provider: str | None = None) -> list[dict[str, Any]]:
    """List all models, optionally filtered by provider."""
    models = _load_json(_MODEL_DEFINITIONS_PATH)
    providers = _load_json(_PROVIDER_DEFINITIONS_PATH)

    result = []
    common_aliases = models.get("common_aliases", [])

    # Get models from provider definitions
    for prov_name, prov_cfg in providers.items():
        if provider and prov_name.lower() != provider.lower():
            continue

        model_name = prov_cfg.get("model", "")
        aliases = prov_cfg.get("extra_aliases", [])

        result.append(
            {
                "provider": prov_name,
                "model": model_name,
                "aliases": aliases,
                "is_default": True,
            }
        )

    # Add common aliases
    if not provider:
        for alias in common_aliases:
            result.append(
                {
                    "provider": "common",
                    "model": alias,
                    "aliases": [],
                    "is_default": False,
                }
            )

    return result


def add_model_alias(provider: str, model: str, alias: str) -> tuple[bool, str]:
    """Add a model alias for a provider."""
    provider = provider.lower().strip()
    providers = _load_json(_PROVIDER_DEFINITIONS_PATH)

    if provider not in providers:
        return False, f"Provider '{provider}' not found"

    aliases = providers[provider].get("extra_aliases", [])
    if alias not in aliases:
        aliases.append(alias)
        providers[provider]["extra_aliases"] = aliases
        _save_json(_PROVIDER_DEFINITIONS_PATH, providers)
        return True, f"Alias '{alias}' added to provider '{provider}'"

    return False, f"Alias '{alias}' already exists for provider '{provider}'"


def remove_model_alias(provider: str, alias: str) -> tuple[bool, str]:
    """Remove a model alias from a provider."""
    provider = provider.lower().strip()
    providers = _load_json(_PROVIDER_DEFINITIONS_PATH)

    if provider not in providers:
        return False, f"Provider '{provider}' not found"

    aliases = providers[provider].get("extra_aliases", [])
    if alias in aliases:
        aliases.remove(alias)
        providers[provider]["extra_aliases"] = aliases
        _save_json(_PROVIDER_DEFINITIONS_PATH, providers)
        return True, f"Alias '{alias}' removed from provider '{provider}'"

    return False, f"Alias '{alias}' not found for provider '{provider}'"


def add_common_alias(alias: str) -> tuple[bool, str]:
    """Add a common model alias that works across providers."""
    models = _load_json(_MODEL_DEFINITIONS_PATH)

    common_aliases = models.get("common_aliases", [])
    if alias not in common_aliases:
        common_aliases.append(alias)
        models["common_aliases"] = common_aliases
        _save_json(_MODEL_DEFINITIONS_PATH, models)
        return True, f"Common alias '{alias}' added"

    return False, f"Common alias '{alias}' already exists"


def remove_common_alias(alias: str) -> tuple[bool, str]:
    """Remove a common model alias."""
    models = _load_json(_MODEL_DEFINITIONS_PATH)

    common_aliases = models.get("common_aliases", [])
    if alias in common_aliases:
        common_aliases.remove(alias)
        models["common_aliases"] = common_aliases
        _save_json(_MODEL_DEFINITIONS_PATH, models)
        return True, f"Common alias '{alias}' removed"

    return False, f"Common alias '{alias}' not found"


# ============ CREDENTIALS MANAGEMENT ============


def list_credentials() -> list[dict[str, Any]]:
    """List all configured credentials (without showing actual keys)."""
    settings = ThegentSettings()
    config_path = _ensure_config(settings)
    config = _load_yaml(config_path)

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
    provider = provider.lower().strip()
    if provider in _OAUTH_ONLY_PROVIDERS:
        return False, f"Provider '{provider}' uses OAuth only. Use: thegent cliproxy login {provider}"
    providers = _load_json(_PROVIDER_DEFINITIONS_PATH)

    if provider not in providers:
        return False, f"Provider '{provider}' not found"

    settings = ThegentSettings()
    config_path = _ensure_config(settings)
    config = _load_yaml(config_path)

    base_url = providers[provider].get("base_url", "")
    model = providers[provider].get("model", provider)

    compat = config.get("openai-compatibility", [])

    upsert_openai_compat_entry(
        compat,
        name=provider,
        base_url=base_url,
        model=model,
        api_key=api_key,
    )

    config["openai-compatibility"] = compat
    _save_yaml(config_path, config)

    return True, f"API key added for provider '{provider}'"


def remove_api_key(provider: str) -> tuple[bool, str]:
    """Remove API key for a provider."""
    provider = provider.lower().strip()

    settings = ThegentSettings()
    config_path = _ensure_config(settings)
    config = _load_yaml(config_path)

    compat = config.get("openai-compatibility", [])
    original_len = len(compat)
    compat = remove_openai_compat_entry(compat, provider)

    if len(compat) == original_len:
        return False, f"No API key found for provider '{provider}'"

    config["openai-compatibility"] = compat
    _save_yaml(config_path, config)

    return True, f"API key removed for provider '{provider}'"


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
    config = _load_yaml(config_path)

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
    _load_yaml(config_path)

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
                )  # record-level malformed entries are dropped, not fatal
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


# ============ CLI INTERFACE ============



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
    "_update_provider_mapping",
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
