"""Shared JSON/YAML storage helpers for provider and model definitions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import orjson

from thegent.infra.fast_yaml_parser import yaml_dumps, yaml_load

_DATA_DIR = Path(__file__).resolve().parent / "agents" / "cliproxy_data"

MODEL_DEFINITIONS_PATH = _DATA_DIR / "model_definitions.json"
PROVIDER_DEFINITIONS_PATH = _DATA_DIR / "provider_definitions.json"
PROVIDER_MAPPING_PATH = _DATA_DIR / "provider_mapping.json"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = orjson.loads(path.read_bytes())
    return data if isinstance(data, dict) else {}


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(orjson.dumps(data, option=orjson.OPT_INDENT_2))


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml_load(path)
    return data if isinstance(data, dict) else {}


def save_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml_dumps(data, sort_keys=False), encoding="utf-8")


def update_provider_mapping(
    path: Path,
    name: str,
    *,
    is_openai_compat: bool = False,
    remove: bool = False,
) -> None:
    mapping = load_json(path)
    openai_compat = list(mapping.get("openai_compat", []))
    providers = list(mapping.get("providers", []))

    if remove:
        openai_compat = [item for item in openai_compat if item != name]
        providers = [item for item in providers if item != name]
    else:
        if name not in providers:
            providers.append(name)
        if is_openai_compat and name not in openai_compat:
            openai_compat.append(name)

    mapping["providers"] = providers
    mapping["openai_compat"] = openai_compat
    save_json(path, mapping)

