# base_provider API Reference

> **Source**: `src/thegent/isolation/base_provider.py`

Abstract base class for isolation providers.

---

## IsolationProvider

Abstract interface for tenant isolation.

**Inherits from**: `ABC`

### Methods

#### IsolationProvider.allocate_tenant

```python
allocate_tenant(self: Any, tenant_id: str, agent_id: Any)
```

Allocate resources for a tenant.

**Parameters**:

- `tenant_id`: Unique identifier for the tenant
- `agent_id`: Optional agent identifier

**Returns**: TenantContext with allocated resources

---

#### IsolationProvider.cleanup_tenant

```python
cleanup_tenant(self: Any, context: TenantContext)
```

Clean up resources allocated for a tenant.

**Parameters**:

- `context`: TenantContext to clean up

---

#### IsolationProvider.execute_in_context

```python
execute_in_context(self: Any, context: TenantContext, command: list, timeout_sec: int)
```

Execute a command in the tenant's isolated context.

**Parameters**:

- `context`: TenantContext for this execution
- `command`: List of command arguments
- `timeout_sec`: Execution timeout in seconds

**Returns**: Dict with 'returncode', 'stdout', 'stderr'

---

---

## allocate_tenant

```python
allocate_tenant(self: Any, tenant_id: str, agent_id: Any)
```

Allocate resources for a tenant.

**Parameters**:

- `tenant_id`: Unique identifier for the tenant
- `agent_id`: Optional agent identifier

**Returns**: TenantContext with allocated resources

**Raises**:

- `TenantAllocationError`: If allocation fails

---

## cleanup_tenant

```python
cleanup_tenant(self: Any, context: TenantContext)
```

Clean up resources allocated for a tenant.

**Parameters**:

- `context`: TenantContext to clean up

**Raises**:

- `IsolationError`: If cleanup fails

---

## execute_in_context

```python
execute_in_context(self: Any, context: TenantContext, command: list, timeout_sec: int)
```

Execute a command in the tenant's isolated context.

**Parameters**:

- `context`: TenantContext for this execution
- `command`: List of command arguments
- `timeout_sec`: Execution timeout in seconds

**Returns**: Dict with 'returncode', 'stdout', 'stderr'

**Raises**:

- `ExecutionContextError`: If execution fails

---

