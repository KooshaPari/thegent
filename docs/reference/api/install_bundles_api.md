# install_bundles API Reference

> **Source**: `src/thegent/install_bundles.py`

Bundle manifest loading and path resolution helpers for install workflows.

---

## coerce_bundle_items

```python
coerce_bundle_items(raw: dict[(str, list[dict[(str, Any)]])])
```

Normalize raw manifest payloads into a validated structure.

---

## coerce_path

```python
coerce_path(value: str)
```

Normalize and expand a user path token.

---

## get_bundle_manifest_path

```python
get_bundle_manifest_path(bundle_manifest: Any)
```

Get the bundle manifest path.

---

## get_default_bundle_manifest_path

Default location for the third-party bundle manifest.

---

## list_bundle_names

```python
list_bundle_names(bundle_manifest: Any)
```

List available bundle names from the bundle manifest.

---

## load_bundle_manifest

```python
load_bundle_manifest(path: Any)
```

Load third-party bundle definitions from an external JSON manifest.

---

## resolve_bundle_mode

```python
resolve_bundle_mode(raw_mode: str, fallback: InstallMode)
```

Convert a user-defined bundle mode into an InstallMode.

---

## resolve_bundle_source

```python
resolve_bundle_source(source: str, thegent_root: Path)
```

Resolve a bundle source path.

---

## resolve_bundle_target

```python
resolve_bundle_target(target: str)
```

Resolve a bundle target path.

---

## resolve_bundles

```python
resolve_bundles(bundle_names: Any, bundle_manifest: Any, thegent_root: Path, home: Path, cwd: Path, fallback_mode: InstallMode)
```

Resolve selected bundles to install tuples.

---

## source_requires_pin_and_checksum

```python
source_requires_pin_and_checksum(source: str)
```

Determine whether a source should include immutable pin/checksum metadata.

---

## validate_bundle_manifest

```python
validate_bundle_manifest(bundle_manifest: Any)
```

Validate a bundle manifest file.

---

