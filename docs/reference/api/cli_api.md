# cli API Reference

> **Source**: `src/thegent/task/cli.py`

CLI commands for task management.

---

## display_task_summary

Display task summary.

```python
display_task_summary(task)
```

---

## display_validation_result

Display validation result.

```python
display_validation_result(file_path, result)
```

---

## find_task_file

Find task file by ID.

```python
find_task_file(task_id, tasks_dir)
```

---

## list

List tasks.

```python
list(tasks_dir, priority, subagent)
```

---

## parse

Parse a task file and display or save result.

```python
parse(task_file, output)
```

---

## validate

Validate task file(s).

```python
validate(task_id, task_file, all, tasks_dir)
```

---

