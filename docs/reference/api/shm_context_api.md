# shm_context API Reference

> **Source**: `src/thegent/orchestration/shm_context.py`

WP-21002: Zero-Copy Context Sharing (Shared Memory).
MTSP-09/11: Efficiently share large context blocks across multi-tenant agent runs.

---

## ContextSharer

Manages context sharing across multiple agent runs (Multi-Tenancy).

### Methods

#### ContextSharer.__init__

```python
__init__(self)
```

#### ContextSharer.get_context

Retrieve or create a shared context for a session.

```python
get_context(self, session_id)
```

#### ContextSharer.release_context

Clean up session context.

```python
release_context(self, session_id)
```

---

## ZeroCopyContext

Provides high-performance shared memory context for agent processes.

### Methods

#### ZeroCopyContext.__init__

```python
__init__(self, size)
```

#### ZeroCopyContext.close

Clean up resources.

```python
close(self)
```

#### ZeroCopyContext.read_context

Read context data directly from memory-mapped file.

```python
read_context(self, size, offset)
```

#### ZeroCopyContext.write_context

Write context data directly to memory-mapped file.

```python
write_context(self, data, offset)
```

---

## close

Clean up resources.

```python
close(self)
```

---

## get_context

Retrieve or create a shared context for a session.

```python
get_context(self, session_id)
```

---

## read_context

Read context data directly from memory-mapped file.

```python
read_context(self, size, offset)
```

---

## release_context

Clean up session context.

```python
release_context(self, session_id)
```

---

## write_context

Write context data directly to memory-mapped file.

```python
write_context(self, data, offset)
```

---

