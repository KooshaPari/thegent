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
          "status": "ok"|"error"|"invalid_payload",
          "failure_type": str|None,
          "error_message": str|None,
          "url": str,
          "malformed_count": int,
      }
    }
    """
    results: list[dict[str, Any]] = []
    status: dict[str, Any] = {
        "status": "ok",
        "failure_type": None,
        "error_message": None,
        "url": "http://127.0.0.1:8317/v1/models",
        "malformed_count": 0,
        "provider": provider,
    }
    warning_extra = {"provider": provider}
    settings = ThegentSettings()
    config_path = _ensure_config(settings)
    _config = _load_yaml(config_path)

    _providers = _load_json(_PROVIDER_DEFINITIONS_PATH)

    # Check CLIProxy for available models
    try:
        resp = httpx.get(status["url"], timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            if not isinstance(data, dict):
                status.update(
                    {
                        "status": "invalid_payload",
                        "failure_type": "payload_not_object",
                        "error_message": "top-level JSON is not an object",
                    }
                )
                _LOG.warning(
                    "cliproxy_model_discovery_invalid_payload",
                    extra={"failure_type": "payload_not_object", **warning_extra},
                )
                payload = {"models": results, "discovery": status}
                return payload if include_status else results
            models = data.get("models", []) or data.get("data", [])
            if not isinstance(models, list):
                status.update(
                    {
                        "status": "invalid_payload",
                        "failure_type": "models_not_list",
                        "error_message": "models/data field is not a list",
                    }
                )
                _LOG.warning(
                    "cliproxy_model_discovery_invalid_payload",
                    extra={"failure_type": "models_not_list", **warning_extra},
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
        else:
            status.update(
                {
                    "status": "error",
                    "failure_type": "http_status",
                    "error_message": f"HTTP {resp.status_code}",
                }
            )
            _LOG.warning(
                "cliproxy_model_discovery_http_error",
                extra={"status_code": resp.status_code, **warning_extra},
            )
    except httpx.TimeoutException as exc:
        status.update({"status": "error", "failure_type": "timeout", "error_message": str(exc)})
        _LOG.warning("cliproxy_model_discovery_timeout", extra={"failure_detail": str(exc), **warning_extra})
    except httpx.ConnectError as exc:
        status.update({"status": "error", "failure_type": "connect_error", "error_message": str(exc)})
        _LOG.warning(
            "cliproxy_model_discovery_connect_error",
            extra={"failure_detail": str(exc), **warning_extra},
        )
    except httpx.NetworkError as exc:
        status.update({"status": "error", "failure_type": "network_error", "error_message": str(exc)})
        _LOG.warning(
            "cliproxy_model_discovery_network_error",
            extra={"failure_detail": str(exc), **warning_extra},
        )
    except httpx.HTTPError as exc:
        status.update({"status": "error", "failure_type": "http_error", "error_message": str(exc)})
        _LOG.warning("cliproxy_model_discovery_http_error", extra={"failure_detail": str(exc), **warning_extra})
    except ValueError as exc:
        status.update({"status": "invalid_payload", "failure_type": "json_decode", "error_message": str(exc)})
        _LOG.warning(
            "cliproxy_model_discovery_json_decode_error",
            extra={"failure_detail": str(exc), **warning_extra},
        )

    payload = {"models": results, "discovery": status}
    return payload if include_status else results


# ============ CLI INTERFACE ============


def run_provider_form() -> None:
    """Interactive form for provider management."""
    console.print("\n[bold cyan]Provider Management[/bold cyan]\n")

    while True:
        console.print("\n[bold]Choose an action:[/bold]")
        console.print("  1. List providers")
        console.print("  2. Add provider")
        console.print("  3. Update provider")
        console.print("  4. Delete provider")
        console.print("  5. Validate provider")
        console.print("  6. List credentials")
        console.print("  7. Add API key")
        console.print("  8. Remove API key")
        console.print("  9. Discover models")
        console.print("  0. Exit")

        choice = Prompt.ask("[bold]Choice[/bold]", default="0")

        if choice == "0":
            break
        if choice == "1":
            _form_list_providers()
        elif choice == "2":
            _form_add_provider()
        elif choice == "3":
            _form_update_provider()
        elif choice == "4":
            _form_delete_provider()
        elif choice == "5":
            _form_validate_provider()
        elif choice == "6":
            _form_list_credentials()
        elif choice == "7":
            _form_add_api_key()
        elif choice == "8":
            _form_remove_api_key()
        elif choice == "9":
            _form_discover_models()


def _form_list_providers() -> None:
    providers = list_providers()
    if not providers:
        console.print("[yellow]No providers configured[/yellow]")
        return

    table = Table(title="Providers")
    table.add_column("Name", style="cyan")
    table.add_column("Base URL", style="dim")
    table.add_column("Model", style="green")
    table.add_column("Aliases", style="magenta")

    for p in providers:
        aliases = ", ".join(p.get("extra_aliases", []))
        table.add_row(
            p.get("name", ""),
            p.get("base_url", "")[:40],
            p.get("model", ""),
            aliases[:30],
        )

    console.print(table)


def _form_add_provider() -> None:
    console.print("\n[bold]Add New Provider[/bold]\n")

    name = Prompt.ask("[bold]Provider name[/bold] (e.g., myprovider)")
    base_url = Prompt.ask("[bold]Base URL[/bold] (e.g., https://api.example.com/v1)")
    model = Prompt.ask("[bold]Default model[/bold] (e.g., gpt-4)")

    add_extra = Confirm.ask("[bold]Add extra aliases?[/bold]", default=False)
    extra_aliases = []
    if add_extra:
        aliases_input = Prompt.ask("[bold]Aliases[/bold] (comma-separated)", default="")
        extra_aliases = [a.strip() for a in aliases_input.split(",") if a.strip()]

    add_login = Confirm.ask("[bold]Add login instructions?[/bold]", default=False)
    login_url = ""
    login_instructions = []
    if add_login:
        login_url = Prompt.ask("[bold]Login URL[/bold]")
        instr_input = Prompt.ask("[bold]Instructions[/bold] (one per line, empty to finish)")
        while instr_input:
            login_instructions.append(instr_input)
            instr_input = Prompt.ask("[bold]Next instruction[/bold] (empty to finish)", default="")

    add_creds = Confirm.ask("[bold]Add API key now?[/bold]", default=False)
    api_key = ""
    if add_creds:
        api_key = Prompt.ask("[bold]API Key[/bold]", password=True)

    success, msg = add_provider(
        name=name,
        base_url=base_url,
        model=model,
        login_url=login_url or None,
        login_instructions=login_instructions or None,
        extra_aliases=extra_aliases or None,
        api_key=api_key or None,
    )

    if success:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]{msg}[/red]")


def _prompt_for_provider_selection(
    providers: list[dict[str, Any]],
    prompt_title: str,
    empty_message: str,
) -> dict[str, Any] | None:
    """Prompt user to select a provider from a numbered list."""
    if not providers:
        console.print(f"[yellow]{empty_message}[/yellow]")
        return None

    console.print(f"\n[bold]{prompt_title}[/bold]")
    for i, provider in enumerate(providers):
        console.print(f"  {i + 1}. {provider.get('name')}")

    idx = Prompt.ask("[bold]Provider number[/bold]", default="1")
    try:
        return providers[int(idx) - 1]
    except (ValueError, IndexError):
        console.print("[red]Invalid selection[/red]")
        return None


def _form_update_provider() -> None:
    providers = list_providers()
    provider = _prompt_for_provider_selection(
        providers,
        prompt_title="Select Provider to Update",
        empty_message="No providers to update",
    )
    if not provider:
        return

    name = provider.get("name")
    console.print(f"\n[bold]Updating: {name}[/bold]\n")

    base_url = Prompt.ask(
        "[bold]New base URL[/bold] (leave empty to keep current)", default=provider.get("base_url", "")
    )
    model = Prompt.ask("[bold]New model[/bold] (leave empty to keep current)", default=provider.get("model", ""))

    success, msg = update_provider(
        name=cast("str", name),
        base_url=base_url or None,
        model=model or None,
    )

    if success:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]{msg}[/red]")


def _form_delete_provider() -> None:
    providers = list_providers()
    provider = _prompt_for_provider_selection(
        providers,
        prompt_title="Select Provider to Delete",
        empty_message="No providers to delete",
    )
    if not provider:
        return

    if Confirm.ask(f"[bold]Delete provider '{provider.get('name')}'?[/bold]", default=False):
        success, msg = delete_provider(cast("str", provider.get("name")))
        if success:
            console.print(f"[green]{msg}[/green]")
        else:
            console.print(f"[red]{msg}[/red]")


def _form_validate_provider() -> None:
    providers = list_providers()
    provider = _prompt_for_provider_selection(
        providers,
        prompt_title="Select Provider to Validate",
        empty_message="No providers to validate",
    )
    if not provider:
        return

    console.print(f"\n[dim]Validating {provider.get('name')}...[/dim]")
    success, msg, _details = validate_provider(cast("str", provider.get("name")))

    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[red]✗ {msg}[/red]")


def _form_list_credentials() -> None:
    creds = list_credentials()
    if not creds:
        console.print("[yellow]No credentials configured[/yellow]")
        return

    table = Table(title="Credentials")
    table.add_column("Type", style="cyan")
    table.add_column("Provider", style="green")
    table.add_column("Details", style="dim")

    for c in creds:
        details = c.get("file") or c.get("base_url", "")[:30]
        table.add_row(c.get("type", ""), c.get("provider", ""), details)

    console.print(table)


def _form_add_api_key() -> None:
    providers = list_providers()
    provider = _prompt_for_provider_selection(
        providers,
        prompt_title="Select Provider for API Key",
        empty_message="No providers available",
    )
    if not provider:
        return

    api_key = Prompt.ask(f"[bold]API Key for {provider.get('name')}[/bold]", password=True)

    success, msg = add_api_key(cast("str", provider.get("name")), api_key)
    if success:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]{msg}[/red]")


def _form_remove_api_key() -> None:
    providers = list_providers()
    provider = _prompt_for_provider_selection(
        providers,
        prompt_title="Select Provider to Remove API Key",
        empty_message="No providers available",
    )
    if not provider:
        return

    if Confirm.ask(f"[bold]Remove API key for '{provider.get('name')}'?[/bold]", default=False):
        success, msg = remove_api_key(cast("str", provider.get("name")))
        if success:
            console.print(f"[green]{msg}[/green]")
        else:
            console.print(f"[red]{msg}[/red]")


def _form_discover_models() -> None:
    console.print("\n[dim]Discovering models from CLIProxy...[/dim]")
    discovery = cast("dict[str, Any]", discover_models(include_status=True))
    models = cast("list[dict[str, Any]]", discovery.get("models", []))
    status = cast("dict[str, Any]", discovery.get("discovery", {}))

    if not models:
        if status.get("status") != "ok":
            console.print(
                f"[yellow]Discovery degraded:[/yellow] {status.get('failure_type', 'unknown')} - {status.get('error_message', '')}"
            )
        console.print("[yellow]No models discovered (is CLIProxy running?)[/yellow]")
        return

    table = Table(title="Discovered Models")
    table.add_column("Model ID", style="cyan")
    table.add_column("Provider", style="green")
    table.add_column("Created", style="dim")

    for m in models[:50]:  # Limit to 50
        created = str(m.get("created", ""))[:8]
        table.add_row(m.get("id", "")[:40], m.get("provider", ""), created)

    console.print(table)
    console.print(f"\n[dim]Showing {min(50, len(models))} of {len(models)} models[/dim]")


# ============ MODEL INDICES (context, cost, speed, benchmarks) ============


def get_model_indices(provider: str | None = None, model: str | None = None) -> dict[str, Any]:
    """Get model indices (context limits, cost, speed, benchmarks)."""
    indices = _load_json(_MODEL_INDICES_PATH)

    result = {}
    providers = indices.get("providers", {})

    for prov_name, prov_data in providers.items():
        if provider and prov_name.lower() != provider.lower():
            continue

        models = prov_data.get("models", {})
        for model_name, model_data in models.items():
            if model and model_name.lower() != model.lower():
                continue
            if prov_name not in result:
                result[prov_name] = {"display_name": prov_data.get("display_name", prov_name), "models": {}}
            result[prov_name]["models"][model_name] = model_data

    return result


def list_model_indices(
    provider: str | None = None,
    sort_by: str = "cost",
    include_all: bool = False,
) -> list[dict[str, Any]]:
    """List models with their indices, sorted by specified criteria."""
    indices = _load_json(_MODEL_INDICES_PATH)
    providers = _load_json(_PROVIDER_DEFINITIONS_PATH)
    weights = indices.get("benchmark_weights", {})

    result = []
    seen_models = set()

    prov_data = indices.get("providers", {})
    for prov_name, prov_cfg in prov_data.items():
        if provider and prov_name.lower() != provider.lower():
            continue

        models = prov_cfg.get("models", {})
        for model_name, model_idx in models.items():
            # Cost fields
            cost_input = model_idx.get("cost_per_1m_input", 0) or 0
            cost_output = model_idx.get("cost_per_1m_output", 0) or 0
            total_cost = cost_input + cost_output

            # Speed fields
            tps = model_idx.get("tps")
            latency = model_idx.get("latency_first_token")

            # Benchmarks and composite score
            benchmarks = model_idx.get("benchmarks", {})
            composite_score = calculate_composite_score(benchmarks, weights)

            result.append(
                {
                    "provider": prov_name,
                    "display_name": prov_cfg.get("display_name", prov_name),
                    "model": model_name,
                    "context_limit": model_idx.get("context_limit"),
                    "output_limit": model_idx.get("output_limit"),
                    "cost_per_1m_input": cost_input,
                    "cost_per_1m_output": cost_output,
                    "total_cost_per_1m": total_cost,
                    "tps": tps,
                    "latency_first_token": latency,
                    "composite_score": composite_score,
                    "benchmarks": benchmarks,
                    "modalities": model_idx.get("modalities", {}),
                    "notes": model_idx.get("notes"),
                }
            )
            seen_models.add(f"{prov_name}:{model_name}")

    if include_all:
        for prov_name, prov_cfg in providers.items():
            if provider and prov_name.lower() != provider.lower():
                continue
            model_name = prov_cfg.get("model", "")
            key = f"{prov_name}:{model_name}"
            if key not in seen_models:
                result.append(
                    {
                        "provider": prov_name,
                        "display_name": prov_name.title(),
                        "model": model_name,
                        "context_limit": None,
                        "output_limit": None,
                        "cost_per_1m_input": None,
                        "cost_per_1m_output": None,
                        "total_cost_per_1m": None,
                        "tps": None,
                        "latency_first_token": None,
                        "swebench": None,
                        "termbench": None,
                        "reasoning": None,
                        "vision": None,
                        "notes": "No index data available",
                    }
                )

    sort_model_rows(result, sort_by)

    return result


def add_model_index(
    provider: str,
    model: str,
    context_limit: int | None = None,
    output_limit: int | None = None,
    cost_per_1m_input: float | None = None,
    cost_per_1m_output: float | None = None,
    tps: int | None = None,
    latency_first_token: float | None = None,
    reasoning: bool | None = None,
    vision: bool | None = None,
    swebench: float | None = None,
    termbench: float | None = None,
    notes: str | None = None,
) -> tuple[bool, str]:
    """Add or update model index data."""
    indices = _load_json(_MODEL_INDICES_PATH)

    prov_name = provider.lower()
    if "providers" not in indices:
        indices["providers"] = {}
    if prov_name not in indices["providers"]:
        indices["providers"][prov_name] = {"display_name": provider.title(), "models": {}}
    if "models" not in indices["providers"][prov_name]:
        indices["providers"][prov_name]["models"] = {}

    model_data = indices["providers"][prov_name]["models"].get(model, {})

    if context_limit is not None:
        model_data["context_limit"] = context_limit
    if output_limit is not None:
        model_data["output_limit"] = output_limit
    if cost_per_1m_input is not None:
        model_data["cost_per_1m_input"] = cost_per_1m_input
    if cost_per_1m_output is not None:
        model_data["cost_per_1m_output"] = cost_per_1m_output
    if tps is not None:
        model_data["tps"] = tps
    if latency_first_token is not None:
        model_data["latency_first_token"] = latency_first_token
    if reasoning is not None:
        model_data["reasoning"] = reasoning
    if vision is not None:
        model_data["vision"] = vision
    if swebench is not None:
        model_data["swebench"] = swebench
    if termbench is not None:
        model_data["termbench"] = termbench
    if notes is not None:
        model_data["notes"] = notes

    indices["providers"][prov_name]["models"][model] = model_data
    _save_json(_MODEL_INDICES_PATH, indices)

    return True, f"Index updated for {provider}/{model}"


def remove_model_index(provider: str, model: str) -> tuple[bool, str]:
    """Remove model index data."""
    indices = _load_json(_MODEL_INDICES_PATH)

    prov_name = provider.lower()
    if prov_name in indices.get("providers", {}):
        models = indices["providers"][prov_name].get("models", {})
        if model in models:
            del models[model]
            _save_json(_MODEL_INDICES_PATH, indices)
            return True, f"Index removed for {provider}/{model}"

    return False, f"No index found for {provider}/{model}"


def search_models_by_capability(
    capability: str,
    min_context: int | None = None,
    max_cost_per_1m: float | None = None,
    min_tps: int | None = None,
) -> list[dict[str, Any]]:
    """Search models by capability (reasoning, vision, swebench, termbench)."""
    all_models = list_model_indices(sort_by="cost")

    result = []
    for m in all_models:
        # Check capability
        if capability == "reasoning" and not m.get("reasoning"):
            continue
        if capability == "vision" and not m.get("vision"):
            continue
        # Check benchmark scores
        if capability == "swebench":
            if not m.get("swebench") or cast("float", m.get("swebench")) < 0.4:
                continue
        if capability == "termbench":
            if not m.get("termbench") or cast("float", m.get("termbench")) < 0.45:
                continue

        # Check filters
        if min_context and (m.get("context_limit") or 0) < min_context:
            continue
        if max_cost_per_1m and (m.get("total_cost_per_1m") or float("inf")) > max_cost_per_1m:
            continue
        if min_tps and (m.get("tps") or 0) < min_tps:
            continue

        result.append(m)

    return result


# ============ MODALITIES & CUSTOM BENCHMARKS ============


def get_model_modalities(provider: str | None = None, model: str | None = None) -> dict[str, Any]:
    """Get model modalities/feature flags.

    Args:
        provider: Optional provider filter
        model: Optional model filter

    Returns:
        Dict of models with their modalities
    """
    indices = _load_json(_MODEL_INDICES_PATH)

    result = {}
    providers = indices.get("providers", {})

    for prov_name, prov_data in providers.items():
        if provider and prov_name.lower() != provider.lower():
            continue

        models = prov_data.get("models", {})
        for model_name, model_data in models.items():
            if model and model_name.lower() != model.lower():
                continue

            modalities = model_data.get("modalities", {})
            if modalities:
                result[f"{prov_name}/{model_name}"] = {
                    "provider": prov_name,
                    "model": model_name,
                    "modalities": modalities,
                }

    return result


def calculate_composite_score(
    benchmarks: dict[str, float],
    weights: dict[str, float] | None = None,
) -> float | None:
    """Calculate composite performance score from benchmarks.

    Uses available benchmarks only - missing benchmarks don't penalize.
    Results are normalized to 0-100 scale.

    Args:
        benchmarks: Dict of benchmark_name -> score (0-1)
        weights: Optional custom weights for benchmarks

    Returns:
        Composite score 0-100, or None if no benchmarks available
    """
    if not benchmarks:
        return None

    # Default weights for standard benchmarks
    default_weights = {
        "swebench": 0.25,
        "termbench": 0.25,
        "humaneval": 0.20,
        "mmlu": 0.15,
        "reasoning": 0.15,
    }

    if weights is None:
        weights = default_weights

    total_weight = 0.0
    weighted_sum = 0.0

    for benchmark, score in benchmarks.items():
        if score is None:
            continue

        weight = weights.get(benchmark, 0.1)  # Default 0.1 for custom benchmarks
        weighted_sum += score * weight
        total_weight += weight

    if total_weight == 0:
        return None

    # Normalize to 0-100 scale
    return (weighted_sum / total_weight) * 100


def list_models_with_scores(
    provider: str | None = None,
    min_score: float | None = None,
    modality: str | None = None,
    sort_by: str = "composite_score",
) -> list[dict[str, Any]]:
    """List models with composite performance scores.

    Args:
        provider: Optional provider filter
        min_score: Minimum composite score filter
        modality: Only include models with this modality enabled
        sort_by: Sort by 'composite_score', 'cost', 'context', 'tps'

    Returns:
        List of models with computed composite scores
    """
    indices = _load_json(_MODEL_INDICES_PATH)
    weights = indices.get("benchmark_weights", {})

    result = []
    providers_map = indices.get("providers", {})

    for prov_name, prov_data in providers_map.items():
        if provider and prov_name.lower() != provider.lower():
            continue

        models = prov_data.get("models", {})
        for model_name, model_data in models.items():
            # Check modality filter
            if modality:
                modalities = model_data.get("modalities", {})
                if not modalities.get(modality, False):
                    continue

            # Get benchmarks
            benchmarks = model_data.get("benchmarks", {})
            composite_score = calculate_composite_score(benchmarks, weights)

            # Get cost efficiency (score per dollar)
            cost_input = model_data.get("cost_per_1m_input", 0) or 0
            cost_output = model_data.get("cost_per_1m_output", 0) or 0
            total_cost = cost_input + cost_output

            result.append(
                {
                    "provider": prov_name,
                    "model": model_name,
                    "display_name": prov_data.get("display_name", prov_name),
                    "context_limit": model_data.get("context_limit"),
                    "cost_per_1m": total_cost,
                    "tps": model_data.get("tps"),
                    "composite_score": composite_score,
                    "benchmarks": benchmarks,
                    "modalities": model_data.get("modalities", {}),
                    "notes": model_data.get("notes"),
                }
            )

    sort_model_rows(result, sort_by)

    # Filter by minimum score
    if min_score is not None:
        result = [m for m in result if (m.get("composite_score") or 0) >= min_score]

    return result


def add_custom_benchmark(
    provider: str,
    model: str,
    benchmark_name: str,
    score: float,
    category: str = "custom",
    description: str = "",
) -> tuple[bool, str]:
    """Add a custom benchmark entry for a model.

    Args:
        provider: Provider name
        model: Model name
        benchmark_name: Name of the benchmark
        score: Score (0-1)
        category: Category (coding, reasoning, general, etc.)
        description: Optional description

    Returns:
        (success, message)
    """
    indices = _load_json(_MODEL_INDICES_PATH)

    prov_name = provider.lower()
    model_name = model.lower()

    # Ensure structure exists
    if "providers" not in indices:
        return False, "No providers in indices"
    if prov_name not in indices["providers"]:
        return False, f"Provider '{provider}' not found"

    models = indices["providers"][prov_name].get("models", {})
    if model_name not in models:
        return False, f"Model '{model}' not found"

    # Add custom benchmark
    if "benchmarks" not in models[model_name]:
        models[model_name]["benchmarks"] = {}

    models[model_name]["benchmarks"][benchmark_name] = score

    # Store custom benchmark metadata
    if "custom_benchmarks" not in indices:
        indices["custom_benchmarks"] = {}
    indices["custom_benchmarks"][benchmark_name] = {
        "category": category,
        "description": description,
        "added_by": "user",
    }

    _save_json(_MODEL_INDICES_PATH, indices)
    return True, f"Added benchmark '{benchmark_name}'={score} for {provider}/{model}"


def fuzzy_search_models(
    query: str,
    fields: list[str] | None = None,
    provider: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Fuzzy search models by query string.

    Simple fuzzy matching - matches query as substring in any field.

    Args:
        query: Search query
        fields: Fields to search (default: provider, model, notes)
        provider: Optional provider filter
        limit: Maximum results

    Returns:
        List of matching models
    """
    if fields is None:
        fields = ["provider", "model", "notes"]

    all_models = list_model_indices(provider=provider, include_all=True)
    query_lower = query.lower()

    result = []
    for m in all_models:
        score = 0

        # Calculate fuzzy match score
        for field in fields:
            value = str(m.get(field, "")).lower()
            if value == query_lower:
                score += 10  # Exact match
            elif query_lower in value:
                score += 5  # Substring match
            elif any(q in value for q in query_lower.split()):
                score += 2  # Word match

        if score > 0:
            m["_fuzzy_score"] = score
            result.append(m)

    # Sort by fuzzy score
    result.sort(key=lambda x: x.get("_fuzzy_score", 0), reverse=True)

    return result[:limit]


def add_model_modality(
    provider: str,
    model: str,
    modality: str,
    value: bool | str = True,
) -> tuple[bool, str]:
    """Add or update a modality/feature flag for a model.

    Args:
        provider: Provider name
        model: Model name
        modality: Modality/feature name
        value: Value (true/false or custom string)

    Returns:
        (success, message)
    """
    indices = _load_json(_MODEL_INDICES_PATH)

    prov_name = provider.lower()
    model_name = model.lower()

    if "providers" not in indices:
        return False, "No providers in indices"
    if prov_name not in indices["providers"]:
        return False, f"Provider '{provider}' not found"

    models = indices["providers"][prov_name].get("models", {})
    if model_name not in models:
        return False, f"Model '{model}' not found"

    if "modalities" not in models[model_name]:
        models[model_name]["modalities"] = {}

    models[model_name]["modalities"][modality] = value
    _save_json(_MODEL_INDICES_PATH, indices)

    return True, f"Set {modality}={value} for {provider}/{model}"


def list_available_modalities() -> dict[str, Any]:
    """List all available modality definitions."""
    indices = _load_json(_MODEL_INDICES_PATH)
    return indices.get("modalities_schema", {})


def search_by_modalities(
    required_modalities: list[str],
    excluded_modalities: list[str] | None = None,
    provider: str | None = None,
    sort_by: str = "composite_score",
) -> list[dict[str, Any]]:
    """Search models by modality requirements.

    Args:
        required_modalities: List of modalities that must be enabled
        excluded_modalities: List of modalities that must NOT be enabled
        provider: Optional provider filter
        sort_by: Sort field

    Returns:
        Matching models
    """
    all_models = list_models_with_scores(provider=provider, sort_by=sort_by)

    result = []
    for m in all_models:
        modalities = m.get("modalities", {})

        # Check required
        if not all(modalities.get(mod, False) for mod in required_modalities):
            continue

        # Check excluded
        if excluded_modalities:
            if any(modalities.get(mod, False) for mod in excluded_modalities):
                continue

        result.append(m)

    return result
