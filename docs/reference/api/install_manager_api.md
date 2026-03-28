# install_manager API Reference

> **Source**: `src/thegent/install_manager.py`

Install manager for thegent.

Handles file installation, backup, and uninstallation.
Extracted from install.py for maintainability.

---

## InstallManager

Manages installation, backup, and uninstallation of thegent files.

### Methods

#### InstallManager.__init__

```python
__init__(self: Any, dry_run: bool, verbose: bool)
```

Initialize the install manager.

**Parameters**:

- `dry_run`: If True, don't make actual changes
- `verbose`: If True, print detailed output

---

#### InstallManager.install_file

```python
install_file(self: Any, source: Path, target: Path, mode: InstallMode)
```

Install a file from source to target.

**Parameters**:

- `source`: Source file path
- `target`: Target file path
- `mode`: Installation mode

**Returns**: FileAction indicating what was done

---

#### InstallManager.save_manifest

```python
save_manifest(self: Any)
```

Save the manifest to disk.

---

#### InstallManager.uninstall

```python
uninstall(self: Any)
```

Uninstall all managed files and revert configs.

**Returns**: Dict with counts: removed, restored, reverted, errors

---

#### InstallManager.update_config

```python
update_config(self: Any, config_path: Path, key_path: str, value: Any)
```

Update a JSON config file at a specific key path.

**Parameters**:

- `config_path`: Path to the config file
- `key_path`: Dot-separated key path (e.g., 'mcpServers.thegent')
- `value`: Value to set

**Returns**: True if successful

---

---

## get_backup_dir

Get the path to the backup directory.

---

## get_home_dir

Get the home directory.

---

## get_manifest_path

Get the path to the install manifest.

---

## install_file

```python
install_file(self: Any, source: Path, target: Path, mode: InstallMode)
```

Install a file from source to target.

**Parameters**:

- `source`: Source file path
- `target`: Target file path
- `mode`: Installation mode

**Returns**: FileAction indicating what was done

---

## save_manifest

```python
save_manifest(self: Any)
```

Save the manifest to disk.

---

## uninstall

```python
uninstall(self: Any)
```

Uninstall all managed files and revert configs.

**Returns**: Dict with counts: removed, restored, reverted, errors

---

## update_config

```python
update_config(self: Any, config_path: Path, key_path: str, value: Any)
```

Update a JSON config file at a specific key path.

**Parameters**:

- `config_path`: Path to the config file
- `key_path`: Dot-separated key path (e.g., 'mcpServers.thegent')
- `value`: Value to set

**Returns**: True if successful

---

