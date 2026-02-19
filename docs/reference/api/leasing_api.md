# leasing API Reference

> **Source**: `src/thegent/orchestration/leasing.py`

## EditLease

### Methods

#### EditLease.is_expired

```python
is_expired(self)
```

---

## EditLeaseManager

MTSP-11: Centralized edit lease management for multi-tenant agent environments.
Prevents agent-on-agent edit collisions by providing advisory locks with TTL.

### Methods

#### EditLeaseManager.__init__

```python
__init__(self, state_dir)
```

#### EditLeaseManager.acquire

Acquire an advisory lease on a file path.

```python
acquire(self, path, agent_id, duration, force)
```

#### EditLeaseManager.check

Check if a path is currently leased by another agent.

```python
check(self, path, agent_id)
```

#### EditLeaseManager.prune

Remove all expired leases.

```python
prune(self)
```

#### EditLeaseManager.release

Release a lease if held by the agent.

```python
release(self, path, agent_id)
```

---

## acquire

Acquire an advisory lease on a file path.

```python
acquire(self, path, agent_id, duration, force)
```

---

## check

Check if a path is currently leased by another agent.

```python
check(self, path, agent_id)
```

---

## get_lease_manager

Return shared in-memory EditLeaseManager. MTSP-14: zero-latency lock coordination.

```python
get_lease_manager(state_dir)
```

---

## is_expired

```python
is_expired(self)
```

---

## prune

Remove all expired leases.

```python
prune(self)
```

---

## release

Release a lease if held by the agent.

```python
release(self, path, agent_id)
```

---

