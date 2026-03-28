# egress API Reference

> **Source**: `src/thegent/observability/egress.py`

Structured SIEM egress helpers.

---

## EgressEvent

Structured event payload for external egress sinks.

---

## SIEMEgress

Push governance events to an HTTP SIEM endpoint.

### Methods

#### SIEMEgress.__init__

```python
__init__(self: Any, endpoint_url: str)
```

---

#### SIEMEgress.format_for_syslog

```python
format_for_syslog(self: Any, event: EgressEvent)
```

Render a compact syslog-style line for an event.

---

#### SIEMEgress.push_event

```python
push_event(self: Any, event: EgressEvent)
```

Send an event to the configured SIEM endpoint.

---

---

## format_for_syslog

```python
format_for_syslog(self: Any, event: EgressEvent)
```

Render a compact syslog-style line for an event.

---

## push_event

```python
push_event(self: Any, event: EgressEvent)
```

Send an event to the configured SIEM endpoint.

---

