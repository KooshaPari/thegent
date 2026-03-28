# plan_workstream_state_cmds API Reference

> **Source**: `src/thegent/cli/plan/plan_workstream_state_cmds.py`

Thegent CLI plan/DAG commands domain - extracted from cli.py (WL-124).

---

## plan_claim_cmd

```python
plan_claim_cmd(item_id: str, agent_id: Any, cd: Any)
```

Claim an item in the unified work stream.

---

## plan_complete_cmd

```python
plan_complete_cmd(item_id: str, agent_id: Any, cd: Any)
```

Mark an item as complete in the unified work stream.

---

## plan_incorporate_cmd

```python
plan_incorporate_cmd(cd: Any, dry_run: bool)
```

Merge fragments from 02-UNIFIED-WBS into WORK_STREAM.md. Preserves CLAIMED and COMPLETED.

---

## plan_lint_workstream_cmd

```python
plan_lint_workstream_cmd(cd: Any)
```

Validate canonical WORK_STREAM schema structure.

---

## plan_normalize_workstream_cmd

```python
plan_normalize_workstream_cmd(cd: Any)
```

Sort and normalize WL sections and status-line formatting.

---

## plan_verify_workstream_cmd

```python
plan_verify_workstream_cmd(cd: Any, format: Any)
```

Verify WORK_STREAM invariants for CLAIMED/COMPLETED overlap by exact ID match.

---

