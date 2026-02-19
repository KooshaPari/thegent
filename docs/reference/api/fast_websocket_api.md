# fast_websocket API Reference

> **Source**: `src/thegent/infra/fast_websocket.py`

Fast WebSocket client with optimized backends.

This module provides optimized WebSocket client support:
- websockets library (modern, fast, async-first)
- websocket-client fallback (legacy support)
- Unified API for both sync and async operations

Performance improvements:
- websockets: Modern, faster, better async support
- Better resource management
- Automatic backend selection

---

## FastWebSocket

High-performance WebSocket client with automatic backend selection.

### Methods

#### FastWebSocket.__init__

Initialize WebSocket client.

Args:
    url: WebSocket URL (ws:// or wss://)
    **kwargs: Additional connection options

```python
__init__(self, url)
```

#### FastWebSocket.close_sync

Close connection synchronously.

```python
close_sync(self)
```

#### FastWebSocket.connect_sync

Connect synchronously using websocket-client.

Performance:
    - websocket-client: Legacy, sync-only
    - Fallback for compatibility

```python
connect_sync(self)
```

#### FastWebSocket.recv_sync

Receive data synchronously.

```python
recv_sync(self)
```

#### FastWebSocket.send_sync

Send data synchronously.

```python
send_sync(self, data)
```

---

## close_sync

Close connection synchronously.

```python
close_sync(self)
```

---

## connect_sync

Connect synchronously using websocket-client.

Performance:
    - websocket-client: Legacy, sync-only
    - Fallback for compatibility

```python
connect_sync(self)
```

---

## recv_sync

Receive data synchronously.

```python
recv_sync(self)
```

---

## send_sync

Send data synchronously.

```python
send_sync(self, data)
```

---

## websocket_connect_sync

Create and connect WebSocket synchronously.

```python
websocket_connect_sync(url)
```

---

