"""Unified config parsing - consolidate YAML/JSON/TOML parsers using anyconfig."""

import anyconfig

# Re-export for consistency
__all__ = ["load_config", "dump_config", "merge", "validate"]
