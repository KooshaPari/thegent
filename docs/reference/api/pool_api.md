# pool API Reference

> **Source**: `src/thegent/orchestration/resource/pool.py`

Thread-safe resource pool for agent orchestration.

FR-ORCH-001: ResourcePool must serialise concurrent allocate() calls so that
capacity is never over-committed.

---

## ResourceAllocationError

Raised when a resource allocation request cannot be satisfied.

**Inherits from**: `Exception`

---

## ResourcePool

Thread-safe capacity pool for agent resource allocation.

A single unit of capacity may be claimed by exactly one caller.
Concurrent ``allocate`` calls beyond capacity raise

### Methods

#### ResourcePool.__init__

```python
__init__(self: Any, capacity: int)
```

---

#### ResourcePool.allocate

```python
allocate(self: Any, agent_id: str, amount: int)
```

Allocate *amount* units for *agent_id*.

**Parameters**:

- `agent_id`: Identifier of the requesting agent.
- `amount`:   Units to allocate (default 1).

**Returns**: A dict with ``agent_id`` and ``amount`` on success.

---

#### ResourcePool.available

```python
available(self: Any)
```

Return the number of currently available units.

---

#### ResourcePool.capacity

```python
capacity(self: Any)
```

Total pool capacity.

---

#### ResourcePool.release

```python
release(self: Any, amount: int)
```

Release *amount* previously allocated units back to the pool.

**Parameters**:

- `amount`: Units to return (default 1).

---

---

## allocate

```python
allocate(self: Any, agent_id: str, amount: int)
```

Allocate *amount* units for *agent_id*.

**Parameters**:

- `agent_id`: Identifier of the requesting agent.
- `amount`:   Units to allocate (default 1).

**Returns**: A dict with ``agent_id`` and ``amount`` on success.

**Raises**:

- `ResourceAllocationError`: When insufficient capacity remains.

---

## available

```python
available(self: Any)
```

Return the number of currently available units.

---

## capacity

```python
capacity(self: Any)
```

Total pool capacity.

---

## release

```python
release(self: Any, amount: int)
```

Release *amount* previously allocated units back to the pool.

**Parameters**:

- `amount`: Units to return (default 1).

---

