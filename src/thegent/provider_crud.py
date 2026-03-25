"""Provider CRUD operations.

Extracted from provider_model_manager.py for maintainability.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)

# Paths
_PROVIDER_DEFINITIONS_PATH = Path.home() / ".config" / "thegent" / "provider_definitions.json"
_CLIPROXY_CONFIG_PATH = Path.home() / ".config" / "cli-proxy-api" / "config.json"

# OAuth-only providers that can't use API keys
_OAUTH_ONLY_PROVIDERS = {"kiro", "cursor", "copilot"}


def _load_json(path: Path) -> dict[str, Any]:
    """Load JSON file safely."""
    if not path.exists():
        return {}
    try:
        import orjson as json

        return json.loads(path.read_text())
    except Exception:
        return {}


def _save_json(path: Path, data: dict[str, Any]) -> None:
    """Save JSON file safely."""
    path.parent.mkdir(parents=True, exist_ok=True)
    import json

    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def list_providers(include_credentials: bool = False) -> list[dict[str, Any]]:
    """List all configured providers.

    Args:
        include_credentials: If True, include API keys

    Returns:
        List of provider dicts
    """
    providers = _load_json(_PROVIDER_DEFINITIONS_PATH)
    result = []
    for name, cfg in providers.items():
        entry = {"name": name, **cfg}
        if not include_credentials:
            entry.pop("api_key", None)
            if "login" in entry:
                entry["login"] = {k: v for k, v in entry["login"].items() if k != "credentials"}
        result.append(entry)
    return result


def get_provider(name: str) -> dict[str, Any] | None:
    """Get a specific provider.

    Args:
        name: Provider name

    Returns:
        Provider config or None if not found
    """
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
    """Add a new provider.

    Args:
        name: Provider name
        base_url: API base URL
        model: Default model ID
        login_url: Optional login URL
        login_instructions: Optional login instructions
        display_name: Optional display name
        extra_aliases: Optional extra model aliases
        api_key: Optional API key
        base_url_env: Optional env var for base URL

    Returns:
        Tuple of (success, message)
    """
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

    if api_key:
        _add_api_key_to_cliproxy(name, api_key)

    providers[name] = provider_cfg
    _save_json(_PROVIDER_DEFINITIONS_PATH, providers)

    logger.info(f"Added provider: {name}")
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
    name = name.lower()
    providers = _load_json(_PROVIDER_DEFINITIONS_PATH)

    if name not in providers:
        return False, f"Provider '{name}' not found"

    cfg = providers[name]

    if base_url is not None:
        cfg["base_url"] = base_url
    if model is not None:
        cfg["model"] = model
    if base_url_env is not None:
        cfg["base_url_env"] = base_url_env
    if extra_aliases is not None:
        cfg["extra_aliases"] = extra_aliases

    if login_url or login_instructions or display_name:
        if "login" not in cfg:
            cfg["login"] = {}
        if login_url is not None:
            cfg["login"]["url"] = login_url
        if display_name is not None:
            cfg["login"]["display_name"] = display_name
        if login_instructions is not None:
            cfg["login"]["instructions"] = login_instructions

    if api_key:
        _add_api_key_to_cliproxy(name, api_key)

    providers[name] = cfg
    _save_json(_PROVIDER_DEFINITIONS_PATH, providers)

    logger.info(f"Updated provider: {name}")
    return True, f"Provider '{name}' updated successfully"


def delete_provider(name: str, remove_credentials: bool = True) -> tuple[bool, str]:
    """Delete a provider."""
    name = name.lower()
    providers = _load_json(_PROVIDER_DEFINITIONS_PATH)

    if name not in providers:
        return False, f"Provider '{name}' not found"

    del providers[name]
    _save_json(_PROVIDER_DEFINITIONS_PATH, providers)

    if remove_credentials:
        _remove_api_key_from_cliproxy(name)

    logger.info(f"Deleted provider: {name}")
    return True, f"Provider '{name}' deleted"


def list_credentials() -> list[dict[str, Any]]:
    """List all credentials."""
    config = _load_json(_CLIPROXY_CONFIG_PATH)
    result = []

    providers = config.get("providers", {})
    for name, cfg in providers.items():
        has_key = bool(cfg.get("api_key"))
        key_preview = ""
        if has_key:
            key = cfg.get("api_key", "")
            key_preview = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"

        result.append(
            {
                "provider": name,
                "has_api_key": has_key,
                "key_preview": key_preview,
            }
        )

    return result


def add_api_key(provider: str, api_key: str) -> tuple[bool, str]:
    """Add an API key for a provider."""
    provider = provider.lower()
    _add_api_key_to_cliproxy(provider, api_key)
    return True, f"API key added for '{provider}'"


def remove_api_key(provider: str) -> tuple[bool, str]:
    """Remove an API key for a provider."""
    provider = provider.lower()
    _remove_api_key_from_cliproxy(provider)
    return True, f"API key removed for '{provider}'"


def validate_provider(name: str) -> tuple[bool, str, dict[str, Any]]:
    """Validate a provider configuration."""
    provider = get_provider(name)

    if not provider:
        return False, f"Provider '{name}' not found", {}

    details = {
        "has_base_url": bool(provider.get("base_url")),
        "has_model": bool(provider.get("model")),
        "has_api_key": bool(_get_api_key(name)),
    }

    issues = []
    if not details["has_base_url"]:
        issues.append("Missing base URL")
    if not details["has_model"]:
        issues.append("Missing default model")

    if issues:
        return False, f"Issues: {', '.join(issues)}", details

    return True, "Provider configuration valid", details


def _add_api_key_to_cliproxy(provider: str, api_key: str) -> None:
    """Add API key to cliproxy config."""
    config = _load_json(_CLIPROXY_CONFIG_PATH)
    if "providers" not in config:
        config["providers"] = {}
    config["providers"][provider] = {"api_key": api_key}
    _save_json(_CLIPROXY_CONFIG_PATH, config)


def _remove_api_key_from_cliproxy(provider: str) -> None:
    """Remove API key from cliproxy config."""
    config = _load_json(_CLIPROXY_CONFIG_PATH)
    if "providers" in config and provider in config["providers"]:
        del config["providers"][provider]
        _save_json(_CLIPROXY_CONFIG_PATH, config)


def _get_api_key(provider: str) -> str | None:
    """Get API key for a provider."""
    config = _load_json(_CLIPROXY_CONFIG_PATH)
    providers = config.get("providers", {})
    return providers.get(provider, {}).get("api_key")


__all__ = [
    "list_providers",
    "get_provider",
    "add_provider",
    "update_provider",
    "delete_provider",
    "list_credentials",
    "add_api_key",
    "remove_api_key",
    "validate_provider",
]
