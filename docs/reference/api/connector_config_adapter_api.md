# connector_config_adapter API Reference

> **Source**: `src/thegent/integrations/adapters/connector_config_adapter.py`

Connector configuration adapter for workstream autosync.

Handles connector-specific configuration (timeouts, circuit breakers, etc).

---

## ConnectorConfigAdapter

Adapter for connector-specific configuration.

### Methods

#### ConnectorConfigAdapter.__init__

```python
__init__(self: Any, config: Any)
```

---

#### ConnectorConfigAdapter.create_rate_limiter

```python
create_rate_limiter(self: Any)
```

Create rate limiter with config.

---

#### ConnectorConfigAdapter.get_connector_breaker

```python
get_connector_breaker(self: Any, connector: str)
```

Get circuit breaker for connector.

---

#### ConnectorConfigAdapter.get_connector_timeout

```python
get_connector_timeout(self: Any, connector: str, direction: str)
```

Get timeout for connector operation.

---

#### ConnectorConfigAdapter.get_error_budget

```python
get_error_budget(self: Any, connector: str)
```

Get error budget tracker for connector.

---

---

## create_rate_limiter

```python
create_rate_limiter(self: Any)
```

Create rate limiter with config.

---

## get_connector_breaker

```python
get_connector_breaker(self: Any, connector: str)
```

Get circuit breaker for connector.

---

## get_connector_timeout

```python
get_connector_timeout(self: Any, connector: str, direction: str)
```

Get timeout for connector operation.

---

## get_error_budget

```python
get_error_budget(self: Any, connector: str)
```

Get error budget tracker for connector.

---

