# session_control_impl API Reference

> **Source**: `src/thegent/cli/commands/session_control_impl.py`

Session control operations: wait, stop, send, history, metrics, prune, events,

meta, negotiate, purge, explain.

Extracted from session_ops_impl.py as part of WL-120 max-lines enforcement.
Contains:
- wait_impl: wait for a background session to complete
- session_send_impl: send a message to a running session
- stop_impl: stop a background session
- history_impl: list execution history
- metrics_impl: gather metrics for the agent registry
- prune_sessions_impl: prune old session data
- events_impl: list raw telemetry events
- session_meta_impl: get full session metadata
- session_contract_negotiate_impl: contract negotiation
- purge_impl: tiered retention purge
- explain_run_impl: multi-tier explanation for run decisions

---

## events_impl

```python
events_impl(run_id: Any, limit: int)
```

List raw telemetry events from the run registry.

---

## explain_run_impl

```python
explain_run_impl(run_id: str)
```

WP-4002: Multi-tier explanation framework for run decisions.

---

## history_impl

```python
history_impl(limit: int)
```

List execution history from the run registry.

---

## metrics_impl

Gather metrics for the agent registry (WP-9005).

---

## prune_sessions_impl

```python
prune_sessions_impl(days: Any)
```

Prune old session data (WP-3006).

---

## purge_impl

```python
purge_impl(dry_run: bool)
```

WP-3006: Tiered retention purge implementation (G-GP-07).

---

## session_contract_negotiate_impl

```python
session_contract_negotiate_impl(contract_id: str, supported_versions: list[str])
```

WP-7001: Implementation of contract negotiation logic.

---

## session_meta_impl

```python
session_meta_impl(session_id: str)
```

Get full session metadata. Returns meta dict or error.

---

## session_send_impl

```python
session_send_impl(session_id: str, message: str, msg_type: str)
```

Send a message to a running session by queuing it in the registry (WP-9004).

---

## stop_impl

```python
stop_impl(session_id: str, force: bool)
```

Stop a background session.

---

## wait_impl

```python
wait_impl(session_id: str, timeout: Any)
```

Wait for a background session to complete.

---

