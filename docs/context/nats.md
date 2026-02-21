# NATS (nats-py Python Client) Context

> Definitive reference for NATS messaging with the nats-py Python async client.
> Sources: nats-io.github.io/nats.py, docs.nats.io, github.com/nats-io/nats.py (fetched 2026-02-20).
> **Version covered: nats-py >= 2.12.0 (trace project version)**

---

## What is NATS

**NATS** is a cloud-native, high-performance messaging system. It provides:

- **Core NATS**: At-most-once pub/sub, request-reply, queue groups — fast, ephemeral
- **JetStream**: Persistent streaming, at-least-once and exactly-once delivery, key-value store, object store
- **Subject-based addressing**: Messages routed by subject strings (`"orders.created"`, `"users.>"`), with wildcards

NATS is the transport layer for event-driven, loosely-coupled services. Unlike Kafka, it has no broker-side consumer groups; consumers are process-side.

**trace Use Case:** `nats-py>=2.12.0` + `nkeys>=0.2.1` in `pyproject.toml`. Used for real-time event distribution between trace services (Go backend, Python backend, worker processes) — agent job events, webhook delivery, inter-service messaging.

---

## Key Concepts

| Term | Definition |
|------|-----------|
| **Subject** | Dot-delimited routing key, e.g., `"orders.created"`, `"users.*.updated"` |
| **Wildcard `*`** | Matches one token: `"orders.*.created"` matches `"orders.123.created"` |
| **Wildcard `>`** | Matches remaining tokens: `"orders.>"` matches all under `orders.` |
| **Queue group** | Named group where only one subscriber receives each message (load balancing) |
| **JetStream** | Persistence layer on top of core NATS; streams store messages |
| **Stream** | Named, durable collection of messages filtered by subjects |
| **Consumer** | Named cursor on a stream; tracks delivery progress |
| **KV bucket** | JetStream-backed key-value store |
| **NUID** | NATS unique ID generator (fast, URL-safe) |
| **nkeys** | Ed25519-based decentralized auth for NATS v2+ |

---

## Installation

```bash
pip install nats-py
# With nkeys for NATS v2 decentralized auth
pip install nats-py[nkeys]
# or separately
pip install nkeys

# Versions in trace project:
# nats-py>=2.12.0
# nkeys>=0.2.1
```

**NATS Server (local dev):**

```bash
brew install nats-server
nats-server -js          # With JetStream enabled

# Or Docker
docker run -p 4222:4222 nats:latest -js
```

---

## Connection

```python
import asyncio
import nats
from nats.aio.client import Client as NATS

async def main():
    # Connect to local server
    nc = await nats.connect("nats://localhost:4222")

    # Multiple servers (cluster)
    nc = await nats.connect([
        "nats://server1:4222",
        "nats://server2:4222",
    ])

    # With options
    nc = await nats.connect(
        "nats://localhost:4222",
        name="trace-python-backend",
        connect_timeout=5,            # seconds
        reconnect_time_wait=2,        # seconds between reconnect attempts
        max_reconnect_attempts=10,    # -1 for infinite
        ping_interval=20,             # seconds
        max_outstanding_pings=3,
        # Callbacks
        error_cb=error_handler,
        disconnected_cb=disconnected_handler,
        reconnected_cb=reconnected_handler,
        closed_cb=closed_handler,
    )

    await nc.close()

asyncio.run(main())
```

**Connection state checks:**

```python
nc.is_connected        # bool
nc.is_closed           # bool
nc.is_reconnecting     # bool
nc.connected_url       # URL of active server
nc.max_payload         # Max message size in bytes
nc.client_id           # Unique client identifier
```

---

## Core NATS: Pub/Sub

### Publish

```python
# Publish bytes
await nc.publish("orders.created", b'{"order_id": "123"}')

# With reply subject (for request-reply)
await nc.publish("orders.created", b'data', reply="inbox.123")

# Flush ensures messages reach server
await nc.flush(timeout=5)
```

### Subscribe (Callback-based)

```python
async def message_handler(msg):
    subject = msg.subject
    reply = msg.reply
    data = msg.data.decode()
    print(f"Received on {subject}: {data}")

    # Respond to request-reply
    if msg.reply:
        await nc.publish(msg.reply, b"ACK")

sub = await nc.subscribe("orders.*", cb=message_handler)

# Unsubscribe
await sub.unsubscribe()

# Queue group (load-balanced delivery — only one subscriber gets each message)
sub = await nc.subscribe("orders.created", queue="order-processors", cb=message_handler)
```

### Subscribe (Iterator)

```python
sub = await nc.subscribe("orders.created")

async for msg in sub.messages:
    data = msg.data.decode()
    print(f"Message: {data}")
    if should_stop:
        break

await sub.unsubscribe()
```

### Subscribe (next_msg)

```python
sub = await nc.subscribe("responses")

# Wait for one message
msg = await sub.next_msg(timeout=5.0)
print(msg.data.decode())

await sub.unsubscribe()
```

---

## Request-Reply

```python
# Send request; wait for first reply (1 second timeout)
reply = await nc.request("service.get_user", b'{"user_id": "123"}', timeout=1.0)
user_data = reply.data.decode()

# Service handler
async def user_service(msg):
    user_id = json.loads(msg.data)["user_id"]
    user = await db.get_user(user_id)
    await msg.respond(json.dumps(user).encode())

await nc.subscribe("service.get_user", cb=user_service)
```

**`NoRespondersError`**: Raised when no subscriber matches the subject. Handle it:

```python
from nats.errors import NoRespondersError

try:
    reply = await nc.request("service.unknown", b"", timeout=1.0)
except NoRespondersError:
    print("No service listening on that subject")
```

---

## JetStream

JetStream adds persistence, acknowledgment, and replay capabilities.

### JetStream Context

```python
js = nc.jetstream()
# or with options
js = nc.jetstream(timeout=5)
```

### Stream Management

```python
from nats.js.api import StreamConfig, RetentionPolicy, StorageType

# Create stream
await js.add_stream(StreamConfig(
    name="ORDERS",
    subjects=["orders.>"],          # All subjects under orders.
    retention=RetentionPolicy.LIMITS,
    storage=StorageType.FILE,
    max_msgs=1_000_000,
    max_bytes=1024 * 1024 * 1024,   # 1GB
    max_age=86400,                  # 1 day in seconds
))

# Get stream info
info = await js.stream_info("ORDERS")
print(info.config.subjects)

# Update stream
await js.update_stream(StreamConfig(name="ORDERS", max_msgs=2_000_000, subjects=["orders.>"]))

# Delete stream
await js.delete_stream("ORDERS")

# Purge stream (remove all messages)
await js.purge_stream("ORDERS")
```

### Publishing to JetStream

```python
import json

# Publish and wait for ACK
ack = await js.publish("orders.created", json.dumps({"id": "123"}).encode())
print(f"Published: stream={ack.stream}, seq={ack.seq}")

# Publish with deduplication (exactly-once)
ack = await js.publish(
    "orders.created",
    json.dumps({"id": "123"}).encode(),
    headers={"Nats-Msg-Id": "order-123"},  # Idempotency key
)
```

### Push Subscription (Async, Real-time)

```python
from nats.js.api import ConsumerConfig, AckPolicy, DeliverPolicy

# Subscribe (creates ephemeral consumer)
sub = await js.subscribe("orders.>", durable="order-processor")

async for msg in sub.messages:
    data = json.loads(msg.data)
    try:
        await process_order(data)
        await msg.ack()                  # Acknowledge
    except Exception as e:
        await msg.nak(delay=5)           # Negative ack, retry after 5s

# Or with callback
async def order_handler(msg):
    data = json.loads(msg.data)
    await process_order(data)
    await msg.ack()

sub = await js.subscribe(
    "orders.>",
    cb=order_handler,
    durable="order-processor",
    stream="ORDERS",
    config=ConsumerConfig(
        ack_policy=AckPolicy.EXPLICIT,
        deliver_policy=DeliverPolicy.ALL,  # Start from beginning
        max_deliver=3,                     # Max delivery attempts
    ),
)
```

### Pull Subscription (Batched)

```python
# Create durable pull consumer
sub = await js.pull_subscribe("orders.>", durable="batch-processor", stream="ORDERS")

# Fetch a batch
msgs = await sub.fetch(batch=10, timeout=2.0)
for msg in msgs:
    await process(msg.data)
    await msg.ack()

# Consumer info
info = await sub.consumer_info()
print(f"Pending: {info.num_pending}")
```

**Message acknowledgment modes:**

| Method | Behavior |
|--------|---------|
| `await msg.ack()` | Acknowledge — don't redeliver |
| `await msg.ack_sync()` | Acknowledge with server confirmation |
| `await msg.nak()` | Negative ack — redeliver immediately |
| `await msg.nak(delay=5)` | Negative ack — redeliver after 5 seconds |
| `await msg.in_progress()` | Heartbeat — still processing, reset ack wait |
| `await msg.term()` | Terminate — stop redelivery permanently |

---

## Key-Value Store

JetStream-backed KV with watch capability.

```python
# Create KV bucket
kv = await js.create_key_value(
    bucket="trace-config",
    ttl=3600,            # 1 hour TTL (seconds)
    history=5,           # Keep 5 historical values per key
    storage=StorageType.FILE,
)

# Or get existing bucket
kv = await js.key_value("trace-config")

# CRUD operations
await kv.put("feature.new_ui", b"true")
entry = await kv.get("feature.new_ui")
print(entry.value.decode())    # "true"

await kv.update("feature.new_ui", b"false", last_revision=entry.revision)

await kv.delete("feature.old_flag")
await kv.purge("feature.old_flag")   # Remove all history for key

# Status
status = await kv.status()
print(f"Bucket: {status.bucket}, Keys: {status.values}")

# Watch for changes
async for entry in await kv.watch("feature.*"):
    if entry is None:
        break  # Initial values delivered
    print(f"Key: {entry.key}, Value: {entry.value}, Op: {entry.operation}")
```

---

## Authentication

```python
# Username/password
nc = await nats.connect("nats://user:pass@localhost:4222")

# Token
nc = await nats.connect("nats://mytoken@localhost:4222")
# or
nc = await nats.connect("nats://localhost:4222", token="mytoken")

# NKeys (Ed25519; NATS v2 decentralized auth)
import nkeys

# From seed file
with open("user.nk") as f:
    seed = f.read().strip().encode()
keypair = nkeys.from_seed(seed)

nc = await nats.connect(
    "nats://localhost:4222",
    nkeys_seed=keypair.seed,
)

# TLS
import ssl
ssl_ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
ssl_ctx.load_verify_locations("ca.pem")
ssl_ctx.load_cert_chain("client.pem", "client-key.pem")

nc = await nats.connect("nats://localhost:4222", tls=ssl_ctx)
```

---

## Error Handling

```python
from nats.errors import (
    TimeoutError,
    NoRespondersError,
    ConnectionClosedError,
    AuthorizationError,
    MaxPayloadError,
)
from nats.js.errors import (
    NotFoundError,
    ServiceUnavailableError,
    FetchTimeoutError,
    KeyNotFoundError,
)

# Connection error callbacks
async def error_handler(e):
    if isinstance(e, ConnectionClosedError):
        print("Connection closed:", e)
    elif isinstance(e, AuthorizationError):
        print("Auth failed:", e)
    else:
        print("NATS error:", e)

async def disconnected_handler():
    print("Disconnected from NATS")

async def reconnected_handler():
    print("Reconnected to NATS")

nc = await nats.connect(
    "nats://localhost:4222",
    error_cb=error_handler,
    disconnected_cb=disconnected_handler,
    reconnected_cb=reconnected_handler,
)
```

---

## Graceful Shutdown

```python
async def shutdown(nc):
    # Drain: process pending messages, then close
    await nc.drain()
    # After drain, nc.is_closed == True; do NOT call nc.close() after drain
```

---

## NUID (Unique ID Generator)

```python
from nats.nuid import NUID

nuid = NUID()
unique_id = nuid.next().decode()  # "4kMEXOoWQQ56gd8dqLI4l3"
# Fast URL-safe unique IDs; ~50ns per ID
```

---

## Code Examples: trace Service Pattern

```python
import asyncio
import json
import nats
from nats.aio.client import Client as NATS

class TraceEventBus:
    """Wrapper around NATS for trace service events."""

    def __init__(self, nc: NATS):
        self._nc = nc
        self._js = nc.jetstream()

    @classmethod
    async def connect(cls, servers: list[str]) -> "TraceEventBus":
        nc = await nats.connect(servers, name="trace-backend")
        return cls(nc)

    async def publish_job_event(self, job_id: str, event: str, data: dict) -> None:
        subject = f"jobs.{job_id}.{event}"
        payload = json.dumps({"job_id": job_id, "event": event, **data}).encode()
        await self._js.publish(subject, payload, headers={"Nats-Msg-Id": f"{job_id}-{event}"})

    async def subscribe_job_events(self, job_id: str, handler) -> None:
        sub = await self._js.subscribe(
            f"jobs.{job_id}.>",
            durable=f"job-{job_id}-handler",
        )
        async for msg in sub.messages:
            event_data = json.loads(msg.data)
            await handler(event_data)
            await msg.ack()

    async def close(self) -> None:
        await self._nc.drain()
```

---

## thegent / trace Integration

- **trace**: `nats-py>=2.12.0`, `nkeys>=0.2.1` in `pyproject.toml`
- **Pattern**: JetStream for durable event delivery; KV store for feature flags / runtime config
- **Subjects**: Dot-delimited hierarchy (e.g., `"jobs.{id}.created"`, `"agents.{id}.status"`)
- **Server**: JetStream-enabled (`nats-server -js`); Streams and consumers managed by Python backend on startup

---

## Known Issues / Gotchas

1. **JetStream requires `-js` flag**: `nats-server` without `-js` flag ignores JetStream API calls silently.
2. **Drain vs Close**: After `nc.drain()`, do NOT call `nc.close()` — drain handles the close. Calling both causes errors.
3. **Durable name required for persistence**: Without `durable=`, JetStream creates an ephemeral consumer that disappears when subscription ends.
4. **ACK timeout**: Messages not acked within `ack_wait` (default 30s) are redelivered. Always `await msg.ack()` or `await msg.in_progress()` for long tasks.
5. **At-most-once for core NATS**: Core NATS pub/sub has no persistence. Use JetStream if you need guaranteed delivery.
6. **Max payload**: Default max is 1MB per message. Configure `max_payload` on server for larger messages.
7. **Subject namespace**: Subjects are global. Use dot-delimited namespaces to avoid collision across services.

---

## Sources & References

- **nats-py Documentation**: https://nats-io.github.io/nats.py/ (fetched 2026-02-20)
- **NATS Docs**: https://docs.nats.io (fetched 2026-02-20)
- **GitHub**: https://github.com/nats-io/nats.py (fetched 2026-02-20)
- **JetStream Docs**: https://docs.nats.io/nats-concepts/jetstream (fetched 2026-02-20)
- **PyPI**: https://pypi.org/project/nats-py/ (fetched 2026-02-20)
- **Last Verified**: 2026-02-20

---

## Quick Reference

| Item | Value |
|------|-------|
| Package | `nats-py>=2.12.0` |
| Auth extra | `nats-py[nkeys]` |
| Default port | `4222` |
| JetStream flag | `nats-server -js` |
| Core NATS | At-most-once, ephemeral |
| JetStream | At-least-once / exactly-once, persistent |

### Subject Wildcard Rules

```
orders.*        → matches orders.created, orders.updated (one token)
orders.>        → matches orders.created, orders.123.items (one or more tokens)
>               → matches everything
```

### Common Patterns

```python
# Connect
nc = await nats.connect("nats://localhost:4222")

# Core pub/sub
await nc.publish("subject", b"data")
sub = await nc.subscribe("subject.*", cb=handler)

# Request-reply
reply = await nc.request("service.method", b"data", timeout=1.0)

# JetStream context
js = nc.jetstream()

# Publish to stream
ack = await js.publish("orders.created", b"data", headers={"Nats-Msg-Id": "msg-001"})

# Subscribe from stream
sub = await js.subscribe("orders.>", durable="processor")
async for msg in sub.messages:
    await process(msg.data)
    await msg.ack()

# KV store
kv = await js.key_value("my-bucket")
await kv.put("key", b"value")
entry = await kv.get("key")

# Graceful shutdown
await nc.drain()
```
