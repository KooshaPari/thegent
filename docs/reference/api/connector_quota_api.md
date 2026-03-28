# connector_quota API Reference

> **Source**: `src/thegent/integrations/connector_quota.py`

Connector quota budget management for sync operations.

# @trace WL-221

---

## ConnectorQuota

Represents the quota allocation for a single connector.

### Methods

#### ConnectorQuota.is_exhausted

```python
is_exhausted(self: Any)
```

Check if quota is exhausted.

---

#### ConnectorQuota.remaining

```python
remaining(self: Any)
```

Return the remaining quota for today.

---

---

## QuotaBudgetManager

Manages quota budgets for multiple connectors.

### Methods

#### QuotaBudgetManager.__init__

```python
__init__(self: Any)
```

Initialize the quota budget manager.

---

#### QuotaBudgetManager.check_quota

```python
check_quota(self: Any, connector: str, n: int)
```

Check if quota is available for the given connector.

**Parameters**:

- `connector`: Name of the connector.
- `n`: Number of operations to check (default: 1).

**Returns**: True if quota is available, False otherwise.

---

#### QuotaBudgetManager.consume

```python
consume(self: Any, connector: str, n: int)
```

Consume quota for a connector.

**Parameters**:

- `connector`: Name of the connector.
- `n`: Number of operations to consume (default: 1).

---

#### QuotaBudgetManager.get_all_quotas

```python
get_all_quotas(self: Any)
```

Get all registered quotas.

**Returns**: Dictionary mapping connector names to their quotas.

---

#### QuotaBudgetManager.get_quota

```python
get_quota(self: Any, connector: str)
```

Get the quota object for a connector.

**Parameters**:

- `connector`: Name of the connector.

**Returns**: The ConnectorQuota object.

---

#### QuotaBudgetManager.register

```python
register(self: Any, connector_name: str, daily_limit: int)
```

Register a connector with a daily quota limit.

**Parameters**:

- `connector_name`: Name of the connector.
- `daily_limit`: Daily quota limit (number of operations allowed).

---

#### QuotaBudgetManager.reset_daily

```python
reset_daily(self: Any)
```

Reset all quotas if their reset time has passed.

---

---

## QuotaExhaustedError

Raised when a connector's daily quota budget is exhausted.

**Inherits from**: `Exception`

---

## check_quota

```python
check_quota(self: Any, connector: str, n: int)
```

Check if quota is available for the given connector.

**Parameters**:

- `connector`: Name of the connector.
- `n`: Number of operations to check (default: 1).

**Returns**: True if quota is available, False otherwise.

**Raises**:

- `KeyError`: If connector is not registered.

---

## consume

```python
consume(self: Any, connector: str, n: int)
```

Consume quota for a connector.

**Parameters**:

- `connector`: Name of the connector.
- `n`: Number of operations to consume (default: 1).

**Raises**:

- `KeyError`: If connector is not registered.
- `QuotaExhaustedError`: If insufficient quota is available.

---

## get_all_quotas

```python
get_all_quotas(self: Any)
```

Get all registered quotas.

**Returns**: Dictionary mapping connector names to their quotas.

---

## get_quota

```python
get_quota(self: Any, connector: str)
```

Get the quota object for a connector.

**Parameters**:

- `connector`: Name of the connector.

**Returns**: The ConnectorQuota object.

**Raises**:

- `KeyError`: If connector is not registered.

---

## is_exhausted

```python
is_exhausted(self: Any)
```

Check if quota is exhausted.

---

## register

```python
register(self: Any, connector_name: str, daily_limit: int)
```

Register a connector with a daily quota limit.

**Parameters**:

- `connector_name`: Name of the connector.
- `daily_limit`: Daily quota limit (number of operations allowed).

**Raises**:

- `ValueError`: If daily_limit is <= 0.

---

## remaining

```python
remaining(self: Any)
```

Return the remaining quota for today.

---

## reset_daily

```python
reset_daily(self: Any)
```

Reset all quotas if their reset time has passed.

---

