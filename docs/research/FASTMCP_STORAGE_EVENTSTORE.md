# FastMCP Storage Backends & EventStore

**Source:** gofastmcp.com/servers/storage-backends, fastmcp/server/event_store  
**Date:** 2026-02-14  
**Purpose:** Extract RedisStore, DiskStore usage, EventStore(storage=), FernetEncryptionWrapper for thegent MCP server.

---

## 1. Storage Backends (py-key-value-aio)

FastMCP uses pluggable storage backends for caching and OAuth state. Default: in-memory.

### 1.1 MemoryStore (Default)

```python
from key_value.aio.stores.memory import MemoryStore
cache_store = MemoryStore()
```

- Development, single-process
- Data lost on restart
- No setup required

### 1.2 DiskStore

```python
from key_value.aio.stores.disk import DiskStore
from fastmcp.server.middleware.caching import ResponseCachingMiddleware

middleware = ResponseCachingMiddleware(
    cache_storage=DiskStore(directory="/var/cache/fastmcp")
)
```

For OAuth:

```python
from fastmcp.server.auth.providers.github import GitHubProvider
auth = GitHubProvider(
    client_storage=DiskStore(directory="/var/lib/fastmcp/oauth")
)
```

- Single-server production
- Data persists across restarts
- Not suitable for distributed deployments

### 1.3 RedisStore

```python
from key_value.aio.stores.redis import RedisStore
# Requires: pip install 'py-key-value-aio[redis]'

middleware = ResponseCachingMiddleware(
    cache_storage=RedisStore(host="redis.example.com", port=6379)
)

# With auth
RedisStore(host="redis.example.com", port=6379, password="your-redis-password")
```

For OAuth:

```python
auth = GitHubProvider(
    client_storage=RedisStore(host="redis.example.com", port=6379)
)
```

- Distributed production
- Multi-server deployments
- Built-in TTL support

### 1.4 FernetEncryptionWrapper (OAuth)

For production OAuth, wrap storage with encryption:

```python
from key_value.aio.wrappers.encryption import FernetEncryptionWrapper
from cryptography.fernet import Fernet

auth = GitHubProvider(
    client_storage=FernetEncryptionWrapper(
        key_value=RedisStore(host="redis.example.com", port=6379),
        fernet=Fernet(os.environ["STORAGE_ENCRYPTION_KEY"])
    )
)
```

- Required for production OAuth
- Without it, tokens stored in plaintext

### 1.5 PrefixCollectionsWrapper (Multi-tenant)

```python
from key_value.aio.wrappers.prefix_collections import PrefixCollectionsWrapper

base_store = RedisStore(host="redis.example.com")
namespaced_store = PrefixCollectionsWrapper(
    key_value=base_store,
    prefix="my-server"
)
middleware = ResponseCachingMiddleware(cache_storage=namespaced_store)
```

---

## 2. EventStore (SSE Polling)

From `fastmcp.server.event_store.EventStore`:

```python
from fastmcp.server.event_store import EventStore
from key_value.aio.stores.redis import RedisStore

# Default in-memory
event_store = EventStore()

# Redis for distributed
event_store = EventStore(storage=RedisStore(url="redis://localhost"))
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| storage | AsyncKeyValue | MemoryStore() | Backend for event storage |
| max_events_per_stream | int | 100 | Max events retained per stream |
| ttl | int | 3600 | Event TTL in seconds; None = no expiration |

### Usage with HTTP app

```python
app = mcp.http_app(
    event_store=event_store,
    retry_interval=2000,  # ms before client reconnects
    transport="streamable-http",
)
```

### ctx.close_sse_stream()

During long runs, periodically close the stream to avoid LB timeouts:

```python
if i % 30 == 0 and i > 0:
    await ctx.close_sse_stream()
```

Client reconnects with `Last-Event-ID`; EventStore resumes from last event.

---

## 3. thegent Application

| Use Case | Backend | Config |
|----------|---------|--------|
| Response cache (ps, list_agents, list_models) | DiskStore or RedisStore | `cache_storage=DiskStore(directory="/var/cache/thegent")` |
| EventStore (long thegent_run) | MemoryStore or RedisStore | `EventStore(storage=RedisStore(...))` |
| OAuth (if added) | RedisStore + FernetEncryptionWrapper | `client_storage=FernetEncryptionWrapper(...)` |
| Docket tasks (background) | `FASTMCP_DOCKET_URL=redis://...` | Task backend |

### Config Variables

| Variable | Default | Description |
|----------|---------|-------------|
| THGENT_CACHE_STORAGE | memory | `memory`, `disk:/path`, or `redis://host:port` |
| FASTMCP_DOCKET_URL | memory:// | Task backend for background tasks |
