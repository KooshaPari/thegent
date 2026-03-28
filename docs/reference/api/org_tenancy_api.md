# org_tenancy API Reference

> **Source**: `src/thegent/infra/org_tenancy.py`

WL-051: Org-level namespace hierarchy above ProjectTenancy.

Implements:
  - OrgNamespace: org_id, org_name, tenants list
  - OrgRegistry: singleton backed by ~/.thegent/orgs/registry.json
  - Module-level helpers: org_create, org_get, org_list, org_add_tenant

---

## OrgNamespace

Org-level namespace that groups multiple tenant IDs (WL-051).

**Inherits from**: `BaseModel`

---

## OrgRegistry

Manages org-level namespaces backed by a strict JSON registry (WL-051).

Thread-safety: not guaranteed. The registry is a single JSON file; callers
must serialise concurrent writes externally if needed.

### Methods

#### OrgRegistry.__init__

```python
__init__(self: Any, registry_path: Any)
```

---

#### OrgRegistry.add_tenant

```python
add_tenant(self: Any, org_id: str, tenant_id: str)
```

Add tenant_id to an org. Raises ValueError if already present.

---

#### OrgRegistry.create_org

```python
create_org(self: Any)
```

Create a new org namespace and persist it.

Raises ValueError on duplicate org_id or org_name.

---

#### OrgRegistry.get_org

```python
get_org(self: Any)
```

Return an org by id or name.

Raises KeyError if not found.  Raises ValueError if selector is ambiguous.

---

#### OrgRegistry.list_orgs

```python
list_orgs(self: Any)
```

Return all org namespaces sorted by creation time.

---

#### OrgRegistry.remove_tenant

```python
remove_tenant(self: Any, org_id: str, tenant_id: str)
```

Remove tenant_id from an org. Raises ValueError if not present.

---

---

## OrgRegistryPayload

On-disk registry payload schema.

**Inherits from**: `BaseModel`

---

## add_tenant

```python
add_tenant(self: Any, org_id: str, tenant_id: str)
```

Add tenant_id to an org. Raises ValueError if already present.

---

## create_org

```python
create_org(self: Any)
```

Create a new org namespace and persist it.

Raises ValueError on duplicate org_id or org_name.

---

## get_org

```python
get_org(self: Any)
```

Return an org by id or name.

Raises KeyError if not found.  Raises ValueError if selector is ambiguous.

---

## list_orgs

```python
list_orgs(self: Any)
```

Return all org namespaces sorted by creation time.

---

## org_add_tenant

```python
org_add_tenant(org_id: str, tenant_id: str) -> OrgNamespace
```

---

## org_create

---

## org_get

---

## org_list

---

## remove_tenant

```python
remove_tenant(self: Any, org_id: str, tenant_id: str)
```

Remove tenant_id from an org. Raises ValueError if not present.

---

