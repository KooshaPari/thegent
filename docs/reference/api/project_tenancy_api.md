# project_tenancy API Reference

> **Source**: `src/thegent/infra/project_tenancy.py`

Project tenancy and AG-DD template orchestration.

---

## AssetInstallResult

Deterministic template install result.

---

## ProjectTenancy

Project tenancy manager backed by a strict JSON registry.

### Methods

#### ProjectTenancy.__init__

```python
__init__(self: Any, registry_path: Any)
```

---

#### ProjectTenancy.get_project

```python
get_project(self: Any)
```

---

#### ProjectTenancy.init_project

```python
init_project(self: Any)
```

---

#### ProjectTenancy.install_project_assets

```python
install_project_assets(self: Any, path: Any)
```

---

#### ProjectTenancy.list_projects

```python
list_projects(self: Any)
```

---

#### ProjectTenancy.spawn_template_agdd

```python
spawn_template_agdd(self: Any, path: Any, mode: TemplateMode)
```

---

#### ProjectTenancy.sync_project

```python
sync_project(self: Any)
```

Update selected tenancy fields for an existing project record.

---

---

## TenancyProject

Strict persisted model for project tenancy records.

**Inherits from**: `BaseModel`

---

## TenancyRegistryPayload

On-disk registry payload schema.

**Inherits from**: `BaseModel`

---

## get_project

```python
get_project(self: Any) -> Any
```

---

## init_project

```python
init_project(self: Any) -> TenancyProject
```

---

## install_project_assets

```python
install_project_assets(self: Any, path: Any) -> AssetInstallResult
```

---

## list_projects

```python
list_projects(self: Any) -> list[TenancyProject]
```

---

## spawn_template_agdd

```python
spawn_template_agdd(self: Any, path: Any, mode: TemplateMode) -> AssetInstallResult
```

---

## sync_project

```python
sync_project(self: Any)
```

Update selected tenancy fields for an existing project record.

---

