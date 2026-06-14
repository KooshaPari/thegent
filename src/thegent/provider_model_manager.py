"""Provider and model discovery/validation helpers."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import httpx

from thegent.config import ThegentSettings
from thegent.infra.fast_yaml_parser import yaml_load

_LOG = logging.getLogger(__name__)
_DATA_DIR = Path(__file__).resolve().parent / "agents" / "cliproxy_data"

__all__ = ["discover_models", "run_provider_form", "validate_provider"]


def _ensure_config(settings: ThegentSettings | None = None) -> Path:
    """Ensure the cliproxy config file exists and return its path."""

    settings = settings or ThegentSettings()
    config_path = settings.cliproxy_config_path.expanduser().resolve()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if not config_path.exists():
        config_path.write_text("port: %d\n" % settings.cliproxy_port, encoding="utf-8")
    return config_path


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML config file."""

    try:
        data = yaml_load(path)
    except Exception:  # noqa: BLE001
        return {}
    return data if isinstance(data, dict) else {}


def _load_json(name: str) -> dict[str, Any]:
    """Load a JSON payload from the bundled cliproxy data directory."""

    path = _DATA_DIR / name
    if not path.exists():
        return {}
    try:
        import json

        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return data if isinstance(data, dict) else {}


def _normalize_base_url(base_url: str | None, port: int | None = None) -> str:
    if base_url:
        return base_url.rstrip("/")
    effective_port = port or ThegentSettings().cliproxy_port
    return f"http://127.0.0.1:{effective_port}"


def _failure_details(
    *,
    provider: str | None,
    failure_class: str,
    failure_type: str,
    message: str,
    catalog_state: str = "empty",
    malformed_count: int = 0,
) -> dict[str, Any]:
    return {
        "provider": provider,
        "status": "error",
        "failure_class": failure_class,
        "failure_type": failure_type,
        "failure_message": message,
        "catalog_state": catalog_state,
        "malformed_count": malformed_count,
        "error": True,
    }


def _success_details(
    *,
    provider: str | None,
    catalog_state: str,
    malformed_count: int,
    message: str | None = None,
) -> dict[str, Any]:
    return {
        "provider": provider,
        "status": "ok",
        "failure_class": None,
        "failure_type": None,
        "failure_message": message,
        "catalog_state": catalog_state,
        "malformed_count": malformed_count,
        "error": False,
    }


def _classify_transport_error(exc: Exception) -> tuple[str, str]:
    if isinstance(exc, httpx.TimeoutException):
        return "transport", "timeout"
    if isinstance(exc, httpx.ConnectError):
        return "transport", "connect_error"
    return "transport", exc.__class__.__name__.lower()


def _lookup_provider_definition(provider: str | None, provider_defs: dict[str, Any]) -> dict[str, Any] | None:
    if not provider:
        return None
    entry = provider_defs.get(provider.lower())
    return entry if isinstance(entry, dict) else None


def _extract_provider_config(config: dict[str, Any], provider: str | None) -> dict[str, Any] | None:
    if not provider:
        return None

    compat = config.get("openai-compatibility")
    if isinstance(compat, list):
        for entry in compat:
            if isinstance(entry, dict) and str(entry.get("name", "")).lower() == provider.lower():
                return entry
    providers = config.get("providers")
    if isinstance(providers, dict):
        entry = providers.get(provider.lower())
        if isinstance(entry, dict):
            return entry
    return None


def _provider_base_url(provider: str | None, provider_defs: dict[str, Any], config: dict[str, Any]) -> str:
    provider_entry = _lookup_provider_definition(provider, provider_defs)
    if provider_entry:
        base_url = provider_entry.get("base_url") or provider_entry.get("base-url")
        if isinstance(base_url, str) and base_url.strip():
            return base_url.rstrip("/")

    config_entry = _extract_provider_config(config, provider)
    if config_entry:
        base_url = config_entry.get("base_url") or config_entry.get("base-url")
        if isinstance(base_url, str) and base_url.strip():
            return base_url.rstrip("/")

    port = config.get("port")
    if isinstance(port, int):
        return _normalize_base_url(None, port)

    return _normalize_base_url(None)


def _provider_model(provider: str | None, provider_defs: dict[str, Any], config: dict[str, Any]) -> str:
    provider_entry = _lookup_provider_definition(provider, provider_defs)
    if provider_entry:
        model = provider_entry.get("model")
        if isinstance(model, str) and model.strip():
            return model

    config_entry = _extract_provider_config(config, provider)
    if config_entry:
        model = config_entry.get("model")
        if isinstance(model, str) and model.strip():
            return model

    return provider or "model"


def _response_json(response: Any) -> Any:
    if not hasattr(response, "json"):
        return None
    return response.json()


def discover_models(provider: str | None = None, include_status: bool = False) -> list[dict[str, Any]] | dict[str, Any]:
    """Discover available models from the local provider proxy."""

    provider_name = provider.lower() if isinstance(provider, str) and provider.strip() else None
    config_path = _ensure_config()
    config = _load_yaml(config_path)
    provider_defs = _load_json("provider_definitions.json")

    base_url = _provider_base_url(provider_name, provider_defs, config)
    url = f"{base_url}/v1/models"

    try:
        response = httpx.get(url, timeout=10)
    except Exception as exc:  # noqa: BLE001
        failure_class, failure_type = _classify_transport_error(exc)
        _LOG.warning(
            "provider discovery failed",
            extra={"provider": provider_name, "failure_class": failure_class, "failure_type": failure_type},
        )
        payload = {
            "models": [],
            "discovery": _failure_details(
                provider=provider_name,
                failure_class=failure_class,
                failure_type=failure_type,
                message=str(exc),
            ),
        }
        return payload if include_status else payload["models"]

    if getattr(response, "status_code", 0) >= 400:
        message = f"unexpected status {getattr(response, 'status_code', 'unknown')}"
        _LOG.warning(
            "provider discovery failed",
            extra={"provider": provider_name, "failure_class": "protocol", "failure_type": "status_error"},
        )
        payload = {
            "models": [],
            "discovery": _failure_details(
                provider=provider_name,
                failure_class="protocol",
                failure_type="status_error",
                message=message,
            ),
        }
        return payload if include_status else payload["models"]

    try:
        data = _response_json(response)
    except Exception as exc:  # noqa: BLE001
        _LOG.warning(
            "provider discovery failed",
            extra={"provider": provider_name, "failure_class": "protocol", "failure_type": "payload_decode_error"},
        )
        payload = {
            "models": [],
            "discovery": _failure_details(
                provider=provider_name,
                failure_class="protocol",
                failure_type="payload_decode_error",
                message=str(exc),
            ),
        }
        return payload if include_status else payload["models"]

    if not isinstance(data, dict):
        _LOG.warning(
            "provider discovery failed",
            extra={"provider": provider_name, "failure_class": "protocol", "failure_type": "payload_not_object"},
        )
        payload = {
            "models": [],
            "discovery": _failure_details(
                provider=provider_name,
                failure_class="protocol",
                failure_type="payload_not_object",
                message="discovery payload is not an object",
            ),
        }
        return payload if include_status else payload["models"]

    models_raw = data.get("models")
    if not isinstance(models_raw, list):
        _LOG.warning(
            "provider discovery failed",
            extra={"provider": provider_name, "failure_class": "protocol", "failure_type": "models_not_list"},
        )
        payload = {
            "models": [],
            "discovery": _failure_details(
                provider=provider_name,
                failure_class="protocol",
                failure_type="models_not_list",
                message="models field is not a list",
            ),
        }
        return payload if include_status else payload["models"]

    models: list[dict[str, Any]] = []
    malformed_count = 0
    for row in models_raw:
        if not isinstance(row, dict):
            malformed_count += 1
            continue
        row_provider = row.get("owned_by")
        if not isinstance(row_provider, str) or not row_provider.strip():
            malformed_count += 1
            continue
        if provider_name and row_provider.lower() != provider_name:
            continue
        entry = dict(row)
        entry["provider"] = row_provider
        models.append(entry)

    catalog_state = "available" if models else "empty"
    payload = {
        "models": models,
        "discovery": _success_details(
            provider=provider_name,
            catalog_state=catalog_state,
            malformed_count=malformed_count,
        ),
    }
    return payload if include_status else payload["models"]


def validate_provider(provider: str, *_args: Any, **_kwargs: Any) -> tuple[bool, str, dict[str, Any]]:
    """Validate a provider by probing its OpenAI-compatible endpoint."""

    provider_name = provider.lower().strip()
    config_path = _ensure_config()
    config = _load_yaml(config_path)
    provider_defs = _load_json("provider_definitions.json")
    provider_entry = _lookup_provider_definition(provider_name, provider_defs) or _extract_provider_config(config, provider_name)

    if not provider_entry:
        details = _failure_details(
            provider=provider_name,
            failure_class="configuration",
            failure_type="provider_not_found",
            message=f"Provider '{provider_name}' not found",
        )
        return False, details["failure_message"], details

    base_url = _provider_base_url(provider_name, provider_defs, config)
    model = _provider_model(provider_name, provider_defs, config)
    url = f"{base_url}/v1/responses"
    payload = {
        "model": model,
        "input": [{"role": "user", "content": "validate provider"}],
        "max_output_tokens": 1,
    }

    try:
        response = httpx.post(url, json=payload, timeout=10)
    except Exception as exc:  # noqa: BLE001
        failure_class, failure_type = _classify_transport_error(exc)
        _LOG.warning(
            "provider validation failed",
            extra={"provider": provider_name, "failure_class": failure_class, "failure_type": failure_type},
        )
        details = _failure_details(
            provider=provider_name,
            failure_class=failure_class,
            failure_type=failure_type,
            message=str(exc),
        )
        return False, details["failure_message"], details

    if getattr(response, "status_code", 0) >= 400:
        failure_type = f"status_{getattr(response, 'status_code', 'unknown')}"
        _LOG.warning(
            "provider validation failed",
            extra={"provider": provider_name, "failure_class": "protocol", "failure_type": failure_type},
        )
        details = _failure_details(
            provider=provider_name,
            failure_class="protocol",
            failure_type=failure_type,
            message=f"unexpected status {getattr(response, 'status_code', 'unknown')}",
        )
        return False, details["failure_message"], details

    try:
        data = _response_json(response)
    except Exception as exc:  # noqa: BLE001
        _LOG.warning(
            "provider validation failed",
            extra={"provider": provider_name, "failure_class": "protocol", "failure_type": "payload_decode_error"},
        )
        details = _failure_details(
            provider=provider_name,
            failure_class="protocol",
            failure_type="payload_decode_error",
            message=str(exc),
        )
        return False, details["failure_message"], details

    if data is not None and not isinstance(data, dict):
        _LOG.warning(
            "provider validation failed",
            extra={"provider": provider_name, "failure_class": "protocol", "failure_type": "payload_not_object"},
        )
        details = _failure_details(
            provider=provider_name,
            failure_class="protocol",
            failure_type="payload_not_object",
            message="validation payload is not an object",
        )
        return False, details["failure_message"], details

    details = _success_details(
        provider=provider_name,
        catalog_state="available",
        malformed_count=0,
        message="provider validated",
    )
    details["response_status"] = getattr(response, "status_code", None)
    return True, f"Provider '{provider_name}' validated", details


def run_provider_form() -> None:
    """Compatibility stub for the legacy interactive provider form."""

    return None
