# fast_http_client API Reference

> **Source**: `src/thegent/infra/fast_http_client.py`

Fast HTTP client with optimized backends.

This module provides a high-performance abstraction layer for HTTP requests
that automatically selects the fastest available backend:
- curl_cffi: 2-3x faster, libcurl-based, browser fingerprinting
- httpx: Modern, well-maintained, good async/sync support
- requests: Legacy fallback

Performance improvements:
- curl_cffi uses libcurl (2-3x faster than httpx)
- Better connection pooling
- Browser fingerprinting support
- Automatic backend selection

---

## FastHTTPClient

High-performance HTTP client with automatic backend selection.

Backend priority (fastest first):
1. curl_cffi (if installed) - 2-3x faster, libcurl-based
2. httpx (modern, well-maintained) - good balance
3. requests (legacy fallback) - baseline

### Methods

#### FastHTTPClient.__init__

Initialize HTTP client.

Args:
    impersonate: Browser to impersonate (curl_cffi only, e.g., "chrome", "safari")

```python
__init__(self, impersonate)
```

#### FastHTTPClient.backend

Get current backend name.

```python
backend(self)
```

#### FastHTTPClient.get

Perform GET request.

Args:
    url: URL to request
    **kwargs: Additional request options

Returns:
    Response object

```python
get(self, url)
```

#### FastHTTPClient.post

Perform POST request.

Args:
    url: URL to request
    **kwargs: Additional request options

Returns:
    Response object

```python
post(self, url)
```

#### FastHTTPClient.request

Perform HTTP request.

Args:
    method: HTTP method (GET, POST, etc.)
    url: URL to request
    **kwargs: Additional request options

Returns:
    Response object

```python
request(self, method, url)
```

---

## backend

Get current backend name.

```python
backend(self)
```

---

## get

Perform GET request.

Args:
    url: URL to request
    **kwargs: Additional request options

Returns:
    Response object

```python
get(self, url)
```

---

## get_http_client

Get global fast HTTP client instance.

Args:
    impersonate: Browser to impersonate (curl_cffi only)

Returns:
    FastHTTPClient instance

```python
get_http_client(impersonate)
```

---

## http_get

Perform GET request using fastest available backend.

```python
http_get(url)
```

---

## http_post

Perform POST request using fastest available backend.

```python
http_post(url)
```

---

## http_request

Perform HTTP request using fastest available backend.

```python
http_request(method, url)
```

---

## post

Perform POST request.

Args:
    url: URL to request
    **kwargs: Additional request options

Returns:
    Response object

```python
post(self, url)
```

---

## request

Perform HTTP request.

Args:
    method: HTTP method (GET, POST, etc.)
    url: URL to request
    **kwargs: Additional request options

Returns:
    Response object

```python
request(self, method, url)
```

---

