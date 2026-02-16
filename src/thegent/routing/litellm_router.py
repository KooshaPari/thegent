"""LiteLLM Router wrapper for multi-provider API routing."""

from __future__ import annotations

import logging
import os
from typing import Any

from litellm import Router

from thegent.models.catalog import Route, _get_catalog
from thegent.routing.provider_types import (
    API_KEY_PROVIDERS,
    NATIVE_CLI_PROVIDERS,
    ExecutionPath,
    get_execution_path,
)

logger = logging.getLogger(__name__)


def _route_to_litellm_config(route: Route) -> dict[str, Any]:
    """Convert a catalog Route to LiteLLM model_list config.

    Args:
        route: Catalog route with provider, model_alias, etc.

    Returns:
        LiteLLM model_list entry dict
    """
    model_name = route.model_alias
    provider = route.provider

    # Determine litellm model string
    # LiteLLM format: "provider/model-name"
    litellm_model = f"{provider}/{model_name}"

    # For API key providers, get API key from environment
    api_key_env = _get_api_key_env(provider)
    api_key = os.environ.get(api_key_env, "dummy-key")

    config = {
        "model_name": model_name,
        "litellm_params": {
            "model": litellm_model,
            "api_key": api_key,
        },
    }

    # For CLIProxyAPIPlus providers, route through proxy
    if get_execution_path(provider) == ExecutionPath.CLIPROXY_API:
        config["litellm_params"]["api_base"] = "http://localhost:8317/v1"

    return config


def _get_api_key_env(provider: str) -> str:
    """Get environment variable name for provider API key."""
    mapping = {
        "minimax": "MINIMAX_API_KEY",
        "nim": "NVIDIA_API_KEY",
        "glm": "ZHIPU_API_KEY",
        "kilo": "KILO_API_KEY",
    }
    return mapping.get(provider, f"{provider.upper()}_API_KEY")


def build_litellm_model_list() -> list[dict[str, Any]]:
    """Build LiteLLM model_list from catalog routes.

    Excludes NATIVE_CLI_PROVIDERS (codex, claude).
    Routes API_KEY_PROVIDERS directly.
    Routes LOGIN_AUTH_PROVIDERS via CLIProxyAPIPlus.

    Returns:
        List of LiteLLM model_list entries
    """
    model_list: list[dict[str, Any]] = []
    seen_models: set[str] = set()

    catalog = _get_catalog()
    for model_id, routes in catalog.items():
        for route in routes:
            # Skip native CLI providers
            if route.provider in NATIVE_CLI_PROVIDERS:
                continue

            # Avoid duplicates
            key = f"{route.provider}/{route.model_alias}"
            if key in seen_models:
                continue
            seen_models.add(key)

            config = _route_to_litellm_config(route)
            model_list.append(config)

    return model_list


def get_litellm_router(policy: str = "cheapest") -> Router:
    """Get configured LiteLLM Router instance.

    Args:
        policy: Routing policy (cheapest, fastest, round_robin)

    Returns:
        Configured LiteLLM Router
    """
    model_list = build_litellm_model_list()

    return Router(
        model_list=model_list,
        routing_strategy=policy,
        num_retries=2,
        timeout=300,
        retry_after=5,
    )
