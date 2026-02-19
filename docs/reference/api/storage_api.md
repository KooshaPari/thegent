# storage API Reference

> **Source**: `src/thegent/queue/storage.py`

WP-7001: Unified prompt queue storage.

---

## PromptQueue

Manages a unified queue of deferred agent prompts.

### Methods

#### PromptQueue.__init__

```python
__init__(self, session_dir)
```

#### PromptQueue.append

Append a new prompt to the queue.

```python
append(self, prompt, project, agent)
```

#### PromptQueue.get_pending_count

Return count of pending items.

```python
get_pending_count(self)
```

#### PromptQueue.list_pending

List all pending (unclaimed) items.

```python
list_pending(self)
```

---

## append

Append a new prompt to the queue.

```python
append(self, prompt, project, agent)
```

---

## get_pending_count

Return count of pending items.

```python
get_pending_count(self)
```

---

## list_pending

List all pending (unclaimed) items.

```python
list_pending(self)
```

---

