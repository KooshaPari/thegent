# cliproxy_header_utils API Reference

> **Source**: `src/thegent/cliproxy_header_utils.py`

## extract_websocket_forward_headers

```python
extract_websocket_forward_headers(websocket_headers: dict[(str, str)])
```

Build headers for WS->HTTP forwarding while preserving authorization.

---

## filter_inbound_response_headers

```python
filter_inbound_response_headers(response_headers: dict[(str, Any)])
```

Drop hop-by-hop response headers before returning to clients.

---

## sanitize_outbound_request_headers

```python
sanitize_outbound_request_headers(request_headers: dict[(str, Any)])
```

Return outbound request headers with hop-by-hop fields removed.

---

