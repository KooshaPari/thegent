"""CLIProxy config helpers for provider/model manager."""

from __future__ import annotations

from typing import Any


def upsert_openai_compat_entry(
    compat: list[dict[str, Any]],
    *,
    name: str,
    base_url: str,
    model: str,
    api_key: str,
) -> None:
    """Add or update an openai-compatibility entry in-place."""
    for entry in compat:
        if entry.get("name") == name:
            entry["api-key-entries"] = [{"api-key": api_key}]
            return
    compat.append(
        {
            "name": name,
            "base-url": base_url,
            "api-key-entries": [{"api-key": api_key}],
            "models": [{"name": model, "alias": model}],
        }
    )


def remove_openai_compat_entry(compat: list[dict[str, Any]], name: str) -> list[dict[str, Any]]:
    """Return compat entries excluding the requested provider name."""
    return [entry for entry in compat if entry.get("name") != name]


def get_api_key_from_compat(compat: list[dict[str, Any]], name: str) -> str | None:
    """Get first API key from provider compat entry."""
    for entry in compat:
        if entry.get("name") == name:
            entries = entry.get("api-key-entries", [])
            if entries:
                return entries[0].get("api-key")
            return None
    return None
