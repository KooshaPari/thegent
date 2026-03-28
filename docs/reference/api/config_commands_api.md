# config_commands API Reference

> **Source**: `src/thegent/infra/config_commands.py`

Configuration management commands for thegent.

This module provides commands for validating, showing, and migrating configuration.

---

## config_migrate_cmd

```python
config_migrate_cmd(source: str, target: str, dry_run: bool)
```

Migrate configuration from old format to new format.

**Examples**:

```python
thegent config migrate
thegent config migrate --source .env.old --target .env.new --dry-run
```

---

## config_show_cmd

```python
config_show_cmd(config_path: str)
```

Show current configuration.

**Examples**:

```python
thegent config show
thegent config show --config .env.production
```

---

## config_validate_cmd

```python
config_validate_cmd(config_path: str)
```

Validate configuration file.

**Examples**:

```python
thegent config validate
thegent config validate --config .env.production
```

---

## config_wizard_cmd

```python
config_wizard_cmd(config_path: str)
```

Run interactive configuration wizard.

**Examples**:

```python
thegent config wizard
thegent config wizard --config .env.production
```

---

