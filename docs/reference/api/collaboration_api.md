# collaboration API Reference

> **Source**: `src/thegent/orchestration/collaboration.py`

WP-6008: Collaborative task resolution.

---

## CollaborativeSession

A session where multiple agents collaborate on a task.

### Methods

#### CollaborativeSession.__init__

```python
__init__(self, settings, task_id)
```

#### CollaborativeSession.broadcast_state

Broadcast state updates to all participants.

```python
broadcast_state(self, state)
```

#### CollaborativeSession.recruit_participants

Recruit external agents based on capabilities (including P2P).

```python
recruit_participants(self, needed_capabilities)
```

---

## broadcast_state

Broadcast state updates to all participants.

```python
broadcast_state(self, state)
```

---

## recruit_participants

Recruit external agents based on capabilities (including P2P).

```python
recruit_participants(self, needed_capabilities)
```

---

