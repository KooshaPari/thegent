# config_validators API Reference

> **Source**: `src/thegent/config_validators.py`

Validators for thegent configuration.

Extracted from config.py for maintainability.

---

## _SettingsLike

Subset of settings fields validated by this module.

**Inherits from**: `Protocol`

---

## parse_appdata_path

```python
parse_appdata_path(v: object)
```

Parse appdata_path for Windows.

**Parameters**:

- `v`: Input value

**Returns**: Path object or None

---

## parse_check_leaks

```python
parse_check_leaks(v: object)
```

Parse check_leaks boolean.

**Parameters**:

- `v`: Input value (bool, string, int)

**Returns**: Boolean value

---

## parse_env_allowlist

```python
parse_env_allowlist(v: object)
```

Parse sandbox_env_allowlist from various formats.

**Parameters**:

- `v`: Input value (string, list, or None)

**Returns**: List of allowed environment variable names

---

## parse_mac_keep_awake_agents

```python
parse_mac_keep_awake_agents(v: object)
```

Parse mac_keep_awake_agents list.

**Parameters**:

- `v`: Input value (string, list, or None)

**Returns**: List of agent names

---

## parse_retention_by_domain

```python
parse_retention_by_domain(v: object)
```

Parse retention_by_domain from various formats.

**Parameters**:

- `v`: Input value (string, dict, or None)

**Returns**: Dict mapping domains to retention days

---

## parse_shell_path

```python
parse_shell_path(v: object)
```

Parse shell_path, defaulting to /bin/zsh.

**Parameters**:

- `v`: Input value

**Returns**: Shell path string

---

## parse_testing_mode

```python
parse_testing_mode(v: object)
```

Parse testing_mode boolean.

**Parameters**:

- `v`: Input value

**Returns**: Boolean value

---

## parse_virtual_env

```python
parse_virtual_env(v: object)
```

Parse virtual_env path.

**Parameters**:

- `v`: Input value (path string or None)

**Returns**: Path object or None

---

## parse_zen_api_key

```python
parse_zen_api_key(v: object)
```

Parse zen_api_key, stripping whitespace.

**Parameters**:

- `v`: Input value

**Returns**: Cleaned API key string

---

## validate_settings_setup

```python
validate_settings_setup(settings: _SettingsLike)
```

Validate settings for common issues.

**Parameters**:

- `settings`: Settings object to validate

**Returns**: List of error messages (empty if valid)

---

