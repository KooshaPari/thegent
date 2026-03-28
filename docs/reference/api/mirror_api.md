# mirror API Reference

> **Source**: `src/thegent/utils/routing_impl/mirror.py`

GW-59: Traffic mirroring — shadow A/B deployment (send to secondary silently).

Sends a copy of the request to a secondary endpoint asynchronously.
The primary response is returned; secondary response is discarded.

# @trace FR-AROUTE-059

---

## MirrorConfig

Configuration for traffic mirroring to a secondary endpoint.

---

## MirrorResult

Result of a mirroring attempt.

---

## should_mirror

```python
should_mirror(config: MirrorConfig)
```

Determine whether the current request should be mirrored.

**Parameters**:

- `config`: Mirror configuration.

**Returns**: True if mirroring should occur for this request.

---

