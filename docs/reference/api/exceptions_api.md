# exceptions API Reference

> **Source**: `src/thegent/isolation/exceptions.py`

Isolation-related exceptions.

---

## ExecutionContextError

Raised when execution in isolated context fails.

**Inherits from**: `IsolationError`

**Method Resolution Order**: `ExecutionContextError -> IsolationError`

---

## IsolationError

Base exception for isolation-related errors.

**Inherits from**: `Exception`

---

## LeaseConflictError

Raised when a lease conflict is detected.

**Inherits from**: `IsolationError`

**Method Resolution Order**: `LeaseConflictError -> IsolationError`

---

## TenantAllocationError

Raised when tenant allocation fails.

**Inherits from**: `IsolationError`

**Method Resolution Order**: `TenantAllocationError -> IsolationError`

---

