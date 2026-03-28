# storage API Reference

> **Source**: `src/thegent/ports/driven/storage.py`

StoragePort: Interface for file/database persistence.

---

## StoragePort

Port interface for persisting and retrieving provider/model data.

**Inherits from**: `Protocol`

### Methods

#### StoragePort.create_directory

```python
create_directory(self: Any, path: Path)
```

Create a directory and all parents.

**Parameters**:

- `path`: Directory path to create.

---

#### StoragePort.file_exists

```python
file_exists(self: Any, path: Path)
```

Check if a file exists.

**Parameters**:

- `path`: Path to check.

**Returns**: True if file exists, False otherwise.

---

#### StoragePort.load_json

```python
load_json(self: Any, path: Path)
```

Load JSON data from file.

**Parameters**:

- `path`: Path to JSON file.

**Returns**: Parsed JSON data as dict. Returns empty dict if file doesn't exist.

---

#### StoragePort.load_yaml

```python
load_yaml(self: Any, path: Path)
```

Load YAML configuration file.

**Parameters**:

- `path`: Path to YAML file.

**Returns**: Parsed YAML data as dict. Returns empty dict if file doesn't exist.

---

#### StoragePort.save_json

```python
save_json(self: Any, path: Path, data: dict[(str, Any)])
```

Save data as JSON.

**Parameters**:

- `path`: Path to JSON file.
- `data`: Data to save.

---

#### StoragePort.save_yaml

```python
save_yaml(self: Any, path: Path, data: dict[(str, Any)])
```

Save data as YAML.

**Parameters**:

- `path`: Path to YAML file.
- `data`: Data to save.

---

---

## create_directory

```python
create_directory(self: Any, path: Path)
```

Create a directory and all parents.

**Parameters**:

- `path`: Directory path to create.

---

## file_exists

```python
file_exists(self: Any, path: Path)
```

Check if a file exists.

**Parameters**:

- `path`: Path to check.

**Returns**: True if file exists, False otherwise.

---

## load_json

```python
load_json(self: Any, path: Path)
```

Load JSON data from file.

**Parameters**:

- `path`: Path to JSON file.

**Returns**: Parsed JSON data as dict. Returns empty dict if file doesn't exist.

---

## load_yaml

```python
load_yaml(self: Any, path: Path)
```

Load YAML configuration file.

**Parameters**:

- `path`: Path to YAML file.

**Returns**: Parsed YAML data as dict. Returns empty dict if file doesn't exist.

---

## save_json

```python
save_json(self: Any, path: Path, data: dict[(str, Any)])
```

Save data as JSON.

**Parameters**:

- `path`: Path to JSON file.
- `data`: Data to save.

---

## save_yaml

```python
save_yaml(self: Any, path: Path, data: dict[(str, Any)])
```

Save data as YAML.

**Parameters**:

- `path`: Path to YAML file.
- `data`: Data to save.

---

