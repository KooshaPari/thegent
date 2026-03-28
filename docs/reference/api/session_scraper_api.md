# session_scraper API Reference

> **Source**: `src/thegent/orchestration/state/session_scraper.py`

## SessionScrapeRequestEvent

**Inherits from**: `TypedDict`

---

## SessionScraper

MTSP-18: Session Scraper to extract user prompts and context.

Focuses on terminal panes (tmux) and local history files.

### Methods

#### SessionScraper.__init__

```python
__init__(self: Any, project_root: Path)
```

---

#### SessionScraper.collect_all_recent_prompts

```python
collect_all_recent_prompts(self: Any)
```

Unified collection from all available scrapers.

---

#### SessionScraper.collect_snapshot

```python
collect_snapshot(self: Any, trigger: str)
```

Collect a rich, structured session snapshot for memory/documentation pipelines.

---

#### SessionScraper.export_snapshot_daily_index_markdown

```python
export_snapshot_daily_index_markdown(self: Any, limit: int, out_path: Any, root_dir: Any)
```

Persist daily snapshot index markdown.

---

#### SessionScraper.export_snapshot_index_markdown

```python
export_snapshot_index_markdown(self: Any)
```

Persist snapshot index markdown.

---

#### SessionScraper.export_snapshot_markdown

```python
export_snapshot_markdown(self: Any, snapshot_path: Path, out_path: Any)
```

Export snapshot JSON to markdown beside the source (or a provided destination).

---

#### SessionScraper.latest_snapshot

```python
latest_snapshot(self: Any)
```

Return the newest available snapshot if present.

---

#### SessionScraper.list_snapshots

```python
list_snapshots(self: Any)
```

List persisted snapshots, newest first, with optional filters.

---

#### SessionScraper.list_tags

```python
list_tags(self: Any, limit: int, root_dir: Any)
```

Return unique tags from newest snapshots ordered by frequency desc, then name.

---

#### SessionScraper.list_triggers

```python
list_triggers(self: Any, limit: int, root_dir: Any)
```

Return unique trigger names from newest snapshots in first-seen order.

---

#### SessionScraper.load_snapshot

```python
load_snapshot(self: Any, path: Path)
```

Load a snapshot JSON file into SessionSnapshot.

---

#### SessionScraper.persist_snapshot

```python
persist_snapshot(self: Any, trigger: str, out_dir: Any, request_event_id: Any, event_log: Any)
```

Persist a structured snapshot as JSON and return its path.

Optionally emit a session.scraper.snapshot.created or .failed event to event_log.

---

#### SessionScraper.persist_snapshot_daily_index

```python
persist_snapshot_daily_index(self: Any, limit: int, out_path: Any, root_dir: Any)
```

Persist daily snapshot summary index JSON.

---

#### SessionScraper.persist_snapshot_index

```python
persist_snapshot_index(self: Any)
```

Persist snapshot summary index JSON for downstream dashboards/reporting.

---

#### SessionScraper.prune_snapshots

```python
prune_snapshots(self: Any, max_keep: int, root_dir: Any)
```

Delete oldest snapshot JSON files beyond max_keep and return deleted count.

---

#### SessionScraper.scrape_ante_history

```python
scrape_ante_history(self: Any)
```

Scrape prompts from Ante user_input_history.jsonl.

---

#### SessionScraper.scrape_claude_history

```python
scrape_claude_history(self: Any)
```

Scrape prompts from local Claude history files if they exist.

---

#### SessionScraper.scrape_tmux_prompts

```python
scrape_tmux_prompts(self: Any)
```

Scrape likely user prompts from active Claude Code tmux panes.

---

#### SessionScraper.snapshot_daily_index_markdown

```python
snapshot_daily_index_markdown(summary: dict)
```

Render a compact per-day markdown index.

---

#### SessionScraper.snapshot_index_markdown

```python
snapshot_index_markdown(summary: dict[(str, Any)])
```

Render snapshot summary index as markdown.

---

#### SessionScraper.snapshot_markdown

```python
snapshot_markdown(self: Any, snapshot: SessionSnapshot)
```

Render a SessionSnapshot as concise markdown.

---

#### SessionScraper.summarize_snapshots

```python
summarize_snapshots(self: Any)
```

Build summary stats from recent snapshots for memory/research reporting.

---

#### SessionScraper.summarize_snapshots_by_day

```python
summarize_snapshots_by_day(self: Any, limit: int, root_dir: Any)
```

Build per-day totals for snapshots, prompts, commands, and files.

---

---

## SessionSnapshot

Structured snapshot of recently observed session context.

**Inherits from**: `SerializableMixin`

---

## SessionSnapshotCreatedEvent

**Inherits from**: `TypedDict`

---

## SessionSnapshotFailedEvent

**Inherits from**: `TypedDict`

---

## SnapshotSummary

**Inherits from**: `TypedDict`

---

## collect_all_recent_prompts

```python
collect_all_recent_prompts(self: Any)
```

Unified collection from all available scrapers.

---

## collect_snapshot

```python
collect_snapshot(self: Any, trigger: str)
```

Collect a rich, structured session snapshot for memory/documentation pipelines.

---

## export_snapshot_daily_index_markdown

```python
export_snapshot_daily_index_markdown(self: Any, limit: int, out_path: Any, root_dir: Any)
```

Persist daily snapshot index markdown.

---

## export_snapshot_index_markdown

```python
export_snapshot_index_markdown(self: Any)
```

Persist snapshot index markdown.

---

## export_snapshot_markdown

```python
export_snapshot_markdown(self: Any, snapshot_path: Path, out_path: Any)
```

Export snapshot JSON to markdown beside the source (or a provided destination).

---

## latest_snapshot

```python
latest_snapshot(self: Any)
```

Return the newest available snapshot if present.

---

## list_snapshots

```python
list_snapshots(self: Any)
```

List persisted snapshots, newest first, with optional filters.

---

## list_tags

```python
list_tags(self: Any, limit: int, root_dir: Any)
```

Return unique tags from newest snapshots ordered by frequency desc, then name.

---

## list_triggers

```python
list_triggers(self: Any, limit: int, root_dir: Any)
```

Return unique trigger names from newest snapshots in first-seen order.

---

## load_snapshot

```python
load_snapshot(self: Any, path: Path)
```

Load a snapshot JSON file into SessionSnapshot.

---

## persist_snapshot

```python
persist_snapshot(self: Any, trigger: str, out_dir: Any, request_event_id: Any, event_log: Any)
```

Persist a structured snapshot as JSON and return its path.

Optionally emit a session.scraper.snapshot.created or .failed event to event_log.

---

## persist_snapshot_daily_index

```python
persist_snapshot_daily_index(self: Any, limit: int, out_path: Any, root_dir: Any)
```

Persist daily snapshot summary index JSON.

---

## persist_snapshot_index

```python
persist_snapshot_index(self: Any)
```

Persist snapshot summary index JSON for downstream dashboards/reporting.

---

## prune_snapshots

```python
prune_snapshots(self: Any, max_keep: int, root_dir: Any)
```

Delete oldest snapshot JSON files beyond max_keep and return deleted count.

---

## scrape_ante_history

```python
scrape_ante_history(self: Any)
```

Scrape prompts from Ante user_input_history.jsonl.

---

## scrape_claude_history

```python
scrape_claude_history(self: Any)
```

Scrape prompts from local Claude history files if they exist.

---

## scrape_tmux_prompts

```python
scrape_tmux_prompts(self: Any)
```

Scrape likely user prompts from active Claude Code tmux panes.

---

## snapshot_daily_index_markdown

```python
snapshot_daily_index_markdown(summary: dict)
```

Render a compact per-day markdown index.

---

## snapshot_index_markdown

```python
snapshot_index_markdown(summary: dict[(str, Any)])
```

Render snapshot summary index as markdown.

---

## snapshot_markdown

```python
snapshot_markdown(self: Any, snapshot: SessionSnapshot)
```

Render a SessionSnapshot as concise markdown.

---

## summarize_snapshots

```python
summarize_snapshots(self: Any)
```

Build summary stats from recent snapshots for memory/research reporting.

---

## summarize_snapshots_by_day

```python
summarize_snapshots_by_day(self: Any, limit: int, root_dir: Any)
```

Build per-day totals for snapshots, prompts, commands, and files.

---

