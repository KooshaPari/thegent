"""Compatibility helpers for CLIProxy provider metadata management."""

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
    entry = next((item for item in compat if item.get("name") == name), None)
    if entry is None:
        entry = {"name": name}
        compat.append(entry)
    entry["base_url"] = base_url
    entry["model"] = model
    entry["api_key"] = api_key


def remove_openai_compat_entry(compat: list[dict[str, Any]], name: str) -> list[dict[str, Any]]:
    return [item for item in compat if item.get("name") != name]

