# cursor_provider API Reference

> **Source**: `src/thegent/utils/routing_impl/cursor_provider.py`

CLIProxy Cursor Phase 2 — cursor: schema, token-file provider, token refresh.

G-CP-01 / G-CP-02 / G-CP-03: Adds the Cursor-dedicated block to CLIProxy routing.

Capabilities:
  - cursor: schema support (token-file or auth-token variants)
  - Token refresh: reads sk-... from ~/.cursor-server/ or a configured token-file,
    re-reads on TTL expiry, signals rebindExecutors on change.
  - rebindExecutors: notifies active httpx sessions to re-authenticate after a
    token rotation event.

# @trace FR-CP-002

---

## CursorExecutorManager

Tracks active Cursor HTTP sessions and rebinds them on token rotation.

When the token file changes, `rebindExecutors` closes stale sessions so the
next request picks up the new bearer token automatically.

# @trace FR-CP-002

### Methods

#### CursorExecutorManager.__init__

```python
__init__(self: Any, provider: CursorTokenProvider)
```

---

#### CursorExecutorManager.get_auth_headers

```python
get_auth_headers(self: Any)
```

Build Authorization header dict for the current token.

---

#### CursorExecutorManager.register

```python
register(self: Any, client: Any)
```

Register an httpx.AsyncClient (or compatible) for rebinding.

---

---

## CursorProviderConfig

Full Phase 2 config for the cursor: routing schema.

Maps to CLIProxyAPIPlus CursorKey YAML schema:
    cursor:
      - token-file: <path>
        cursor-api-url: <url>

### Methods

#### CursorProviderConfig.to_cliproxy_block

```python
to_cliproxy_block(self: Any)
```

Serialize to CLIProxyAPIPlus cursor YAML block.

---

---

## CursorTokenProvider

Reads and caches the Cursor session token from a file on disk.

The token file contains a bare `sk-...` bearer token (written by
cursor-api /build-key or auto-managed by thegent).

# @trace FR-CP-002

### Methods

#### CursorTokenProvider.discover

```python
discover(cls: Any)
```

Auto-discover the first readable token file from known Cursor paths.

---

#### CursorTokenProvider.get_token

```python
get_token(self: Any)
```

Return the current token, re-reading from disk when TTL has expired.

---

#### CursorTokenProvider.is_expired

```python
is_expired(self: Any)
```

Return True when the cached token is stale (TTL exceeded).

---

---

## build_cursor_routing_config

```python
build_cursor_routing_config(cursor_api_url: str, token_file: Any, auth_token: Any)
```

Build the cursor: routing config block for CLIProxyAPIPlus.

Validates that exactly one auth mechanism is provided (token-file OR auth-token).

# @trace FR-CP-002

---

## discover

```python
discover(cls: Any)
```

Auto-discover the first readable token file from known Cursor paths.

---

## get_auth_headers

```python
get_auth_headers(self: Any)
```

Build Authorization header dict for the current token.

---

## get_token

```python
get_token(self: Any)
```

Return the current token, re-reading from disk when TTL has expired.

---

## is_expired

```python
is_expired(self: Any)
```

Return True when the cached token is stale (TTL exceeded).

---

## register

```python
register(self: Any, client: Any)
```

Register an httpx.AsyncClient (or compatible) for rebinding.

---

## to_cliproxy_block

```python
to_cliproxy_block(self: Any)
```

Serialize to CLIProxyAPIPlus cursor YAML block.

---

