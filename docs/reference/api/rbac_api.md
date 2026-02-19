# rbac API Reference

> **Source**: `src/thegent/security/rbac.py`

WP-19002: Role-Based Access Control (RBAC).
Formally defines roles, permissions, and access checks.

---

## Permission

Fine-grained permissions.

**Inherits from**: `str, Enum`

---

## RBACManager

Orchestrates RBAC checks across the system.

### Methods

#### RBACManager.__init__

```python
__init__(self)
```

#### RBACManager.check_access

Hybrid check using both fine-grained permissions and persona-based constraints.

```python
check_access(self, role, operation, lane)
```

#### RBACManager.has_permission

Check if a role has a specific permission.

```python
has_permission(self, role, permission)
```

---

## Role

Standard operator roles.

**Inherits from**: `str, Enum`

---

## check_access

Hybrid check using both fine-grained permissions and persona-based constraints.

```python
check_access(self, role, operation, lane)
```

---

## has_permission

Check if a role has a specific permission.

```python
has_permission(self, role, permission)
```

---

