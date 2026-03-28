# cliproxy_http API Reference

> **Source**: `src/thegent/adapters/driven/cliproxy_http.py`

HTTP client adapter for cliproxy backend requests.

Handles:
- HTTP request/response proxying
- SSE streaming
- Request transformation (Responses -> Chat Completions)
- Response transformation
- Error handling and retries
- OpenRouter-specific logic

---

## CliproxyHTTPClient

HTTP client for cliproxy backend communication.

### Methods

#### CliproxyHTTPClient.__init__

```python
__init__(self: Any, backend_url: str, timeout: float)
```

---

---

## CliproxyHeaderManager

Manages request/response headers for cliproxy.

### Methods

#### CliproxyHeaderManager.filter_inbound_headers

```python
filter_inbound_headers(headers: dict[(str, str)])
```

Filter headers from backend response.

---

#### CliproxyHeaderManager.inject_openrouter_headers

```python
inject_openrouter_headers(headers: dict[(str, str)], backend_url: str)
```

Inject OpenRouter attribution headers if needed.

---

#### CliproxyHeaderManager.sanitize_outbound_headers

```python
sanitize_outbound_headers(headers: dict[(str, str)])
```

Sanitize headers for backend request.

---

---

## CliproxyResponseTransformer

Transforms responses between protocols.

### Methods

#### CliproxyResponseTransformer.transform_models_response

```python
transform_models_response(response_body: bytes, inject_openrouter: bool)
```

Transform /v1/models response to canonical format.

Returns (transformed_body, etag) or None if not transformable.

---

#### CliproxyResponseTransformer.transform_request_body

```python
transform_request_body(body: dict[(str, Any)])
```

Transform /v1/responses request to /v1/chat/completions.

---

---

## filter_inbound_headers

```python
filter_inbound_headers(headers: dict[(str, str)])
```

Filter headers from backend response.

---

## inject_openrouter_headers

```python
inject_openrouter_headers(headers: dict[(str, str)], backend_url: str)
```

Inject OpenRouter attribution headers if needed.

---

## sanitize_outbound_headers

```python
sanitize_outbound_headers(headers: dict[(str, str)])
```

Sanitize headers for backend request.

---

## transform_models_response

```python
transform_models_response(response_body: bytes, inject_openrouter: bool)
```

Transform /v1/models response to canonical format.

Returns (transformed_body, etag) or None if not transformable.

---

## transform_request_body

```python
transform_request_body(body: dict[(str, Any)])
```

Transform /v1/responses request to /v1/chat/completions.

---

