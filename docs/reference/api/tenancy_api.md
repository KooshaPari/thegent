# tenancy API Reference

> **Source**: `src/thegent/security/tenancy.py`

WP-19001: Multi-Tenant Key Isolation.
Ensures API keys are isolated by owner/tenant in the auth directory.

---

## KeyIsolator

Manages isolated key storage for multi-tenant environments.

### Methods

#### KeyIsolator.__init__

```python
__init__(self, settings)
```

#### KeyIsolator.delete_tenant

Delete all keys for a specific tenant.

```python
delete_tenant(self, owner)
```

#### KeyIsolator.get_key

Retrieve a key for a specific owner and provider.

```python
get_key(self, owner, provider)
```

#### KeyIsolator.get_tenant_dir

Get the isolated auth directory for a specific owner.

```python
get_tenant_dir(self, owner)
```

#### KeyIsolator.isolate_key

Write an API key to the isolated tenant directory.

```python
isolate_key(self, owner, provider, api_key)
```

#### KeyIsolator.list_tenants

List all tenants with isolated keys.

```python
list_tenants(self)
```

---

## delete_tenant

Delete all keys for a specific tenant.

```python
delete_tenant(self, owner)
```

---

## get_key

Retrieve a key for a specific owner and provider.

```python
get_key(self, owner, provider)
```

---

## get_tenant_dir

Get the isolated auth directory for a specific owner.

```python
get_tenant_dir(self, owner)
```

---

## isolate_key

Write an API key to the isolated tenant directory.

```python
isolate_key(self, owner, provider, api_key)
```

---

## list_tenants

List all tenants with isolated keys.

```python
list_tenants(self)
```

---

