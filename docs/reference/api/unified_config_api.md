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

### Methods

#### UnifiedConfigManager.__init__

```python
__init__(self: Any)
```

Initialize unified configuration manager.

---

#### UnifiedConfigManager.get_unified_setting

```python
get_unified_setting(self: Any, key: str, system: Any)
```

Get setting from unified config.

**Parameters**:

- `key`: Configuration key (supports dot notation, e.g., "providers.anthropic")
- `system`: Specific system to query, or None for priority-based lookup

**Returns**: Configuration value, or None if not found

---

#### UnifiedConfigManager.sync_configs

```python
sync_configs(self: Any)
```

Synchronize configurations across systems.

Applies deterministic precedence rules:
``thegent > manage > workstream > plan``.
When conflicts are detected, the higher-priority value wins and
reconciled values are persisted back to source files.

---

---

## get_unified_setting

```python
get_unified_setting(self: Any, key: str, system: Any)
```

Get setting from unified config.

**Parameters**:

- `key`: Configuration key (supports dot notation, e.g., "providers.anthropic")
- `system`: Specific system to query, or None for priority-based lookup

**Returns**: Configuration value, or None if not found

---

## sync_configs

```python
sync_configs(self: Any)
```

Synchronize configurations across systems.

Applies deterministic precedence rules:
``thegent > manage > workstream > plan``.
When conflicts are detected, the higher-priority value wins and
reconciled values are persisted back to source files.

---

