# playbooks API Reference

> **Source**: `src/thegent/orchestration/playbooks.py`

Recovery playbook automation (WP-2004, FR-008).

---

## execute_playbook_step

Execute a single playbook step. Returns status dict.

```python
execute_playbook_step(session_dir, step, run_id, context)
```

---

## get_playbook_for_failure

Return ordered recovery steps for a failure (playbook).

```python
get_playbook_for_failure(error_message)
```

---

