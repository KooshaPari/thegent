# playbooks API Reference

> **Source**: `src/thegent/orchestration/playbooks.py`

Recovery playbook automation (WP-2004, FR-008).

---

## execute_playbook_step

```python
execute_playbook_step(session_dir: Path, step: str, run_id: str, context: Any)
```

Execute a single playbook step. Returns status dict.

---

## get_playbook_for_failure

```python
get_playbook_for_failure(error_message: str)
```

Return ordered recovery steps for a failure (playbook).

---

