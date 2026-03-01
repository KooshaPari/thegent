"""JSON/YAML file I/O adapter for provider/model persistence.

This module adapts the storage port to concrete JSON and YAML file implementations.
It delegates to provider_model_manager_io for core persistence logic.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from thegent.provider_model_manager_io import (
    MODEL_DEFINITIONS_PATH,
    MODEL_INDICES_PATH,
    PROVIDER_DEFINITIONS_PATH,
    PROVIDER_MAPPING_PATH,
    load_json,
    load_yaml,
    save_json,
    save_yaml,
)

_LOG = logging.getLogger(__name__)


class ProviderIOAdapter:
    """Adapter for JSON-based provider/model I/O."""

    @staticmethod
    def load_providers() -> dict[str, Any]:
        """Load all provider definitions from JSON.

        Returns:
            Dict mapping provider name to configuration.
        """
        return load_json(PROVIDER_DEFINITIONS_PATH)

    @staticmethod
    def save_providers(providers: dict[str, Any]) -> None:
        """Save provider definitions to JSON.

        Args:
            providers: Dict mapping provider name to configuration.
        """
        save_json(PROVIDER_DEFINITIONS_PATH, providers)

    @staticmethod
    def load_models() -> dict[str, Any]:
        """Load all model definitions from JSON.

        Returns:
            Dict with model metadata and common aliases.
        """
        return load_json(MODEL_DEFINITIONS_PATH)

    @staticmethod
    def save_models(models: dict[str, Any]) -> None:
        """Save model definitions to JSON.

        Args:
            models: Dict with model metadata and common aliases.
        """
        save_json(MODEL_DEFINITIONS_PATH, models)

    @staticmethod
    def load_provider_mapping() -> dict[str, Any]:
        """Load provider mapping (lists of compatible/native providers).

        Returns:
            Dict with mapping metadata.
        """
        return load_json(PROVIDER_MAPPING_PATH)

    @staticmethod
    def save_provider_mapping(mapping: dict[str, Any]) -> None:
        """Save provider mapping to JSON.

        Args:
            mapping: Dict with mapping metadata.
        """
        save_json(PROVIDER_MAPPING_PATH, mapping)

    @staticmethod
    def load_model_indices() -> dict[str, Any]:
        """Load model indices from JSON.

        Returns:
            Dict with model index data.
        """
        return load_json(MODEL_INDICES_PATH)

    @staticmethod
    def save_model_indices(indices: dict[str, Any]) -> None:
        """Save model indices to JSON.

        Args:
            indices: Dict with model index data.
        """
        save_json(MODEL_INDICES_PATH, indices)


class CliproxyIOAdapter:
    """Adapter for YAML-based CLIProxy config I/O."""

    @staticmethod
    def load_config(config_path: Path) -> dict[str, Any]:
        """Load CLIProxy configuration from YAML.

        Args:
            config_path: Path to the config file.

        Returns:
            Dict with CLIProxy configuration.
        """
        return load_yaml(config_path)

    @staticmethod
    def save_config(config_path: Path, config: dict[str, Any]) -> None:
        """Save CLIProxy configuration to YAML.

        Args:
            config_path: Path to the config file.
            config: Dict with CLIProxy configuration.
        """
        save_yaml(config_path, config)


__all__ = [
    "ProviderIOAdapter",
    "CliproxyIOAdapter",
]
