# tools_workstream_governance API Reference

> **Source**: `src/thegent/mcp/server/tools_workstream_governance.py`

Workstream/governance status tool registrations for MCP server.

---

## register_workstream_governance_tools

---

## thegent_govern_approve

```python
thegent_govern_approve(run_id: str, reason: Any)
```

Approve a HITL-blocked run (G-GP-05 / WL-019).

Reads pending approvals from governance_events.jsonl, updates status to
'approved', and triggers continuation of the blocked run.
Equivalent to: thegent govern approve <run_id> [--reason <r>]

---

## thegent_govern_reject

```python
thegent_govern_reject(run_id: str, reason: Any)
```

Reject a HITL-blocked run (G-GP-05 / WL-019).

Reads pending approvals from governance_events.jsonl, updates status to
'rejected', and cancels the blocked run.
Equivalent to: thegent govern reject <run_id> [--reason <r>]

---

## thegent_heliosShield_status

Get status from thegent.mesh harness.

---

## thegent_workstream_query

```python
thegent_workstream_query(query: str)
```

Execute SQL query on workstream database.

Returns query results as JSON. Use for exploring session/workstream data.
Example: "SELECT * FROM sessions WHERE status='running' LIMIT 10"

---

## thegent_workstream_stats

Get workstream statistics.

Returns statistics including running/completed counts, success rate,
average duration, deferred tasks, and lane breakdown.

---

