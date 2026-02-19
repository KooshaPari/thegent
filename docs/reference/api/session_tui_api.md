# session_tui API Reference

> **Source**: `src/thegent/ux/session_tui.py`

Rich TUI for session management with subagent monitoring and control.

---

## SessionTUI

Rich-based TUI for session management with subagent monitoring.

### Methods

#### SessionTUI.__init__

```python
__init__(self, session_id)
```

#### SessionTUI.manage_session

Manage a session (stop, pause, resume, logs).

```python
manage_session(self, session_id, action)
```

#### SessionTUI.render_session_view

Render detailed view for a specific session.

```python
render_session_view(self, session_id)
```

#### SessionTUI.render_sessions_list

Render list of all sessions.

```python
render_sessions_list(self)
```

#### SessionTUI.show

Show session view (single session or list).

```python
show(self, session_id)
```

#### SessionTUI.watch

Watch sessions live with auto-refresh.

```python
watch(self, session_id, interval)
```

---

## manage_session

Manage a session (stop, pause, resume, logs).

```python
manage_session(self, session_id, action)
```

---

## render_session_view

Render detailed view for a specific session.

```python
render_session_view(self, session_id)
```

---

## render_sessions_list

Render list of all sessions.

```python
render_sessions_list(self)
```

---

## show

Show session view (single session or list).

```python
show(self, session_id)
```

---

## watch

Watch sessions live with auto-refresh.

```python
watch(self, session_id, interval)
```

---

