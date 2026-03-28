# crew API Reference

> **Source**: `src/thegent/cli/apps/crew.py`

Logical stream: top-level crew management commands.

---

## add_agent_cmd

```python
add_agent_cmd(crew_id: str, role: str, name: str, description: str, capabilities: str, model: str) -> None
```

---

## add_task_cmd

```python
add_task_cmd(crew_id: str, description: str, dependencies: str, agent_id: str) -> None
```

---

## create_cmd

```python
create_cmd(name: str, description: str, mode: str, output: str) -> None
```

---

## execute_cmd

```python
execute_cmd(crew_file: str, cwd: str, mode: str, timeout: int, model: str) -> None
```

---

## list_cmd

---

## show_cmd

```python
show_cmd(crew_id: str) -> None
```

---

## status_cmd

```python
status_cmd(crew_id: str) -> None
```

---

