# provider_model_manager_io API Reference

> **Source**: `src/thegent/provider_model_manager_io.py`

I/O and path helpers for provider/model manager data files.

---

## load_json

```python
load_json(path: Path)
```

Load JSON file.

---

## load_yaml

```python
load_yaml(path: Path)
```

Load YAML file.

---

## save_json

```python
save_json(path: Path, data: dict[(str, Any)])
```

Save JSON file.

---

## save_yaml

```python
save_yaml(path: Path, data: dict[(str, Any)])
```

Save YAML file.

---

## update_provider_mapping

```python
update_provider_mapping(mapping_path: Path, name: str)
```

Update provider_mapping.json lists.

---

