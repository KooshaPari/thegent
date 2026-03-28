# tools_queue_mutations API Reference

> **Source**: `src/thegent/mcp/server/tools_queue_mutations.py`

Registration helpers for queue mutation MCP tools.

---

## register_queue_mutation_tools

---

## thegent_queue_add

```python
thegent_queue_add(prompt: str, project: str, agent: Any)
```

Add a prompt to the queue (deferred execution). Equivalent to $defer in prompt.

---

## thegent_queue_done

```python
thegent_queue_done(item_id: int)
```

Mark a queue item as done by id. Use id from thegent_queue_list or thegent_queue_claim.

---

## thegent_queue_edit

```python
thegent_queue_edit(item_id: int, prompt: str)
```

Edit prompt for a pending or claimed queue item. Cannot edit done items.

---

## thegent_queue_extend_lease

```python
thegent_queue_extend_lease(item_id: int, lease_seconds: int)
```

Extend lease for a claimed queue item. Use before lease expires.

---

## thegent_queue_release

```python
thegent_queue_release(item_id: int)
```

Release a claimed queue item back to pending. Use when worker cannot complete.

---

