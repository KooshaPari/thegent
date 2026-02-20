# summary API Reference

> **Source**: `src/thegent/summary.py`

Summary and audit log implementation for thegent.

---

## get_chat_logs

```python
get_chat_logs(session_dir: Path, project_key: str, start_dt: datetime, end_dt: datetime)
```

Fetch chat logs from project session directory.

---

## get_git_commits

```python
get_git_commits(project_path: Path, start_dt: datetime, end_dt: datetime)
```

Fetch git commits within the time range.

---

## get_project_key

```python
get_project_key(project_path: Path)
```

Generate filesystem-safe key for project path (WP-3006).

---

## get_time_range

```python
get_time_range(period: str)
```

Resolve period string into start and end datetimes.

---

## summary_impl

```python
summary_impl(period: str, project_path: Any, summarize: bool, agent: str)
```

FR-X09: Unified summary and audit log across runs, chats, and commits.

---

