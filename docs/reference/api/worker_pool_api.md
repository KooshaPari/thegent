# worker_pool API Reference

> **Source**: `src/thegent/orchestration/worker_pool.py`

MTSP-06: Persistent Python Worker Pool.

Reduces interpreter startup latency by keeping warm processes alive.

---

## PersistentWorkerPool

A pool of persistent Python processes for executing tasks (MTSP-06).

### Methods

#### PersistentWorkerPool.__init__

```python
__init__(self, size)
```

#### PersistentWorkerPool.get_instance

```python
get_instance(cls, size)
```

#### PersistentWorkerPool.start

Initialize the process pool.

```python
start(self)
```

#### PersistentWorkerPool.stop

Shut down the pool.

```python
stop(self)
```

---

## get_instance

```python
get_instance(cls, size)
```

---

## get_worker_pool

Helper for dependency injection.

---

## start

Initialize the process pool.

```python
start(self)
```

---

## stop

Shut down the pool.

```python
stop(self)
```

---

