"""Unified configuration system across all systems."""

import contextlib
import re
from pathlib import Path
from typing import Any

from thegent.infra import yaml_load, yaml_loads, get_cache
from thegent.platform_paths import get_config_dir

__all__ = ["UnifiedConfigManager"]

# OPT-019: Cache for unified config (configs don't change often)
try:
    _UNIFIED_CONFIG_CACHE = get_cache(l1_size=10, l2_size=50, l3_path=None, default_ttl=300)
    _USE_UNIFIED_CACHE = True
except ImportError:
    _USE_UNIFIED_CACHE = False


class UnifiedConfigManager:
    """Unified configuration across systems.

    This class harmonizes configuration from multiple sources:
    - thegent (primary)
    - manage devkit
    - workstream
    - plan system

    Examples:
        >>> config = UnifiedConfigManager()
        >>> value = config.get_unified_setting("key")
        >>> value = config.get_unified_setting("key", system="thegent")
        >>> config.sync_configs()
    """

    def __init__(self) -> None:
        """Initialize unified configuration manager."""
        self.config_sources = [
            ("thegent", get_config_dir() / "config.yaml"),
            ("manage", Path.home() / ".manage" / "config.yaml"),
            ("workstream", Path("docs/reference/WORK_STREAM.md")),
            ("plan", Path("PLAN.md")),
        ]
        self.unified_config: dict[str, dict[str, Any]] = {}
        self._load_unified_config()

    def _load_unified_config(self) -> None:
        """Load configuration from all sources."""
        # OPT-019: Check cache first
        if _USE_UNIFIED_CACHE:
            cached = _UNIFIED_CONFIG_CACHE.get("unified_config")
            if cached is not None:
                self.unified_config = cached
                return
        
        for system_name, config_path in self.config_sources:
            if config_path.exists():
                try:
                    if config_path.suffix == ".yaml":
                        config = yaml_load(config_path) or {}
                    elif config_path.suffix == ".md":
                        config = self._parse_markdown_config(config_path)
                    else:
                        continue

                    self.unified_config[system_name] = config
                except (OSError, Exception):
                    # Load failed, skip this source
                    continue
        
        # OPT-019: Cache the result
        if _USE_UNIFIED_CACHE:
            _UNIFIED_CONFIG_CACHE.set("unified_config", self.unified_config, ttl=300)

    def _parse_markdown_config(self, path: Path) -> dict[str, Any]:
        """Parse configuration from markdown.

        Extracts configuration from markdown tables and frontmatter.

        Args:
            path: Path to markdown file

        Returns:
            Configuration dictionary
        """
        config = {}

        try:
            content = path.read_text(encoding="utf-8")

            # Try to parse frontmatter
            frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)
                with contextlib.suppress(Exception):
                    config.update(yaml_loads(frontmatter) or {})

            # Extract configuration from tables
            # This is a simplified version - full implementation would
            # parse specific table structures
        except OSError:
            pass

        return config

    def get_unified_setting(self, key: str, system: str | None = None) -> Any | None:
        """Get setting from unified config.

        Args:
            key: Configuration key (supports dot notation, e.g., "providers.anthropic")
            system: Specific system to query, or None for priority-based lookup

        Returns:
            Configuration value, or None if not found
        """
        if system:
            # Query specific system
            config = self.unified_config.get(system, {})
            return self._get_nested_value(config, key)

        # Check all systems (priority order)
        for system_name in ["thegent", "manage", "workstream", "plan"]:
            if system_name in self.unified_config:
                config = self.unified_config[system_name]
                value = self._get_nested_value(config, key)
                if value is not None:
                    return value

        return None

    def _get_nested_value(self, config: dict, key: str) -> Any | None:
        """Get nested value from config using dot notation.

        Args:
            config: Configuration dictionary
            key: Key with optional dot notation (e.g., "providers.anthropic")

        Returns:
            Value or None
        """
        keys = key.split(".")
        current = config

        for k in keys:
            if isinstance(current, dict):
                current = current.get(k)
                if current is None:
                    return None
            else:
                return None

        return current

    def sync_configs(self) -> None:
        """Synchronize configurations across systems.

        Ensures consistency between different configuration sources.
        This is a simplified version - full implementation would
        handle conflicts and merge strategies.
        """
        # For now, this is a placeholder
        # Full implementation would:
        # 1. Detect conflicts
        # 2. Apply merge strategy
        # 3. Update source files if needed
