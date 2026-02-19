# config API Reference

> **Source**: `src/thegent/config.py`

Pydantic settings for thegent.

---

## ThegentSettings

Configuration for thegent CLI.

**Inherits from**: `BaseSettings`

### Methods

#### ThegentSettings.validate_setup

ROB-013: Configuration validation on startup (fail-fast).

Ensures directories exist and critical settings are sane.

```python
validate_setup(self)
```

---

## validate_setup

ROB-013: Configuration validation on startup (fail-fast).

Ensures directories exist and critical settings are sane.

```python
validate_setup(self)
```

---

