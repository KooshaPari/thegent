# coordination API Reference

> **Source**: `src/thegent/team/coordination.py`

WP-9003: Teammate Coordination Protocol.
Handles inter-agent communication, idle detection, and task completion hooks.

---

## TeamCoordinator

Coordinates teammates during a multi-agent run.

### Methods

#### TeamCoordinator.__init__

```python
__init__(self, session_dir)
```

#### TeamCoordinator.broadcast_message

WP-9003: Broadcast a message to all teammates in a team.

```python
broadcast_message(self, team_id, sender, message)
```

#### TeamCoordinator.call_vote

WP-9003: Call a vote among teammates.

```python
call_vote(self, team_id, caller, subject, options)
```

#### TeamCoordinator.cast_vote

WP-9003: Cast a vote.

```python
cast_vote(self, team_id, vote_id, voter, option)
```

#### TeamCoordinator.detect_idle

WP-9003: Detect if a teammate agent is idle and needs input.
Looks for common patterns like 'waiting for input', 'how can I help?', etc.

```python
detect_idle(self, stdout)
```

#### TeamCoordinator.get_vote_result

WP-9003: Get current results of a vote.

```python
get_vote_result(self, team_id, vote_id)
```

#### TeamCoordinator.handle_task_completed

WP-9003: Handle a task completion event from a teammate.

```python
handle_task_completed(self, team_id, task_id, result)
```

#### TeamCoordinator.wait_for_task

WP-9003: Wait for a task to be completed by a teammate.

```python
wait_for_task(self, team_id, task_id, timeout)
```

---

## broadcast_message

WP-9003: Broadcast a message to all teammates in a team.

```python
broadcast_message(self, team_id, sender, message)
```

---

## call_vote

WP-9003: Call a vote among teammates.

```python
call_vote(self, team_id, caller, subject, options)
```

---

## cast_vote

WP-9003: Cast a vote.

```python
cast_vote(self, team_id, vote_id, voter, option)
```

---

## detect_idle

WP-9003: Detect if a teammate agent is idle and needs input.
Looks for common patterns like 'waiting for input', 'how can I help?', etc.

```python
detect_idle(self, stdout)
```

---

## get_vote_result

WP-9003: Get current results of a vote.

```python
get_vote_result(self, team_id, vote_id)
```

---

## handle_task_completed

WP-9003: Handle a task completion event from a teammate.

```python
handle_task_completed(self, team_id, task_id, result)
```

---

## wait_for_task

WP-9003: Wait for a task to be completed by a teammate.

```python
wait_for_task(self, team_id, task_id, timeout)
```

---

