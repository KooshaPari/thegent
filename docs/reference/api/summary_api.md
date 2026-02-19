# summary API Reference

> **Source**: `src/thegent/summary.py`

Summary and audit log implementation for thegent.

---

## get_chat_logs

Fetch chat logs from project session directory.

```python
get_chat_logs(session_dir, project_key, start_dt, end_dt)
```

---

## get_git_commits

Fetch git commits within the time range.

```python
get_git_commits(project_path, start_dt, end_dt)
```

---

## get_project_key

Generate filesystem-safe key for project path (WP-3006).

```python
get_project_key(project_path)
```

---

## get_time_range

Resolve period string into start and end datetimes.

```python
get_time_range(period)
```

---

## summary_impl

FR-X09: Unified summary and audit log across runs, chats, and commits.

```python
summary_impl(period, project_path, summarize, agent)
```

---

