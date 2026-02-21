"""I/O and path helpers for provider/model manager data files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

# Paths to definition files used by provider_model_manager.
CLIPROXY_DATA_DIR = Path(__file__).parent / "agents" / "cliproxy_data"
PROVIDER_DEFINITIONS_PATH = CLIPROXY_DATA_DIR / "provider_definitions.json"
MODEL_DEFINITIONS_PATH = CLIPROXY_DATA_DIR / "model_definitions.json"
PROVIDER_MAPPING_PATH = CLIPROXY_DATA_DIR / "provider_mapping.json"
MODEL_INDICES_PATH = CLIPROXY_DATA_DIR / "model_indices.json"


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON file."""
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_json(path: Path, data: dict[str, Any]) -> None:
    """Save JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML file."""
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def save_yaml(path: Path, data: dict[str, Any]) -> None:
    """Save YAML file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False)


def update_provider_mapping(
    mapping_path: Path,
    name: str,
    *,
    is_openai_compat: bool = False,
    remove: bool = False,
) -> None:
    """Update provider_mapping.json lists."""
    mapping = load_json(mapping_path)

    openai_list = mapping.get("openai_compat_providers", [])
    native_list = mapping.get("cliproxy_native_providers", [])

    if remove:
        openai_list = [provider for provider in openai_list if provider != name]
        native_list = [provider for provider in native_list if provider != name]
    elif is_openai_compat and name not in openai_list:
        openai_list.append(name)
    elif not is_openai_compat and name not in native_list:
        native_list.append(name)

    mapping["openai_compat_providers"] = openai_list
    mapping["cliproxy_native_providers"] = native_list
    save_json(mapping_path, mapping)
