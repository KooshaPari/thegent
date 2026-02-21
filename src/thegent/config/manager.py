"""Configuration management."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ConfigManager:
    """Configuration manager."""

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize config manager.

        Args:
            config_path: Config file path
        """
        self.config_path = config_path or Path("~/.thegent/config.json").expanduser()
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config: dict[str, Any] = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load config from file.

        Returns:
            Config dictionary
        """
        if self.config_path.exists():
            try:
                return json.loads(self.config_path.read_text())
            except Exception:
                return {}
        return {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value.

        Args:
            key: Config key
            default: Default value

        Returns:
            Config value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set config value.

        Args:
            key: Config key
            value: Config value
        """
        self.config[key] = value
        self._save_config()

    def _save_config(self) -> None:
        """Save config to file."""
        self.config_path.write_text(json.dumps(self.config, indent=2))
