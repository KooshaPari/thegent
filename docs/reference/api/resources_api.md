# resources API Reference

> **Source**: `src/thegent/scaling/resources.py`

Resource Monitor

Samples system resources for dynamic scaling decisions.

---

## ResourceMonitor

Monitors system resources.

### Methods

#### ResourceMonitor.__init__

```python
__init__(self: Any, sample_interval: float)
```

---

#### ResourceMonitor.average_pressure

```python
average_pressure(self: Any, window: int)
```

Get average pressure over window.

---

#### ResourceMonitor.latest

```python
latest(self: Any)
```

Get latest sample.

---

#### ResourceMonitor.sample

```python
sample(self: Any)
```

Take a resource sample.

---

---

## ResourceSample

Resource sample at a point in time.

### Methods

#### ResourceSample.pressure_score

```python
pressure_score(self: Any)
```

Combined pressure score (0-1).

---

---

## average_pressure

```python
average_pressure(self: Any, window: int)
```

Get average pressure over window.

---

## latest

```python
latest(self: Any)
```

Get latest sample.

---

## pressure_score

```python
pressure_score(self: Any)
```

Combined pressure score (0-1).

---

## sample

```python
sample(self: Any)
```

Take a resource sample.

---

