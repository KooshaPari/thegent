# gh_project_sync API Reference

> **Source**: `src/thegent/integrations/gh_project_sync.py`

GitHub Projects v2 Bidirectional Sync Integration (WL-157).

Provides optional, standalone-safe bidirectional syncing with GitHub Projects v2.
Skips gracefully when disabled or when gh auth lacks project scope.

Key Principles:
- Standalone-safe: No crash or side effects when disabled or gh auth missing
- Optional: Fully backward compatible; can be disabled entirely
- Bidirectional: Read/write thegent workstream to/from GitHub Projects
- Composable: Works with existing WORK_STREAM.md format

---

## GHProjectAuthError

Authentication/authorization error (e.g., missing project scope).

**Inherits from**: `GHProjectSyncError`

**Method Resolution Order**: `GHProjectAuthError -> GHProjectSyncError`

---

## GHProjectConfig

Configuration for GitHub Projects sync.

### Methods

#### GHProjectConfig.can_read

```python
can_read(self: Any)
```

Check if sync direction allows reading.

---

#### GHProjectConfig.can_write

```python
can_write(self: Any)
```

Check if sync direction allows writing.

---

#### GHProjectConfig.effective_project_number

```python
effective_project_number(self: Any)
```

Return target project number honoring sandbox mode.

---

#### GHProjectConfig.is_valid

```python
is_valid(self: Any)
```

Check if config is valid for sync operations.

---

---

## GHProjectNotFoundError

Project not found error.

**Inherits from**: `GHProjectSyncError`

**Method Resolution Order**: `GHProjectNotFoundError -> GHProjectSyncError`

---

## GHProjectSyncError

Base exception for GitHub Projects sync errors.

**Inherits from**: `Exception`

---

## can_read

```python
can_read(self: Any)
```

Check if sync direction allows reading.

---

## can_write

```python
can_write(self: Any)
```

Check if sync direction allows writing.

---

## close_or_comment_github_issue_refs

```python
close_or_comment_github_issue_refs(issue_refs: list[str])
```

Close issues and optionally post status comments.

---

## effective_project_number

```python
effective_project_number(self: Any)
```

Return target project number honoring sandbox mode.

---

## export_to_csv

```python
export_to_csv(config: GHProjectConfig, output_path: Path)
```

Export GitHub Project to CSV.

**Parameters**:

- `config`: GitHub Projects configuration
- `output_path`: Path to write CSV export

**Returns**: Dict with export results: items_exported, file_path

---

## extract_github_issue_refs

```python
extract_github_issue_refs(raw_item: dict[(str, Any)])
```

Extract issue references from a GitHub project item payload.

---

## get_project_status

```python
get_project_status(config: GHProjectConfig)
```

Get GitHub Project sync status.

**Parameters**:

- `config`: GitHub Projects configuration

**Returns**: Dict with project metadata, item count, and sync status.
Returns empty dict if sync disabled or auth unavailable.

**Raises**:

- `GHProjectSyncError`: For unexpected errors (not auth issues)

---

## import_from_csv

```python
import_from_csv(config: GHProjectConfig, csv_path: Path)
```

Import items to GitHub Project from CSV.

**Parameters**:

- `config`: GitHub Projects configuration
- `csv_path`: Path to CSV file to import

**Returns**: Dict with import results: items_imported, errors

---

## is_valid

```python
is_valid(self: Any)
```

Check if config is valid for sync operations.

---

## sync_from_github

```python
sync_from_github(config: GHProjectConfig)
```

Sync GitHub Projects to thegent workstream.

**Parameters**:

- `config`: GitHub Projects configuration

**Returns**: Dict with sync results: items_imported, errors

**Raises**:

- `GHProjectSyncError`: For unexpected errors (not auth issues)

---

## sync_to_github

```python
sync_to_github(config: GHProjectConfig, workstream_data: list[dict[(str, Any)]])
```

Sync thegent workstream to GitHub Projects.

**Parameters**:

- `config`: GitHub Projects configuration
- `workstream_data`: Workstream items (from WORK_STREAM.md or similar)

**Returns**: Dict with sync results: items_created, items_updated, errors

**Raises**:

- `GHProjectSyncError`: For unexpected errors (not auth issues)

---

