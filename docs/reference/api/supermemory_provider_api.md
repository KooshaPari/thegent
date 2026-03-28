# supermemory_provider API Reference

> **Source**: `src/thegent/memory/supermemory_provider.py`

SupermemoryProvider: cloud persistence for ContinuityPackets (L3/L4).

Wraps SupermemoryClient to store and retrieve ContinuityPackets by
session_id using the Supermemory.ai API.

No fallbacks — if the API is unavailable, raises SupermemoryUnavailableError.

Config:
    THGENT_SUPERMEMORY_API_KEY  - Required. API key.
    THGENT_SUPERMEMORY_BASE_URL - Optional. Defaults to https://api.supermemory.ai/v3.

# @trace FR-HAX-004

---

## SupermemoryProvider

Cloud persistence provider for ContinuityPackets.

Uses SupermemoryClient to POST (store) and GET (retrieve) continuity
packets associated with a session_id.

Raises SupermemoryUnavailableError if the API key is not configured
or the API is unreachable — no silent fallbacks.

Example::

    provider = SupermemoryProvider()
    memory_id = await provider.store(packet)
    recovered = await provider.retrieve(session_id)

### Methods

#### SupermemoryProvider.__init__

```python
__init__(self: Any, api_key: Any, base_url: Any)
```

Initialise the provider.

**Parameters**:

- `api_key`: Supermemory API key. Falls back to THGENT_SUPERMEMORY_API_KEY.
- `base_url`: Optional base URL override.

---

---

## SupermemoryUnavailableError

Raised when the Supermemory API is not reachable or not configured.

**Inherits from**: `Exception`

---

