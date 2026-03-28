# cliproxy API Reference

> **Source**: `src/thegent/ports/driven/cliproxy.py`

Port interface (Protocol) for cliproxy provider lifecycle.

Defines the contract for cliproxy management without tying to specific implementations.

---

## CliproxyCredentialsManager

Interface for cliproxy credentials and configuration.

**Inherits from**: `Protocol`

### Methods

#### CliproxyCredentialsManager.get_provider_config

```python
get_provider_config(self: Any, provider: str)
```

Get provider login configuration.

---

#### CliproxyCredentialsManager.has_credentials

```python
has_credentials(self: Any, provider: str)
```

Check if provider already has credentials configured.

---

#### CliproxyCredentialsManager.setup_provider

```python
setup_provider(self: Any, provider: str, api_key: Any)
```

Setup provider with API key or OAuth.

Returns 0 on success, 1 on skip, 2 on error.

---

---

## CliproxyHTTPAdapter

HTTP adapter interface for cliproxy requests.

**Inherits from**: `Protocol`

### Methods

#### CliproxyHTTPAdapter.proxy_request

```python
proxy_request(self: Any, method: str, path: str, body: Any, headers: Any)
```

Proxy HTTP request to cliproxy backend.

Returns (status_code, response_body, response_headers).

---

#### CliproxyHTTPAdapter.proxy_stream

```python
proxy_stream(self: Any, method: str, path: str, body: Any, headers: Any)
```

Proxy streaming HTTP request (SSE).

Returns async generator yielding response chunks.

---

---

## CliproxyProvider

Interface for cliproxy provider lifecycle management.

**Inherits from**: `Protocol`

### Methods

#### CliproxyProvider.ensure_running

```python
ensure_running(self: Any)
```

Ensure cliproxy is running and return base_url.

Raises FileNotFoundError if binary not available.
Raises RuntimeError if startup fails.

---

#### CliproxyProvider.fetch_metrics

```python
fetch_metrics(self: Any)
```

Fetch per-provider metrics from /v1/metrics/providers.

Returns metrics dict or None if unavailable.

---

#### CliproxyProvider.get_last_metrics_status

```python
get_last_metrics_status(self: Any)
```

Return status metadata from latest metrics fetch.

---

#### CliproxyProvider.kill

```python
kill(self: Any)
```

Kill proxy process. Returns True if a process was killed.

---

#### CliproxyProvider.start_managed

```python
start_managed(self: Any)
```

Start proxy and return (proc, base_url) for lifecycle management.

proc is None if proxy already running. Caller must terminate proc.

---

---

## ensure_running

```python
ensure_running(self: Any)
```

Ensure cliproxy is running and return base_url.

Raises FileNotFoundError if binary not available.
Raises RuntimeError if startup fails.

---

## fetch_metrics

```python
fetch_metrics(self: Any)
```

Fetch per-provider metrics from /v1/metrics/providers.

Returns metrics dict or None if unavailable.

---

## get_last_metrics_status

```python
get_last_metrics_status(self: Any)
```

Return status metadata from latest metrics fetch.

---

## get_provider_config

```python
get_provider_config(self: Any, provider: str)
```

Get provider login configuration.

---

## has_credentials

```python
has_credentials(self: Any, provider: str)
```

Check if provider already has credentials configured.

---

## kill

```python
kill(self: Any)
```

Kill proxy process. Returns True if a process was killed.

---

## proxy_request

```python
proxy_request(self: Any, method: str, path: str, body: Any, headers: Any)
```

Proxy HTTP request to cliproxy backend.

Returns (status_code, response_body, response_headers).

---

## proxy_stream

```python
proxy_stream(self: Any, method: str, path: str, body: Any, headers: Any)
```

Proxy streaming HTTP request (SSE).

Returns async generator yielding response chunks.

---

## setup_provider

```python
setup_provider(self: Any, provider: str, api_key: Any)
```

Setup provider with API key or OAuth.

Returns 0 on success, 1 on skip, 2 on error.

---

## start_managed

```python
start_managed(self: Any)
```

Start proxy and return (proc, base_url) for lifecycle management.

proc is None if proxy already running. Caller must terminate proc.

---

