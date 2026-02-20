# cli API Reference

> **Source**: `src/thegent/task/cli.py`

CLI commands for task management.

---

## claim

```python
claim(task_id: str, agent_id: str, work_stream: Path)
```

Claim a task (move from BACKLOG to CLAIMED in WORK_STREAM.md).

---

## complete

```python
complete(task_id: str, agent_id: str, work_stream: Path)
```

Complete a task (move from CLAIMED to COMPLETED in WORK_STREAM.md).

---

## display_task_summary

```python
display_task_summary(task: dict)
```

Display task summary.

---

## display_validation_result

```python
display_validation_result(file_path: Path, result: ValidationResult)
```

Display validation result.

---

## find_task_file

```python
find_task_file(task_id: str, tasks_dir: Path)
```

Find task file by ID.

---

## list_tasks

```python
list_tasks(tasks_dir: Path, priority: Any, subagent: Any)
```

List tasks.

---

## migrate

```python
migrate(work_stream: Path, tasks_dir: Path, dry_run: bool, legacy_file: Any)
```

Migrate legacy task formats to YAML frontmatter format.

---

## parse

```python
parse(task_file: Path, output: Any)
```

Parse a task file and display or save result.

---

## status

```python
status(task_id: str, work_stream: Path)
```

Get status of a task in WORK_STREAM.md.

---

## sync

```python
sync(work_stream: Path, tasks_dir: Path, direction: str)
```

Sync task files with WORK_STREAM.md.

---

## validate

```python
validate(task_id: Any, task_file: Any, all: bool, tasks_dir: Path)
```

Validate task file(s).

---

