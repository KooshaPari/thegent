# board_adapters API Reference

> **Source**: `src/thegent/sync/board_adapters.py`

Board sync adapter implementations for `thegent sync board`.

---

## BoardSyncAdapter

Protocol for board sync adapters.

**Inherits from**: `Protocol`

### Methods

#### BoardSyncAdapter.fetch_remote_status

```python
fetch_remote_status(self: Any, board_id: str, work_stream_items: list[dict[(str, str)]])
```

Fetch remote status mapping for local work-stream item ids.

---

#### BoardSyncAdapter.sync

```python
sync(self: Any, board_id: str, work_stream_items: list[dict[(str, str)]])
```

Sync local work-stream items to a remote board.

---

---

## GitHubBoardAdapter

GitHub Projects adapter backed by existing WL-157 integration.

### Methods

#### GitHubBoardAdapter.fetch_remote_status

```python
fetch_remote_status(self: Any, board_id: str, work_stream_items: list[dict[(str, str)]])
```

---

#### GitHubBoardAdapter.sync

```python
sync(self: Any, board_id: str, work_stream_items: list[dict[(str, str)]])
```

---

---

## LinearBoardAdapter

Linear adapter using GraphQL API (issue upsert by WL-tagged title).

### Methods

#### LinearBoardAdapter.fetch_remote_status

```python
fetch_remote_status(self: Any, board_id: str, work_stream_items: list[dict[(str, str)]])
```

---

#### LinearBoardAdapter.sync

```python
sync(self: Any, board_id: str, work_stream_items: list[dict[(str, str)]])
```

---

---

## fetch_remote_status

```python
fetch_remote_status(self: Any, board_id: str, work_stream_items: list[dict[(str, str)]]) -> dict[(str, str)]
```

---

## resolve_board_adapter

```python
resolve_board_adapter(source: str)
```

Resolve adapter implementation for board source.

---

## sync

```python
sync(self: Any, board_id: str, work_stream_items: list[dict[(str, str)]]) -> dict[(str, Any)]
```

---

