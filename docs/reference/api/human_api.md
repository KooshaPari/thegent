# human API Reference

> **Source**: `src/thegent/tools/human.py`

Human-in-the-loop tools for thegent (WP-4009).

---

## HumanInputRequest

Request for human intervention or clarification.

**Inherits from**: `BaseModel`

---

## ask_human

WP-4009: Human-as-a-Tool (HaaT).
Pauses execution and waits for human input via the Cockpit or CLI.

```python
ask_human(prompt, options)
```

---

