# benchmark_store API Reference

> **Source**: `src/thegent/utils/benchmark_store.py`

Unified benchmark store with tokenledger integration.

Provides a unified interface for benchmark data that:
1. Tries tokenledger first for dynamic data
2. Falls back to hardcoded values
3. Maintains backward compatibility with existing QUALITY_PROXY

Usage:
    from thegent.utils.benchmark_store import BenchmarkStore

    store = BenchmarkStore()
    quality = store.get_quality("gpt-4o")  # Returns 0.85
    cost = store.get_cost("gpt-4o")  # Returns 0.005

---

## BenchmarkStore

Unified benchmark store with tokenledger integration.

Tries tokenledger first, then falls back to hardcoded values.

### Methods

#### BenchmarkStore.__init__

```python
__init__(self: Any, tokenledger_config: Optional[TokenledgerConfig], use_tokenledger: bool)
```

---

#### BenchmarkStore.get_all_models

```python
get_all_models(self: Any)
```

Get all known model IDs.

---

#### BenchmarkStore.get_benchmark

```python
get_benchmark(self: Any, model_id: str)
```

Get full benchmark data for a model.

**Parameters**:

- `model_id`: Model identifier

**Returns**: BenchmarkData or None if not found

---

#### BenchmarkStore.get_cost

```python
get_cost(self: Any, model_id: str)
```

Get cost per 1K tokens for a model.

**Parameters**:

- `model_id`: Model identifier

**Returns**: Cost per 1K tokens in USD or None if not found

---

#### BenchmarkStore.get_latency

```python
get_latency(self: Any, model_id: str)
```

Get latency in ms for a model.

**Parameters**:

- `model_id`: Model identifier

**Returns**: Latency in milliseconds or None if not found

---

#### BenchmarkStore.get_quality

```python
get_quality(self: Any, model_id: str)
```

Get quality score for a model.

**Parameters**:

- `model_id`: Model identifier

**Returns**: Quality score (0-1) or None if not found

---

#### BenchmarkStore.refresh

```python
refresh(self: Any)
```

Refresh benchmark data from tokenledger.

---

#### BenchmarkStore.tokenledger

```python
tokenledger(self: Any)
```

Get the tokenledger adapter.

---

---

## get_all_models

```python
get_all_models(self: Any)
```

Get all known model IDs.

---

## get_benchmark

```python
get_benchmark(self: Any, model_id: str)
```

Get full benchmark data for a model.

**Parameters**:

- `model_id`: Model identifier

**Returns**: BenchmarkData or None if not found

---

## get_cost

```python
get_cost(self: Any, model_id: str)
```

Get cost per 1K tokens for a model.

**Parameters**:

- `model_id`: Model identifier

**Returns**: Cost per 1K tokens in USD or None if not found

---

## get_latency

```python
get_latency(self: Any, model_id: str)
```

Get latency in ms for a model.

**Parameters**:

- `model_id`: Model identifier

**Returns**: Latency in milliseconds or None if not found

---

## get_quality

```python
get_quality(self: Any, model_id: str)
```

Get quality score for a model.

**Parameters**:

- `model_id`: Model identifier

**Returns**: Quality score (0-1) or None if not found

---

## get_store

Get the global benchmark store instance.

---

## refresh

```python
refresh(self: Any)
```

Refresh benchmark data from tokenledger.

---

## tokenledger

```python
tokenledger(self: Any)
```

Get the tokenledger adapter.

---

