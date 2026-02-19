# subprocess_manager API Reference

> **Source**: `src/thegent/infra/subprocess_manager.py`

Resource-aware subprocess management with automatic cleanup.

---

## SubprocessManager

Manager for subprocess lifecycle with resource tracking.

### Methods

#### SubprocessManager.__init__

```python
__init__(self)
```

#### SubprocessManager.popen

Context manager for subprocess.Popen with automatic cleanup.

```python
popen(self, args, name)
```

#### SubprocessManager.run

Run subprocess with resource tracking.

```python
run(self, args, name, timeout)
```

---

## get_subprocess_manager

Get global subprocess manager.

---

## popen

Context manager for subprocess.Popen with automatic cleanup.

```python
popen(self, args, name)
```

---

## run

Run subprocess with resource tracking.

```python
run(self, args, name, timeout)
```

---

