# install API Reference

> **Source**: `src/thegent/install.py`

Install module for managed installation and synchronization of thegent components.

---

## BundleItem

**Inherits from**: `BaseModel`

---

## BundleManifest

Optional external manifest describing installable third-party bundles.

**Inherits from**: `BaseModel`

---

## ConfigManifest

**Inherits from**: `BaseModel`

---

## FileAction

**Inherits from**: `StrEnum`

---

## FileManifest

**Inherits from**: `BaseModel`

---

## InstallManager

### Methods

#### InstallManager.__init__

```python
__init__(self, dry_run, verbose)
```

#### InstallManager.install_file

```python
install_file(self, source, target, mode)
```

#### InstallManager.save_manifest

```python
save_manifest(self)
```

#### InstallManager.uninstall

```python
uninstall(self)
```

#### InstallManager.update_config

Update a JSON config file at a specific key path (e.g. 'mcpServers.thegent').

```python
update_config(self, config_path, key_path, value)
```

---

## InstallManifest

**Inherits from**: `BaseModel`

---

## InstallMode

**Inherits from**: `StrEnum`

---

## create_symlink

Legacy shim for tests.

```python
create_symlink(source, target, dry_run)
```

---

## get_backup_dir

---

## get_bundle_manifest_path

Get the bundle manifest path.

Args:
    bundle_manifest: Optional path to a bundle manifest file.

Returns:
    The path to the bundle manifest file.

```python
get_bundle_manifest_path(bundle_manifest)
```

---

## get_default_bundle_manifest_path

Default location for the third-party bundle manifest.

---

## get_home_dir

---

## get_manifest_path

---

## get_source_dest_mapping

Legacy shim for tests.

```python
get_source_dest_mapping(thegent_root, bundle)
```

---

## install_file

```python
install_file(self, source, target, mode)
```

---

## list_bundle_names

List available bundle names from the bundle manifest.

Args:
    bundle_manifest: Optional path to a bundle manifest file.

Returns:
    List of bundle names available in the bundle manifest.

```python
list_bundle_names(bundle_manifest)
```

---

## load_bundle_manifest

Load third-party bundle definitions from an external JSON manifest.

Expected schema:
  {
    "bundles": {
      "name": {
        "items": [
          {"source": "...", "target": "...", "mode": "smart|force|editable"}
        ]
      }
    }
  }

```python
load_bundle_manifest(path)
```

---

## resolve_bundles

Resolve selected bundles to install tuples.

```python
resolve_bundles(bundle_names, bundle_manifest, thegent_root, home, cwd, fallback_mode)
```

---

## run_install

```python
run_install(target, mode, dry_run, verbose, url, install_service, bundles, bundle_manifest, bundle_conflict_policy)
```

---

## run_wizard

Interactive installation wizard using rich.

```python
run_wizard(url)
```

---

## save_manifest

```python
save_manifest(self)
```

---

## service_install

---

## service_start

---

## service_uninstall

---

## should_exclude

Legacy shim for tests.

```python
should_exclude(path)
```

---

## smart_copy_file

Legacy shim for tests.

```python
smart_copy_file(source, target, dry_run)
```

---

## uninstall

```python
uninstall(self)
```

---

## update_config

Update a JSON config file at a specific key path (e.g. 'mcpServers.thegent').

```python
update_config(self, config_path, key_path, value)
```

---

## validate_bundle_manifest

Validate a bundle manifest file.

Args:
    bundle_manifest: Optional path to a bundle manifest file.

Returns:
    Tuple of (is_valid, list of issues).

```python
validate_bundle_manifest(bundle_manifest)
```

---

