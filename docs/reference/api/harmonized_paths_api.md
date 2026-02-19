# harmonized_paths API Reference

> **Source**: `src/thegent/integration/harmonized_paths.py`

Harmonized path strategy across all integrated systems.

---

## HarmonizedPathManager

Harmonize paths across systems.

This class creates consistent path mappings across all integrated systems
(thegent, manage devkit, workstream, plan system) to ensure harmonious
directory structures.

Examples:
    >>> paths = HarmonizedPathManager()
    >>> config_path = paths.get_harmonized_path("thegent", "config")
    >>> paths.create_shared_structure()

### Methods

#### HarmonizedPathManager.__init__

Initialize harmonized path manager.

```python
__init__(self)
```

#### HarmonizedPathManager.create_shared_structure

Create shared directory structure.

Creates common parent directories and ensures consistent structure
across all integrated systems.

```python
create_shared_structure(self)
```

#### HarmonizedPathManager.get_harmonized_path

Get harmonized path for system.

Args:
    system: System name (thegent, manage, workstream, plan)
    path_type: Path type (config, cache, data, bin, log, temp)

Returns:
    Path object, or None if not found

```python
get_harmonized_path(self, system, path_type)
```

---

## create_shared_structure

Create shared directory structure.

Creates common parent directories and ensures consistent structure
across all integrated systems.

```python
create_shared_structure(self)
```

---

## get_harmonized_path

Get harmonized path for system.

Args:
    system: System name (thegent, manage, workstream, plan)
    path_type: Path type (config, cache, data, bin, log, temp)

Returns:
    Path object, or None if not found

```python
get_harmonized_path(self, system, path_type)
```

---

