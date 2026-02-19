# manager API Reference

> **Source**: `src/thegent/team/manager.py`

WP-6008: Multi-agent team management and task coordination.

---

## TeamManager

Manages multi-agent teams and their shared task lists.

### Methods

#### TeamManager.__init__

```python
__init__(self, session_dir)
```

#### TeamManager.add_task

Add a task to the team's shared list.

```python
add_task(self, team_id, title, description, dependencies)
```

#### TeamManager.assign_task

Assign a task to an agent.

```python
assign_task(self, team_id, task_id, agent_id)
```

#### TeamManager.create_team

Create a new team and return its ID.

```python
create_team(self, name, leader, teammates)
```

#### TeamManager.list_tasks

List all tasks for a team.

```python
list_tasks(self, team_id)
```

#### TeamManager.update_task

Update a task's fields.

```python
update_task(self, team_id, task_id, updates)
```

---

## add_task

Add a task to the team's shared list.

```python
add_task(self, team_id, title, description, dependencies)
```

---

## assign_task

Assign a task to an agent.

```python
assign_task(self, team_id, task_id, agent_id)
```

---

## create_team

Create a new team and return its ID.

```python
create_team(self, name, leader, teammates)
```

---

## list_tasks

List all tasks for a team.

```python
list_tasks(self, team_id)
```

---

## update_task

Update a task's fields.

```python
update_task(self, team_id, task_id, updates)
```

---

