"""Enhance config-get: YAML support, hook-config.yaml, qa-local.json."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ConfigEnhance:
    """Enhanced config management."""

    def __init__(self):
        """Initialize config enhance."""
        self.configs: dict[str, Any] = {}

    def get_config(self, key: str, config_file: Path | None = None) -> Any:
        """Get config value.
        
        Args:
            key: Config key
            config_file: Optional config file path
            
        Returns:
            Config value
        """
        if config_file:
            config = self._load_config(config_file)
            return config.get(key)
        
        # Try hook-config.yaml
        hook_config = Path("hook-config.yaml")
        if hook_config.exists():
            config = self._load_yaml(hook_config)
            return config.get(key)
        
        # Try qa-local.json
        qa_config = Path("qa-local.json")
        if qa_config.exists():
            config = self._load_json(qa_config)
            return config.get(key)
        
        return None

    def _load_config(self, config_file: Path) -> dict[str, Any]:
        """Load config file.
        
        Args:
            config_file: Config file path
            
        Returns:
            Config dictionary
        """
        if config_file.suffix == ".yaml":
            return self._load_yaml(config_file)
        elif config_file.suffix == ".json":
            return self._load_json(config_file)
        return {}

    def _load_yaml(self, yaml_file: Path) -> dict[str, Any]:
        """Load YAML file.
        
        Args:
            yaml_file: YAML file path
            
        Returns:
            Parsed dictionary
        """
        try:
            import yaml
            return yaml.safe_load(yaml_file.read_text()) or {}
        except Exception as e:
            logger.error(f"Error loading YAML {yaml_file}: {e}")
            return {}

    def _load_json(self, json_file: Path) -> dict[str, Any]:
        """Load JSON file.
        
        Args:
            json_file: JSON file path
            
        Returns:
            Parsed dictionary
        """
        try:
            return json.loads(json_file.read_text())
        except Exception as e:
            logger.error(f"Error loading JSON {json_file}: {e}")
            return {}
