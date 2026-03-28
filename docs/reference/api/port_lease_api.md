# port_lease API Reference

> **Source**: `src/thegent/testing/port_lease.py`

Test runner port leasing (MTSP-16).

Provides a mechanism to lease unique ports for parallel test execution
to avoid port collisions.

---

## PortLeaseManager

Manages port leasing for parallel test execution (MTSP-16).

### Methods

#### PortLeaseManager.__init__

```python
__init__(self: Any, lease_dir: Any, port_range: tuple[(int, int)])
```

---

#### PortLeaseManager.lease_port

```python
lease_port(self: Any, timeout: int)
```

Lease a unique port. Returns the port number.

---

#### PortLeaseManager.release_port

```python
release_port(self: Any, port: int)
```

Release a previously leased port.

---

---

## lease_port

```python
lease_port(self: Any, timeout: int)
```

Lease a unique port. Returns the port number.

---

## release_port

```python
release_port(self: Any, port: int)
```

Release a previously leased port.

---

