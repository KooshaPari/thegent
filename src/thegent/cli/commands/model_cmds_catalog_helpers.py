"""Catalog/list-model helpers for model_cmds."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

_DEFAULT_PROVIDERS: tuple[str, ...] = (
    "minimax",
    "glm",
    "cursor",
    "kiro",
    "gemini",
    "copilot",
    "interactive_agent",
    "headless_agent",
    "antigravity",
)


def emit_contract_view(*, provider: str | None, refresh: bool, console: Any) -> None:
    """Emit contract-style model catalog view."""
    from thegent.models import ModelCatalog
    from thegent.models.scrapers import get_scraped_catalog

    if refresh:
        get_scraped_catalog(refresh=True)
    payload = ModelCatalog.to_contract_view(
        use_scraped=True,
        use_cache=not refresh,
        provider_filter=provider,
    )
    console.print_json(data=payload)


def emit_by_model_view(*, refresh: bool, console: Any) -> None:
    """Emit model-to-provider routing view."""
    from thegent.models import ModelCatalog
    from thegent.models.scrapers import get_scraped_catalog

    get_scraped_catalog(use_cache=not refresh)
    view = ModelCatalog.to_catalog_view(use_scraped=True)
    console.print("\n[bold]Models by model ID (routing)[/bold]")
    for model_id, providers in sorted(view.by_model.items()):
        console.print(f"  {model_id}: {', '.join(providers)}")


def provider_sequence(provider: str | None) -> list[str]:
    """Resolve provider list to emit."""
    return [provider] if provider else list(_DEFAULT_PROVIDERS)


def run_provider_listings(
    providers: list[str],
    *,
    handlers: dict[str, Callable[[], None]],
) -> None:
    """Dispatch provider listing handlers in order."""
    for provider in providers:
        handler = handlers.get(provider)
        if handler is not None:
            handler()
