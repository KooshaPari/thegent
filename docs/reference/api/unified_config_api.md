# unified_config API Reference

> **Source**: `src/thegent/integration/unified_config.py`

Unified configuration system across all systems.

---

## UnifiedConfigManager

Unified configuration across systems.

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

### Methods

#### UnifiedConfigManager.__init__

Initialize unified configuration manager.

```python
__init__(self)
```

#### UnifiedConfigManager.get_unified_setting

Get setting from unified config.

Args:
    key: Configuration key (supports dot notation, e.g., "providers.anthropic")
    system: Specific system to query, or None for priority-based lookup

Returns:
    Configuration value, or None if not found

```python
get_unified_setting(self, key, system)
```

#### UnifiedConfigManager.sync_configs

Synchronize configurations across systems.

Ensures consistency between different configuration sources.
This is a simplified version - full implementation would
handle conflicts and merge strategies.

```python
sync_configs(self)
```

---

## get_unified_setting

Get setting from unified config.

Args:
    key: Configuration key (supports dot notation, e.g., "providers.anthropic")
    system: Specific system to query, or None for priority-based lookup

Returns:
    Configuration value, or None if not found

```python
get_unified_setting(self, key, system)
```

---

## sync_configs

Synchronize configurations across systems.

Ensures consistency between different configuration sources.
This is a simplified version - full implementation would
handle conflicts and merge strategies.

```python
sync_configs(self)
```

---

