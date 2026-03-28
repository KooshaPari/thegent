# server_journal_tools API Reference

> **Source**: `src/thegent/mcp/server_journal_tools.py`

Journal/orchestration-event MCP tool registration helpers.

---

## journal_create_enhanced

```python
journal_create_enhanced(session_id: str, repo_path: str, track_secrets: bool, enable_watching: bool, enable_attestation: bool, batch_size: int)
```

Create an enhanced git journal session with P1 features.

---

## journal_create_session

```python
journal_create_session(session_id: str, repo_path: str, track_secrets: bool)
```

Create a new git journal session for micro-commit audit trail.

---

## journal_finalize

```python
journal_finalize(session_id: str, message: str, repo_path: str)
```

Finalize a journal session with a summary commit.

---

## journal_flush_batch

```python
journal_flush_batch(session_id: str, repo_path: str)
```

Flush pending batched changes as a single commit.

---

## journal_get_attestations

```python
journal_get_attestations(session_id: str, repo_path: str)
```

Get cryptographic attestations for a journal session.

---

## journal_get_log

```python
journal_get_log(session_id: str, repo_path: str)
```

Get the audit log for a journal session.

---

## journal_get_stats

```python
journal_get_stats(session_id: str, repo_path: str)
```

Get performance statistics for a journal session.

---

## journal_list_sessions

```python
journal_list_sessions(repo_path: str)
```

List all git journal sessions in a repository.

---

## journal_prune

```python
journal_prune(repo_path: str, max_age_days: int)
```

Prune old journal sessions.

---

## journal_record_change

```python
journal_record_change(session_id: str, file_path: str, action: str, repo_path: str, content: Any)
```

Record a file change as a micro-commit in the journal.

---

## journal_snapshot

```python
journal_snapshot(session_id: str, message: str, repo_path: str)
```

Create a snapshot of the current working tree state.

---

## journal_start_watching

```python
journal_start_watching(session_id: str, repo_path: str)
```

Start real-time file watching for a journal session.

---

## register_journal_tools

Register journal and orchestration-event MCP tools.

---

## thegent_orchestration_events

```python
thegent_orchestration_events(max_events: int, timeout_ms: int)
```

WL-085: Drain SubAgentEvents from the process-global event queue.

---

