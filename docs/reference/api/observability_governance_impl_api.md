# observability_governance_impl API Reference

> **Source**: `src/thegent/cli/commands/observability_governance_impl.py`

Observability governance, review, and compliance implementations (WL-120).

Governance approval/rejection, code review, data protection, sitback dashboard.

---

## get_compliance_report_impl

Generate compliance evidence retention report (WP-3006).

---

## get_data_protection_status_impl

Return status of data protection and privacy controls (WP-3006).

---

## get_server_meta_impl

Return server metadata dict for thegent://meta resource.

---

## govern_approve_impl

```python
govern_approve_impl(run_id: str, reason: Any)
```

WL-019-B: Approve a HITL-blocked run, updating governance_events.jsonl to 'approved'.

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

```python
govern_vet_impl(run_id: str, policy: str, session: Any, dry_run: bool)
```

WL-098: Evaluate an existing run against Vetter policy checks.

---

## review_impl

```python
review_impl(prompt: str, agent: Any, model: Any)
```

WL-107: Read-only agent review turn with structured output.

---

## sitback_dashboard_impl

```python
sitback_dashboard_impl(profile: str)
```

Unified sitback dashboard: sessions, cockpit (circuits, drift, budget), terminals.

---

