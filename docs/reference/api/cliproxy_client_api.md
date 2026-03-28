# cliproxy_client API Reference

> **Source**: `src/thegent/utils/routing_impl/cliproxy_client.py`

CLIProxy client for routing decisions.

This client replaces LiteLLM-based routing. All routing decisions go through CLIProxy
localhost:8317 /v1/routing/select endpoint.

@trace FR-CLIPROXY-INTEGRATION-001

---

## CLIProxyRoutingClient

Client for CLIProxy routing endpoint.

### Methods

#### CLIProxyRoutingClient.__init__

```python
__init__(self: Any, base_url: Any, timeout: float)
```

Initialize the CLIProxy routing client.

**Parameters**:

- `base_url`: Base URL for CLIProxy. Defaults to http://localhost:8317
- `timeout`: Request timeout in seconds.

---

#### CLIProxyRoutingClient.client

```python
client(self: Any)
```

Lazy initialization of HTTP client.

---

#### CLIProxyRoutingClient.close

```python
close(self: Any)
```

Close the HTTP client.

---

#### CLIProxyRoutingClient.select_model

```python
select_model(self: Any, task_complexity: str, max_cost_per_call: float, max_latency_ms: int, min_quality_score: float)
```

Select optimal model via CLIProxy Pareto router.

**Parameters**:

- `task_complexity`: FAST, NORMAL, COMPLEX, or HIGH_COMPLEX
- `max_cost_per_call`: Maximum cost in USD
- `max_latency_ms`: Maximum latency in milliseconds
- `min_quality_score`: Minimum quality threshold (0.0-1.0)

**Returns**: RoutingResponse with model_id, provider, estimated_cost, estimated_latency_ms, quality_score

---

---

## RoutingResponse

Response from CLIProxy /v1/routing/select endpoint.

---

## client

```python
client(self: Any)
```

Lazy initialization of HTTP client.

---

## close

```python
close(self: Any)
```

Close the HTTP client.

---

## select_model

```python
select_model(self: Any, task_complexity: str, max_cost_per_call: float, max_latency_ms: int, min_quality_score: float)
```

Select optimal model via CLIProxy Pareto router.

**Parameters**:

- `task_complexity`: FAST, NORMAL, COMPLEX, or HIGH_COMPLEX
- `max_cost_per_call`: Maximum cost in USD
- `max_latency_ms`: Maximum latency in milliseconds
- `min_quality_score`: Minimum quality threshold (0.0-1.0)

**Returns**: RoutingResponse with model_id, provider, estimated_cost, estimated_latency_ms, quality_score

**Raises**:

- `httpx.HTTPError`: If the request fails

---

