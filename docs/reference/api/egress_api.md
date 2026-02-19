# egress API Reference

> **Source**: `src/thegent/observability/egress.py`

WP-15001: External SOC/SIEM event egress for enterprise observability.

---

## EgressEvent

---

## SIEMEgress

Pushes normalized events to external enterprise security systems (WP-15001).

### Methods

#### SIEMEgress.__init__

```python
__init__(self, endpoint_url)
```

#### SIEMEgress.format_for_syslog

Format the event for traditional RFC 5424 syslog.

```python
format_for_syslog(self, event)
```

#### SIEMEgress.push_event

Push an event to the external SIEM endpoint via HTTP POST.

```python
push_event(self, event)
```

---

## format_for_syslog

Format the event for traditional RFC 5424 syslog.

```python
format_for_syslog(self, event)
```

---

## push_event

Push an event to the external SIEM endpoint via HTTP POST.

```python
push_event(self, event)
```

---

