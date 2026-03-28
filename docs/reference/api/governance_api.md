# governance API Reference

> **Source**: `src/thegent/cli/governance/governance.py`

Governance and escalation service helpers for CLI commands.

---

## _SchemaOutputModel

**Inherits from**: `BaseModel`

---

## escalate_add_impl

```python
escalate_add_impl(run_id: str, reason: str, sla_minutes: int, owner: Any, agent: Any, lane: str, priority: int)
```

WP-3008: Add a blocked run to the escalation queue.

---

## escalate_approve_impl

```python
escalate_approve_impl(run_id: str)
```

WP-3008: Approve an escalation, marking it as approved in the queue (G-GP-05).

---

## escalate_list_impl

```python
escalate_list_impl(past_sla_only: bool, limit: int)
```

WP-3008: List escalation queue items (blocked runs with SLA).

---

## escalate_resolve_impl

```python
escalate_resolve_impl(run_id: str, resolution: str)
```

WP-3008: Mark an escalation item as resolved.

---

## govern_approve_impl

```python
govern_approve_impl(run_id: str, reason: Any)
```

WL-019-B: Approve a HITL-blocked run, updating governance_events.jsonl to 'approved'.

---

## govern_get_pending_approval_impl

WL-100: Return a single pending approval event for a run.

---

## govern_list_pending_impl

WL-019-B: List all pending HITL approval events from governance_events.jsonl.

---

## govern_reject_impl

```python
govern_reject_impl(run_id: str, reason: Any)
```

WL-019-B: Reject a HITL-blocked run, updating governance_events.jsonl to 'rejected'.

---

## govern_vet_impl

WL-098: Vet a recorded run by run_id using VetterOrchestrator.

---

