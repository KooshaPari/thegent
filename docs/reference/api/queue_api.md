# queue API Reference

> **Source**: `src/thegent/cli/apps/queue.py`

thegent queue: Unified Prompt Queue CLI commands (FR-HAX-001).

Subcommands:
  add "<prompt>"  -- enqueue a task
  list            -- show pending items
  next            -- claim and print next item
  done <id>       -- mark item complete
  tui             -- show TUI (list/claim/complete UI)

# @trace FR-HAX-001

---

## queue_add

```python
queue_add(prompt: str, project: Any, output_format: str)
```

Add a task prompt to the queue.

# @trace FR-HAX-001

---

## queue_done

```python
queue_done(item_id: str, output_format: str)
```

Mark a queue item as done.

# @trace FR-HAX-001

---

## queue_list

```python
queue_list(project: Any, all_items: bool, output_format: str)
```

List pending queue items.

# @trace FR-HAX-001

---

## queue_next

```python
queue_next(project: Any, output_format: str)
```

Claim and print the next pending queue item.

Exits with code 1 if the queue is empty.

# @trace FR-HAX-001

---

## queue_tui

```python
queue_tui(watch: bool, interval: float, project: Any)
```

Show the queue in a TUI (list/claim/complete UI).

# @trace FR-HAX-001

---

